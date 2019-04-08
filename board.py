"""Contains board class"""
import enum
from typing import Union, List, Dict, Optional, Set, Tuple
import dataclasses
from dataclasses import dataclass
import itertools


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


class Board:
    """Solitaire board"""

    def __init__(self) -> None:
        self.field: List[List[Card]] = [[]] * 8
        self.bunker: List[Union[Tuple[SpecialCard, int], Optional[Card]]] = [None] * 3
        self.goal: Dict[NumberCard.Suit, int] = {
            NumberCard.Suit.Red: 0,
            NumberCard.Suit.Green: 0,
            NumberCard.Suit.Black: 0,
        }

    flowerGone: bool = False

    def check_correct(self) -> bool:
        """Returns true, if the board is in a valid state"""
        number_cards: Dict[NumberCard.Suit, Set[int]] = {
            NumberCard.Suit.Red: set(),
            NumberCard.Suit.Green: set(),
            NumberCard.Suit.Black: set(),
        }
        special_cards: Dict[SpecialCard, int] = {
            SpecialCard.Zhong: 0,
            SpecialCard.Bai: 0,
            SpecialCard.Fa: 0,
            SpecialCard.Hua: 0,
        }

        if self.flowerGone:
            special_cards[SpecialCard.Hua] += 1

        for card in itertools.chain(
            self.bunker,
            itertools.chain.from_iterable(stack for stack in self.field if stack),
        ):
            if isinstance(card, tuple):
                special_cards[card[0]] += 4  # pylint: disable=E1136
            elif isinstance(card, SpecialCard):
                special_cards[card] += 1
            elif isinstance(card, NumberCard):
                if card.number in number_cards[card.suit]:
                    return False
                number_cards[card.suit].add(card.number)

        for _, numbers in number_cards.items():
            if set(range(1, 10)) != numbers:
                return False

        for cardtype, count in special_cards.items():
            if cardtype == SpecialCard.Hua:
                if count != 1:
                    return False
            else:
                if count != 4:
                    return False
        return True
