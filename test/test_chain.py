"""Contains tests for chain module"""
import unittest

from .context import shenzhen_solitaire
from shenzhen_solitaire.board import NumberCard, SpecialCard, Board, Position
from shenzhen_solitaire.board_actions import MoveAction, BunkerizeAction, GoalAction, HuaKillAction
from shenzhen_solitaire import board_possibilities
from .boards import my_board


class ChainTestClass(unittest.TestCase):
    """Tests the chain class"""

    def test_sequence(self) -> None:
        """Tests a given sequence. Might break if I change the iterators"""

        self.assertTrue(my_board.check_correct())
        sequence = [
            MoveAction(
                cards=[
                    NumberCard(
                        suit=NumberCard.Suit.Red,
                        number=7),
                    NumberCard(
                        suit=NumberCard.Suit.Green,
                        number=6)],
                source_id=3,
                destination_id=7),
            BunkerizeAction(
                card=NumberCard(
                    suit=NumberCard.Suit.Red,
                    number=6),
                bunker_id=0,
                field_id=2,
                to_bunker=True),
            GoalAction(
                card=NumberCard(
                    suit=NumberCard.Suit.Green,
                    number=1),
                source_id=2,
                source_position=Position.Field),
            MoveAction(
                cards=[
                    NumberCard(
                        suit=NumberCard.Suit.Red,
                        number=4)],
                source_id=2,
                destination_id=5),
            GoalAction(
                card=NumberCard(
                    suit=NumberCard.Suit.Red,
                    number=1),
                source_id=2,
                source_position=Position.Field),
            HuaKillAction(source_field_id=2),
            MoveAction(
                cards=[
                    NumberCard(
                        suit=NumberCard.Suit.Black, number=9),
                    NumberCard(suit=NumberCard.Suit.Red, number=8)],
                source_id=6,
                destination_id=2),
            GoalAction(
                card=NumberCard(
                    suit=NumberCard.Suit.Green, number=2),
                source_id=6,
                source_position=Position.Field)
        ]
        for action in sequence:
            step = list(board_possibilities.possible_actions(my_board))
            self.assertIn(action, step)
            action.apply(my_board)
