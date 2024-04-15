import numpy as np
from leoedge_filters.config.load_models import load_models as load_nn_models
from leoedge_filters.yolov5.models.common import DetectMultiBackend
from leoedge_filters.preprocessing.apply_color_curve_for_yolo import apply_color_curve
from leoedge_filters.yolov5.utils.augmentations import letterbox
import torch
from copy import deepcopy


def load_models(device="x"):
    models = {}
    nn_models = load_nn_models(device)
    models = {name: wrap_nn_functions(nn_models[name]) for name in nn_models}
    models['forest_model'] = models['forest']
    ca_list = open("ca_files").read().splitlines()
    forest_list = open("forest").read().splitlines()
    models['forest'] = forest_historical_data(forest_list)
    models["california"] = california(ca_list)
    models["port"] = port

    # TODO(@ochabra2) copy your model weight and set the paths here, change the image size the same as you did profiling
    models["vessel"] = build_yolo_model(
        "/projects/vasishtgroup/omWork/yolov5/runs/train/exp16/weights/best.pt",
        device,
        "/home/yutao4/leoedge_filters/results/model/transform.pkl",
        640,
    )
    return models

def wrap_nn_functions(nn_function):
    def wrapped_nn_function(image,*args,**kwargs):
        return nn_function(image.data), []
    return wrapped_nn_function

# the dictionary look-up models not defined in leoedge_filters/config/load_models.py
def california(image, california_image_list=[],*args,**kwargs):
    return image.name in california_image_list, []

def port(image, port_image_list=[],*args,**kwargs):
    return image.name in port_image_list, []

def forest_historical_data(image, forest_historical_data_list=[],*args,**kwargs):
    return image.name in forest_historical_data_list, []

def build_yolo_model(yolo_weight_file, device, color_curve_files, image_size):
    yolo_model = DetectMultiBackend(weights=yolo_weight_file, device=device)

    def detect_vessels(image,*args,**kwargs):
        image_data = np.array(image.data)
        image_data = apply_color_curve(image_data, color_curve_files)
        image_data = letterbox(image_data, new_shape=image_size)[0]
        image_data = image_data.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
        image_data = np.ascontiguousarray(image_data)
        image_data = torch.from_numpy(image_data).to(device)
        image_data = image_data.float()  # uint8 to fp16/32
        image_data /= 255.0  # 0 - 255 to 0.0 - 1.0
        image_data = image_data.unsqueeze(0)
        pred = yolo_model(image_data, augment=False)
        number_of_vessels = len(pred[0])
        new_image = Image("")
        new_image.captureTime = image.captureTime
        new_image.name = image.name + "_vessel_digest"
        new_image.imgPath = image.imgPath + "_vessel_digest"
        new_image.data = number_of_vessels
        new_image.size = 8
        return 0, [new_image]

    return detect_vessels


if __name__ == "__main__":
    from node import Image

    # Test the models
    model = load_models()
    print(model)
    random_image = Image()
    Image.data = np.random.rand(8000, 12000, 4)
    Image.name = "test"
    # Test forest model
    print("=======Testing forest model========")
    print(model["forest"](deepcopy(random_image)))
    print(model["forest"](deepcopy(random_image),[]))
    # Test model-based forest model
    print("=======Testing model-based forest model========")
    print(model["forest_model"](deepcopy(random_image)))
    # Test vessel model
    print("=======Testing vessel model========")
    print(model["vessel"](deepcopy(random_image)))
    # Test california model
    print("=======Testing california model========")
    print(model["california"](deepcopy(random_image)))
    print(model["california"](deepcopy(random_image),[]))
    # Test port model
    print("=======Testing port model========")
    print(model["port"](deepcopy(random_image)))
    print(model["port"](deepcopy(random_image),[]))
    # Test fire model
    print("=======Testing fire model========")
    print(model["fire"](deepcopy(random_image)))