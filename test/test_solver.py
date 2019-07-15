"""Contains the SolverTest class"""
import unittest
import copy

from shenzhen_solitaire import solver

from .boards import my_board


class SolverTest(unittest.TestCase):
    """Tests the solitaire solver"""

    def test_solver(self) -> None:
        """Tests solver"""
        board_copy = copy.deepcopy(my_board)
        board_id = my_board.state_identifier
        board_solution_iterator = solver.solve(my_board)
        for _, current_solution in zip(range(1), board_solution_iterator):
            self.assertEqual(board_id, board_copy.state_identifier)
            for action in current_solution:
                action.apply(board_copy)
                self.assertTrue(board_copy.check_correct())
            self.assertTrue(board_copy.solved())
