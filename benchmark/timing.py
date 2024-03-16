import multiprocessing
from pathlib import Path

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
        pool.close()
        pool.join()


if __name__ == "__main__":
    main()
