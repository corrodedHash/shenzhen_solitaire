import numpy as np
import cv2
from shenzhen_solitaire.card_detection.configuration import Configuration
import shenzhen_solitaire.card_detection.adjustment as adjustment
import shenzhen_solitaire.card_detection.card_finder as card_finder
import copy


def main() -> None:
    """Generate a configuration"""
    image = cv2.imread("pictures/20190809172213_1.jpg")

    border_adjustment = adjustment.adjust_squares(image, count_x=8, count_y=13)
    border_square_pos = adjustment.adjust_squares(
        image, count_x=1, count_y=1, adjustment=copy.deepcopy(border_adjustment)
    )
    border_square = card_finder.get_field_squares(image, border_square_pos, 1, 1)
    empty_square = card_finder.get_field_squares(image, border_square_pos, 1, 1)


if __name__ == "__main__":
    main()

