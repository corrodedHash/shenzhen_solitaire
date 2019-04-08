"""Contains board class"""
import enum
from typing import Union, Tuple, List
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


class BunkerStatus(enum.Enum):
    """States a bunker can be in, if it not holding a card"""
    Empty = enum.auto()
    Dragon = enum.auto()


@dataclass
class Board:
    """Solitaire board"""
    field: List[List[Card]] = []
    bunker: Tuple[Union[BunkerStatus, Card],
                  Union[BunkerStatus, Card],
                  Union[BunkerStatus, Card]] = (BunkerStatus.Empty,
                                                BunkerStatus.Empty, BunkerStatus.Empty,)
    goal: List[Tuple[NumberCard.Suit, int]] = []
    flowerGone: bool = False
