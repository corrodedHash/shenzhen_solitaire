"""Contains configuration class"""
import dataclasses
import enum
import io
import json
import tempfile
import zipfile
from dataclasses import dataclass
from typing import Dict, List, Tuple, Union

import cv2
import numpy as np

from .. import board
from . import adjustment, card_finder

ADJUSTMENT_FILE_NAME = "adjustment.json"

FIELD_ADJUSTMENT_KEY = "field"
BORDER_ADJUSTMENT_KEY = "border"
GOAL_ADJUSTMENT_KEY = "goal"
BUNKER_ADJUSTMENT_KEY = "bunker"
HUA_ADJUSTMENT_KEY = "hua"
SPECIAL_BUTTON_ADJUSTMENT_KEY = "special_button"

TEMPLATES_DIRECTORY = "templates"
CARD_BORDER_DIRECTORY = "borders"
EMPTY_CARD_DIRECTORY = "empty_cards"
GREEN_CARD_DIRECTORY = "green_cards"
SPECIAL_BUTTON_DIRECTORY = "special_buttons"
CARD_BACK_DIRECTORY = "card_backs"

PICTURE_EXTENSION = "png"


class ButtonState(enum.Enum):
    normal = enum.auto()
    greyed = enum.auto()
    shiny = enum.auto()


@dataclass
class Configuration:
    """Configuration for solitaire cv"""

    field_adjustment: adjustment.Adjustment = dataclasses.field(
        default_factory=adjustment.Adjustment
    )
    border_adjustment: adjustment.Adjustment = dataclasses.field(
        default_factory=adjustment.Adjustment
    )
    goal_adjustment: adjustment.Adjustment = dataclasses.field(
        default_factory=adjustment.Adjustment
    )
    bunker_adjustment: adjustment.Adjustment = dataclasses.field(
        default_factory=adjustment.Adjustment
    )
    hua_adjustment: adjustment.Adjustment = dataclasses.field(
        default_factory=adjustment.Adjustment
    )
    special_button_adjustment: adjustment.Adjustment = dataclasses.field(
        default_factory=adjustment.Adjustment
    )
    catalogue: List[
        Tuple[np.ndarray, Union[board.SpecialCard, board.NumberCard]]
    ] = dataclasses.field(default_factory=list)
    card_border: List[np.ndarray] = dataclasses.field(default_factory=list)
    empty_card: List[np.ndarray] = dataclasses.field(default_factory=list)
    green_card: List[np.ndarray] = dataclasses.field(default_factory=list)
    special_buttons: List[
        Tuple[ButtonState, board.SpecialCard, np.ndarray]
    ] = dataclasses.field(default_factory=list)
    card_back: List[np.ndarray] = dataclasses.field(default_factory=list)
    meta: Dict[str, str] = dataclasses.field(default_factory=dict)


def _save_catalogue(
    zip_file: zipfile.ZipFile, catalogue: List[Tuple[np.ndarray, board.Card]]
) -> None:
    for counter, (square, card) in enumerate(catalogue, start=1):
        fd, myfile = tempfile.mkstemp(suffix=f".{PICTURE_EXTENSION}")

        cv2.imwrite(myfile, square)
        file_name = ""
        if isinstance(card, board.SpecialCard):
            file_name = f"s{card.value}-{card.name}-{counter}"
        elif isinstance(card, board.NumberCard):
            file_name = (
                f"n{card.suit.value}{card.number}" f"-{card.suit.name}-{counter}"
            )
        else:
            raise AssertionError()
        zip_file.write(
            myfile, arcname=f"{TEMPLATES_DIRECTORY}/{file_name}.{PICTURE_EXTENSION}"
        )


