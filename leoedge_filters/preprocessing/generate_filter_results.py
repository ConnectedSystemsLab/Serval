import logging
import os
import numpy as np
from datetime import datetime
from config.load_models import load_models
import argparse
from tifffile import imread
from util import rotate_image
import re
import pickle
import cv2

def evaluate_on_image(img,filter):
    img=rotate_image(img)
    img=img.astype(np.float32)
    start_time=datetime.now()
    prediction=filter(img)
    end_time=datetime.now()
    runtime=(end_time-start_time).total_seconds()
    logging.getLogger("Evaluate").debug(f"result: {prediction} in {runtime} seconds")
    results=[prediction,runtime]
    return results

def extract_image_id_from_path(path):
    image_name=path.split("/")[-1].split(".")[0]
    pattern=re.compile(r"([0-9]{8}_[0-9]{6}(_[0-9]{2}){0,1}_[0-9a-z]+)")
    match=pattern.match(image_name)
    if match is None:
        raise ValueError(f"Could not extract image id from {path}")
    return match.group(1)

import random
if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument('--log_file', type=str, default='log.log')
    parser.add_argument('--config_file', type=str, default='/home/ochabra2/fileInfo/firstDay')
    parser.add_argument('--array_id', type=int, default=0)
    parser.add_argument('--array_size', type=int, default=0)
    parser.add_argument('--debug', action='store_true', default=False)
    parser.add_argument('--device', type=str, default='cuda')
    parser.add_argument('--output_folder', type=str, default='results/filter_results')
    parser.add_argument('--filter_name', type=str, required=True, help="Filter types: fire, cloud, forest")
    args=parser.parse_args()
    models=load_models(device=args.device)
    model=models[args.filter_name]
    logging.basicConfig(
		filename=args.log_file,
		level=logging.INFO if not args.debug else logging.DEBUG,
		format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(name)s: %(levelname)s - %(message)s',
		datefmt='%H:%M:%S'
	)
    f = open(args.config_file, "r")
    lines = f.readlines()
    # random.shuffle(lines)
    f.close()

    newLines = []
    for f in lines:
        t = f.replace("\n", "")
        if t == "":
            continue
        newLines.append(t)
    if args.array_size > 0:
        newLines = newLines[args.array_id::args.array_size]
    if args.filter_name == "forest":
        l = {extract_image_id_from_path(i):evaluate_on_image(cv2.imread(i),model) for i in newLines}
    else:
        l = {extract_image_id_from_path(i):evaluate_on_image(imread(i),model) for i in newLines}
    os.makedirs(f"results/filter_results/{args.filter_name}", exist_ok=True)
    with open(f"results/filter_results/{args.filter_name}/{args.array_id}.pkl", "wb+") as f:
        pickle.dump(l, f)
    print("Done")
