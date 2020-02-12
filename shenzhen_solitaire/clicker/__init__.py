import time
from typing import List, Tuple

import pyautogui
import shenzhen_solitaire.board as board
import shenzhen_solitaire.card_detection.adjustment as adjustment
import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.solver.board_actions as board_actions
import warnings


def drag(
    src: Tuple[int, int], dst: Tuple[int, int], offset: Tuple[int, int] = (0, 0)
) -> None:

    pyautogui.moveTo(x=src[0] + offset[0], y=src[1] + offset[1])
    pyautogui.dragTo(
        x=dst[0] + offset[0],
        y=dst[1] + offset[1],
        duration=0.4,
        tween=lambda x: 0 if x < 0.5 else 1,
    )


def dragSquare(
    src: Tuple[int, int, int, int],
    dst: Tuple[int, int, int, int],
    offset: Tuple[int, int] = (0, 0),
) -> None:
    drag(
        (src[0] + (src[2] - src[0]) // 2, src[1] + (src[3] - src[1]) // 2),
        (dst[0] + (dst[2] - dst[0]) // 2, dst[1] + (dst[3] - dst[1]) // 2),
        offset,
    )


def click(point: Tuple[int, int], offset: Tuple[int, int] = (0, 0)) -> None:
    pyautogui.moveTo(x=point[0] + offset[0], y=point[1] + offset[1])
    pyautogui.mouseDown()
    time.sleep(0.2)
    pyautogui.mouseUp()


def clickSquare(
    field: Tuple[int, int, int, int], offset: Tuple[int, int] = (0, 0)
) -> None:
    click(
        (field[0] + (field[2] - field[0]) // 2, field[1] + (field[3] - field[1]) // 2),
        offset,
    )


def handle_action(
    action: board_actions.Action,
    offset: Tuple[int, int],
    conf: configuration.Configuration,
) -> None:
    if isinstance(action, board_actions.MoveAction):
        src = adjustment.get_square(
            conf.field_adjustment,
            index_x=action.source_id,
            index_y=action.source_row_index,
        )
        dst = adjustment.get_square(
            conf.field_adjustment,
            index_x=action.destination_id,
            index_y=action.destination_row_index,
        )
        dragSquare(src, dst, offset)
        return
    if isinstance(action, board_actions.HuaKillAction):
        warnings.warn("Hua kill should be handled before handle_action")
        return
    if isinstance(action, board_actions.BunkerizeAction):
        field = adjustment.get_square(
            conf.field_adjustment,
            index_x=action.field_id,
            index_y=action.field_row_index,
        )
        bunker = adjustment.get_square(
            conf.bunker_adjustment, index_x=action.bunker_id, index_y=0,
        )
        if action.to_bunker:
            dragSquare(field, bunker, offset)
        else:
            dragSquare(bunker, field, offset)
        return
    if isinstance(action, board_actions.DragonKillAction):
        dragon_sequence = [
            board.SpecialCard.Zhong,
            board.SpecialCard.Fa,
            board.SpecialCard.Bai,
        ]
        field = adjustment.get_square(
            conf.special_button_adjustment,
            index_x=0,
            index_y=dragon_sequence.index(action.dragon),
        )
        clickSquare(
            field, offset,
        )
        time.sleep(1)
        return
    if isinstance(action, board_actions.GoalAction):
        dst = adjustment.get_square(
            conf.goal_adjustment, index_x=action.goal_id, index_y=0,
        )
        if action.source_position == board.Position.Field:
            assert action.source_row_index is not None
            src = adjustment.get_square(
                conf.field_adjustment,
                index_x=action.source_id,
                index_y=action.source_row_index,
            )
        else:
            assert action.source_position == board.Position.Bunker
            src = adjustment.get_square(
                conf.bunker_adjustment, index_x=action.source_id, index_y=0,
            )
        dragSquare(src, dst, offset)
        return
    raise AssertionError("You forgot an Action type")


def handle_actions(
    actions: List[board_actions.Action],
    offset: Tuple[int, int],
    conf: configuration.Configuration,
) -> None:
    automatic_count = 0
    for action in actions:
        print(action)
        if isinstance(action, board_actions.HuaKillAction):
            automatic_count += 1
        else:
            time.sleep(0.5 * automatic_count)
            automatic_count = 0
            handle_action(action, offset, conf)
    time.sleep(0.5 * automatic_count)