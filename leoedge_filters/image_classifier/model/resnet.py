import torch
import torchvision
from typing import *


class ResnetClassifier(torch.nn.Module):
    def __init__(self, cfg):
        super().__init__()
        num_classes,top_dims=cfg
        self.model = torchvision.models.resnet50(pretrained=True)
        if top_dims is None:
            top_dims = []
        top_dims.append(num_classes)
        num_ftrs = self.model.fc.in_features
        top_dims = [num_ftrs] + top_dims
        print(top_dims)
        self.model.fc = torch.nn.Sequential(
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
        return self.model(input[0])
