"""Contains function to manually test the visual detection of a board"""

import unittest

import cv2
import numpy as np

from shenzhen_solitaire import board
from shenzhen_solitaire.card_detection import adjustment, board_parser
import shenzhen_solitaire.card_detection.configuration as configuration
from . import boards


class CardDetectionTest(unittest.TestCase):
    def test_parse(self) -> None:
        """Parse a configuration and a board"""
        image = cv2.imread("pictures/20190809172206_1.jpg")

        loaded_config = configuration.load("test_config.zip")
        my_board = board_parser.parse_board(image, loaded_config)

        for correct_row, my_row in zip(boards.B20190809172206_1.field, my_board.field):
            self.assertListEqual(correct_row, my_row)
