import argparse
import sys

import cv2

import shenzhen_solitaire.card_detection.configuration as configuration
from shenzhen_solitaire.card_detection.board_parser import parse_to_json


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse board to json")
    parser.add_argument("board_path", type=str, help="Path to image of board")
    parser.add_argument(
        "--config", dest="config_path", type=str, help="Config path",
    )

    args = parser.parse_args()
    image = cv2.imread(args.board_path)

    conf = configuration.load("test_config.zip")

    print(parse_to_json(image, conf))


if __name__ == "__main__":
    main()
