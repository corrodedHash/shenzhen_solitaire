import tempfile
import time
from pathlib import Path

import cv2
import numpy as np

import pyautogui
import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.clicker as clicker
import shenzhen_solitaire.solver.solver as solver
from shenzhen_solitaire.card_detection.board_parser import parse_board

OFFSET = (0, 0)
SIZE = (2560, 1440)
NEW_BUTTON = (1900, 1100)


def solve() -> None:
    with tempfile.TemporaryDirectory() as screenshot_dir:
        print("Taking screenshot")
        screenshot_file = Path(screenshot_dir) / "screenshot.png"
        screenshot = pyautogui.screenshot(region=(*OFFSET, *SIZE))
        screenshot.save(screenshot_file)
        image = cv2.imread(str(screenshot_file))

    print("Solving")
    conf = configuration.load("test_config.zip")
    board = parse_board(image, conf)
    assert board.check_correct()
    solution_iterator = next(solver.solve(board, timeout=10), None)
    if solution_iterator is None:
        clicker.click(NEW_BUTTON, OFFSET)
        time.sleep(10)
        return
    solution=list(solution_iterator)
    print(f"Solved in {len(solution)} steps")
    clicker.handle_actions(solution, OFFSET, conf)
    time.sleep(2)
    clicker.click(NEW_BUTTON, OFFSET)
    time.sleep(7)


def main() -> None:
    time.sleep(3)
    while True:
        solve()


if __name__ == "__main__":
    main()
