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
from shenzhen_solitaire import board
from shenzhen_solitaire.cv.configuration import Configuration


def main() -> None:
    with open("Solitaire.png", 'rb') as fd:
        img_str = fd.read()
    nparr = np.frombuffer(img_str, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    Configuration.generate(image)


if __name__ == "__main__":
    main()
