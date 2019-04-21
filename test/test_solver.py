import unittest
import copy

from .context import shenzhen_solitaire
from shenzhen_solitaire import solver

from .boards import my_board


class SolverTest(unittest.TestCase):
    def test_solver(self) -> None:
        board_copy = copy.deepcopy(my_board)
        board_id = my_board.state_identifier
        A = solver.solve(my_board)
        for _, B in zip(range(1), A):
            self.assertEqual(board_id, board_copy.state_identifier)
            for x in B:
                x.apply(board_copy)
                self.assertTrue(board_copy.check_correct())
            self.assertTrue(board_copy.solved())
