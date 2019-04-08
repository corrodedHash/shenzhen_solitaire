"""Contains actions that can be used on the board"""
from typing import List, Tuple, Union
from dataclasses import dataclass
import board


@dataclass
class GoalAction:
    """Move card from field to goal"""
    card: board.NumberCard
    source_id: int
    source_position: board.Position

    def apply(self, action_board: board.Board) -> None:
        """Do action"""
        if self.source_position == board.Position.Field:
            assert action_board.field[self.source_id][-1] == self.card
            assert action_board.goal[self.card.suit] + 1 == self.card.number
            action_board.field[self.source_id].pop()
            action_board.goal[self.card.suit] += 1
        elif self.source_position == board.Position.Bunker:
            assert action_board.bunker[self.source_id] == self.card
            assert action_board.goal[self.card.suit] + 1 == self.card.number
            action_board.bunker[self.source_id] = None
            action_board.goal[self.card.suit] += 1
        else:
            raise RuntimeError("Unknown position")

    def undo(self, action_board: board.Board) -> None:
        """Undo action"""
        assert action_board.goal[self.card.suit] == self.card.number
        if self.source_position == board.Position.Field:
            action_board.field[self.source_id].append(self.card)
        elif self.source_position == board.Position.Bunker:
            assert action_board.bunker[self.source_id] is None
            action_board.bunker[self.source_id] = self.card
        else:
            raise RuntimeError("Unknown position")
        action_board.goal[self.card.suit] -= 1


@dataclass
class RestoreAction:
    """Move card from bunker to field"""
    card: board.Card
    source_id: int
    destination_id: int

    def apply(self, action_board: board.Board) -> None:
        """Do action"""
        assert action_board.bunker[self.source_id] == self.card
        action_board.bunker[self.source_id] = None



@dataclass
class StoreAction:
    """Move card from field to bunker"""
    card: board.Card
    source_id: int
    destination_id: int


@dataclass
class MoveAction:
    """Moving a card from one field stack to another"""
    card: board.Card
    source_id: int
    destination_id: int

    def apply(self, action_board: board.Board) -> None:
        """Do action"""


@dataclass
class DragonKillAction:
    """Removing four dragons from the top of the stacks to a bunker"""
    dragon: board.SpecialCard
    source_stacks: List[Tuple[board.Position, int]]
    destination_bunker_id: int

    def apply(self, action_board: board.Board) -> None:
        """Do action"""
        assert (action_board.bunker[self.destination_bunker_id] is None or
                action_board.bunker[self.destination_bunker_id] == self.dragon)
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
        action_board.bunker[self.destination_bunker_id] = board.KilledDragon(
            self.dragon)

    def undo(self, action_board: board.Board) -> None:
        """Undo action"""
        assert action_board.bunker[self.destination_bunker_id] == board.KilledDragon(
            self.dragon)
        assert len(self.source_stacks) == 4
        for position, index in self.source_stacks:
            if position == board.Position.Field:
                action_board.field[index].append(self.dragon)
            elif position == board.Position.Bunker:
                action_board.bunker[index] = self.dragon
            else:
                raise RuntimeError("Can only kill dragons in field and bunker")
        action_board.bunker[self.destination_bunker_id] = None


@dataclass
class HuaKillAction:
    """Remove the flower card"""
    source_field_id: int

    def apply(self, action_board: board.Board) -> None:
        """Do action"""
        assert not action_board.flowerGone
        assert action_board.field[self.source_field_id] == board.SpecialCard.Hua
        action_board.field[self.source_field_id].pop()
        action_board.flowerGone = True

    def undo(self, action_board: board.Board) -> None:
        """Undo action"""
        assert action_board.flowerGone
        action_board.field[self.source_field_id].append(board.SpecialCard.Hua)
        action_board.flowerGone = False


Action = Union[MoveAction, DragonKillAction,
               HuaKillAction, StoreAction, RestoreAction, GoalAction]
