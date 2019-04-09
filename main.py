"""Main module"""
from typing import List, Tuple
from board import Board, NumberCard, SpecialCard
import board_possibilities
import board_actions


class SolitaireSolver:
    """Solver for Shenzhen Solitaire"""

    search_board: Board
    stack: List[Tuple[board_actions.Action, int]]


def main() -> None:
    t: Board = Board()
    t.field[0] = [
        SpecialCard.Fa,
        NumberCard(NumberCard.Suit.Black, 8),
        SpecialCard.Bai,
        NumberCard(NumberCard.Suit.Black, 7),
        SpecialCard.Zhong,
    ]

    t.field[1] = [
        NumberCard(NumberCard.Suit.Red, 9),
        SpecialCard.Zhong,
        SpecialCard.Zhong,
        NumberCard(NumberCard.Suit.Black, 4),
        NumberCard(NumberCard.Suit.Black, 3),
    ]

    t.field[2] = [
        SpecialCard.Hua,
        NumberCard(NumberCard.Suit.Red, 1),
        NumberCard(NumberCard.Suit.Red, 4),
        NumberCard(NumberCard.Suit.Green, 1),
        NumberCard(NumberCard.Suit.Red, 6),
    ]

    t.field[3] = [
        SpecialCard.Bai,
        SpecialCard.Zhong,
        NumberCard(NumberCard.Suit.Red, 3),
        NumberCard(NumberCard.Suit.Red, 7),
        NumberCard(NumberCard.Suit.Green, 6),
    ]

    t.field[4] = [
        NumberCard(NumberCard.Suit.Green, 7),
        NumberCard(NumberCard.Suit.Green, 4),
        NumberCard(NumberCard.Suit.Red, 5),
        NumberCard(NumberCard.Suit.Green, 5),
        NumberCard(NumberCard.Suit.Black, 6),
    ]

    t.field[5] = [
        NumberCard(NumberCard.Suit.Green, 3),
        SpecialCard.Bai,
        SpecialCard.Fa,
        NumberCard(NumberCard.Suit.Black, 2),
        NumberCard(NumberCard.Suit.Black, 5),
    ]

    t.field[6] = [
        SpecialCard.Fa,
        NumberCard(NumberCard.Suit.Green, 9),
        NumberCard(NumberCard.Suit.Green, 2),
        NumberCard(NumberCard.Suit.Black, 9),
        NumberCard(NumberCard.Suit.Red, 8),
    ]

    t.field[7] = [
        SpecialCard.Bai,
        NumberCard(NumberCard.Suit.Red, 2),
        SpecialCard.Fa,
        NumberCard(NumberCard.Suit.Black, 1),
        NumberCard(NumberCard.Suit.Green, 8),
    ]

    print(t.check_correct())
    step = list(board_possibilities.possible_actions(t))
    print(*step, sep="\n")
    sequence = [
        0, 4, 0, 1, 0, 0, 8, 0, 1, 3, 0, 9, 0, 2, 0, 1, 1, 1, 2, 0, 2, 1, 6,
        12, 0, 0, 1, 0, 0, 17, 11, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    ]
    for x in sequence:
        print("Executing " + str(step[x]))
        step[x].apply(t)
        print(t.goal)
        step = list(board_possibilities.possible_actions(t))
        print(*enumerate(step), sep="\n")
        print()


if __name__ == "__main__":
    main()
