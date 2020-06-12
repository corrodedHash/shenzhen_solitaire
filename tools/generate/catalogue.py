import argparse

import cv2
import numpy as np

from shenzhen_solitaire.card_detection import configuration, adjustment, card_finder
from shenzhen_solitaire.card_detection.configuration import Configuration


def main() -> None:
    """Generate a configuration"""
    parser = argparse.ArgumentParser(
        description="Generate pictures for symbols. "
        "Requires screenshot of field with no moved cards, "
        "so 8 columns of 5 cards each"
    )
    parser.add_argument(
        "screenshot_path",
        metavar="screenshot_path",
        type=str,
        help="Path to the screenshot",
    )
    parser.add_argument(
        "--config",
        dest="config_path",
        type=str,
        default="config.zip",
        help="Path to existing config to be merged, or new config",
    )

    args = parser.parse_args()
    image = cv2.imread(args.screenshot_path)
    conf = configuration.load(args.config_path)
    squares = card_finder.get_field_squares(image, conf.field_adjustment, 5, 8)
    catalogue = card_finder.catalogue_cards(squares)
    conf.card_border.extend(
        card_finder.get_field_squares(image, conf.border_adjustment, 1, 1)
    )
    conf.green_card.extend(
        card_finder.get_field_squares(image, conf.bunker_adjustment, 1, 3)
    )
    conf.green_card.extend(
        card_finder.get_field_squares(image, conf.goal_adjustment, 1, 3)
    )
    conf.green_card.extend(
        card_finder.get_field_squares(image, conf.hua_adjustment, 1, 1)
    )
    conf.catalogue.extend(catalogue)
    configuration.save(conf, args.config_path)


if __name__ == "__main__":
    main()
