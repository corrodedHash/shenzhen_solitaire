"""Contains function to iterate different kinds of possible actions"""
from typing import Iterator, List, Tuple
from .. import board
from . import board_actions


def possible_huakill_action(
        search_board: board.Board
) -> Iterator[board_actions.HuaKillAction]:
    """Check if the flowercard can be eliminated"""
    for index, stack in enumerate(search_board.field):
        if stack and stack[-1] == board.SpecialCard.Hua:
            yield board_actions.HuaKillAction(source_field_id=index)


def possible_dragonkill_actions(
        search_board: board.Board
) -> Iterator[board_actions.DragonKillAction]:
    """Enumerate all possible dragon kills"""
    possible_dragons = [
        board.SpecialCard.Zhong,
        board.SpecialCard.Fa,
        board.SpecialCard.Bai,
    ]
    if not any(x is None for x in search_board.bunker):
        new_possible_dragons = []
        for dragon in possible_dragons:
            if any(x == dragon for x in search_board.bunker):
                new_possible_dragons.append(dragon)
        possible_dragons = new_possible_dragons

    for dragon in possible_dragons:
        bunker_dragons = [i for i, d in
                          enumerate(search_board.bunker) if d == dragon]
        field_dragons = [
            i for i, f in enumerate(search_board.field) if f if f[-1] == dragon
        ]
        if len(bunker_dragons) + len(field_dragons) != 4:
            continue
        destination_bunker_id = 0
        if bunker_dragons:
            destination_bunker_id = bunker_dragons[0]
        else:
            destination_bunker_id = [
                i for i, x in enumerate(search_board.bunker) if x is None
            ][0]

        source_stacks = [(board.Position.Bunker, i) for i in bunker_dragons]
        source_stacks.extend([(board.Position.Field, i)
                              for i in field_dragons])

        yield board_actions.DragonKillAction(
            dragon=dragon,
            source_stacks=source_stacks,
            destination_bunker_id=destination_bunker_id,
        )


def possible_bunkerize_actions(
        search_board: board.Board
) -> Iterator[board_actions.BunkerizeAction]:
    """Enumerates all possible card moves from the field to the bunker"""
    open_bunker_list = [
        i for i, x in enumerate(
            search_board.bunker) if x is None]

    if not open_bunker_list:
        return

    open_bunker = open_bunker_list[0]
    for index, stack in enumerate(search_board.field):
        if not stack:
            continue
        yield board_actions.BunkerizeAction(
            card=stack[-1],
            field_id=index,
            bunker_id=open_bunker,
            to_bunker=True
        )


def possible_debunkerize_actions(
        search_board: board.Board
) -> Iterator[board_actions.BunkerizeAction]:
    """Enumerates all possible card moves from the bunker to the field"""
    bunker_number_cards = [
        (i, x)
        for i, x in enumerate(search_board.bunker)
        if isinstance(x, board.NumberCard)
    ]
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
            yield board_actions.BunkerizeAction(
                card=card,
                bunker_id=index,
                field_id=other_index,
                to_bunker=False
            )


def possible_goal_move_actions(
        search_board: board.Board
) -> Iterator[board_actions.GoalAction]:
    """Enumerates all possible moves from anywhere to the goal"""
    field_cards = [
        (board.Position.Field, index, stack[-1])
        for index, stack in enumerate(search_board.field)
        if stack
        if isinstance(stack[-1], board.NumberCard)
    ]
    bunker_cards = [
        (board.Position.Bunker, index, stack)
        for index, stack in enumerate(search_board.bunker)
        if isinstance(stack, board.NumberCard)
    ]
    top_cards = field_cards + bunker_cards

    for suit, number in search_board.goal.items():
        for source, index, stack in top_cards:
            if not (stack.suit == suit and stack.number == number + 1):
                continue
            yield board_actions.GoalAction(
                card=stack, source_id=index, source_position=source
            )
            break


def _can_stack(bottom: board.Card, top: board.Card) -> bool:
    if not isinstance(bottom, board.NumberCard):
        return False
    if not isinstance(top, board.NumberCard):
        return False
    if bottom.suit == top.suit:
        return False
    if bottom.number != top.number + 1:
        return False
    return True


def _get_cardstacks(search_board: board.Board) -> List[List[board.Card]]:
    """Returns all cards on one stack that can be moved at once"""
    result: List[List[board.Card]] = []
    for stack in search_board.field:
        result.append([])
        if not stack:
            continue
        result[-1].append(stack[-1])
        for card in stack[-2::-1]:
            if not _can_stack(card, result[-1][0]):
                break
            if not isinstance(card, board.NumberCard):
                break
            result[-1].insert(0, card)
    return result


def possible_field_move_actions(
        search_board: board.Board
) -> Iterator[board_actions.MoveAction]:
    """Enumerate all possible move actions
    from one field stack to another field stack"""
    first_empty_field_id = -1
    cardstacks = [(index, stack)
                  for index, stack in enumerate(_get_cardstacks(search_board))]
    cardstacks = [x for x in cardstacks if x[1]]
    cardstacks = sorted(cardstacks, key=lambda x: len(x[1]))
    substacks: List[Tuple[int, List[board.Card]]] = []

    for index, stack in cardstacks:
        substacks.extend((index, substack)
                         for substack in (stack[i:]
                                          for i in range(len(stack))))

    for index, substack in substacks:
        for other_index, other_stack in enumerate(search_board.field):
            if index == other_index:
                continue
            if other_stack:
                if not _can_stack(other_stack[-1], substack[0]):
                    continue
            elif len(substack) == len(search_board.field[index]):
                continue
            elif first_empty_field_id == -1:
                first_empty_field_id = other_index
            elif other_index != first_empty_field_id:
                continue
            yield board_actions.MoveAction(
                cards=substack, source_id=index, destination_id=other_index
            )


def possible_actions(
        search_board: board.Board) -> Iterator[board_actions.Action]:
    """Enumerate all possible actions on the current search_board"""
    yield from possible_huakill_action(search_board)
    yield from possible_dragonkill_actions(search_board)
    yield from possible_goal_move_actions(search_board)
    yield from possible_debunkerize_actions(search_board)
    yield from possible_field_move_actions(search_board)
    yield from possible_bunkerize_actions(search_board)
