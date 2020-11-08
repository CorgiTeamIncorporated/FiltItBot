import numpy as np
from skimage.util import img_as_float


def adjust_contast_brightness(image: np.ndarray, alpha=1.0,
                              betta=0.0) -> np.ndarray:
    image = img_as_float(image)
    return np.clip(alpha*image + betta, 0, 1)
