import time
from typing import List, Tuple, Dict, Any

import pyautogui
import shenzhen_solitaire.board as board
import shenzhen_solitaire.card_detection.adjustment as adjustment
import shenzhen_solitaire.card_detection.configuration as configuration
import warnings

from dataclasses import dataclass


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


@dataclass
class DragAction:
    source: Tuple[int, int]
    destination: Tuple[int, int]


@dataclass
class ClickAction:
    destination: Tuple[int, int]


class WaitAction:
    pass


def _parse_field(
    field: Dict[str, Any], conf: configuration.Configuration
) -> Tuple[int, int]:
    return (
        int(field["column"]) * conf.field_adjustment.dx + conf.field_adjustment.x,
        int(field["row"]) * conf.field_adjustment.dy + conf.field_adjustment.y,
    )


def parse_action(action: Dict[str, Any], conf: configuration.Configuration):
    assert len(action) == 1
    action_name, info = next(iter(action.items()))
    action_name = action_name.lower()
    if action_name == "bunkerize":
        field = _parse_field(info["field_position"], conf)
        bunker = (
            int(info["bunker_slot_index"]) * conf.bunker_adjustment.dx
            + conf.bunker_adjustment.x,
            conf.bunker_adjustment.y,
        )
        if str(info["to_bunker"]).lower() == "true":
            return DragAction(source=field, destination=bunker)
        else:
            return DragAction(source=bunker, destination=field)
    elif action_name == "move":
        return DragAction(
            source=_parse_field(info["source"], conf),
            destination=_parse_field(info["source"], conf),
        )
    elif action_name == "dragonkill":
        return ClickAction()
    elif action_name == "goal":
        goal = (
            int(info["goal_slot_index"]) * conf.goal_adjustment.dx
            + conf.goal_adjustment.x,
            conf.goal_adjustment.y,
        )
        if "Field" in info["source"]:
            source = _parse_field(info["source"]["Field"], conf)
        else:
            source = (
                int(info["source"]["Bunker"]["slot_index"]) * conf.bunker_adjustment.dx
                + conf.bunker_adjustment.x,
                conf.bunker_adjustment.y,
            )
        return DragAction(source=source, destination=goal)
    elif action_name == "huakill":
        return WaitAction()


def handle_actions(
    actions: List[Dict[str, Dict[str, Any]]],
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
