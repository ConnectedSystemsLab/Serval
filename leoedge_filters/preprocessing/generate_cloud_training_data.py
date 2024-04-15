import argparse
import os
import numpy as np

import tifffile
from util import rotate_image,scale_image
from pathlib import Path
if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_catalog', type=str, default='data/ca_20day/image_files_sorted')
    parser.add_argument('--udm_catalog', type=str, default='data/ca_20day/udm_files_sorted')
    parser.add_argument('--output_dir', type=str, default='data/cloud_training_data')
    parser.add_argument('--base_dir', type=str, default='data/ca_20day/')
    parser.add_argument('--chips_per_image', type=int, default=1)
    parser.add_argument('--chip_size', type=int, default=256)
    parser.add_argument('--threshold', type=float, default=0.5)
    parser.add_argument('--job_array_index', type=int, default=0)
    parser.add_argument('--job_array_size', type=int, default=1)
    args=parser.parse_args()
    base_dir=args.base_dir
    image_catalog=open(args.image_catalog).readlines()
    image_catalog=[base_dir+x.strip() for x in image_catalog]
    image_catalog=image_catalog[args.job_array_index::args.job_array_size]
    udm_catalog=open(args.udm_catalog).readlines()
    udm_catalog=[base_dir+x.strip() for x in udm_catalog]
    udm_catalog=udm_catalog[args.job_array_index::args.job_array_size]
    output_dir=Path(args.output_dir)
    output_dir.mkdir(exist_ok=True,parents=True)
    for image_file,udm_file in zip(image_catalog,udm_catalog):
        image=tifffile.imread(image_file)
        udm=tifffile.imread(udm_file)[5,:,:]
        print(image.shape,udm.shape)
        combined=np.concatenate([image,udm[:,:,None]],axis=2)
        combined=rotate_image(combined)
        udm=combined[:,:,4]
        image=combined[:,:,0:4]
        image=scale_image(image)
        image=np.clip(image,0,1)
        for i in range(args.chips_per_image):
            x0=np.random.randint(0,image.shape[0]-args.chip_size)
            y0=np.random.randint(0,image.shape[1]-args.chip_size)
            chip=image[x0:x0+args.chip_size,y0:y0+args.chip_size]
            udm_chip=udm[x0:x0+args.chip_size,y0:y0+args.chip_size]
            if np.average(udm_chip)>args.threshold:
                label=1
            else:
                label=0
            chip_file=output_dir/f"{label}_{image_file.split('/')[-1].split('.')[0]}_{i}.npy"
            np.save(chip_file,chip)
