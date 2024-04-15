import os
import argparse
import numpy as np
import pickle
from PIL import Image
from matplotlib import pyplot as plt
import tifffile
from util import rotate_image

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

def process_image(image_path, output_path, parameter_file):
    try:
        # Open image and apply color curve transform
        img_arr= tifffile.imread(image_path)
        img_arr=np.ascontiguousarray(img_arr)
        img_arr = rotate_image(img_arr)
        transformed_img = apply_color_curve(img_arr, parameter_file)/255
        
        # Save transformed image as JPEG
        filename = os.path.splitext(os.path.basename(image_path))[0]
        output_filename = os.path.join(output_path, f"{filename}.jpeg")
        plt.imsave(output_filename, transformed_img)
            
        print(f"Processed {image_path}")
        
    except Exception as e:
        print(f"Error processing {image_path}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Apply color curve transform to all .tif images in a directory and its subdirectories.')
    parser.add_argument('--image_list', type=str, help='Path to the directory containing the .tif images')
    parser.add_argument('--output_path', type=str, help='Path to the directory where the transformed .jpeg images will be saved')
    parser.add_argument('--parameter_file', type=str, help='Path to the parameter file for the color curve transform', default="results/model/transform.pkl")
    parser.add_argument('--job_array_index', type=int, help='Index of the job array', default=0)
    parser.add_argument('--job_array_size', type=int, help='Size of the job array', default=1)
    args = parser.parse_args()
    os.makedirs(args.output_path, exist_ok=True)
    with open(args.image_list, 'r') as f:
        image_list = f.readlines()

    print(len(image_list))
    for i, image_path in enumerate(image_list):
        if i % args.job_array_size == args.job_array_index:
            process_image(image_path.strip(), args.output_path, args.parameter_file)
