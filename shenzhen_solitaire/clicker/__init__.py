import time
from typing import List, Tuple, Dict, Any, Union

import pyautogui
import shenzhen_solitaire.board as board
import shenzhen_solitaire.card_detection.adjustment as adjustment
import shenzhen_solitaire.card_detection.configuration as configuration
import warnings

from dataclasses import dataclass
from shenzhen_solitaire.board import SpecialCard

DRAG_DURATION = 0.4
CLICK_DURATION = 0.5


def drag(
    src: Tuple[int, int], dst: Tuple[int, int], offset: Tuple[int, int] = (0, 0)
) -> None:

    pyautogui.moveTo(x=src[0] + offset[0], y=src[1] + offset[1])
    pyautogui.dragTo(
        x=dst[0] + offset[0],
        y=dst[1] + offset[1],
        duration=DRAG_DURATION,
        tween=lambda x: 0 if x < 0.5 else 1,
    )


def click(point: Tuple[int, int], offset: Tuple[int, int] = (0, 0)) -> None:
    pyautogui.moveTo(x=point[0] + offset[0], y=point[1] + offset[1])
    pyautogui.mouseDown()
    time.sleep(CLICK_DURATION)
    pyautogui.mouseUp()


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
        int(field["column"]) * conf.field_adjustment.dx
        + conf.field_adjustment.x
        + conf.field_adjustment.w // 2,
        int(field["row"]) * conf.field_adjustment.dy
        + conf.field_adjustment.y
        + conf.field_adjustment.h // 2,
    )


def parse_action(
    action: Dict[str, Any],
    conf: configuration.Configuration,
    goal_values: Dict[str, int],
) -> Union[DragAction, ClickAction, WaitAction]:
    assert len(action) == 1
    action_name, info = next(iter(action.items()))
    action_name = action_name.lower()
    if action_name == "bunkerize":
        field = _parse_field(info["field_position"], conf)
        bunker = (
            int(info["bunker_slot_index"]) * conf.bunker_adjustment.dx
            + conf.bunker_adjustment.x
            + conf.bunker_adjustment.w // 2,
            conf.bunker_adjustment.y + conf.bunker_adjustment.h // 2,
        )
        if str(info["to_bunker"]).lower() == "true":
            return DragAction(source=field, destination=bunker)
        else:
            return DragAction(source=bunker, destination=field)
    elif action_name == "move":
        return DragAction(
            source=_parse_field(info["source"], conf),
            destination=_parse_field(info["destination"], conf),
        )
    elif action_name == "dragonkill":
        dragon_sequence = [SpecialCard.Zhong, SpecialCard.Fa, SpecialCard.Bai]
        dragon_name_map = {
            "zhong": SpecialCard.Zhong,
            "fa": SpecialCard.Fa,
            "bai": SpecialCard.Bai,
        }
        card_type = dragon_name_map[info["card"].lower()]
        dragon_id = dragon_sequence.index(card_type)
        return ClickAction(
            destination=(
                conf.special_button_adjustment.x
                + conf.special_button_adjustment.w // 2,
                conf.special_button_adjustment.y
                + dragon_id * conf.special_button_adjustment.dy
                + conf.special_button_adjustment.h // 2,
            )
        )
    elif action_name == "goal":
        obvious = (
            goal_values[info["card"]["suit"].lower()] <= min(goal_values.values()) + 1
        )
        assert (goal_values[info["card"]["suit"].lower()] == 0) or (
            goal_values[info["card"]["suit"].lower()] + 1 == info["card"]["value"]
        )
        goal_values[info["card"]["suit"].lower()] = info["card"]["value"]
        if obvious:
            return WaitAction()
        goal = (
            int(info["goal_slot_index"]) * conf.goal_adjustment.dx
            + conf.goal_adjustment.x
            + conf.goal_adjustment.w // 2,
            conf.goal_adjustment.y + conf.goal_adjustment.h // 2,
        )
        if "Field" in info["source"]:
            source = _parse_field(info["source"]["Field"], conf)
        else:
            source = (
                int(info["source"]["Bunker"]["slot_index"]) * conf.bunker_adjustment.dx
                + conf.bunker_adjustment.x
                + conf.bunker_adjustment.w // 2,
                conf.bunker_adjustment.y + conf.bunker_adjustment.h // 2,
            )
        return DragAction(source=source, destination=goal)
    elif action_name == "huakill":
        return WaitAction()


def handle_actions(
    actions: List[Dict[str, Dict[str, Any]]],
    offset: Tuple[int, int],
    conf: configuration.Configuration,
) -> None:
    goal_values = {"red": 0, "black": 0, "green": 0}
    action_tuples = [
        (action, parse_action(action, conf, goal_values)) for action in actions
    ]
    for name, action in action_tuples:
        print(name)
        if isinstance(action, DragAction):
            drag(action.source, action.destination, offset)
        elif isinstance(action, ClickAction):
            click(action.destination, offset)
        elif isinstance(action, WaitAction):
            time.sleep(2)
