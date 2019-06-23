"""Contains functions to find significant pieces of a solitaire screenshot"""

from typing import Optional, Tuple
from dataclasses import dataclass
import numpy
import cv2


@dataclass
class Adjustment:
    """Configuration for a grid"""
    x: int
    y: int
    w: int
    h: int
    dx: int
    dy: int


def get_square(adjustment: Adjustment, index_x: int = 0,
               index_y: int = 0) -> Tuple[int, int, int, int]:
    """Get one square from index and adjustment"""
    return (adjustment.x + adjustment.dx * index_x,
            adjustment.y + adjustment.dy * index_y,
            adjustment.x + adjustment.w + adjustment.dx * index_x,
            adjustment.y + adjustment.h + adjustment.dy * index_y)


def _adjust_squares(
        image: numpy.ndarray,
        count_x: int,
        count_y: int,
        adjustment: Optional[Adjustment] = None) -> Adjustment:
    if not adjustment:
        adjustment = Adjustment(0, 0, 0, 0, 0, 0)
    while True:
        working_image = image.copy()
        for index_x in range(count_x):
            for index_y in range(count_y):
                square = get_square(adjustment, index_x, index_y)
                cv2.rectangle(working_image,
                              (square[0], square[1]),
                              (square[2], square[3]),
                              (0, 0, 0))
        cv2.imshow('Window', working_image)
        k = cv2.waitKey(0)
        print(k)
        if k == 27:
            break
        elif k == 81:
            adjustment.x -= 1
        elif k == 83:
            adjustment.x += 1
        elif k == 82:
            adjustment.y -= 1
        elif k == 84:
            adjustment.y += 1
        elif k == 104:
            adjustment.x -= 10
        elif k == 115:
            adjustment.x += 10
        elif k == 116:
            adjustment.y -= 10
        elif k == 110:
            adjustment.y += 10
        elif k == 97:
            adjustment.w -= 1
        elif k == 111:
            adjustment.h -= 1
        elif k == 101:
            adjustment.h += 1
        elif k == 117:
            adjustment.w += 1
        elif k == 59:
            adjustment.dx -= 1
        elif k == 44:
            adjustment.dy -= 1
        elif k == 46:
            adjustment.dy += 1
        elif k == 112:
            adjustment.dx += 1

    cv2.destroyWindow('Window')
    return adjustment


def adjust_field(image: numpy.ndarray) -> Adjustment:
    """Open configuration grid for the field"""
    return _adjust_squares(image, 8, 5, Adjustment(42, 226, 15, 15, 119, 24))


def adjust_bunker(image: numpy.ndarray) -> Adjustment:
    """Open configuration grid for the bunker"""
    return _adjust_squares(image, 3, 1)


def adjust_hua(image: numpy.ndarray) -> Adjustment:
    """Open configuration grid for the flower card"""
    return _adjust_squares(image, 1, 1)


def adjust_goal(image: numpy.ndarray) -> Adjustment:
    """Open configuration grid for the goal"""
    return _adjust_squares(image, 3, 1)
