import argparse
import copy
import json
import os
import time

import numpy as np
import torch
import torch.multiprocessing
import torch.utils
from torch.utils.data import DataLoader
from torchvision import transforms

from image_classifier.load_data import PlanetImage
from image_classifier.model import get_model
from config.dataset_catalog import DatasetCatalog
from util import scale_image


# import pydevd_pycharm
#
# pydevd_pycharm.settrace('localhost', port=6789, stdoutToServer=True, stderrToServer=True)


def train_model(model, criterion, optimizer, scheduler, dataloaders, device="cuda", num_epochs=25):
    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0

    for epoch in range(num_epochs):
        print('Epoch {}/{}'.format(epoch, num_epochs - 1))
        print('-' * 10)
        #count_output = []
        # Each epoch has a training and validation phase
        for phase in ['train', 'val']:
            count_pred = []
            count_label = []
            if phase == 'train':
                model.train()  # Set model to training mode
            else:
                model.eval()  # Set model to evaluate mode

            running_loss = 0.0
            running_corrects = 0

            # Iterate over data.
            for inputs, labels in dataloaders[phase]:
                inputs = inputs.to(device)
                labels = labels.to(device)

                # zero the parameter gradients
                optimizer.zero_grad()

                # forward
                # track history if only in train
                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    #if (phase == 'val'):
                     #   count_output = np.concatenate((count_output, outputs.cpu().numpy()))
                    # print(outputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                    soft_output = torch.nn.functional.softmax(outputs)
                # statistics
                running_loss += loss.item() * inputs.size(0)
                running_corrects += torch.sum(preds == labels.data).item()
                count_label = np.concatenate((count_label, labels.data.cpu().numpy()))
                count_pred = np.concatenate((count_pred, preds.cpu().numpy()))
            if phase == 'train':
                scheduler.step()

            epoch_loss = running_loss / len(dataloaders[phase].dataset)
            epoch_acc = running_corrects / len(dataloaders[phase].dataset)
            
            if (phase == "val"):
                preds_cpu = preds.cpu().numpy()
                labels_cpu =  labels.data.cpu().numpy()
                print("ground truth:")
                print(count_label)
                print("prediction:")
                print(count_pred)

            print('{} Loss: {:.4f} Acc: {:.4f}'.format(
                phase, epoch_loss, epoch_acc))

            # deep copy the model
            if phase == 'val' and epoch_acc > best_acc:
                best_acc = epoch_acc
                best_model_wts = copy.deepcopy(model.state_dict())

        print()

    time_elapsed = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(
        time_elapsed // 60, time_elapsed % 60))
    print('Best val Acc: {:4f}'.format(best_acc))

    # load best model weights
    model.load_state_dict(best_model_wts)
    return model


if __name__ == '__main__':
    # torch.multiprocessing.set_sharing_strategy('file_system')
    parser = argparse.ArgumentParser()
    parser.add_argument('--backbone', required=True, type=str)
    parser.add_argument('--cfg', required=True, type=str)
    parser.add_argument('--model_name', required=True, type=str)
    parser.add_argument('--cuda', dest='cuda', action='store_true')
    parser.add_argument('--no-cuda', dest='cuda', action='store_false')
    parser.add_argument('--dataset', required=True, type=str)
    parser.add_argument('--train_dir', required=True, type=str)
    parser.add_argument('--val_dir', required=True, type=str)
    parser.add_argument('--lr', required=True, type=float)
    parser.add_argument('--batch_size', default=32, type=int, required=False)
    parser.add_argument('--num_epochs', default=25, type=int, required=False)
    parser.add_argument('--num_workers', default=8, type=int, required=False)
    parser.set_defaults(cuda=True)
    args = parser.parse_args()
    cfg = json.loads(args.cfg)
    train_data = DatasetCatalog.get_dataset(args.dataset, args.train_dir)
    val_data = DatasetCatalog.get_dataset(args.dataset, args.val_dir)
    dataloader = {
        'train': DataLoader(train_data, shuffle=True, num_workers=args.num_workers, batch_size=args.batch_size),
        'val': DataLoader(val_data, shuffle=True, num_workers=args.num_workers, batch_size=args.batch_size)
    }
    model = get_model(args.backbone, cfg)
    if args.cuda:
        model = model.cuda()
        model = torch.nn.DataParallel(model)
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=args.lr)
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
    model = train_model(model, criterion, optimizer, lr_scheduler, dataloader, device='cuda' if args.cuda else 'cpu',
                        num_epochs=args.num_epochs)
    torch.save(model, open(f'{args.model_name}_{args.backbone}_{cfg}', 'wb+'))
