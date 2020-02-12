"""Contains functions to find significant pieces of a solitaire screenshot"""

import itertools
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy


@dataclass
class Adjustment:
    """Configuration for a grid"""

    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0
    dx: int = 0
    dy: int = 0


def get_square(
    adjustment: Adjustment, index_x: int = 0, index_y: int = 0
) -> Tuple[int, int, int, int]:
    """Get one square from index and adjustment"""
    return (
        adjustment.x + adjustment.dx * index_x,
        adjustment.y + adjustment.dy * index_y,
        adjustment.x + adjustment.w + adjustment.dx * index_x,
        adjustment.y + adjustment.h + adjustment.dy * index_y,
    )


def adjust_squares(
    image: numpy.ndarray,
    count_x: int,
    count_y: int,
    adjustment: Optional[Adjustment] = None,
) -> Adjustment:

    if not adjustment:
        adjustment = Adjustment(w=10, h=10)

    def _adjustment_step(keycode: int) -> None:
        assert adjustment is not None
        x_keys = {81: -1, 83: +1, 104: -10, 115: +10}
        y_keys = {82: -1, 84: +1, 116: -10, 110: +10}
        w_keys = {97: -1, 117: +1}
        h_keys = {111: -1, 101: +1}
        dx_keys = {59: -1, 112: +1}
        dy_keys = {44: -1, 46: +1}
        if keycode in x_keys:
            adjustment.x += x_keys[keycode]
        elif keycode in y_keys:
            adjustment.y += y_keys[keycode]
        elif keycode in w_keys:
            adjustment.w += w_keys[keycode]
        elif keycode in h_keys:
            adjustment.h += h_keys[keycode]
        elif keycode in dx_keys:
            adjustment.dx += dx_keys[keycode]
        elif keycode in dy_keys:
            adjustment.dy += dy_keys[keycode]

    while True:
        working_image = image.copy()
        for index_x, index_y in itertools.product(range(count_x), range(count_y)):
            square = get_square(adjustment, index_x, index_y)
            cv2.rectangle(
                working_image, (square[0], square[1]), (square[2], square[3]), (0, 0, 0)
            )
        cv2.imshow("Window", working_image)
        keycode = cv2.waitKey(0)
        print(keycode)
        if keycode == 27:
            break
        _adjustment_step(keycode)

    cv2.destroyWindow("Window")
    return adjustment


def adjust_field(image: numpy.ndarray) -> Adjustment:
    """Open configuration grid for the field"""
    return adjust_squares(image, 8, 13, Adjustment(42, 226, 15, 15, 119, 24))


def adjust_bunker(image: numpy.ndarray) -> Adjustment:
    """Open configuration grid for the bunker"""
    return adjust_squares(image, 3, 1)


def adjust_hua(image: numpy.ndarray) -> Adjustment:
    """Open configuration grid for the flower card"""
    return adjust_squares(image, 1, 1)


def adjust_goal(image: numpy.ndarray) -> Adjustment:
    """Open configuration grid for the goal"""
    return adjust_squares(image, 3, 1)
