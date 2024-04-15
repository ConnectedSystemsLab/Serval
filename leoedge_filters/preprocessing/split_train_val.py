import argparse
from pathlib import Path
import numpy as np
import shutil


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root_dir", type=str, default="data/cloud_training_data")
    parser.add_argument("--output_dir", type=str, default="data/cloud_training_data_split")
    parser.add_argument("--split", type=float, default=0.8)
    args=parser.parse_args()
    root_dir=Path(args.root_dir)
    output_dir=Path(args.output_dir)
    print(output_dir)
    (output_dir/"train").mkdir(exist_ok=True,parents=True)
    (output_dir/"val").mkdir(exist_ok=True,parents=True)
    for img in root_dir.iterdir():
        random_numbe=np.random.uniform(0,1)
        if random_numbe<args.split:
            shutil.copy(img,output_dir/"train")
        else:
            shutil.copy(img,output_dir/"val")


if __name__ == "__main__":
    main()