"""Contains parse_board function"""

import itertools
from typing import Any, Iterable, List, Optional, Tuple, Union, Dict

import cv2
import numpy as np

from ..board import Board, Card, NumberCard, SpecialCard
from . import card_finder
from .configuration import Configuration


def grouper(
    iterable: Iterable[Any], groupsize: int, fillvalue: Any = None
) -> Iterable[Iterable[Any]]:
    "Collect data into fixed-length chunks or blocks"
    args = [iter(iterable)] * groupsize
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def get_field_square_iterator(
    image: np.ndarray, conf: Configuration, row_count: int, column_count: int
) -> Iterable[Tuple[np.ndarray, np.ndarray]]:
    """Return iterator for both the square, as well as the matching card border"""
    fake_adjustments = conf.field_adjustment
    fake_adjustments.x -= 5
    fake_adjustments.y -= 5
    fake_adjustments.h += 10
    fake_adjustments.w += 10
    squares = card_finder.get_field_squares(
        image, fake_adjustments, count_x=row_count, count_y=column_count
    )
    border_squares = card_finder.get_field_squares(
        image, conf.border_adjustment, count_x=row_count, count_y=column_count
    )
    grouped_squares = grouper(squares, row_count)
    grouped_border_squares = grouper(border_squares, row_count)
    return zip(grouped_squares, grouped_border_squares)


def match_template(template: np.ndarray, search_image: np.ndarray) -> float:
    """Return matchiness for the template on the search image"""

    res = cv2.matchTemplate(search_image, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    assert isinstance(max_val, (int, float))
    return float(max_val)


def parse_field_square(
    square: np.ndarray, border: np.ndarray, conf: Configuration
) -> Tuple[Union[NumberCard, SpecialCard], bool]:
    square_fits = [
        (match_template(template, square), name) for template, name in conf.catalogue
    ]
    best_val, best_name = max(square_fits, key=lambda x: x[0])

    best_border = max(
        match_template(template=template, search_image=border)
        for template in conf.card_border
    )
    best_empty = max(
        match_template(template=template, search_image=border)
        for template in conf.empty_card
    )

    assert best_name is not None
    assert best_empty is not None
    assert best_border is not None
    row_finished = best_empty > best_border

    return (best_name, row_finished)


def parse_field(image: np.ndarray, conf: Configuration) -> List[List[Card]]:
    """Parse a screenshot of the game, using a given configuration"""
    square_iterator = get_field_square_iterator(
        image, conf, row_count=Board.MAX_ROW_SIZE, column_count=Board.MAX_COLUMN_SIZE
    )
    result = []
    for square_group, border_group in square_iterator:
        group_field = []
        for index, (square, border_square) in enumerate(
            zip(square_group, border_group)
        ):
            value, row_finished = parse_field_square(square, border_square, conf)
            group_field.append(value)
            if row_finished:
                break

        result.append(group_field)

    return result


def parse_hua(image: np.ndarray, conf: Configuration) -> bool:
    """Return true if hua is in the hua spot, false if hua spot is empty"""
    raise NotImplementedError()


def parse_bunker(
    image: np.ndarray, conf: Configuration
) -> List[Union[Tuple[SpecialCard, int], Optional[Card]]]:
    raise NotImplementedError()


def parse_goal(image: np.ndarray, conf: Configuration) -> Dict[NumberCard.Suit, int]:
    raise NotImplementedError()


def parse_board(image: np.ndarray, conf: Configuration) -> Board:
    result = Board()
    result.field = parse_field(image, conf)
    # result.flower_gone = parse_hua(image, conf)
    # result.bunker = parse_bunker(image, conf)
    # result.goal = parse_goal(image, conf)
    return result
