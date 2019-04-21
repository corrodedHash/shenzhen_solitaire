from typing import Optional, Tuple
from dataclasses import dataclass
import cv2
import numpy


@dataclass
class Adjustment:
    x: int
    y: int
    w: int
    h: int
    dx: int
    dy: int


def get_square(adjustment: Adjustment, ix: int = 0,
               iy: int = 0) -> Tuple[int, int, int, int]:
    return (adjustment.x + adjustment.dx * ix,
            adjustment.y + adjustment.dy * iy,
            adjustment.x + adjustment.w + adjustment.dx * ix,
            adjustment.y + adjustment.h + adjustment.dy * iy)


def _adjust_squares(
        image: numpy.ndarray,
        count_x: int,
        count_y: int,
        adjustment: Optional[Adjustment] = None) -> Adjustment:
    if not adjustment:
        adjustment = Adjustment(0, 0, 0, 0, 0, 0)
    while True:
        B = image.copy()
        for ix in range(count_x):
            for iy in range(count_y):
                square = get_square(adjustment, ix, iy)
                cv2.rectangle(B,
                              (square[0], square[1]),
                              (square[2], square[3]),
                              (0, 0, 0))
        cv2.imshow('Window', B)
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


def adjust_field(image) -> Adjustment:
    return _adjust_squares(image, 8, 5, Adjustment(42, 226, 15, 15, 119, 24))


def adjust_bunker(image) -> Adjustment:
    return _adjust_squares(image, 3, 1)


def adjust_hua(image) -> Adjustment:
    return _adjust_squares(image, 1, 1)


def adjust_goal(image) -> Adjustment:
    return _adjust_squares(image, 3, 1)