def _save_adjustments(zip_file: zipfile.ZipFile, conf: Configuration) -> None:
    adjustments = {}
    adjustments[FIELD_ADJUSTMENT_KEY] = dataclasses.asdict(conf.field_adjustment)
    adjustments[BORDER_ADJUSTMENT_KEY] = dataclasses.asdict(conf.border_adjustment)
    adjustments[GOAL_ADJUSTMENT_KEY] = dataclasses.asdict(conf.goal_adjustment)
    adjustments[BUNKER_ADJUSTMENT_KEY] = dataclasses.asdict(conf.bunker_adjustment)
    adjustments[HUA_ADJUSTMENT_KEY] = dataclasses.asdict(conf.hua_adjustment)
    adjustments[SPECIAL_BUTTON_ADJUSTMENT_KEY] = dataclasses.asdict(
        conf.special_button_adjustment
    )
    zip_file.writestr(
        ADJUSTMENT_FILE_NAME, json.dumps(adjustments),
    )


def _save_special_images(zip_file: zipfile.ZipFile, conf: Configuration) -> None:
    def _save_special_image(
        zip_file: zipfile.ZipFile, images: List[np.ndarray], directory: str
    ) -> None:
        for index, image in enumerate(images):
            fd, myfile = tempfile.mkstemp(suffix=f".{PICTURE_EXTENSION}")
            cv2.imwrite(myfile, image)
            file_name = ""
            zip_file.write(
                myfile, arcname=f"{directory}/{index:03}.{PICTURE_EXTENSION}"
            )

    _save_special_image(zip_file, conf.card_border, CARD_BORDER_DIRECTORY)
    _save_special_image(zip_file, conf.empty_card, EMPTY_CARD_DIRECTORY)
    _save_special_image(zip_file, conf.green_card, GREEN_CARD_DIRECTORY)
    _save_special_image(zip_file, conf.card_back, CARD_BACK_DIRECTORY)


def _generate_special_button_filename(
    state: ButtonState, special_card: board.SpecialCard
) -> str:
    state_char_map = {
        ButtonState.normal: "n",
        ButtonState.greyed: "g",
        ButtonState.shiny: "s",
    }
    special_card_char_map = {
        board.SpecialCard.Fa: "f",
        board.SpecialCard.Zhong: "z",
        board.SpecialCard.Bai: "b",
    }
    return f"{state_char_map[state]}{special_card_char_map[special_card]}"


def _save_special_button_images(
    zip_file: zipfile.ZipFile,
    special_button_images: List[Tuple[ButtonState, board.SpecialCard, np.ndarray]],
):
    for index, (state, card, image) in enumerate(special_button_images):
        fd, myfile = tempfile.mkstemp(suffix=f".{PICTURE_EXTENSION}")
        cv2.imwrite(myfile, image)
        file_name = ""
        zip_file.write(
            myfile,
            arcname=f"{SPECIAL_BUTTON_DIRECTORY}/"
            f"{_generate_special_button_filename(state,card)}"
            f"{index:03}.{PICTURE_EXTENSION}",
        )


def save(conf: Configuration, filename: str) -> None:
    """Save configuration to zip archive"""
    zip_stream = io.BytesIO()

    with zipfile.ZipFile(zip_stream, "w") as zip_file:
        _save_adjustments(zip_file, conf)
        _save_catalogue(zip_file, conf.catalogue)
        _save_special_images(zip_file, conf)
        _save_special_button_images(zip_file, conf.special_buttons)
    with open(filename, "wb") as zip_archive:
        zip_archive.write(zip_stream.getvalue())


def _parse_file_name(card_filename: str) -> board.Card:
    if card_filename[0] == "s":
        return board.SpecialCard(int(card_filename[1]))
    if card_filename[0] == "n":
        return board.NumberCard(
            suit=board.NumberCard.Suit(int(card_filename[1])),
            number=int(card_filename[2]),
        )
    raise AssertionError("Template files need to start with either 's' or 'n'")


