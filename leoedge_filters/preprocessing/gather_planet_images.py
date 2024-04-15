from pathlib import Path
from argparse import ArgumentParser
from random import random

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--root', type=str, required=True,
                        help='Root directory of the images', action='append')
    parser.add_argument('--portion', type=float, required=True,
                        help='Portion of the images to use', action='append')
    parser.add_argument('--output', type=str, required=True,
                        help='Output directory')
    args = parser.parse_args()
    assert len(args.root) == len(args.portion), "Number of roots and portions must be equal"
    with open(args.output, 'w+') as f:
        for root in args.root:
            for path in Path(root).iterdir():
                for image in Path(path, "PSScene").glob('*AnalyticMS.tif'):
                    if random() < float(args.portion[args.root.index(root)]):
                        f.write(image.absolute().as_posix() + '\n')
