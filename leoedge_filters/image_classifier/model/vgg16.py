import torch
import torchvision
from typing import *


class VGG16Classifier(torch.nn.Module):
    def __init__(self, cfg):
        super().__init__()
        num_classes, top_dims = cfg
        self.model = torchvision.models.vgg16(pretrained=True)
        #print(self.model)
        #self.features = self.model.features
        #for param in self.features.parameters(): #NOTE: prune:True  // finetune:False
         #   param.requires_grad = True
        if top_dims is None:
            top_dims = []
        top_dims.append(num_classes)
        num_ftrs = self.model.classifier[0].in_features
        #print(num_ftrs)
        top_dims = [num_ftrs] + top_dims
        #print(top_dims)
        self.model.classifier = torch.nn.Sequential(
            *[
                torch.nn.Sequential(
                    torch.nn.BatchNorm1d(top_dims[i]),
                    torch.nn.Linear(top_dims[i], top_dims[i + 1]),
                    torch.nn.ReLU()
                )
                for i in range(len(top_dims) - 2)],
            torch.nn.Linear(top_dims[-2], top_dims[-1])
        )

    def forward(self, *input: Any, **kwargs: Any):
        #print("input")
        #print(input)
        img=torch.nn.functional.interpolate(input[0],size=224)
        output = self.model(img)
        #print(output)
        return output
        #return self.model(input[0])