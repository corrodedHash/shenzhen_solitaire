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
    "pictures/unsolved/tmp1ern14si.png",
    "pictures/unsolved/tmp2_0vn4tl.png",
    "pictures/unsolved/tmp32jmcnfp.png",
    "pictures/unsolved/tmpcml2ldfl.png",
    "pictures/unsolved/tmpd7rbwwdb.png",
    "pictures/unsolved/tmpdudxuw0s.png",
    "pictures/unsolved/tmpeplvz9bk.png",
    "pictures/unsolved/tmph_esy__3.png",
    "pictures/unsolved/tmpn95ueb7_.png",
    "pictures/unsolved/tmpqzay4q08.png",
    "pictures/unsolved/tmputbych59.png",
    "pictures/unsolved/tmpx4uo6pg3.png",
]


def runner(benchmark: Path) -> None:
    run_benchmark(benchmark, timeout=60)


def main() -> None:
    with multiprocessing.Pool() as pool:
        result = pool.imap_unordered(
            runner, [Path(benchmark) for benchmark in benchmark_files]
        )
        pool.close()
        pool.join()


if __name__ == "__main__":
    main()
