import numpy as np
from skimage.util import img_as_float


def rgb2gray(image):
    image = img_as_float(image)

    R = 0.2125*image[:, :, 0]
    G = 0.7154*image[:, :, 1]
    B = 0.0721*image[:, :, 2]

    gray_image = R + G + B
    gray_image = np.clip(gray_image, 0, 1)
    return gray_image
