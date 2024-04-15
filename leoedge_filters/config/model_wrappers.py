import torch
import numpy as np
from torchvision import transforms
import cv2

data_transform = transforms.Compose([
            # transforms.Resize(224),
            transforms.ToTensor(),
            # transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

def build_cv_image_filter(base_model,chip_size=(256,256),device='cpu',batch_size=32, transform_function=lambda x:x): # We need to try different threshold so leave it to Sat_Simulator
    def image_filter(input_image,*_):
        # Expand the image to multiple of M,N
        M,N = chip_size
        if not(M==-1 and N==-1):
            input_image = np.pad(input_image,((0,M-input_image.shape[0]%M),(0,N-input_image.shape[1]%N),(0,0)),'constant')
            input_image=transform_function(input_image)
            # Chop the image into patches
            tiles = [input_image[x:x+M,y:y+N,:] for x in range(0,input_image.shape[0],M) for y in range(0,input_image.shape[1],N)]
            all_outputs=[]
            # divide tiles into batches
            for i in range(0,len(tiles),batch_size):
                batch = tiles[i:i+batch_size]
                # Preprocess the patches
                batch = [data_transform(x) for x in batch]
                # Run the model on the patches
                with torch.no_grad():
                    output = base_model(torch.stack(batch).to(device)) # type:ignore
                    # Compute softmax for "fire" class
                    output = torch.nn.functional.softmax(output,dim=1)[:,1].cpu().numpy().tolist()
                all_outputs.extend(output)
            print("Median: ", np.quantile(all_outputs, 0.5))
            print("Mean: ", np.average(all_outputs))
            model_result=np.average(all_outputs)
            # model_result=np.average(all_outputs)
        else:
            input_image=cv2.resize(input_image, (600,370)) #resizing. TODO: may want to change norm+resize fore fire model to a util function
            input_image=transform_function(input_image)
            input_image = data_transform(input_image)
            all_outputs=[]
            with torch.no_grad():
                    output = base_model(torch.stack([input_image]).to(device))
                    # Compute softmax for "fire" class
                    output = torch.nn.functional.softmax(output,dim=1)[:,1].cpu().numpy().tolist()
            all_outputs.extend(output)
            model_result=np.average(all_outputs)
        return model_result
    return image_filter
