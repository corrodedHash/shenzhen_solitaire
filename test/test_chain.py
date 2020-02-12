"""Contains tests for chain module"""
import unittest

from shenzhen_solitaire.board import NumberCard, Position
from shenzhen_solitaire.solver import board_possibilities
from shenzhen_solitaire.solver.board_actions import (
    BunkerizeAction,
    GoalAction,
    HuaKillAction,
    MoveAction,
)

from .boards import TEST_BOARD


class ChainTest(unittest.TestCase):
    """Tests the chain class"""

    def test_sequence(self) -> None:
        """Tests a given sequence. Might break if I change the iterators"""

        self.assertTrue(TEST_BOARD.check_correct())
        sequence = [
            MoveAction(
                cards=[
                    NumberCard(suit=NumberCard.Suit.Red, number=7),
                    NumberCard(suit=NumberCard.Suit.Green, number=6),
                ],
                source_id=3,
                source_row_index=3,
                destination_id=7,
                destination_row_index=5,
            ),
            BunkerizeAction(
                card=NumberCard(suit=NumberCard.Suit.Red, number=6),
                bunker_id=0,
                field_id=2,
                field_row_index=4,
                to_bunker=True,
            ),
            GoalAction(
                card=NumberCard(suit=NumberCard.Suit.Green, number=1),
                source_id=2,
                source_row_index=3,
                source_position=Position.Field,
                obvious=True,
                goal_id=0,
            ),
            MoveAction(
                cards=[NumberCard(suit=NumberCard.Suit.Red, number=4)],
                source_id=2,
                source_row_index=2,
                destination_id=5,
                destination_row_index=5,
            ),
            GoalAction(
                card=NumberCard(suit=NumberCard.Suit.Red, number=1),
                source_id=2,
                source_row_index=1,
                source_position=Position.Field,
                obvious=True,
                goal_id=1,
            ),
            HuaKillAction(source_field_id=2, source_field_row_index=0),
            MoveAction(
                cards=[
                    NumberCard(suit=NumberCard.Suit.Black, number=9),
                    NumberCard(suit=NumberCard.Suit.Red, number=8),
                ],
                source_id=6,
                source_row_index=3,
                destination_id=2,
                destination_row_index=0,
            ),
            GoalAction(
                card=NumberCard(suit=NumberCard.Suit.Green, number=2),
                source_id=6,
                source_row_index=2,
                source_position=Position.Field,
                obvious=False,
                goal_id=0,
            ),
        ]
        for action in sequence:
            step = list(board_possibilities.possible_actions(TEST_BOARD))
            self.assertIn(action, step)
            action.apply(TEST_BOARD)
