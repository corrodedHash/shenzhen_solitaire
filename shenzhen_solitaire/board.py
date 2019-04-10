"""Contains board class"""
import enum
from typing import Union, List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
import itertools


class SpecialCard(enum.Enum):
    """Different types of special cards"""

    Zhong = 0
    Bai = 1
    Fa = 2
    Hua = 3

    def identifier(self) -> int:
        """Returns unique identifier representing this card"""
        return int(self.value)


@dataclass(frozen=True)
class NumberCard:
    """Different number cards"""

    class Suit(enum.Enum):
        """Different colors number cards can have"""

        Red = 0
        Green = 1
        Black = 2

    suit: Suit
    number: int  # [1 - 9]

    def identifier(self) -> int:
        """Returns unique identifier representing this card"""
        return int(self.number - 1 + 9 ** int(self.suit.value))


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
        self.bunker: List[Union[Tuple[SpecialCard, int],
                                Optional[Card]]] = [None] * 3
        self.goal: Dict[NumberCard.Suit, int] = {
            NumberCard.Suit.Red: 0,
            NumberCard.Suit.Green: 0,
            NumberCard.Suit.Black: 0,
        }
        self.flower_gone: bool = False

    def state_identifier(self) -> int:
        """Returns a unique identifier to represent the board state"""
        result: int = 0
        for card in self.bunker:
            result <<= 2
            if isinstance(card, tuple):
                result |= 0
                result <<= 2
                result |= card[0].identifier()  # pylint: disable=E1136
            elif card is None:
                result |= 1
            else:
                result |= 2
                result <<= 5
                result |= card.identifier()


        result <<= 1
        if self.flower_gone:
            result |= 1

        for _, goal_count in self.goal.items():
            result <<= 4
            result |= goal_count

        # Max stack size is 13 (4 random cards from the start, plus a stack from 9 to 1]
        # So 4 bits are sufficient
        for stack in self.field:
            assert len(stack) == len(stack) & 0b1111
            result <<= 4
            result |= len(stack)

        for field_card in itertools.chain.from_iterable(self.field):
            result <<= 5
            result |= field_card.identifier()

        return 0

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

        if self.flower_gone:
            special_cards[SpecialCard.Hua] += 1

        for card in itertools.chain(
            self.bunker, itertools.chain.from_iterable(
                stack for stack in self.field if stack), ):
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
