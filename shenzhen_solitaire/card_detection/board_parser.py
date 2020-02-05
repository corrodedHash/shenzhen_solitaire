"""Contains parse_board function"""

import numpy as np
from .configuration import Configuration
from ..board import Board
from . import card_finder
import cv2
from typing import Iterable, Any, List
import itertools


def parse_board(image: np.ndarray, conf: Configuration) -> Board:
    """Parse a screenshot of the game, using a given configuration"""
    fake_adjustments = conf.field_adjustment
    fake_adjustments.x -= 5
    fake_adjustments.y -= 5
    fake_adjustments.h += 10
    fake_adjustments.w += 10
    row_count = 13
    column_count = 8

    def grouper(iterable: Iterable[Any], groupsize: int, fillvalue: Any = None) -> Iterable[Any]:
        "Collect data into fixed-length chunks or blocks"
        args = [iter(iterable)] * groupsize
        return itertools.zip_longest(*args, fillvalue=fillvalue)

    squares = card_finder.get_field_squares(
        image, conf.field_adjustment, count_x=row_count, count_y=column_count
    )
    grouped_squares = grouper(squares, row_count)
    result = Board()
    for group_index, square_group in enumerate(grouped_squares):
        group_field = []
        for index, square in enumerate(square_group):
            best_val = None
            best_name = None
            for template, name in conf.catalogue:
                res = cv2.matchTemplate(square, template, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
                if best_val is None or max_val > best_val:
                    best_val = max_val
                    best_name = name
            assert best_name is not None
            group_field.append(best_name)

            # print(f"\t{best_val}: {best_name}")
            # cv2.imshow("Catalogue", cv2.resize(square, (500, 500)))
            # cv2.waitKey()

        result.field[group_index] = group_field

    return result
