import os
from validator_collection import validators, checkers
from PIL import Image
import requests
from torchvision import datasets, transforms

EFFICIENTNET_IMAGE_SIZE = 224
EFFICIENTNET_TRANSFER = transforms.Compose([
    transforms.Resize(EFFICIENTNET_IMAGE_SIZE),
    transforms.CenterCrop(EFFICIENTNET_IMAGE_SIZE),
    transforms.RandomAffine(degrees=0, translate=(0.05, 0.05)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225]),
])


def read_img_from_url(url, transfer_to_tensor=False):
    img = Image.open(requests.get(url, stream=True).raw).convert('RGB')
    if transfer_to_tensor:
        img = EFFICIENTNET_TRANSFER(img)
    return img

def create_dir(path):
    try:
        os.makedirs(path)
        print("creat dir {}".format(path))
    except:
        pass


def is_image_path(imagepath):
    if not checkers.is_url(imagepath):
        return False

    if isinstance(imagepath, str):
        if imagepath.lower().endswith(('bmp', 'dib', 'png', 'jpg', 'jpeg', 'pbm', 'pgm', 'ppm', 'tif', 'tiff')):
            return True
        else:
            return False