def _load_dir_with_name(
    zip_file: zipfile.ZipFile, dirname: str
) -> List[Tuple[str, np.ndarray]]:
    mydir = tempfile.mkdtemp()
    image_filenames = [
        image_filename
        for image_filename in (
            x
            for x in zip_file.namelist()
            if x.startswith(dirname + "/") and x != dirname + "/"
        )
    ]
    images = [
        (
            image_filename[len(dirname + "/") :],
            cv2.imread(zip_file.extract(image_filename, path=mydir)),
        )
        for image_filename in image_filenames
    ]
    assert all(x[1] is not None for x in images)
    return images


def _load_catalogue(zip_file: zipfile.ZipFile,) -> List[Tuple[np.ndarray, board.Card]]:

    catalogue = [
        (image, _parse_file_name(filename))
        for filename, image in _load_dir_with_name(zip_file, TEMPLATES_DIRECTORY)
    ]

    return catalogue


def _parse_special_button_filename(
    filename: str,
) -> Tuple[ButtonState, board.SpecialCard]:
    assert len(filename) >= 2

    state_char_map = {
        "n": ButtonState.normal,
        "g": ButtonState.greyed,
        "s": ButtonState.shiny,
    }
    special_card_char_map = {
        "f": board.SpecialCard.Fa,
        "z": board.SpecialCard.Zhong,
        "b": board.SpecialCard.Bai,
    }
    assert filename[0] in state_char_map
    assert filename[1] in special_card_char_map
    return (state_char_map[filename[0]], special_card_char_map[filename[1]])


def _load_special_buttions(
    zip_file: zipfile.ZipFile,
) -> List[Tuple[ButtonState, board.SpecialCard, np.ndarray]]:
    result = [
        (*_parse_special_button_filename(filename), image)
        for filename, image in _load_dir_with_name(zip_file, SPECIAL_BUTTON_DIRECTORY)
    ]
    return result


def _load_dir(zip_file: zipfile.ZipFile, dirname: str) -> List[np.ndarray]:
    return [image for filename, image in _load_dir_with_name(zip_file, dirname)]


def load(filename: str) -> Configuration:
    """Load configuration from zip archive"""

    with zipfile.ZipFile(filename, "r") as zip_file:
        adjustment_dict = json.loads(zip_file.read(ADJUSTMENT_FILE_NAME))

        result = Configuration(
            field_adjustment=adjustment.Adjustment(
                **adjustment_dict.get(FIELD_ADJUSTMENT_KEY, {})
            ),
            border_adjustment=adjustment.Adjustment(
                **adjustment_dict.get(BORDER_ADJUSTMENT_KEY, {})
            ),
            goal_adjustment=adjustment.Adjustment(
                **adjustment_dict.get(GOAL_ADJUSTMENT_KEY, {})
            ),
            bunker_adjustment=adjustment.Adjustment(
                **adjustment_dict.get(BUNKER_ADJUSTMENT_KEY, {})
            ),
            hua_adjustment=adjustment.Adjustment(
                **adjustment_dict.get(HUA_ADJUSTMENT_KEY, {})
            ),
            special_button_adjustment=adjustment.Adjustment(
                **adjustment_dict.get(SPECIAL_BUTTON_ADJUSTMENT_KEY, {})
            ),
            catalogue=_load_catalogue(zip_file),
            card_border=_load_dir(zip_file, CARD_BORDER_DIRECTORY),
            empty_card=_load_dir(zip_file, EMPTY_CARD_DIRECTORY),
            green_card=_load_dir(zip_file, GREEN_CARD_DIRECTORY),
            card_back=_load_dir(zip_file, CARD_BACK_DIRECTORY),
            special_buttons=_load_special_buttions(zip_file),
            meta={},
        )
        return result


def generate(image: np.ndarray) -> Configuration:
    """Generate a configuration with user input"""
    adj = adjustment.adjust_field(image)
    squares = card_finder.get_field_squares(image, adj, 5, 8)
    catalogue = card_finder.catalogue_cards(squares)
    return Configuration(field_adjustment=adj, catalogue=catalogue, meta={})
