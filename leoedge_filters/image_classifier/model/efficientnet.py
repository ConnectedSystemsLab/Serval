import torch
# pip install efficientnet_pytorch
from efficientnet_pytorch import EfficientNet
from typing import *


class EfficientNetClassifier(torch.nn.Module):
    def __init__(self, cfg):
        super().__init__()
        num_classes, top_dims = cfg
        self.model = EfficientNet.from_pretrained('efficientnet-b5')
        if top_dims is None:
            top_dims = []
        top_dims.append(num_classes)
        num_ftrs = self.model._fc.in_features
        top_dims = [num_ftrs] + top_dims
        print(top_dims)
        self.model._fc = torch.nn.Sequential(
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
        output = self.model(input[0])
        # print(output)
        return output
