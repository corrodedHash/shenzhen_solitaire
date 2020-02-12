import multiprocessing
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np

import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.solver.solver as solver
from shenzhen_solitaire.card_detection.board_parser import parse_board

from .util import run_benchmark

benchmark_files = [
    "pictures/20190809172206_1.jpg",
    "pictures/20190809172213_1.jpg",
    "pictures/20190809172219_1.jpg",
    "pictures/20190809172225_1.jpg",
    "pictures/20190809172232_1.jpg",
    "pictures/20190809172238_1.jpg",
]


def main() -> None:
    with multiprocessing.Pool() as pool:
        result = pool.imap_unordered(
            run_benchmark, [Path(benchmark) for benchmark in benchmark_files]
        )
        for current_result in result:
            print(current_result)


if __name__ == "__main__":
    main()
