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


def debug_screenshot(image):
    cv2.namedWindow("Name", cv2.WINDOW_KEEPRATIO)
    cv2.imshow("Name", image)
    cv2.waitKey(0)
    input()
    cv2.destroyAllWindows()


def solve() -> None:
    screenshot_dir = Path(tempfile.mkdtemp())
    screenshot_file = screenshot_dir / "screenshot.png"
    screenshot = pyautogui.screenshot(region=(*OFFSET, *SIZE))
    screenshot.save(screenshot_file)
    image = cv2.imread(str(screenshot_file))
    # debug_screenshot()

    print("Solving")
    conf = configuration.load("test_config.zip")
    board = parse_board(image, conf)
    print(board)
    solution = list(next(solver.solve(board)))
    print(*solution, sep="\n")
    time.sleep(1)
    for step in solution:
        print(step)
        # time.sleep(0.5)
        clicker.handle_action(step, OFFSET, conf)
    clicker.click(NEW_BUTTON, OFFSET)
    time.sleep(10)


def main() -> None:
    time.sleep(3)
    while True:
        solve()


if __name__ == "__main__":
    main()
