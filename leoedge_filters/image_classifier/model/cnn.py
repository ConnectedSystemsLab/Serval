import torch
from typing import *


class ConvBlock(torch.nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, activation='relu', stride=1, padding='same', dilation=1,
                 groups=1, maxpool=None):
        # missing bn params : eps=1e-05, momentum=0.1, affine=True, track_running_stats=True

        super(ConvBlock, self).__init__()

        self.c = torch.nn.Conv2d(in_channels, out_channels, kernel_size, stride=stride, padding=padding,
                                 dilation=dilation, groups=groups)
        self.b = torch.nn.BatchNorm2d(out_channels)
        if maxpool:
            self.maxpool = torch.nn.MaxPool2d(maxpool)
        else:
            self.maxpool = None
        if activation == 'relu':
            self.a = torch.nn.ReLU()
        elif activation == 'tanh':
            self.a = torch.nn.Tanh()
        # add others if you want.

    def forward(self, x):
        res = self.a(self.b(self.c(x)))
        if self.maxpool:
            res = self.maxpool(res)
        return res


class CNNClassifier(torch.nn.Module):
    def __init__(self, cfg):
        super().__init__()
        in_shape, cnn_cfg, top_cfg, num_classes = cfg
        self.cnn = self.__parse_cnn__(cnn_cfg, in_shape)
        top_cfg = [cnn_cfg[-1][0]] + top_cfg
        self.top = self.__parse_top__(top_cfg, num_classes)
        # self.model = torch.nn.Sequential(cnn, top)
        # print(self.model)

    def __parse_cnn__(self, cfg: List, in_shape: List[int]):
        cnn_list = []
        h, w, c = in_shape
        last_channel = c
        cfg.pop(0)
        for c, k, m, p in cfg:
            cnn_list.append(ConvBlock(last_channel, c, k, maxpool=m, padding=p))
            last_channel = c
            if m:
                h /= m
                w /= m
        cnn_list.append(torch.nn.MaxPool2d((int(h), int(w))))
        return torch.nn.Sequential(*cnn_list)

    def __parse_top__(self, cfg, out_dim):
        fc_list = []
        last_dim = cfg.pop(0)
        for dim in cfg:
            fc_list.append(torch.nn.Linear(last_dim, dim))
            fc_list.append(torch.nn.ReLU())
            fc_list.append(torch.nn.BatchNorm1d(dim))
            last_dim = dim
        fc_list.append(torch.nn.Linear(last_dim, out_dim))
        return torch.nn.Sequential(*fc_list)

    def forward(self, *input: Any, **kwargs: Any):
        feature = self.cnn(input[0])
        b, c, h, w = feature.shape
        feature = feature.view((b, c))
        return self.top(feature)
