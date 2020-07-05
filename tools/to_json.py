import argparse
import sys

import cv2

import shenzhen_solitaire.card_detection.configuration as configuration
from shenzhen_solitaire.card_detection.board_parser import parse_board, parse_start_board


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse board to json")
    parser.add_argument("board_path", type=str, help="Path to image of board")
    parser.add_argument(
        "--config", dest="config_path", type=str, help="Config path",
    )
    parser.add_argument("--simple", action="store_true", help="Parse a start board, use when config is not complete")

    args = parser.parse_args()
    image = cv2.imread(args.board_path)

    conf = configuration.load(args.config_path)

    if args.simple:
        print(parse_start_board(image, conf).to_json())
    else:
        print(parse_board(image, conf).to_json())


if __name__ == "__main__":
    main()
