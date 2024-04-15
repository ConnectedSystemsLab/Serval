import re

import numpy as np
from PIL import Image
from pathlib import Path
from torch.utils.data import Dataset


class PlanetImage(Dataset):
    def __init__(self, config_file, split=None, debug=False, transform=None):
        super().__init__()
        self.img_file, self.label_file = [], []
        with open(str(config_file)) as f:
            for line in f:
                img_file, label_file = line.split()
                self.img_file.append(img_file)
                self.label_file.append(label_file)
        self.split = split
        self.debug = debug
        self.transform = transform
        if self.split:
            start, end = self.split
            self.img_file = self.img_file[int(start * len(self.img_file)):int(end * len(self.img_file))]
            self.label_file = self.label_file[int(start * len(self.label_file)):int(end * len(self.label_file))]


    def __len__(self):
        return len(self.img_file)

    def __getitem__(self, idx):
        img = np.load(self.img_file[idx])
        label = np.load(self.label_file[idx]).item()
        return img.astype(dtype=np.float32).transpose((2, 0, 1)), int(label) if int(label) <= 1 else 0


class LandCoverNet(Dataset):
    def __init__(self, image_root_dir, label_root_dir, split=None, debug=False, transform=None):
        super().__init__()
        self.img_root = Path(image_root_dir).absolute()
        name_pattern = re.compile('ref_landcovernet_v1_source_([0-9A-Z]{5})_([0-9]{2})_[0-9]{8}')
        self.img_files = [x for x in self.img_root.iterdir() if name_pattern.fullmatch(x.name) is not None]
        self.label_root = Path(label_root_dir).absolute()
        self.split = split
        self.debug = debug
        self.transform = transform

    def __len__(self):
        return len(self.img_files)

    def __getitem__(self, idx):
        img_folder_name = self.img_files[idx]
        image_subdir = Path(img_folder_name)
        name_pattern = re.compile('ref_landcovernet_v1_source_([0-9A-Z]{5})_([0-9]{2})_[0-9]{8}')
        match = name_pattern.fullmatch(img_folder_name.name)
        tile, number = match.group(1), match.group(2)
        label_folder_name = f'ref_landcovernet_v1_labels_{tile}_{number}'
        label_subdir = self.label_root / label_folder_name
        img = np.asarray([
            np.array(Image.open(str(image_subdir / 'B04.tif'))),
            np.array(Image.open(str(image_subdir / 'B03.tif'))),
            np.array(Image.open(str(image_subdir / 'B02.tif')))
        ], dtype=np.float32)
        img = img.transpose((1, 2, 0))
        with open(str(label_subdir / 'labels.txt')) as f:
            label = str(f.readline())
        if self.transform:
            img = self.transform(img)
        return img, int(label)

# data_dir = 'data/hymenoptera_data'
# image_datasets = {x: datasets.ImageFolder(os.path.join(data_dir, x),
#                                          data_transforms[x])
#                  for x in ['train', 'val']}
# dataloaders = {x: torch.utils.data.DataLoader(image_datasets[x], batch_size=4,
#                                             shuffle=True, num_workers=4)
#             for x in ['train', 'val']}
# dataset_sizes = {x: len(image_datasets[x]) for x in ['train', 'val']}
# class_names = image_datasets['train'].classes

# device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
