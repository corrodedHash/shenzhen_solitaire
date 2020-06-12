import os
import tempfile
import time
from pathlib import Path
from typing import List

import cv2
import numpy as np
import pyautogui

import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.clicker as clicker
import shenzhen_solitaire.solver.solver as solver
from shenzhen_solitaire.board import Board
from shenzhen_solitaire.card_detection.board_parser import parse_start_board
from shenzhen_solitaire.solver.board_actions import Action

OFFSET = (0, 0)
# SIZE = (2560, 1440)
SIZE = (1366, 768)
NEW_BUTTON = (1900, 1100)

SAVE_UNSOLVED = False
UNSOLVED_DIR = "E:/shenzhen-solitaire/unsolved"


def extern_solve(board: Board) -> List[Action]:
    pass


def solve(conf: configuration.Configuration) -> None:
    with tempfile.TemporaryDirectory(prefix="shenzhen_solitaire") as screenshot_dir:
        print("Taking screenshot")
        screenshot_file = Path(screenshot_dir) / "screenshot.png"
        screenshot = pyautogui.screenshot(region=(*OFFSET, *SIZE))
        screenshot.save(screenshot_file)
        image = cv2.imread(str(screenshot_file))
        input()

    print("Solving")
    board = parse_start_board(image, conf)
    print(board.to_json())
    assert board.check_correct()
    input()
    solution_iterator = next(solver.solve(board, timeout=10, verbose=True), None)
    if solution_iterator is None:
        clicker.click(NEW_BUTTON, OFFSET)
        time.sleep(10)
        if SAVE_UNSOLVED:
            fd, outfile = tempfile.mkstemp(dir=UNSOLVED_DIR, suffix=".png")
            sock = os.fdopen(fd, "w")
            sock.close()
            cv2.imwrite(outfile, image)
        return
    solution = list(solution_iterator)
    print(f"Solved in {len(solution)} steps")
    clicker.handle_actions(solution, OFFSET, conf)
    print("Solved")
    time.sleep(2)
    clicker.click(NEW_BUTTON, OFFSET)
    time.sleep(7)


def main() -> None:
    time.sleep(3)
    conf = configuration.load("test_config.zip")
    while True:
        solve(conf)


if __name__ == "__main__":
    main()
