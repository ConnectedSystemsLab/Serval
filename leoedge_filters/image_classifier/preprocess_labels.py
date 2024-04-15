from multiprocessing import Pool

import numpy as np
import re
from pathlib import Path


def process_item(args):
    label_subdir = args
    label_mat = np.load(str(label_subdir / 'labels.npy'))
    value, count = np.unique(label_mat, return_counts=True)
    label = value[np.argmax(count)] - 1
    with open(str(label_subdir / 'labels.txt'), 'w+') as f:
        f.write(str(label))


if __name__ == '__main__':
    img_dir = Path(__file__).parent.parent / 'data' / 'img'
    label_dir = Path(__file__).parent.parent / 'data' / 'label'
    pool = Pool()
    args = []
    pool.map(process_item, label_dir.iterdir())
