"""Contains actions that can be used on the board"""
from typing import List, Tuple, Union
from dataclasses import dataclass
import board


@dataclass
class MoveAction:
    """Moving a card from one stack to another"""
    card: board.Card
    source_position: board.Position
    source_id: int
    destination_position: board.Position
    destination_id: int


@dataclass
class DragonKillAction:
    """Removing four dragons from the top of the stacks to a bunker"""
    dragon: board.SpecialCard
    source_stacks: List[Tuple[board.Position, int]]
    destination_bunker_id: int


@dataclass
class HuaKillAction:
    """Remove the flower card"""
    source_field_id: int


Action = Union[MoveAction, DragonKillAction, HuaKillAction]
