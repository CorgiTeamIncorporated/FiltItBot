import numpy as np


def rgb2gray(image):
    image = image/255.0
    R = 0.2125*image[:, :, 0]
    G = 0.7154*image[:, :, 1]
    B = 0.0721*image[:, :, 2]

    gray_image = R + G + B
    gray_image = np.clip(gray_image, 0, 1)
    return gray_image
