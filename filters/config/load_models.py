import cv2
import torch
import sys

from util import scale_image
from .model_wrappers import *
from torchvision import transforms
from PIL import Image

sys.path.append("/home/yutao4/leoedge_filters/image_classifier")
sys.path.append("/home/janveja2/leoedge_filters/image_classifier")

def load_models(device='cpu'):
    # vessel_model=torch.load("vessel_model.pt")
    # vessel_model.eval()
    fire_model=torch.load("/projects/vasishtgroup/latest_models/fire_model.pkl", map_location=torch.device(device))
    if isinstance(fire_model,torch.nn.DataParallel):
        fire_model=fire_model.module
    fire_model=fire_model.to(device)
    fire_model.eval()
    cloud_model=torch.load("/projects/vasishtgroup/latest_models/cloud_model.pkl", map_location=torch.device(device))
    cloud_model.eval()
    if isinstance(cloud_model,torch.nn.DataParallel):
        cloud_model=cloud_model.module
    cloud_model=cloud_model.to(device)
    forest_model=torch.load("/projects/vasishtgroup/forest_trial3-moredata_resnet_[2, None]", map_location=torch.device(device))
    if isinstance(forest_model,torch.nn.DataParallel):
        forest_model=forest_model.module
    forest_model=forest_model.to(device)

    cloud_model=build_cv_image_filter(cloud_model,device=device,transform_function=lambda x:scale_image(x))
    forest_model.eval()
    fire_model=build_cv_image_filter(fire_model,chip_size=(-1,-1),device=device,transform_function=lambda x: cv2.normalize(x, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F))


    def preprocess_forest_image(x):
        # x = 1024*(x/65536)
        x = x[:,:,0:3:1] # want to use only rgb channels for now
        x = 3*x.astype('uint8') # pixel values above 255 have to capped to 255
        x = Image.fromarray(x)
        data_transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
        x=data_transform(x)
        x=x.numpy().transpose(1,2,0)
        return x

    forest_model=build_cv_image_filter(forest_model,transform_function=preprocess_forest_image,device=device)
    return {
        "fire":fire_model,
        "cloud":cloud_model,
        "forest":forest_model
    }
