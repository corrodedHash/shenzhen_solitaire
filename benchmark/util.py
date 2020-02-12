import time
from pathlib import Path

import cv2

import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.solver.solver as solver
from shenzhen_solitaire.card_detection.board_parser import parse_board


def run_benchmark(benchmark: Path) -> str:
    result = ""
    result += f"{benchmark}:\n"
    read_file_time = time.time()
    image = cv2.imread(str(benchmark))
    load_config_time = time.time()
    result += f"\tLoad image:  {load_config_time - read_file_time:5.2f}\n"

    conf = configuration.load("test_config.zip")
    parse_board_time = time.time()
    result += f"\tLoad config: {parse_board_time - load_config_time:5.2f}\n"

    board = parse_board(image, conf)
    solve_time = time.time()
    result += f"\tParse image: {solve_time - parse_board_time:5.2f}\n"

    solution_iterator = next(solver.solve(board, timeout=10), None)
    finished_time = time.time()
    result += f"\tSolve board: {finished_time - solve_time:5.2f}\n"

    assert board.check_correct()
    if solution_iterator is None:
        result += "\tSolution timed out\n"
    else:
        result += f"\tSolved in {len(list(solution_iterator))} steps\n"
    return result
