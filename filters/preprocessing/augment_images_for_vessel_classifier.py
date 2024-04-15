import argparse
from pathlib import Path
import random
from torchvision import transforms
from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_dir", type=str, default="data/shipsnet")
    parser.add_argument("--output_dir", type=str, default="data/shipsnet_augmented")
    parser.add_argument("--split", type=float, default=0.8)
    parser.add_argument("--augment_factor", type=int, default=10)
    args = parser.parse_args()
    root_dir = Path(args.root_dir)
    output_dir = Path(args.output_dir)
    (output_dir/"train").mkdir(exist_ok=True, parents=True)
    (output_dir/"val").mkdir(exist_ok=True, parents=True)
    output_dir.mkdir(exist_ok=True, parents=True)
    input_imgs = list(root_dir.glob("*.png"))
    # Shuffle the images
    random.shuffle(input_imgs)
    train_imgs = input_imgs[:int(len(input_imgs) * args.split)]
    val_imgs = input_imgs[int(len(input_imgs) * args.split):]
    image_augment_transform = transforms.AutoAugment()
    for img in train_imgs:
        img_name = img.name
        img_label = int(img_name[0])
        image = Image.open(img)
        for i in range(args.augment_factor):
            augmented_image = image_augment_transform(image)
            augmented_image.save(output_dir/"train" /
                                 f"{img_label}_{i}_{img_name}")
    for img in val_imgs:
        img_name = img.name
        img_label = int(img_name[0])
        image = Image.open(img)
        image.save(output_dir/"val"/img_name)


if __name__ == "__main__":
    main()
