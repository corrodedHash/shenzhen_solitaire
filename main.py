"""Main module"""
from typing import List, Union, Tuple, Iterator
import enum
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


@dataclass
class MoveAction:
    """Moving a card from one stack to another"""
    card: Card
    source_position: Position
    source_id: int
    destination_position: Position
    destination_id: int


@dataclass
class DragonKillAction:
    """Removing four dragons from the top of the stacks to a bunker"""
    dragon: SpecialCard
    source_stacks: List[Tuple[Position, int]]
    destination_bunker_id: int


@dataclass
class HuaKillAction:
    """Remove the flower card"""
    source_field_id: int


Action = Union[MoveAction, DragonKillAction, HuaKillAction]


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

    def possible_huakill_action(self) -> Iterator[HuaKillAction]:
        """Check if the flowercard can be eliminated"""
        for index, stack in enumerate(self.field):
            if stack[-1] == SpecialCard.Hua:
                yield HuaKillAction(source_field_id=index)

    def possible_dragonkill_actions(self) -> Iterator[DragonKillAction]:
        """Enumerate all possible dragon kills"""
        possible_dragons = [SpecialCard.Zhong, SpecialCard.Fa, SpecialCard.Bai]
        if not any(x == BunkerStatus.Empty for x in self.bunker):
            new_possible_dragons = []
            for dragon in possible_dragons:
                if any(x == dragon for x in self.bunker):
                    new_possible_dragons.append(dragon)
            possible_dragons = new_possible_dragons

        for dragon in possible_dragons:
            bunker_dragons = [i for i, d in enumerate(
                self.bunker) if d == dragon]
            field_dragons = [i for i, f in enumerate(
                self.field) if f if f[-1] == dragon]
            if len(bunker_dragons) + len(field_dragons) != 4:
                continue
            destination_bunker_id = 0
            if bunker_dragons:
                destination_bunker_id = bunker_dragons[0]
            else:
                destination_bunker_id = [
                    i for i, x in enumerate(self.bunker) if x == BunkerStatus.Empty][0]

            source_stacks = [(Position.Bunker, i) for i in bunker_dragons]
            source_stacks.extend([(Position.Field, i) for i in field_dragons])

            yield DragonKillAction(dragon=dragon, source_stacks=source_stacks,
                                   destination_bunker_id=destination_bunker_id)

    def possible_bunkerize_actions(self) -> Iterator[MoveAction]:
        """Enumerates all possible card moves from the field to the bunker"""
        open_bunker_list = [i for i, x in enumerate(
            self.bunker) if x == BunkerStatus.Empty]

        if not open_bunker_list:
            return

        open_bunker = open_bunker_list[0]
        for index, stack in enumerate(self.field):
            if not stack:
                continue
            yield MoveAction(card=stack[-1],
                             source_position=Position.Field,
                             source_id=index,
                             destination_position=Position.Bunker,
                             destination_id=open_bunker)

    def possible_debunkerize_actions(self) -> Iterator[MoveAction]:
        """Enumerates all possible card moves from the bunker to the field"""
        bunker_number_cards = [(i, x) for i, x in enumerate(
            self.bunker) if isinstance(x, NumberCard)]
        for index, card in bunker_number_cards:
            for other_index, other_stack in enumerate(self.field):
                if not other_stack:
                    continue
                if not isinstance(other_stack[-1], NumberCard):
                    continue
                if other_stack[-1].suit == card.suit:
                    continue
                if other_stack[-1].number != card.number + 1:
                    continue
                yield MoveAction(card=card,
                                 source_position=Position.Bunker,
                                 source_id=index,
                                 destination_position=Position.Field,
                                 destination_id=other_index)

    def possible_goal_move_actions(self) -> Iterator[MoveAction]:
        """Enumerates all possible moves from anywhere to the goal"""
        #TODO



    def possible_field_move_actions(self) -> Iterator[MoveAction]:
        """Enumerate all possible move actions from one field stack to another field stack"""
        for index, stack in enumerate(self.field):
            if not stack:
                continue
            if not isinstance(stack[-1], NumberCard):
                continue
            for other_index, other_stack in enumerate(self.field):
                if not other_stack:
                    continue
                if not isinstance(other_stack[-1], NumberCard):
                    continue
                if other_stack[-1].suit == stack[-1].suit:
                    continue
                if other_stack[-1].number != stack[-1].number + 1:
                    continue
                yield MoveAction(card=stack[-1],
                                 source_position=Position.Field,
                                 source_id=index,
                                 destination_position=Position.Field,
                                 destination_id=other_index)

    def possible_actions(self) -> Iterator[Action]:
        """Enumerate all possible actions on the current board"""
        yield from self.possible_huakill_action()
        yield from self.possible_dragonkill_actions()
        yield from self.possible_debunkerize_actions()
        yield from self.possible_field_move_actions()
        yield from self.possible_bunkerize_actions()


class SolitaireSolver:
    """Solver for Shenzhen Solitaire"""
    board: Board
    stack: List[Tuple[Action, int]]
