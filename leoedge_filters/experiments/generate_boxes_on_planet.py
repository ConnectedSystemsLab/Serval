# %%
import pickle
from util import rotate_image
from imutils.object_detection import non_max_suppression
import tifffile
import cv2
import numpy as np
import torch
from image_classifier.model import get_model
from argparse import ArgumentParser
from pathlib import Path
from matplotlib import pyplot as plt


# %%


def find_regions(image, method):

    ss = cv2.ximgproc.segmentation.createSelectiveSearchSegmentation()
    ss.setBaseImage(image)

    if method == 'fast':
        ss.switchToSelectiveSearchFast()
    else:
        ss.switchToSelectiveSearchQuality()

    rects = ss.process()
    boxes = []
    for (x, y, w, h) in rects:

        boxes.append([x, y, w, h])
        pass

    return boxes


def apply_color_curve(image, parameter_file):
    popts = pickle.load(open(parameter_file, "rb"))

    def transform(x, a, b, c):
        y = a*np.log(x+b)+c
        y = np.clip(y, 0, 255)
        return y

    def red_curve(x):
        return transform(x, *popts[0])

    def green_curve(x):
        return transform(x, *popts[1])

    def blue_curve(x):
        return transform(x, *popts[2])
    return np.array(np.stack([red_curve(image[:, :, 2]), green_curve(image[:, :, 1]), blue_curve(image[:, :, 0])], axis=2))


def process_image(image, model, device='cuda', mode='fast', chip_size=1024, batch_size=32, threshold=0.5):
    probs, locs = [], []
    original_image = np.ascontiguousarray(np.array(image))
    for x0 in range(0, image.shape[0], chip_size//2):
        for y0 in range(0, image.shape[1], chip_size//2):
            _rois, _locs = [], []
            chip = image[x0:x0+chip_size, y0:y0+chip_size]
            png_chip = np.array(np.clip(chip*255, 0, 255), dtype=np.uint8)
            boxes = find_regions(png_chip, mode)
            for (x, y, w, h) in boxes:
                roi = chip[y:y+h, x:x+w]
                roi = cv2.resize(roi, (80, 80))
                roi = roi.transpose(2, 0, 1)
                _rois.append(roi)
                _locs.append((y+x0, x+y0, y+h+x0, x+w+y0))
            with torch.no_grad():
                for i in range(0, len(_rois), batch_size):
                    batch = np.array(_rois[i:i+batch_size], dtype=np.float32)
                    batch = torch.from_numpy(batch).to(device)
                    output = model(batch)
                    output = torch.nn.functional.softmax(output, dim=1)
                    for j in range(output.shape[0]):
                        if output[j, 1] > threshold:
                            locs.append(_locs[i+j])
                            probs.append(output[j, 1].item())
    selected_boxes = non_max_suppression(np.array(locs), probs)
    # Mark the image with the selected boxes
    for (x1, y1, x2, y2) in selected_boxes:
        cv2.rectangle(original_image, (y1, x1), (y2, x2), (0, 1, 0), 2)
    # Convert boxes to yolov5 format
    yolo_lines = []
    for (y1, x1, y2, x2) in selected_boxes:
        assert 0 <= x1 <= image.shape[1] and 0 <= x2 <= image.shape[1]
        assert 0 <= y1 <= image.shape[0] and 0 <= y2 <= image.shape[0]
        xc = (x1+x2)/2
        yc = (y1+y2)/2
        w = abs(x2-x1)
        h = abs(y2-y1)
        yolo_lines.append(
            f"0 {xc/image.shape[1]} {yc/image.shape[0]} {w/image.shape[1]} {h/image.shape[0]}")
    return yolo_lines, original_image


# %%
def main():
    parser = ArgumentParser()
    parser.add_argument('--model', type=str,
                        default='resnet', help='Model to use')
    parser.add_argument('--cfg', type=str,
                        default='[2, []]', help='Model config')
    parser.add_argument('--weight', type=str,
                        default='results/model/ship_classifier.pth', help='Trained weight to use')
    parser.add_argument('--images', type=str,
                        default='/projects/vasishtgroup/yutao4/planet_data/ca_20day/images_sorted', help='Image to process')
    parser.add_argument('--output', type=str,
                        default='results/yolo_training', help='Output image folder')
    parser.add_argument('--threshold', type=float, default=0.5,
                        help='Threshold for positive detection')
    parser.add_argument('--batch_size', type=int, default=32,
                        help='Batch size for inference')
    parser.add_argument('--chip_size', type=int, default=256,
                        help='Chip size for inference')
    parser.add_argument('--mode', type=str, default='fast',
                        help='Mode for selective search')
    parser.add_argument('--device', type=str,
                        default='cuda', help='Device to use')
    parser.add_argument('--save_marked_image', action='store_true',
                        help='Save marked image', default=False)
    parser.add_argument('--job_array_index', type=int,
                        default=0, help='Job array index')
    parser.add_argument('--job_array_size', type=int,
                        default=1, help='Job array size')
    parser.add_argument('-output_image_size', type=int,
                        default=1280, help='Output image size')
    args = parser.parse_args()
    print(args)
    print("Generating model...")
    model = get_model(args.model, eval(args.cfg))
    if args.device == 'cuda':
        model = model.cuda()
    elif args.device == 'cpu':
        model = model.cpu()
    print("Loading weight...")
    best_weight = torch.load(
        args.weight, map_location=torch.device(args.device))
    model.load_state_dict(best_weight)
    cv2.setUseOptimized(True)
    model.eval()
    print("Creating output folder...")
    root_dir = Path(args.output)
    root_dir.mkdir(exist_ok=True)
    images_dir = root_dir / 'images'
    images_dir.mkdir(exist_ok=True)
    labels_dir = root_dir / 'labels'
    labels_dir.mkdir(exist_ok=True)
    marked_dir = root_dir / 'marked'
    marked_dir.mkdir(exist_ok=True)
    print("Processing images...")
    for (lineno, line) in enumerate(open(args.images)):
        try:
            print(f"Processing image {line}...")
            if lineno % args.job_array_size != args.job_array_index:
                continue
            image = tifffile.imread(line.strip())
            image = np.array(image)
            image_name = line.strip().split('/')[-1].split('.')[0]
            # Convert image to visual and rotate
            image = rotate_image(image)
            image = apply_color_curve(image, "results/model/transform.pkl")/255
            # split image into output image size
            chip_count = 0
            for i in range(0, image.shape[0], args.output_image_size):
                for j in range(0, image.shape[1], args.output_image_size):
                    print(f"Processing chip {chip_count}...")
                    image_chip = image[i:i+args.output_image_size,
                                       j:j+args.output_image_size]
                    result, image_chip_processed = process_image(image=np.array(image_chip), model=model, chip_size=args.chip_size,
                                                                 batch_size=args.batch_size, threshold=args.threshold, device=args.device, mode=args.mode)
                    if args.save_marked_image:
                        plt.imsave(
                            str(marked_dir / f"{lineno}_{chip_count}.jpg"), image_chip_processed)
                    print("Total number of boxes: ", len(result))
                    with open(labels_dir / f"{lineno}_{chip_count}.txt", 'w+') as f:
                        for line in result:
                            f.write(line)
                            f.write('\n')
                    plt.imsave(
                        str(images_dir / f"{lineno}_{chip_count}.jpg"), image_chip)
                    chip_count += 1
        except Exception as e:
            print(e)
            raise


# %%
if __name__ == "__main__":
    main()
