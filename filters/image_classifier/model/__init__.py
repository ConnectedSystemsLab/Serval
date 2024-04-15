from .cnn import CNNClassifier
from .inception import *
from .mobilenet import MobilenetClassifier
from .resnet import *
from .vgg16 import *


def get_model(backbone, cfg):
    if backbone == 'resnet':
        model = ResnetClassifier(cfg)
    elif backbone == 'cnn':
        model = CNNClassifier(cfg)
    elif backbone == 'mobilenet':
        model = MobilenetClassifier(cfg)
    elif backbone == 'vgg16':
        model = VGG16Classifier(cfg)
        #print(model)
    elif backbone == 'inception':
        model = InceptionClassifier(cfg)
    else:
        raise ValueError
    return model
