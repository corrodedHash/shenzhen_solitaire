"""Functions to detect card value"""

from typing import List, Tuple, Optional, Dict
import enum
import itertools
import numpy as np  # type: ignore
import cv2  # type: ignore
from .adjustment import Adjustment, get_square


def _extract_squares(image: np.ndarray,
                     squares: List[Tuple[int,
                                         int,
                                         int,
                                         int]]) -> List[np.ndarray]:
    return [image[square[1]:square[3], square[0]:square[2]].copy()
            for square in squares]


def get_field_squares(image: np.ndarray,
                      adjustment: Adjustment) -> List[np.ndarray]:
    squares = []
    for index_x, index_y in itertools.product(range(8), range(5)):
        squares.append(get_square(adjustment, index_x, index_y))
    return _extract_squares(image, squares)


class Cardcolor(enum.Enum):
    """Relevant colors for different types of cards"""
    Bai = (65, 65, 65)
    Black = (0, 0, 0)
    Red = (22, 48, 178)
    Green = (76, 111, 19)
    Background = (178, 194, 193)


GREYSCALE_COLOR = {
    Cardcolor.Bai: 50,
    Cardcolor.Black: 100,
    Cardcolor.Red: 150,
    Cardcolor.Green: 200,
    Cardcolor.Background: 250}


def simplify(image: np.ndarray) -> Tuple[np.ndarray, Dict[Cardcolor, int]]:
    result_image: np.ndarray = np.zeros(
        (image.shape[0], image.shape[1]), np.uint8)
    result_dict: Dict[Cardcolor, int] = {c: 0 for c in Cardcolor}
    for pixel_x, pixel_y in itertools.product(
            range(result_image.shape[0]),
            range(result_image.shape[1])):
        pixel = image[pixel_x, pixel_y]
        best_color: Optional[Tuple[Cardcolor, int]] = None
        for color in Cardcolor:
            mse = sum((x - y) ** 2 for x, y in zip(color.value, pixel))
            if not best_color or best_color[1] > mse:
                best_color = (color, mse)
        assert best_color
        result_image[pixel_x, pixel_y] = GREYSCALE_COLOR[best_color[0]]
        result_dict[best_color[0]] += 1
    return (result_image, result_dict)


def get_simplified_squares(image: np.ndarray,
                           adjustment: Adjustment) -> List[np.ndarray]:
    squares = get_field_squares(image, adjustment)
    for index, square in enumerate(squares):
        squares[index], _ = simplify(square)
    return squares


def _find_single_square(search_square: np.ndarray,
                        template_square: np.ndarray) -> Tuple[int, Tuple[int, int]]:
    assert search_square.shape[0] <= template_square.shape[0]
    assert search_square.shape[1] <= template_square.shape[1]
    best_result: Optional[Tuple[int, Tuple[int, int]]] = None
    for x, y in itertools.product(
            range(template_square.shape[0], search_square.shape[0] - 1, -1),
            range(template_square.shape[1], search_square.shape[1] - 1, -1)):
        p = template_square[x - search_square.shape[0]:x,
                            y - search_square.shape[1]:y] - search_square
        count = cv2.countNonZero(p)
        if not best_result or count < best_result[0]:
            best_result = (
                count,
                (x - search_square.shape[0],
                 y - search_square.shape[1]))
    assert best_result
    return best_result


def find_square(search_square: np.ndarray,
                squares: List[np.ndarray]) -> Tuple[np.ndarray, int]:
    best_set = False
    best_square: Optional[np.ndarray] = None
    best_count = 0
    best_coord: Optional[Tuple[int, int]] = None
    for square in squares:
        count, coord = _find_single_square(square, search_square)
        if not best_set or count < best_count:
            best_set = True
            best_square = square
            best_count = count
            best_coord = coord
    assert isinstance(best_square, np.ndarray)
    assert isinstance(best_coord, tuple)
    cv2.imshow("Window", best_square -
               search_square[best_coord[0]:best_coord[0] +
                             best_square.shape[0], best_coord[1]:best_coord[1] +
                             best_square.shape[1]])
    while cv2.waitKey(0) != 27:
        pass
    cv2.destroyWindow("Window")
    return (best_square, best_count)
