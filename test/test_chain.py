"""Contains tests for chain module"""
import unittest

from .context import shenzhen_solitaire  # pylint: disable=unused-import
from shenzhen_solitaire.board import NumberCard, SpecialCard, Board  # pylint: disable=wrong-import-order
from shenzhen_solitaire import board_possibilities  # pylint: disable=wrong-import-order


class ChainTestClass(unittest.TestCase):
    """Tests the chain class"""

    def test_sequence(self) -> None:
        """Tests a given sequence. Might break if I change the iterators"""
        my_board: Board = Board()
        my_board.field[0] = [
            SpecialCard.Fa,
            NumberCard(NumberCard.Suit.Black, 8),
            SpecialCard.Bai,
            NumberCard(NumberCard.Suit.Black, 7),
            SpecialCard.Zhong,
        ]

        my_board.field[1] = [
            NumberCard(NumberCard.Suit.Red, 9),
            SpecialCard.Zhong,
            SpecialCard.Zhong,
            NumberCard(NumberCard.Suit.Black, 4),
            NumberCard(NumberCard.Suit.Black, 3),
        ]

        my_board.field[2] = [
            SpecialCard.Hua,
            NumberCard(NumberCard.Suit.Red, 1),
            NumberCard(NumberCard.Suit.Red, 4),
            NumberCard(NumberCard.Suit.Green, 1),
            NumberCard(NumberCard.Suit.Red, 6),
        ]

        my_board.field[3] = [
            SpecialCard.Bai,
            SpecialCard.Zhong,
            NumberCard(NumberCard.Suit.Red, 3),
            NumberCard(NumberCard.Suit.Red, 7),
            NumberCard(NumberCard.Suit.Green, 6),
        ]

        my_board.field[4] = [
            NumberCard(NumberCard.Suit.Green, 7),
            NumberCard(NumberCard.Suit.Green, 4),
            NumberCard(NumberCard.Suit.Red, 5),
            NumberCard(NumberCard.Suit.Green, 5),
            NumberCard(NumberCard.Suit.Black, 6),
        ]

        my_board.field[5] = [
            NumberCard(NumberCard.Suit.Green, 3),
            SpecialCard.Bai,
            SpecialCard.Fa,
            NumberCard(NumberCard.Suit.Black, 2),
            NumberCard(NumberCard.Suit.Black, 5),
        ]

        my_board.field[6] = [
            SpecialCard.Fa,
            NumberCard(NumberCard.Suit.Green, 9),
            NumberCard(NumberCard.Suit.Green, 2),
            NumberCard(NumberCard.Suit.Black, 9),
            NumberCard(NumberCard.Suit.Red, 8),
        ]

        my_board.field[7] = [
            SpecialCard.Bai,
            NumberCard(NumberCard.Suit.Red, 2),
            SpecialCard.Fa,
            NumberCard(NumberCard.Suit.Black, 1),
            NumberCard(NumberCard.Suit.Green, 8),
        ]

        self.assertTrue(my_board.check_correct())
        sequence = [
            0,
            4,
            0,
            1,
            0,
            0,
            8,
            0,
            1,
            3,
            0,
            9,
            0,
            2,
            0,
            1,
            1,
            1,
            2,
            0,
            2,
            1,
            6,
            12,
            0,
            0,
            1,
            0,
            0,
            17,
            11,
            1,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0]
        for action_index in sequence:
            step = list(board_possibilities.possible_actions(my_board))
            step[action_index].apply(my_board)
