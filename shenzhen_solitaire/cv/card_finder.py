from typing import List, Tuple, Optional, Dict
import numpy
from .adjustment import Adjustment, get_square
from .. import board
import enum
import itertools


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


class Cardcolor(enum.Enum):
    Bai = (65, 65, 65)
    Black = (0, 0, 0)
    Red = (22, 48, 178)
    Green = (76, 111, 19)
    Background = (178, 194, 193)


def simplify(image: numpy.ndarray) -> Dict[Cardcolor, int]:
    result_dict: Dict[Cardcolor, int] = {c: 0 for c in Cardcolor}
    for pixel in itertools.chain.from_iterable(image):
        best_color: Optional[Tuple[Cardcolor, int]] = None
        for color in Cardcolor:
            mse = sum((x - y) ** 2 for x, y in zip(color.value, pixel))
            if not best_color or best_color[1] > mse:
                best_color = (color, mse)
        assert best_color
        for i in range(3):
            pixel[i] = best_color[0].value[i]
        result_dict[best_color[0]] += 1
    return result_dict
