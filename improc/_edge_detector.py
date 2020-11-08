import numpy as np
from _rgb2gray import rgb2gray
from skimage.util import img_as_float


def detect_edge(image: np.ndarray, threshhold: float = 0.5) -> np.ndarray:
    # initialize Sobel's operators
    sob_op_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
    sob_op_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])

    edges = np.zeros(image.shape)

    image = img_as_float(image)
    if len(image.shape) != 2:
        image = rgb2gray(image)

    image = np.pad(image, 1, 'linear_ramp')
    for i in range(1, image.shape[0]-1):
        for j in range(1, image.shape[1]-1):
            g_x = np.sum(image[i-1:i+2, j-1:j+2]*sob_op_x)
            g_y = np.sum(image[i-1:i+2, j-1:j+2]*sob_op_y)

            g = np.sqrt(g_x**2 + g_y**2)
            if g > threshhold:
                edges[i-1, j-1] = g

    edges = np.clip(edges, 0, 1)
    return edges
