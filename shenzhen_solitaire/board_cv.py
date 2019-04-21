import cv2
import numpy
from typing import Optional
from dataclasses import dataclass

A = cv2.imread("Solitaire.png")


@dataclass
class Adjustment:
    x: int
    y: int
    w: int
    h: int
    dx: int
    dy: int


def adjust_squares(
        image: numpy.ndarray,
        count_x: int,
        count_y: int,
        preset: Optional[Adjustment] = None) -> Adjustment:
    result = preset
    if not result:
        result = Adjustment(0, 0, 0, 0, 0, 0)
    while True:
        B = image.copy()
        for ix in range(count_x):
            for iy in range(count_y):
                cv2.rectangle(B, (result.x +
                                  result.dx *
                                  ix, result.y +
                                  result.dy *
                                  iy), (result.x +
                                        result.w +
                                        result.dx *
                                        ix, result.y +
                                        result.h +
                                        result.dy *
                                        iy), (0, 0, 0))
        cv2.imshow('Window', B)
        k = cv2.waitKey(0)
        print(k)
        if k == 27:
            break
        elif k == 81:
            result.x -= 1
        elif k == 83:
            result.x += 1
        elif k == 82:
            result.y -= 1
        elif k == 84:
            result.y += 1
        elif k == 104:
            result.x -= 10
        elif k == 115:
            result.x += 10
        elif k == 116:
            result.y -= 10
        elif k == 110:
            result.y += 10
        elif k == 97:
            result.w -= 1
        elif k == 111:
            result.h -= 1
        elif k == 101:
            result.h += 1
        elif k == 117:
            result.w += 1
        elif k == 59:
            result.dx -= 1
        elif k == 44:
            result.dy -= 1
        elif k == 46:
            result.dy += 1
        elif k == 112:
            result.dx += 1

    cv2.destroyWindow('Window')
    return result


def adjust_field(image) -> Adjustment:
    return adjust_squares(image, 8, 5, Adjustment(42, 226, 15, 15, 119, 24))

def adjust_bunker(image) -> Adjustment:
    return adjust_squares(image, 3, 1)

def adjust_hua(image) -> Adjustment:
    return adjust_squares(image, 1, 1)

def adjust_goal(image) -> Adjustment:
    return adjust_squares(image, 3, 1)


print(adjust_field(A))
