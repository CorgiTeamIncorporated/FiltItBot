import numpy as np
import copy


def gaussian_function_1D(x: int, sigma: float) -> float:
    value = np.exp(-(x**2)/(2*sigma**2))/(np.sqrt(2*np.pi)*sigma)
    return value/sum(value)


def gaussian_filter(image: np.ndarray, kernel_size: int = 5,
                    sigma: float = -1) -> np.ndarray:
    # preprocessing
    if sigma == -1:
        sigma = np.sqrt(kernel_size)
    kernel_size = int(kernel_size)
    sigma = float(sigma)

    # check if input args are correct
    if kernel_size < 1:
        raise ValueError('kernel_size < 1 - {}'.format(kernel_size))
    if sigma < 0:
        raise ValueError('sigma < 0 - {}'.format(kernel_size))

    # convert image to image with pad
    padding = kernel_size // 2
    pad_width = ((padding, padding), (padding, padding), (0, 0))
    image = np.pad(image, pad_width, 'constant', constant_values=(0))

    # create gaussian vector
    pattern = np.pad([0], (padding, padding), 'linear_ramp', end_values=2)
    g = gaussian_function_1D(pattern, sigma).reshape(-1)

    # processing
    temp_image = copy.deepcopy(image)
    for i in range(padding, image.shape[0]-padding):
        for j in range(padding, image.shape[1]-padding):
            temp_image[i, j] = np.sum(image[i-padding:i+padding+1, j].T*g,
                                      axis=1)
    image = copy.deepcopy(temp_image)
    for i in range(padding, image.shape[0]-padding):
        for j in range(padding, image.shape[1]-padding):
            temp_image[i, j] = np.sum(image[i, j-padding:j+padding+1].T*g,
                                      axis=1)
    if padding > 0:
        return temp_image[padding:-padding, padding:-padding]
    else:
        return temp_image
