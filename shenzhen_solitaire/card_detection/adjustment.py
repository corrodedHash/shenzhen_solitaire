"""Contains functions to find significant pieces of a solitaire screenshot"""

import itertools
from dataclasses import dataclass
from typing import Optional, Tuple

import cv2
import numpy
import math


@dataclass
class Adjustment:
    """Configuration for a grid"""

    x: int = 0
    y: int = 0
    w: int = 0
    h: int = 0
    dx: float = 0
    dy: float = 0


def get_square(
    adjustment: Adjustment, index_x: int = 0, index_y: int = 0
) -> Tuple[int, int, int, int]:
    """Get one square from index and adjustment"""
    return (
        math.floor(adjustment.x + adjustment.dx * index_x),
        math.floor(adjustment.y + adjustment.dy * index_y),
        math.floor(adjustment.x + adjustment.w + adjustment.dx * index_x),
        math.floor(adjustment.y + adjustment.h + adjustment.dy * index_y),
    )


def adjust_squares(
    image: numpy.ndarray,
    count_x: int,
    count_y: int,
    adjustment: Optional[Adjustment] = None,
) -> Adjustment:

    if not adjustment:
        adjustment = Adjustment(w=10, h=10)
    speed_mod = "n"
    speed_mods = ["n", "s", "h"]

    def _adjustment_step(keycode: int, speed_mod: str) -> None:
        assert adjustment is not None
        x_keys = {104: -1, 115: +1}
        y_keys = {116: -1, 110: +1}
        w_keys = {97: -1, 117: +1}
        h_keys = {111: -1, 101: +1}
        dx_keys = {59: -1, 112: +1}
        dy_keys = {44: -1, 46: +1}
        speed_facs = {"n": 1, "s": 8, "h": 64}
        cur_high_speed_fac = speed_facs[speed_mod]
        if keycode in x_keys:
            adjustment.x += x_keys[keycode] * cur_high_speed_fac
        elif keycode in y_keys:
            adjustment.y += y_keys[keycode] * cur_high_speed_fac
        elif keycode in w_keys:
            adjustment.w += w_keys[keycode] * cur_high_speed_fac
        elif keycode in h_keys:
            adjustment.h += h_keys[keycode] * cur_high_speed_fac
        elif keycode in dx_keys:
            adjustment.dx += dx_keys[keycode] * cur_high_speed_fac * 1 / 8
        elif keycode in dy_keys:
            adjustment.dy += dy_keys[keycode] * cur_high_speed_fac * 1 / 8

    cv2.namedWindow("Window", flags=cv2.WINDOW_NORMAL)

    while True:
        working_image = image.copy()
        for index_x, index_y in itertools.product(range(count_x), range(count_y)):
            square = get_square(adjustment, index_x, index_y)
            cv2.rectangle(
                working_image,
                (math.floor(square[0]), math.floor(square[1])),
                (math.floor(square[2]), math.floor(square[3])),
                (0, 0, 0),
            )
        cv2.imshow("Window", working_image)
        keycode = cv2.waitKey(0)
        print(keycode)
        if keycode == 27:
            break
        if keycode == 229:
            speed_mod = speed_mods[(speed_mods.index(speed_mod) + 1) % len(speed_mods)]
            continue
        _adjustment_step(keycode, speed_mod)

    cv2.destroyWindow("Window")
    return adjustment
