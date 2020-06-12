import argparse
import os
import subprocess
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any
import json
import cv2
import numpy as np
import pyautogui

import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.clicker as clicker
from shenzhen_solitaire.board import Board
from shenzhen_solitaire.card_detection.board_parser import parse_start_board

OFFSET = (0, 0)
# SIZE = (2560, 1440)
SIZE = (1366, 768)
NEW_BUTTON = (1900, 1100)

SAVE_UNSOLVED = False
UNSOLVED_DIR = "E:/shenzhen-solitaire/unsolved"
SOLVER_PATH = '/home/lukas/documents/coding/rust/shenzhen-solitaire/target/release/solver'

def extern_solve(board: Board) -> List[Dict[str, Any]]:
    result = subprocess.run([SOLVER_PATH], input=board.to_json(), capture_output=True, text=True)
    return json.loads(result.stdout)

def take_screenshot() :
    with tempfile.TemporaryDirectory(prefix="shenzhen_solitaire") as screenshot_dir:
        print("Taking screenshot")
        screenshot_file = Path(screenshot_dir) / "screenshot.png"
        screenshot = pyautogui.screenshot(region=(*OFFSET, *SIZE))
        screenshot.save(screenshot_file)
        image = cv2.imread(str(screenshot_file))
    return image

def solve(conf: configuration.Configuration) -> None:
    image = take_screenshot()
    board = parse_start_board(image, conf)
    assert board.check_correct()
    actions = extern_solve(board)
    assert 0
    print(f"Solved in {len(actions)} steps")
    clicker.handle_actions(actions, OFFSET, conf)
    print("Solved")
    time.sleep(2)
    clicker.click(NEW_BUTTON, OFFSET)
    time.sleep(7)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Solve board"
    )
    parser.add_argument(
        "config_path",
        type=str,
        help="Config path",
    )

    args = parser.parse_args()
    time.sleep(3)
    conf = configuration.load(args.config_path)
    while True:
        solve(conf)


if __name__ == "__main__":
    main()
