"""Contains function to manually test the visual detection of a board"""

import copy
import unittest
from typing import List, Optional, Tuple, Union

import cv2
import numpy as np

import shenzhen_solitaire.card_detection.configuration as configuration
from shenzhen_solitaire import board
from shenzhen_solitaire.board import Card, NumberCard, SpecialCard
from shenzhen_solitaire.card_detection import adjustment, board_parser

from . import boards


class CardDetectionTest(unittest.TestCase):
    def test_parse(self) -> None:
        """Parse a configuration and a board"""
        image = cv2.imread("pictures/20190809172206_1.jpg")

        loaded_config = configuration.load("test_config.zip")
        my_board = board_parser.parse_board(image, loaded_config)

        for correct_row, my_row in zip(boards.B20190809172206_1.field, my_board.field):
            self.assertListEqual(correct_row, my_row)

    def test_hua_detection(self) -> None:
        """Read a board and check if it can detect if the flower is gone"""
        loaded_config = configuration.load("test_config.zip")
        imagenames = [
            ("BaiBlack", False),
            ("BaiShiny", True),
            ("BunkerCards", True),
            ("FaShiny", False),
            ("ZhongShiny", False),
        ]
        for imagename, flower_gone in imagenames:
            image = cv2.imread(f"pictures/specific/{imagename}.jpg")
            my_board = board_parser.parse_board(image, loaded_config)
            self.assertEqual(flower_gone, my_board.flower_gone)

    def test_bunker_parsing(self) -> None:
        loaded_config = configuration.load("test_config.zip")
        imagenames: List[
            Tuple[str, List[Union[Tuple[SpecialCard, int], Card, None]]]
        ] = [
            (
                "BaiBlack",
                [(SpecialCard.Bai, 0), None, NumberCard(NumberCard.Suit.Green, 3)],
            ),
            (
                "BaiShiny",
                [(SpecialCard.Zhong, 0), SpecialCard.Bai, (SpecialCard.Fa, 0)],
            ),
            (
                "BunkerCards",
                [
                    NumberCard(NumberCard.Suit.Black, 6),
                    NumberCard(NumberCard.Suit.Green, 9),
                    NumberCard(NumberCard.Suit.Green, 8),
                ],
            ),
            ("FaShiny", [None, NumberCard(NumberCard.Suit.Green, 6), SpecialCard.Fa]),
            (
                "ZhongShiny",
                [
                    (SpecialCard.Fa, 0),
                    NumberCard(NumberCard.Suit.Green, 6),
                    SpecialCard.Zhong,
                ],
            ),
        ]
        for imagename, bunker in imagenames:
            image = cv2.imread(f"pictures/specific/{imagename}.jpg")
            my_board = board_parser.parse_board(image, loaded_config)
            self.assertListEqual(bunker, my_board.bunker)

    def test_goal_parsing(self) -> None:
        loaded_config = configuration.load("test_config.zip")
        imagenames: List[Tuple[str, List[Optional[NumberCard]]]] = [
            ("BaiBlack", [NumberCard(NumberCard.Suit.Green, 2), None, None],),
            (
                "BaiShiny",
                [
                    NumberCard(NumberCard.Suit.Green, 3),
                    NumberCard(NumberCard.Suit.Red, 2),
                    NumberCard(NumberCard.Suit.Black, 3),
                ],
            ),
            (
                "BunkerCards",
                [
                    NumberCard(NumberCard.Suit.Red, 1),
                    NumberCard(NumberCard.Suit.Black, 1),
                    None,
                ],
            ),
            ("FaShiny", [NumberCard(NumberCard.Suit.Green, 2), None, None]),
            ("ZhongShiny", [NumberCard(NumberCard.Suit.Green, 2), None, None]),
        ]
        for imagename, goal in imagenames:
            image = cv2.imread(f"pictures/specific/{imagename}.jpg")
            my_board = board_parser.parse_board(image, loaded_config)
            self.assertListEqual(goal, my_board.goal)
