import tempfile
import time
from pathlib import Path

import cv2
import numpy as np

import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.solver.solver as solver
from shenzhen_solitaire.card_detection.board_parser import parse_board

benchmark_files = [
    "pictures/20190809172206_1.jpg",
    "pictures/20190809172213_1.jpg",
    "pictures/20190809172219_1.jpg",
    "pictures/20190809172225_1.jpg",
    "pictures/20190809172232_1.jpg",
    "pictures/20190809172238_1.jpg",
]


def main() -> None:
    for benchmark in benchmark_files:
        print(f"{benchmark}:")
        read_file_time = time.time()

        image = cv2.imread(benchmark)
        load_config_time = time.time()
        print(f"Load image:  {load_config_time - read_file_time:5.2f}")

        conf = configuration.load("test_config.zip")
        parse_board_time = time.time()
        print(f"Load config: {parse_board_time - load_config_time:5.2f}")

        board = parse_board(image, conf)
        solve_time = time.time()
        print(f"Parse image: {solve_time - parse_board_time:5.2f}")

        solution_iterator = next(solver.solve(board, timeout=10), None)
        finished_time = time.time()
        print(f"Solve board: {finished_time - solve_time:5.2f}")

        assert board.check_correct()
        if solution_iterator is None:
            print("Solution timed out")
        else:
            print(f"Solved in {len(list(solution_iterator))} steps")


if __name__ == "__main__":
    main()
