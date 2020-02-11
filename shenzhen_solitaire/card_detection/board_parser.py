"""Contains parse_board function"""

import copy
import itertools
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import cv2
import numpy as np

from ..board import Board, Card, NumberCard, SpecialCard
from . import adjustment, card_finder
from .configuration import Configuration, ButtonState


def grouper(
    iterable: Iterable[Any], groupsize: int, fillvalue: Any = None
) -> Iterable[Iterable[Any]]:
    "Collect data into fixed-length chunks or blocks"
    args = [iter(iterable)] * groupsize
    return itertools.zip_longest(*args, fillvalue=fillvalue)


def fake_adjustment(adj: adjustment.Adjustment) -> adjustment.Adjustment:
    result = copy.deepcopy(adj)
    result.x -= 5
    result.y -= 5
    result.h += 10
    result.w += 10
    return result


def get_field_square_iterator(
    image: np.ndarray, conf: Configuration, row_count: int, column_count: int
) -> Iterable[Tuple[np.ndarray, np.ndarray]]:
    """Return iterator for both the square, as well as the matching card border"""
    my_adj = fake_adjustment(conf.field_adjustment)
    my_border_adj = fake_adjustment(conf.border_adjustment)

    squares = card_finder.get_field_squares(
        image, my_adj, count_x=row_count, count_y=column_count
    )
    border_squares = card_finder.get_field_squares(
        image, my_border_adj, count_x=row_count, count_y=column_count
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
    my_hua_adj = fake_adjustment(conf.hua_adjustment)
    hua_square = card_finder.get_field_squares(image, my_hua_adj, count_x=1, count_y=1)[
        0
    ]
    hua_templates = [
        image for image, card_type in conf.catalogue if card_type == SpecialCard.Hua
    ]
    best_hua = max(
        match_template(template=template, search_image=hua_square)
        for template in hua_templates
    )
    best_green = max(
        match_template(template=template, search_image=hua_square)
        for template in conf.green_card
    )
    return best_hua > best_green


def parse_bunker_field(
    image: np.ndarray,
    green_cards: List[np.ndarray],
    card_backs: List[np.ndarray],
    catalogue: List[Tuple[np.ndarray, Card]],
) -> Union[Tuple[SpecialCard, int], Optional[Card]]:

    best_green = max(
        match_template(template=template, search_image=image)
        for template in green_cards
    )
    best_back = max(
        match_template(template=template, search_image=image) for template in card_backs
    )

    best_card_value, best_card_name = max(
        ((match_template(template, image), name) for template, name in catalogue),
        key=lambda x: x[0],
    )

    return max(
        [
            (best_green, None),
            (best_back, (SpecialCard.Hua, 0)),
            (best_card_value, best_card_name),
        ],
        key=lambda x: x[0],
    )[1]


def parse_special_button(
    image: np.ndarray,
    position: SpecialCard,
    buttons: List[Tuple[ButtonState, SpecialCard, np.ndarray]],
) -> ButtonState:
    """Return true if special button is greyed out, e.g. this dragon card is removed from the field"""
    square_fits = [
        (match_template(template, image), state, name)
        for state, name, template in buttons
    ]
    best_state, best_name = max(square_fits, key=lambda x: x[0])[1:]
    assert best_name == position
    return best_state


def parse_bunker(
    image: np.ndarray, conf: Configuration
) -> List[Union[Tuple[SpecialCard, int], Optional[Card]]]:
    bunker_squares = card_finder.get_field_squares(
        image, fake_adjustment(conf.bunker_adjustment), count_x=1, count_y=3
    )
    button_squares = card_finder.get_field_squares(
        image, fake_adjustment(conf.special_button_adjustment), count_x=3, count_y=1
    )
    dragon_sequence = [SpecialCard.Zhong, SpecialCard.Fa, SpecialCard.Bai]
    dragons = [
        card_type
        for dragon_image, card_type in zip(button_squares, dragon_sequence)
        if parse_special_button(dragon_image, card_type, conf.special_buttons)
        == ButtonState.greyed
    ]
    dragon_iter = iter(dragons)
    matches = [
        parse_bunker_field(square, conf.green_card, conf.card_back, conf.catalogue)
        for square in bunker_squares
    ]
    matches = [(next(dragon_iter), 0) if isinstance(x, tuple) else x for x in matches]
    assert next(dragon_iter, None) is None
    return matches


def parse_goal_field(
    image: np.ndarray,
    catalogue: List[Tuple[np.ndarray, Card]],
    green_cards: List[np.ndarray],
) -> Optional[NumberCard]:
    square_fits = [
        (match_template(template, image), name) for template, name in catalogue
    ]
    best_card_value, best_card_name = max(square_fits, key=lambda x: x[0])

    best_green_value = max(match_template(template, image) for template in green_cards)
    if best_green_value > best_card_value:
        return None

    assert isinstance(best_card_name, NumberCard)
    return best_card_name


def parse_goal(image: np.ndarray, conf: Configuration) -> List[Optional[NumberCard]]:
    goal_squares = card_finder.get_field_squares(
        image, fake_adjustment(conf.goal_adjustment), count_x=1, count_y=3
    )
    goal_list = [
        parse_goal_field(square, conf.catalogue, conf.green_card)
        for square in goal_squares
    ]

    return goal_list


def parse_board(image: np.ndarray, conf: Configuration) -> Board:
    result = Board()
    result.field = parse_field(image, conf)
    result.flower_gone = parse_hua(image, conf)
    result.bunker = parse_bunker(image, conf)
    result.goal = parse_goal(image, conf)
    return result
