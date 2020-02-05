"""Contains function to manually test the visual detection of a board"""

import unittest

import cv2
import numpy as np

from shenzhen_solitaire import board
from shenzhen_solitaire.card_detection import adjustment, board_parser
from shenzhen_solitaire.card_detection.configuration import Configuration
from . import boards


class CardDetectionTest(unittest.TestCase):
    def test_parse(self) -> None:
        """Parse a configuration and a board"""
        image = cv2.imread("pictures/20190809172206_1.jpg")

        loaded_config = Configuration.load("test_config.zip")
        my_board = board_parser.parse_board(image, loaded_config)

        for rows in zip(boards.B20190809172206_1.field, my_board.field):
            for good_cell, test_cell in zip(*rows):
                self.assertEqual(good_cell, test_cell)

