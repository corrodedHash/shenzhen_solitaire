"""Contains actions that can be used on the board"""
from dataclasses import dataclass
from typing import List, Optional, Tuple

from .. import board


class Action:
    """Base class for a card move action on a solitaire board"""

    _before_state: int = 0
    _after_state: int = 0

    def _apply(self, action_board: board.Board) -> None:
        pass

    def _undo(self, action_board: board.Board) -> None:
        pass

    def apply(self, action_board: board.Board) -> None:
        """Apply action to board"""
        if __debug__:
            self._before_state = action_board.state_identifier
        self._apply(action_board)
        if __debug__:
            self._after_state = action_board.state_identifier

    def undo(self, action_board: board.Board) -> None:
        """Undo action to board"""
        assert action_board.state_identifier == self._after_state
        self._undo(action_board)
        assert action_board.state_identifier == self._before_state


@dataclass
class GoalAction(Action):
    """Move card from field to goal"""

    card: board.NumberCard
    source_id: int
    source_row_index: Optional[int]
    source_position: board.Position
    goal_id: int
    obvious: bool

    def _apply(self, action_board: board.Board) -> None:
        """Do action"""
        assert action_board.getGoalId(self.card.suit) == self.goal_id
        assert action_board.getGoal(self.card.suit) + 1 == self.card.number
        if self.source_position == board.Position.Field:
            assert action_board.field[self.source_id][-1] == self.card
            action_board.field[self.source_id].pop()
            action_board.incGoal(self.card.suit)
        elif self.source_position == board.Position.Bunker:
            assert action_board.bunker[self.source_id] == self.card
            action_board.bunker[self.source_id] = None
            action_board.incGoal(self.card.suit)
        else:
            raise RuntimeError("Unknown position")

    def _undo(self, action_board: board.Board) -> None:
        """Undo action"""
        assert action_board.getGoalId(self.card.suit) == self.goal_id
        assert action_board.getGoal(self.card.suit) == self.card.number
        if self.source_position == board.Position.Field:
            action_board.field[self.source_id].append(self.card)
        elif self.source_position == board.Position.Bunker:
            assert action_board.bunker[self.source_id] is None
            action_board.bunker[self.source_id] = self.card
        else:
            raise RuntimeError("Unknown position")
        action_board.setGoal(self.card.suit, action_board.getGoal(self.card.suit) - 1)


@dataclass
class BunkerizeAction(Action):
    """Move card from bunker to field"""

    card: board.Card
    bunker_id: int
    field_id: int
    field_row_index: int
    to_bunker: bool

    def _move_from_bunker(self, action_board: board.Board) -> None:
        assert action_board.bunker[self.bunker_id] == self.card
        action_board.bunker[self.bunker_id] = None
        action_board.field[self.field_id].append(self.card)

    def _move_to_bunker(self, action_board: board.Board) -> None:
        assert action_board.field[self.field_id][-1] == self.card
        assert action_board.bunker[self.bunker_id] is None
        action_board.bunker[self.bunker_id] = self.card
        action_board.field[self.field_id].pop()

    def _apply(self, action_board: board.Board) -> None:
        """Do action"""
        if self.to_bunker:
            self._move_to_bunker(action_board)
        else:
            self._move_from_bunker(action_board)

    def _undo(self, action_board: board.Board) -> None:
        """Undo action"""
        if self.to_bunker:
            self._move_from_bunker(action_board)
        else:
            self._move_to_bunker(action_board)


@dataclass
class MoveAction(Action):
    """Moving a card from one field stack to another"""

    cards: List[board.Card]
    source_id: int
    source_row_index: int
    destination_id: int
    destination_row_index: int

    def _shift(self, action_board: board.Board, source: int, dest: int) -> None:
        """Shift a card from the field id 'source' to field id 'dest'"""

        for stack_offset, card in enumerate(self.cards, start=-len(self.cards)):
            assert action_board.field[source][stack_offset] == card

        action_board.field[source] = action_board.field[source][: -len(self.cards)]
        action_board.field[dest].extend(self.cards)

    def _apply(self, action_board: board.Board) -> None:
        """Do action"""
        if action_board.field[self.destination_id]:
            dest_card = action_board.field[self.destination_id][-1]
            if not all(isinstance(x, board.NumberCard) for x in self.cards):
                raise AssertionError()
            if not isinstance(dest_card, board.NumberCard):
                raise AssertionError()
            if not isinstance(self.cards[0], board.NumberCard):
                raise AssertionError()
            if dest_card.suit == self.cards[0].suit:
                raise AssertionError()
            if dest_card.number != self.cards[0].number + 1:
                raise AssertionError()
        self._shift(action_board, self.source_id, self.destination_id)

    def _undo(self, action_board: board.Board) -> None:
        """Undo action"""
        self._shift(action_board, self.destination_id, self.source_id)


@dataclass
class DragonKillAction(Action):
    """Removing four dragons from the top of the stacks to a bunker"""

    dragon: board.SpecialCard
    source_stacks: List[Tuple[board.Position, int]]
    destination_bunker_id: int

    def _apply(self, action_board: board.Board) -> None:
        """Do action"""
        assert (
            action_board.bunker[self.destination_bunker_id] is None
            or action_board.bunker[self.destination_bunker_id] == self.dragon
        )
        assert len(self.source_stacks) == 4
        for position, index in self.source_stacks:
            if position == board.Position.Field:
                assert action_board.field[index]
                assert action_board.field[index][-1] == self.dragon
                action_board.field[index].pop()
            elif position == board.Position.Bunker:
                assert action_board.bunker[index] == self.dragon
                action_board.bunker[index] = None
            else:
                raise RuntimeError("Can only kill dragons in field and bunker")
        action_board.bunker[self.destination_bunker_id] = (self.dragon, 4)

    def _undo(self, action_board: board.Board) -> None:
        """Undo action"""
        assert action_board.bunker[self.destination_bunker_id] == (self.dragon, 4)
        assert len(self.source_stacks) == 4
        action_board.bunker[self.destination_bunker_id] = None
        for position, index in self.source_stacks:
            if position == board.Position.Field:
                action_board.field[index].append(self.dragon)
            elif position == board.Position.Bunker:
                action_board.bunker[index] = self.dragon
            else:
                raise RuntimeError("Can only kill dragons in field and bunker")


@dataclass
class HuaKillAction(Action):
    """Remove the flower card"""

    source_field_id: int
    source_field_row_index: int

    def _apply(self, action_board: board.Board) -> None:
        """Do action"""
        assert not action_board.flower_gone
        assert action_board.field[self.source_field_id][-1] == board.SpecialCard.Hua
        action_board.field[self.source_field_id].pop()
        action_board.flower_gone = True

    def _undo(self, action_board: board.Board) -> None:
        """Undo action"""
        assert action_board.flower_gone
        action_board.field[self.source_field_id].append(board.SpecialCard.Hua)
        action_board.flower_gone = False
