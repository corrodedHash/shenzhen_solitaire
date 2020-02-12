import tempfile
import time
from pathlib import Path

import cv2
import numpy as np

import pyautogui
import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.clicker.main as clicker
import shenzhen_solitaire.solver.solver as solver
from shenzhen_solitaire.card_detection.board_parser import parse_board

OFFSET = (0, 0)
SIZE = (2560, 1440)
NEW_BUTTON = (1900, 1100)


def solve() -> None:
    with tempfile.TemporaryDirectory() as screenshot_dir:
        screenshot_file = Path(screenshot_dir) / "screenshot.png"
        screenshot = pyautogui.screenshot(region=(*OFFSET, *SIZE))
        screenshot.save(screenshot_file)
        image = cv2.imread(str(screenshot_file))

    print("Solving")
    conf = configuration.load("test_config.zip")
    board = parse_board(image, conf)
    assert board.check_correct()
    try:
        solution = list(next(solver.solve(board, timeout=10)))
    except StopIteration:
        clicker.click(NEW_BUTTON, OFFSET)
        time.sleep(10)
        return
    print(f"Solved in {len(solution)} steps")
    for step in solution:
        print(step)
        clicker.handle_action(step, OFFSET, conf)
    clicker.click(NEW_BUTTON, OFFSET)
    time.sleep(10)


def main() -> None:
    time.sleep(3)
    while True:
        solve()


if __name__ == "__main__":
    main()
