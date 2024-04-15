from config.dataset_catalog import build_train_and_val_shipsnet_dataset
from image_classifier.model import get_model
from image_classifier.train import train_model
from torch.utils.data import DataLoader
import torch

def main():
    model=get_model("resnet",[2,[]])
    model=model.cuda()
    criterion = torch.nn.CrossEntropyLoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.0001)
    train_dataset, val_dataset = build_train_and_val_shipsnet_dataset("data/shipsnet_augmented")
    dataloader={
        "train":DataLoader(train_dataset,batch_size=32,shuffle=True),
        "val":DataLoader(val_dataset,batch_size=32,shuffle=True)
    }
    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)

    best_weight=train_model(model,criterion,optimizer,lr_scheduler,dataloader,num_epochs=10)
    torch.save(best_weight,"results/model/ship_classifier_augmented.pth")


if __name__ == "__main__":
    main()
