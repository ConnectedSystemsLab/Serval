import torchvision
import torch
from typing import *


class ImageClassifier(torch.nn.Module):
    def __init__(self, num_classes, top_dims=None):
        super().__init__()
        self.model = torchvision.models.resnet50(pretrained=True)
        if top_dims is None:
            top_dims = []
        top_dims.append(num_classes)
        num_ftrs = self.model.fc.in_features
        top_dims = [num_ftrs] + top_dims
        self.model.fc = torch.nn.Sequential(
            *[
                torch.nn.Sequential(
                    torch.nn.Linear(top_dims[i], top_dims[i + 1]),
                    torch.nn.ReLU()
                )
                for i in range(len(top_dims) - 2)],
            torch.nn.Linear(top_dims[-2], top_dims[-1]),
            torch.nn.Softmax()
        )

    def forward(self, *input: Any, **kwargs: Any):
        return self.model(input[0])
