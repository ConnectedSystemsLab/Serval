#import torch
#model = torch.hub.load('pytorch/vision:v0.10.0', 'inception_v3', pretrained=True)
#import timm
import torchvision
import torch
from typing import *
model = torchvision.models.inception_v3( pretrained=True)
print(model)