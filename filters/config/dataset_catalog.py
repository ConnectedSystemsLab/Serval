import re
import random
import numpy as np
from PIL import Image
from pathlib import Path
import torch
from torch.utils.data import Dataset
from util import scale_image

class DatasetCatalog:
    @staticmethod
    def get_dataset(dataset_type,dataset_path,**kwargs):
        dataset_creation_function=getattr(DatasetCatalog,f'get_{dataset_type}')
        return dataset_creation_function(dataset_path,**kwargs)
    
    @staticmethod
    def get_shipsnet(dataset_path):
        images=list(Path(dataset_path).glob("*.png"))
        random.shuffle(images)
        dataset=ShipsNet(images,transform=scale_image)
        return dataset
    
    @staticmethod
    def get_cloud(dataset_path):
        images=list(Path(dataset_path).glob("*.npy"))
        random.shuffle(images)
        dataset=CloudDataset(images)
        return dataset


def build_train_and_val_shipsnet_dataset(root_dir, split=0.8):
    root_dir = Path(root_dir)
    train_dir = root_dir/"train"
    val_dir = root_dir/"val"
    train_imgs = list(train_dir.glob("*.png"))
    val_imgs = list(val_dir.glob("*.png"))
    random.shuffle(train_imgs)
    random.shuffle(val_imgs)
    train_dataset=ShipsNet(train_imgs)
    val_dataset=ShipsNet(val_imgs)
    return train_dataset, val_dataset

class ShipsNet(Dataset):
    def __init__(self, imgs,transform=None):
        self.imgs=imgs
        self.transform=transform
        super().__init__()
    
    def __len__(self):
        return len(self.imgs)

    def __getitem__(self, idx):
        img_path = self.imgs[idx]
        img = Image.open(img_path).convert("RGB")
        img = np.array(img,dtype=np.float32)
        if self.transform is not None:
            img=self.transform(img)
        img=img.transpose(2,0,1)/255
        img_name= img_path.name
        img_label=int(img_name[0])
        return img, img_label

class CloudDataset(Dataset):
    def __init__(self, imgs,transform=None):
        self.imgs=imgs
        self.transform=transform
        super().__init__()
    
    def __len__(self):
        return len(self.imgs)

    def __getitem__(self, idx):
        img_path = self.imgs[idx]
        img=np.load(img_path).astype(np.float32).transpose(2,0,1)
        img_name= img_path.name
        img_label=int(img_name[0])
        return img, img_label