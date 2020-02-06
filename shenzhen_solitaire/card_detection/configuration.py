"""Contains configuration class"""
import zipfile
import json
from typing import List, Tuple, Dict, Union
import io
import dataclasses
from dataclasses import dataclass
import tempfile
import cv2

import numpy as np
from . import adjustment
from . import card_finder
from .. import board

ADJUSTMENT_FILE_NAME = "adjustment.json"
FIELD_ADJUSTMENT_KEY = "field"
BORDER_ADJUSTMENT_KEY = "border"

TEMPLATES_DIRECTORY = "templates"
CARD_BORDER_DIRECTORY = "borders"
EMPTY_CARD_DIRECTORY = "empty_cards"

PICTURE_EXTENSION = "png"


@dataclass
class Configuration:
    """Configuration for solitaire cv"""

    field_adjustment: adjustment.Adjustment
    border_adjustment: adjustment.Adjustment
    catalogue: List[Tuple[np.ndarray, Union[board.SpecialCard, board.NumberCard]]]
    card_border: List[np.ndarray]
    empty_card: List[np.ndarray]
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
    
def _save_adjustments(
    zip_file: zipfile.ZipFile, conf: Configuration
) -> None:
    adjustments = {}
    adjustments[FIELD_ADJUSTMENT_KEY] = dataclasses.asdict(conf.field_adjustment)
    adjustments[BORDER_ADJUSTMENT_KEY] = dataclasses.asdict(conf.border_adjustment)

    zip_file.writestr(
        ADJUSTMENT_FILE_NAME, json.dumps(adjustment),
    )


def save(conf: Configuration, filename: str) -> None:
    """Save configuration to zip archive"""
    zip_stream = io.BytesIO()

    with zipfile.ZipFile(zip_stream, "w") as zip_file:
        _save_adjustments(zip_file, conf)
        _save_catalogue(zip_file, conf.catalogue)

    with open(filename, "wb") as zip_archive:
        zip_archive.write(zip_stream.getvalue())


def _parse_file_name(card_filename: str) -> board.Card:
    assert card_filename.startswith(TEMPLATES_DIRECTORY + "/")
    pure_name = card_filename[len(TEMPLATES_DIRECTORY + "/") :]
    if pure_name[0] == "s":
        return board.SpecialCard(int(pure_name[1]))
    if pure_name[0] == "n":
        return board.NumberCard(
            suit=board.NumberCard.Suit(int(pure_name[1])), number=int(pure_name[2]),
        )
    raise AssertionError("Template files need to start with either 's' or 'n'")


def _load_catalogue(zip_file: zipfile.ZipFile,) -> List[Tuple[np.ndarray, board.Card]]:

    catalogue: List[Tuple[np.ndarray, board.Card]] = []

    mydir = tempfile.mkdtemp()
    for template_filename in (
        x for x in zip_file.namelist() if x.startswith(TEMPLATES_DIRECTORY + "/")
    ):
        myfile = zip_file.extract(template_filename, path=mydir)
        catalogue.append((cv2.imread(myfile), _parse_file_name(template_filename),))
        assert catalogue[-1][0] is not None
    return catalogue


def _load_dir(zip_file: zipfile.ZipFile, dirname: str) -> List[np.ndarray]:
    mydir = tempfile.mkdtemp()
    image_filenames = [
        image_filename
        for image_filename in (
            x for x in zip_file.namelist() if x.startswith(dirname + "/")
        )
    ]
    images = [
        cv2.imread(zip_file.extract(image_filename, path=mydir))
        for image_filename in image_filenames
    ]
    return images


def load(filename: str) -> Configuration:
    """Load configuration from zip archive"""

    with zipfile.ZipFile(filename, "r") as zip_file:
        adjustment_dict = json.loads(zip_file.read(ADJUSTMENT_FILE_NAME))

        return Configuration(
            field_adjustment=adjustment.Adjustment(
                **adjustment_dict[FIELD_ADJUSTMENT_KEY]
            ),
            border_adjustment=adjustment.Adjustment(
                **adjustment_dict[BORDER_ADJUSTMENT_KEY]
            ),
            catalogue=_load_catalogue(zip_file),
            card_border=_load_dir(zip_file, CARD_BORDER_DIRECTORY),
            empty_card=_load_dir(zip_file, EMPTY_CARD_DIRECTORY),
            meta={},
        )


def generate(image: np.ndarray) -> Configuration:
    """Generate a configuration with user input"""
    adj = adjustment.adjust_field(image)
    squares = card_finder.get_field_squares(image, adj, 5, 8)
    catalogue = card_finder.catalogue_cards(squares)
    return Configuration(field_adjustment=adj, catalogue=catalogue, meta={})
