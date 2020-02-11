import shenzhen_solitaire.solver.board_actions as board_actions
import shenzhen_solitaire.card_detection.configuration as configuration
import shenzhen_solitaire.card_detection.adjustment as adjustment
import shenzhen_solitaire.board as board
from typing import List, Tuple
import pyautogui
import time


def drag(
    src: Tuple[int, int], dst: Tuple[int, int], offset: Tuple[int, int] = (0, 0)
) -> None:

    pyautogui.moveTo(x=src[0] + offset[0], y=src[1] + offset[1])
    pyautogui.dragTo(x=dst[0] + offset[0], y=dst[1] + offset[1],
                     duration=0.4, tween=lambda x: 0 if x < 0.5 else 1)


def click(point: Tuple[int, int], offset: Tuple[int, int] = (0, 0)) -> None:
    pyautogui.moveTo(x=point[0] + offset[0], y=point[1] + offset[1])
    pyautogui.mouseDown()
    time.sleep(0.2)
    pyautogui.mouseUp()

def handle_action(
    action: board_actions.Action,
    offset: Tuple[int, int],
    conf: configuration.Configuration,
) -> None:
    if isinstance(action, board_actions.MoveAction):
        src_x, src_y, _, _ = adjustment.get_square(
            conf.field_adjustment,
            index_x=action.source_id,
            index_y=action.source_row_index,
        )
        dst_x, dst_y, _, _ = adjustment.get_square(
            conf.field_adjustment,
            index_x=action.destination_id,
            index_y=action.destination_row_index,
        )
        drag((src_x, src_y), (dst_x, dst_y), offset)
        return
    if isinstance(action, board_actions.HuaKillAction):
        time.sleep(1)
        return
    if isinstance(action, board_actions.BunkerizeAction):
        field_x, field_y, _, _ = adjustment.get_square(
            conf.field_adjustment,
            index_x=action.field_id,
            index_y=action.field_row_index,
        )
        bunker_x, bunker_y, _, _ = adjustment.get_square(
            conf.bunker_adjustment, index_x=action.bunker_id, index_y=0,
        )
        if action.to_bunker:
            drag((field_x, field_y), (bunker_x, bunker_y), offset)
        else:
            drag((bunker_x, bunker_y), (field_x, field_y), offset)
        return
    if isinstance(action, board_actions.DragonKillAction):
        dragon_sequence = [
            board.SpecialCard.Zhong,
            board.SpecialCard.Fa,
            board.SpecialCard.Bai,
        ]
        field_x, field_y, size_x, size_y = adjustment.get_square(
            conf.special_button_adjustment,
            index_x=0,
            index_y=dragon_sequence.index(action.dragon),
        )
        click((field_x + (size_x - field_x) // 2, field_y + (size_y - field_y) // 2), offset)
        time.sleep(0.5)
        return
    if isinstance(action, board_actions.GoalAction):
        if action.obvious:
            time.sleep(1)
            return
        dst_x, dst_y, _, _ = adjustment.get_square(
            conf.goal_adjustment, index_x=action.goal_id, index_y=0,
        )
        if action.source_position == board.Position.Field:
            assert action.source_row_index is not None
            src_x, src_y, _, _ = adjustment.get_square(
                conf.field_adjustment,
                index_x=action.source_id,
                index_y=action.source_row_index,
            )
        else:
            assert action.source_position == board.Position.Bunker
            src_x, src_y, _, _ = adjustment.get_square(
                conf.bunker_adjustment, index_x=action.source_id, index_y=0,
            )
        drag((src_x, src_y), (dst_x, dst_y), offset)
        return
    raise AssertionError("You forgot an Action type")


def handle_actions(
    actions: List[board_actions.Action],
    offset: Tuple[int, int],
    conf: configuration.Configuration,
) -> None:
    for action in actions:
        handle_action(action, offset, conf)
