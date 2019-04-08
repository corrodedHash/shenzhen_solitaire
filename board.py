"""Contains board class"""
import enum
from typing import Union, List, Dict, Optional, NewType
from dataclasses import dataclass


class SpecialCard(enum.Enum):
    """Different types of special cards"""
    Zhong = enum.auto()
    Bai = enum.auto()
    Fa = enum.auto()
    Hua = enum.auto()


@dataclass(frozen=True)
class NumberCard:
    """Different number cards"""
    class Suit(enum.Enum):
        """Different colors number cards can have"""
        Red = enum.auto()
        Green = enum.auto()
        Black = enum.auto()
    suit: Suit
    number: int


Card = Union[NumberCard, SpecialCard]


class Position(enum.Enum):
    """Possible Board positions"""
    Field = enum.auto()
    Bunker = enum.auto()
    Goal = enum.auto()


KilledDragon = NewType('KilledDragon', SpecialCard)

@dataclass
class Board:
    """Solitaire board"""
    field: List[List[Card]] = [[]] * 8
    bunker: List[Union[KilledDragon, Optional[Card]]] = [None] * 3
    goal: Dict[NumberCard.Suit, int] = {NumberCard.Suit.Red: 0,
                                        NumberCard.Suit.Green: 0,
                                        NumberCard.Suit.Black: 0}
    flowerGone: bool = False
