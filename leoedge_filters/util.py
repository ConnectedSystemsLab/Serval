import numpy as np
import imutils

def rotate_image(img):
    #scale to 0-255
    scale_factor=255/np.max(img)
    img = img * scale_factor

    #let's remove all the initial rows and columns that are all zeros
    rows = 0
    while np.all(img[rows] == 0):
        rows += 1
    cols = 0
    while np.all(img[:,cols] == 0):
        cols += 1

    img = img[rows:,cols:]
    #now let's rotate the image so that the first non-zero pixel is in the top left
    firstX = np.nonzero(img[0, :, :])[0][0]
    firstY = np.nonzero(img[:, 0, :])[0][0]
    angle = -np.arctan2(firstX, firstY)

    img = imutils.rotate_bound(img, angle*180/np.pi)
    new_image = np.array(img)

    #let's crop all the rows and columns that are all zeros
    rows = 0
    while np.all(new_image[rows] == 0):
        rows += 1
    cols = 0
    while np.all(new_image[:,cols] == 0):
        cols += 1
    
    new_image = new_image[rows:,cols:]
    #now let's remove the rows and columns that are all zeros from the other side
    rows = new_image.shape[0] - 1
    while np.all(new_image[rows] == 0):
        rows -= 1
    cols = new_image.shape[1] - 1
    while np.all(new_image[:,cols] == 0):
        cols -= 1
    new_image = new_image[:rows+1,:cols+1]

    #now let's rotate the image if x is greater than y
    if new_image.shape[0] > new_image.shape[1]:
        new_image = np.rot90(new_image)
    
    print(new_image.shape)

    return new_image/scale_factor

def scale_image(img):
    new_image = np.array(img)/12500
    new_image=np.clip(new_image,0,1)
    return new_image