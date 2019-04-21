from .context import shenzhen_solitaire
from shenzhen_solitaire import solver

from .boards import my_board


def main() -> None:
    A = solver.solve(my_board)
    for _, B in zip(range(1), A):
        print(*B, sep='\n')
        print(f"Solution: {len(B)}")


if __name__ == "__main__":
    main()
