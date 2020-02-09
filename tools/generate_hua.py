import copy
import dataclasses
import json

import cv2
import numpy as np

import shenzhen_solitaire.card_detection.adjustment as adjustment
import shenzhen_solitaire.card_detection.card_finder as card_finder
from shenzhen_solitaire.card_detection.configuration import Configuration


def main() -> None:
    """Generate a configuration"""
    image = cv2.imread("pictures/specific/BunkerCards.jpg")

    hua_adjustment = adjustment.adjust_squares(
        image,
        count_x=1,
        count_y=1,
        adjustment=adjustment.Adjustment(
            **{"x": 1299, "y": 314, "w": 19, "h": 21, "dx": 0, "dy": 0}
        ),
    )
    print(json.dumps(dataclasses.asdict(hua_adjustment)))
    green_image = cv2.imread("pictures/specific/ZhongShiny.jpg")
    hua_green = card_finder.get_field_squares(
        green_image, hua_adjustment, count_x=1, count_y=1
    )
    cv2.imwrite("/tmp/hua_green.png", hua_green[0])


if __name__ == "__main__":
    main()
