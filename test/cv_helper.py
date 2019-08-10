"""Contains function to manually test the visual detection of a board"""

import numpy as np
import cv2

from shenzhen_solitaire.cv import adjustment
from shenzhen_solitaire.cv import board_parser
from shenzhen_solitaire import board
from shenzhen_solitaire.cv.configuration import Configuration


def generate() -> None:
    """Generate a configuration"""
    with open("pictures/20190809172213_1.jpg", 'rb') as png_file:
        img_str = png_file.read()
    nparr = np.frombuffer(img_str, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    generated_config = Configuration.generate(image)
    generated_config.save('test_config.zip')


def parse() -> board.Board:
    """Parse a configuration"""
    with open("pictures/20190809172213_1.jpg", 'rb') as png_file:
        img_str = png_file.read()
    nparr = np.frombuffer(img_str, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    # image = cv2.resize(image, (1000, 629))

    loaded_config = Configuration.load('test_config.zip')
    # loaded_config.field_adjustment = adjustment.adjust_field(image)
    return board_parser.parse_board(image, loaded_config)


if __name__ == "__main__":
    # generate()
    parse()
