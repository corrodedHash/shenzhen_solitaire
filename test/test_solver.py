"""Contains the SolverTest class"""
import unittest
import copy

from shenzhen_solitaire import solver

from .boards import TEST_BOARD


class SolverTest(unittest.TestCase):
    """Tests the solitaire solver"""

    def test_solver(self) -> None:
        """Tests solver"""
        board_copy = copy.deepcopy(TEST_BOARD)
        board_id = TEST_BOARD.state_identifier  # type: ignore
        board_solution_iterator = solver.solve(TEST_BOARD)
        for _, current_solution in zip(range(1), board_solution_iterator):
            self.assertEqual(board_id, board_copy.state_identifier)
            for action in current_solution:
                action.apply(board_copy)
                self.assertTrue(board_copy.check_correct())
            self.assertTrue(board_copy.solved())
