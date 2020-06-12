"""Contains board class"""
import enum
import itertools
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, Union
import json

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

    def __repr__(self) -> str:
        return f"NumberCard({self.suit.name} {self.number})"


Card = Union[NumberCard, SpecialCard]


class Position(enum.Enum):
    """Possible Board positions"""

    Field = enum.auto()
    Bunker = enum.auto()
    Goal = enum.auto()

def _field_card_to_str(card: Card):
    if card == SpecialCard.Hua:
        return "Hua"
    if isinstance(card, SpecialCard):
        return {"Special": card.name}
    elif isinstance(card, NumberCard):
        return {"Number": {"value": card.number, "suit": card.suit.name}}


def _bunker_card_to_str(card: Union[Tuple[SpecialCard, int], Optional[Card]]):
    if card is None:
        return "Empty"
    if isinstance(card, tuple):
        return {"Blocked": card[0].name}
    return {"Stashed": _field_card_to_str(card)}


def _goal_card_to_str(card: Optional[NumberCard]):
    if card is None:
        return None
    return {"value": card.number, "suit": card.suit.name}

class Board:
    """Solitaire board"""

    # Starting max row is 5, if the last one is a `1`, we can put a `2` - `9` on top of it, resulting in 13 cards
    MAX_ROW_SIZE = 13
    MAX_COLUMN_SIZE = 8

    def __init__(self) -> None:
        self.field: List[List[Card]] = [[]] * Board.MAX_COLUMN_SIZE
        self.bunker: List[Union[Tuple[SpecialCard, int], Optional[Card]]] = [None] * 3
        self.goal: List[Optional[NumberCard]] = [None] * 3
        self.flower_gone: bool = False

    def getGoal(self, suit: NumberCard.Suit) -> int:
        for card in self.goal:
            if card is not None and card.suit == suit:
                return card.number
        else:
            return 0

    def getGoalId(self, suit: NumberCard.Suit) -> int:
        for index, card in enumerate(self.goal):
            if card is not None and card.suit == suit:
                return index
        else:
            return self.goal.index(None)

    def setGoal(self, suit: NumberCard.Suit, value: int) -> None:
        assert len(self.goal) == 3
        assert 0 <= value
        assert value <= 9
        if value == 0:
            self.goal[self.getGoalId(suit)] = None
        else:
            self.goal[self.getGoalId(suit)] = NumberCard(suit, number=value)

    def incGoal(self, suit: NumberCard.Suit) -> None:
        self.setGoal(suit, self.getGoal(suit) + 1)

    def solved(self) -> bool:
        """Returns true if the board is solved"""
        if any(x.number != 9 for x in self.goal if x is not None):
            return False
        if any(not isinstance(x, tuple) for x in self.bunker):
            return False
        if not self.flower_gone:
            return False
        assert all(not x for x in self.field)
        return True

    @property
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

        assert len(self.goal) == 3
        suit_sequence = list(NumberCard.Suit)
        for card in self.goal:
            result <<= 5
            if card is None:
                result |= len(suit_sequence) * 10
            else:
                result |= suit_sequence.index(card.suit) * 10 + card.number

        # Max stack size is 13
        # (4 random cards from the start, plus a stack from 9 to 1)
        # So 4 bits are sufficient
        for stack in self.field:
            assert len(stack) == len(stack) & 0b1111
            result <<= 4
            result |= len(stack)

        for field_card in itertools.chain.from_iterable(self.field):
            result <<= 5
            result |= field_card.identifier()

        return result

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
            self.bunker,
            itertools.chain.from_iterable(stack for stack in self.field if stack),
        ):
            if isinstance(card, tuple):
                special_cards[card[0]] += 4
            elif isinstance(card, SpecialCard):
                special_cards[card] += 1
            elif isinstance(card, NumberCard):
                if card.number in number_cards[card.suit]:
                    return False
                number_cards[card.suit].add(card.number)

        for suit, numbers in number_cards.items():
            if set(range(self.getGoal(suit) + 1, 10)) != numbers:
                return False

        for cardtype, count in special_cards.items():
            if cardtype == SpecialCard.Hua:
                if count != 1:
                    return False
            else:
                if count != 4:
                    return False
        return True

    def to_json(self) -> str:
        mystruct = {
            "field": [[_field_card_to_str(card) for card in row] for row in self.field],
            "hua_set": self.flower_gone,
            "bunker": [_bunker_card_to_str(card) for card in self.bunker],
            "goal": [_goal_card_to_str(card) for card in self.goal],
        }
        return json.dumps(mystruct)
