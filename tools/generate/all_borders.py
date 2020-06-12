import argparse
import copy
import dataclasses
import json
import os

import cv2
import numpy as np

import shenzhen_solitaire.card_detection.adjustment as adjustment
import shenzhen_solitaire.card_detection.card_finder as card_finder
import shenzhen_solitaire.card_detection.configuration as configuration
from shenzhen_solitaire.card_detection.configuration import Configuration


def main() -> None:
    """Generate a configuration"""

    parser = argparse.ArgumentParser(
        description="Calibrate to fit all symbols. "
        "Ideally use a screenshot with cards in the bunker, "
        "in the goal and also with a killed hua card"
    )
    parser.add_argument(
        "screenshot_path",
        metavar="screenshot_path",
        type=str,
        help="Path to the screenshot",
    )
    parser.add_argument(
        "--config",
        metavar="config_path",
        type=str,
        default="test_config.zip",
        help="Config path, either merge or write new",
    )

    args = parser.parse_args()
    print(args.screenshot_path)
    image = cv2.imread(args.screenshot_path)

    if os.path.exists(args.config):
        conf = configuration.load(args.config)
    else:
        conf = Configuration()

    print("Field cards")
    conf.field_adjustment = adjustment.adjust_squares(
        image, count_x=8, count_y=13, adjustment=copy.deepcopy(conf.field_adjustment)
    )
    print("Field borders")
    conf.border_adjustment = adjustment.adjust_squares(
        image, count_x=8, count_y=13, adjustment=copy.deepcopy(conf.field_adjustment)
    )
    for adj in (conf.bunker_adjustment, conf.goal_adjustment,conf.hua_adjustment):
        adj.w = conf.field_adjustment.w
        adj.h = conf.field_adjustment.h
        adj.dx = conf.field_adjustment.dx
        adj.dy = conf.field_adjustment.dy

    conf.bunker_adjustment.x = conf.field_adjustment.x
    print("Bunker cards")
    conf.bunker_adjustment = adjustment.adjust_squares(
        image, count_x=3, count_y=1, adjustment=copy.deepcopy(conf.bunker_adjustment)
    )

    conf.goal_adjustment.x = conf.field_adjustment.x + 5 * conf.field_adjustment.dx
    conf.goal_adjustment.y = conf.bunker_adjustment.y
    print("Goal cards")
    conf.goal_adjustment = adjustment.adjust_squares(
        image, count_x=3, count_y=1, adjustment=copy.deepcopy(conf.goal_adjustment)
    )
    conf.hua_adjustment.y = conf.bunker_adjustment.y
    print("Hua card")
    conf.hua_adjustment = adjustment.adjust_squares(
        image, count_x=1, count_y=1, adjustment=copy.deepcopy(conf.hua_adjustment)
    )

    configuration.save(conf, args.config)


if __name__ == "__main__":
    main()
