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

    bunker_adjustment = adjustment.adjust_squares(
        image,
        count_x=3,
        count_y=1,
        adjustment=adjustment.Adjustment(
            **{"x": 730, "y": 310, "w": 19, "h": 21, "dx": 152, "dy": 0}
        ),
    )
    print(json.dumps(dataclasses.asdict(bunker_adjustment)))

    back_image = cv2.imread("pictures/specific/BaiShiny.jpg")
    back_squares = card_finder.get_field_squares(
        back_image, count_x=1, count_y=3, adjustment=copy.deepcopy(bunker_adjustment)
    )

    green_image = cv2.imread("pictures/20190809172213_1.jpg")
    green_squares = card_finder.get_field_squares(
        green_image, count_x=1, count_y=3, adjustment=copy.deepcopy(bunker_adjustment)
    )

    cv2.imwrite("/tmp/bunker_green_1.png", green_squares[0])
    cv2.imwrite("/tmp/bunker_green_2.png", green_squares[1])
    cv2.imwrite("/tmp/bunker_green_3.png", green_squares[2])


if __name__ == "__main__":
    main()
