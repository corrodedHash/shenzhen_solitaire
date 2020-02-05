"""Contains configuration class"""
import zipfile
import json
from typing import List, Tuple, Dict
import io
import dataclasses
import tempfile
import cv2

import numpy as np
from . import adjustment
from . import card_finder
from .. import board


class Configuration:
    """Configuration for solitaire cv"""

    ADJUSTMENT_FILE_NAME = "adjustment.json"
    TEMPLATES_DIRECTORY = "templates"

    def __init__(
        self,
        adj: adjustment.Adjustment,
        catalogue: List[Tuple[np.ndarray, board.Card]],
        meta: Dict[str, str],
    ) -> None:
        self.field_adjustment = adj
        self.catalogue = catalogue
        self.meta = meta

    def save(self, filename: str) -> None:
        """Save configuration to zip archive"""
        zip_stream = io.BytesIO()

        with zipfile.ZipFile(zip_stream, "w") as zip_file:
            zip_file.writestr(
                self.ADJUSTMENT_FILE_NAME,
                json.dumps(dataclasses.asdict(self.field_adjustment)),
            )

            counter = 0
            extension = ".png"
            for square, card in self.catalogue:
                counter += 1
                fd, myfile = tempfile.mkstemp()
                cv2.imwrite(myfile + extension, square)
                file_name = ""
                if isinstance(card, board.SpecialCard):
                    file_name = f"s{card.value}-{card.name}-{counter}{extension}"
                elif isinstance(card, board.NumberCard):
                    file_name = (
                        f"n{card.suit.value}{card.number}"
                        f"-{card.suit.name}-{counter}{extension}"
                    )
                else:
                    raise AssertionError()
                zip_file.write(myfile + extension, arcname=f"{self.TEMPLATES_DIRECTORY}/{file_name}")

        with open(filename, "wb") as zip_archive:
            zip_archive.write(zip_stream.getvalue())

    @staticmethod
    def load(filename: str) -> "Configuration":
        """Load configuration from zip archive"""

        def _parse_file_name(card_filename: str) -> board.Card:
            assert card_filename.startswith(Configuration.TEMPLATES_DIRECTORY + "/")
            pure_name = card_filename[len(Configuration.TEMPLATES_DIRECTORY + "/") :]
            if pure_name[0] == "s":
                return board.SpecialCard(int(pure_name[1]))
            if pure_name[0] == "n":
                return board.NumberCard(
                    suit=board.NumberCard.Suit(int(pure_name[1])),
                    number=int(pure_name[2]),
                )
            raise AssertionError()

        catalogue: List[Tuple[np.ndarray, board.Card]] = []
        with zipfile.ZipFile(filename, "r") as zip_file:
            adj = adjustment.Adjustment(
                **json.loads(zip_file.read(Configuration.ADJUSTMENT_FILE_NAME))
            )
            mydir=tempfile.mkdtemp()
            for template_filename in (
                x
                for x in zip_file.namelist()
                if x.startswith(Configuration.TEMPLATES_DIRECTORY + "/")
            ):
                myfile = zip_file.extract(template_filename, path=mydir)
                catalogue.append(
                    (
                        cv2.imread(myfile),
                        _parse_file_name(template_filename),
                    )
                )
                assert catalogue[-1][0] is not None
            return Configuration(adj=adj, catalogue=catalogue, meta={})

    @staticmethod
    def generate(image: np.ndarray) -> "Configuration":
        """Generate a configuration with user input"""
        adj = adjustment.adjust_field(image)
        squares = card_finder.get_field_squares(image, adj, 5, 8)
        catalogue = card_finder.catalogue_cards(squares)
        return Configuration(adj=adj, catalogue=catalogue, meta={})
