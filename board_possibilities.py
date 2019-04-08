"""Contains function to iterate different kinds of possible actions"""
from typing import Iterator
import board
import board_actions


def possible_huakill_action(search_board: board.Board) -> Iterator[board_actions.HuaKillAction]:
    """Check if the flowercard can be eliminated"""
    for index, stack in enumerate(search_board.field):
        if stack[-1] == board.SpecialCard.Hua:
            yield board_actions.HuaKillAction(source_field_id=index)


def possible_dragonkill_actions(
        search_board: board.Board) -> Iterator[board_actions.DragonKillAction]:
    """Enumerate all possible dragon kills"""
    possible_dragons = [board.SpecialCard.Zhong,
                        board.SpecialCard.Fa, board.SpecialCard.Bai]
    if not any(x is None for x in search_board.bunker):
        new_possible_dragons = []
        for dragon in possible_dragons:
            if any(x == dragon for x in search_board.bunker):
                new_possible_dragons.append(dragon)
        possible_dragons = new_possible_dragons

    for dragon in possible_dragons:
        bunker_dragons = [i for i, d in enumerate(
            search_board.bunker) if d == dragon]
        field_dragons = [i for i, f in enumerate(
            search_board.field) if f if f[-1] == dragon]
        if len(bunker_dragons) + len(field_dragons) != 4:
            continue
        destination_bunker_id = 0
        if bunker_dragons:
            destination_bunker_id = bunker_dragons[0]
        else:
            destination_bunker_id = [
                i for i, x in enumerate(search_board.bunker) if x is None][0]

        source_stacks = [(board.Position.Bunker, i) for i in bunker_dragons]
        source_stacks.extend([(board.Position.Field, i)
                              for i in field_dragons])

        yield board_actions.DragonKillAction(dragon=dragon, source_stacks=source_stacks,
                                             destination_bunker_id=destination_bunker_id)


def possible_bunkerize_actions(search_board: board.Board) -> Iterator[board_actions.StoreAction]:
    """Enumerates all possible card moves from the field to the bunker"""
    open_bunker_list = [i for i, x in enumerate(
        search_board.bunker) if x is None]

    if not open_bunker_list:
        return

    open_bunker = open_bunker_list[0]
    for index, stack in enumerate(search_board.field):
        if not stack:
            continue
        yield board_actions.StoreAction(card=stack[-1],
                                        source_id=index,
                                        destination_id=open_bunker)


def possible_debunkerize_actions(
        search_board: board.Board) -> Iterator[board_actions.RestoreAction]:
    """Enumerates all possible card moves from the bunker to the field"""
    bunker_number_cards = [(i, x) for i, x in enumerate(
        search_board.bunker) if isinstance(x, board.NumberCard)]
    for index, card in bunker_number_cards:
        for other_index, other_stack in enumerate(search_board.field):
            if not other_stack:
                continue
            if not isinstance(other_stack[-1], board.NumberCard):
                continue
            if other_stack[-1].suit == card.suit:
                continue
            if other_stack[-1].number != card.number + 1:
                continue
            yield board_actions.RestoreAction(card=card,
                                              source_id=index,
                                              destination_id=other_index)


def possible_goal_move_actions(search_board: board.Board) -> Iterator[board_actions.GoalAction]:
    """Enumerates all possible moves from anywhere to the goal"""
    field_cards = [(board.Position.Field, index, stack[-1]) for index, stack in enumerate(
        search_board.field) if stack if isinstance(stack[-1], board.NumberCard)]
    bunker_cards = [(board.Position.Bunker, index, stack)
                    for index, stack in enumerate(search_board.bunker)
                    if isinstance(stack, board.NumberCard)]
    top_cards = field_cards + bunker_cards

    for suit, number in search_board.goal.items():
        for source, index, stack in top_cards:
            if not (stack.suit == suit and stack.number == number + 1):
                continue
            yield board_actions.GoalAction(card=stack, source_id=index, source_position=source)
        break


def possible_field_move_actions(search_board: board.Board) -> Iterator[board_actions.MoveAction]:
    """Enumerate all possible move actions from one field stack to another field stack"""
    for index, stack in enumerate(search_board.field):
        if not stack:
            continue
        if not isinstance(stack[-1], board.NumberCard):
            continue
        for other_index, other_stack in enumerate(search_board.field):
            if not other_stack:
                continue
            if not isinstance(other_stack[-1], board.NumberCard):
                continue
            if other_stack[-1].suit == stack[-1].suit:
                continue
            if other_stack[-1].number != stack[-1].number + 1:
                continue
            yield board_actions.MoveAction(card=stack[-1],
                                           source_id=index,
                                           destination_id=other_index)


def possible_actions(search_board: board.Board) -> Iterator[board_actions.Action]:
    """Enumerate all possible actions on the current search_board"""
    yield from possible_huakill_action(search_board)
    yield from possible_dragonkill_actions(search_board)
    yield from possible_goal_move_actions(search_board)
    yield from possible_debunkerize_actions(search_board)
    yield from possible_field_move_actions(search_board)
    yield from possible_bunkerize_actions(search_board)
