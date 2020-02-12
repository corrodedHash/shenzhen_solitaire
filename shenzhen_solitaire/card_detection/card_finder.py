"""Functions to detect card value"""

import enum
import itertools
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from ..board import Card, NumberCard, SpecialCard
from .adjustment import Adjustment, get_square


def _extract_squares(
    image: np.ndarray, squares: List[Tuple[int, int, int, int]]
) -> List[np.ndarray]:
    return [
        image[square[1] : square[3], square[0] : square[2]].copy() for square in squares
    ]


def get_field_squares(
    image: np.ndarray, adjustment: Adjustment, count_x: int, count_y: int
) -> List[np.ndarray]:
    """Return all squares in the field, according to the adjustment"""
    squares = []
    for index_x, index_y in itertools.product(range(count_y), range(count_x)):
        squares.append(get_square(adjustment, index_x, index_y))
    return _extract_squares(image, squares)


def catalogue_cards(squares: List[np.ndarray]) -> List[Tuple[np.ndarray, Card]]:
    """Run manual cataloging for given squares"""
    cv2.namedWindow("Catalogue", cv2.WINDOW_NORMAL)
    cv2.waitKey(1)
    result: List[Tuple[np.ndarray, Card]] = []
    print("Card ID is [B]ai, [Z]hong, [F]a, [H]ua, [R]ed, [G]reen, [B]lack")
    print("Numbercard e.g. R3")
    abort_row = "a"
    special_card_map = {
        "b": SpecialCard.Bai,
        "z": SpecialCard.Zhong,
        "f": SpecialCard.Fa,
        "h": SpecialCard.Hua,
    }
    suit_map = {
        "r": NumberCard.Suit.Red,
        "g": NumberCard.Suit.Green,
        "b": NumberCard.Suit.Black,
    }
    for square in squares:
        while True:
            cv2.imshow("Catalogue", cv2.resize(square, (500, 500)))
            cv2.waitKey(1)
            card_id = input("Card ID:").lower()
            card_type: Optional[Card] = None
            if len(card_id) == 1:
                if card_id not in special_card_map:
                    continue
                card_type = special_card_map[card_id]
            elif len(card_id) == 2:
                if not card_id[0] in suit_map:
                    continue
                if not card_id[1].isdigit():
                    continue
                if card_id[1] == "0":
                    continue
                card_type = NumberCard(
                    number=int(card_id[1]), suit=suit_map[card_id[0]]
                )
            else:
                continue
            assert card_type is not None
            print(card_type)
            result.append((square, card_type))
            break

    cv2.destroyWindow("Catalogue")
    assert len(result) == len(squares)
    return result
