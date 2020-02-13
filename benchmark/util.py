import time
from pathlib import Path

import cv2

import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.solver.solver as solver
from shenzhen_solitaire.card_detection.board_parser import parse_board
from typing import Callable, List, Tuple


class SingleTimer:
    def __init__(self, name: str, callback: Callable[[str, float], None]):
        self.name = name
        self.callback = callback
        self.start = 0.0

    def __enter__(self) -> None:
        self.start = time.time()
        return

    def __exit__(self, *args) -> None:
        self.callback(self.name, time.time() - self.start)
        return


class BenchmarkTimer:
    def __init__(self) -> None:
        self.timing: List[Tuple[str, float]] = []

    def addTiming(self, name: str, duration: float) -> None:
        self.timing.append((name, duration))

    def stopwatch(self, name: str) -> SingleTimer:
        return SingleTimer(name, self.addTiming)

    @property
    def timings(self) -> List[float]:
        return [x[1] for x in self.timing]


def run_benchmark(benchmark: Path, *, timeout: float = 10) -> None:
    result = ""
    result += f"{benchmark}:\n"
    my_timer = BenchmarkTimer()
    with my_timer.stopwatch("Load image"):
        image = cv2.imread(str(benchmark))

    with my_timer.stopwatch("Load configuration"):
        conf = configuration.load("test_config.zip")

    with my_timer.stopwatch("Parse board"):
        board = parse_board(image, conf)

    with my_timer.stopwatch("Solve board"):
        solution_iterator = next(solver.solve(board, timeout=timeout), None)

    solved_string = (
        "[" + ("Solved" if solution_iterator is not None else "Unsolved") + "]"
    )
    timings_string = "\t".join(f"{x:>5.2f}" for x in my_timer.timings)
    print(f"{solved_string:<10} {benchmark}")
    print(f"{timings_string}")
