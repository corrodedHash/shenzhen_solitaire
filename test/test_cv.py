"""Contains function to manually test the visual detection of a board"""

import unittest

import cv2
import numpy as np

from shenzhen_solitaire import board
from shenzhen_solitaire.card_detection import adjustment, board_parser
from shenzhen_solitaire.card_detection.configuration import Configuration


class CardDetectionTest(unittest.TestCase):
    def test_parse(self) -> None:
        """Parse a configuration"""
        with open("pictures/20190809172213_1.jpg", "rb") as png_file:
            img_str = png_file.read()
        nparr = np.frombuffer(img_str, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # image = cv2.resize(image, (1000, 629))

        loaded_config = Configuration.load("test_config.zip")
        # loaded_config.field_adjustment = adjustment.adjust_field(image)
        print(board_parser.parse_board(image, loaded_config))
