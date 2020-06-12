import argparse

import cv2
import numpy as np

from shenzhen_solitaire.card_detection import configuration, adjustment, card_finder
from shenzhen_solitaire.card_detection.configuration import Configuration


def main() -> None:
    """Generate a configuration"""
    parser = argparse.ArgumentParser(
        description="Generate pictures for symbols, "
        "requires screenshot of field with no moved cards, "
        "so 8 columns of 5 cards each"
    )
    parser.add_argument(
        "screenshot_path",
        metavar="screenshot_path",
        type=str,
        help="Path to the screenshot",
    )
    parser.add_argument(
        "--conf",
        dest="config_path",
        type=str,
        default="config.zip",
        help="Path to existing config to be merged, or new config",
    )

    args = parser.parse_args()
    print(args.screenshot_path)
    image = cv2.imread(args.screenshot_path)

    adj = adjustment.adjust_field(image)
    squares = card_finder.get_field_squares(image, adj, 5, 8)
    catalogue = card_finder.catalogue_cards(squares)
    generated_config = Configuration(field_adjustment=adj, catalogue=catalogue, meta={})
    configuration.save(generated_config, args.config_path)


if __name__ == "__main__":
    main()
