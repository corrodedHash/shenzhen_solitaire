import copy
import dataclasses
import json
import tempfile
from pathlib import Path

import cv2
import numpy as np

import shenzhen_solitaire.card_detection.adjustment as adjustment
import shenzhen_solitaire.card_detection.card_finder as card_finder
from shenzhen_solitaire.card_detection.configuration import Configuration


def main() -> None:
    """Generate a configuration"""
    normal_image = cv2.imread("pictures/specific/BunkerCards.jpg")

    picture_dir = Path(tempfile.mkdtemp(prefix="shenzhen-special-buttons-"))
    print(picture_dir)
    button_adjustment = adjustment.adjust_squares(normal_image, count_x=1, count_y=3)
    normal_squares = card_finder.get_field_squares(
        normal_image, button_adjustment, 3, 1
    )
    cv2.imwrite(str(picture_dir / "nz.png"), normal_squares[0])
    cv2.imwrite(str(picture_dir / "nf.png"), normal_squares[1])
    cv2.imwrite(str(picture_dir / "nb.png"), normal_squares[2])

    fa_shiny_image = cv2.imread("pictures/specific/FaShiny.jpg")
    fa_shiny_squares = card_finder.get_field_squares(
        fa_shiny_image, button_adjustment, 3, 1
    )
    cv2.imwrite(str(picture_dir / "sf.png"), fa_shiny_squares[1])

    zhong_shiny_image = cv2.imread("pictures/specific/ZhongShiny.jpg")
    zhong_shiny_squares = card_finder.get_field_squares(
        zhong_shiny_image, button_adjustment, 3, 1
    )
    cv2.imwrite(str(picture_dir / "sz.png"), zhong_shiny_squares[0])

    bai_shiny_image = cv2.imread("pictures/specific/BaiShiny.jpg")
    bai_shiny_squares = card_finder.get_field_squares(
        bai_shiny_image, button_adjustment, 3, 1
    )
    cv2.imwrite(str(picture_dir / "sb.png"), bai_shiny_squares[2])
    cv2.imwrite(str(picture_dir / "gz.png"), bai_shiny_squares[0])
    cv2.imwrite(str(picture_dir / "gf.png"), bai_shiny_squares[1])

    bai_black_image = cv2.imread("pictures/specific/BaiBlack.jpg")
    bai_black_squares = card_finder.get_field_squares(
        bai_black_image, button_adjustment, 3, 1
    )
    cv2.imwrite(str(picture_dir / "gb.png"), bai_black_squares[2])
    print(picture_dir)
    print(json.dumps(dataclasses.asdict(button_adjustment)))


if __name__ == "__main__":
    main()
