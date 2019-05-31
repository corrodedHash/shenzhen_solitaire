import itertools
from typing import Tuple, List, Dict
import zipfile
import io
import json
import dataclasses

import numpy as np
import cv2

from .context import shenzhen_solitaire
from shenzhen_solitaire.cv import adjustment
from shenzhen_solitaire.cv import card_finder
from shenzhen_solitaire.cv import board_parser
from shenzhen_solitaire import board
from shenzhen_solitaire.cv.configuration import Configuration


def generate() -> None:
    with open("Solitaire.png", 'rb') as fd:
        img_str = fd.read()
    nparr = np.frombuffer(img_str, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    a = Configuration.generate(image)
    a.save('test_config.zip')

def parse() -> board.Board:
    with open("Solitaire2.png", 'rb') as fd:
        img_str = fd.read()
    nparr = np.frombuffer(img_str, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    image = cv2.resize(image, (1000, 629))

    a = Configuration.load('test_config.zip')
    a.field_adjustment = adjustment.adjust_field(image)
    return board_parser.parse_board(image, a)


if __name__ == "__main__":
    #generate()
    parse()
