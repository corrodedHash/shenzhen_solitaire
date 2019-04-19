"""Contains tests for chain module"""
import unittest

from .context import shenzhen_solitaire
from shenzhen_solitaire.board import NumberCard, SpecialCard, Board
from shenzhen_solitaire import board_possibilities
from .boards import my_board


class ChainTestClass(unittest.TestCase):
    """Tests the chain class"""

    def test_sequence(self) -> None:
        """Tests a given sequence. Might break if I change the iterators"""

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
