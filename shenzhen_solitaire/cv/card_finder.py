from typing import List, Tuple
import numpy
from .adjustment import Adjustment, get_square
from .. import board


def _extract_squares(image: numpy.ndarray,
                     squares: List[Tuple[int,
                                         int,
                                         int,
                                         int]]) -> List[numpy.ndarray]:
    return [image[square[1]:square[3], square[0]:square[2]].copy()
            for square in squares]


def get_field_squares(image: numpy.ndarray,
                      adjustment: Adjustment) -> List[numpy.ndarray]:
    squares = []
    for ix in range(8):
        for iy in range(5):
            squares.append(get_square(adjustment, ix, iy))
    return _extract_squares(image, squares)
