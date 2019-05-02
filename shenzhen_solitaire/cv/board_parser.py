import numpy as np
from .configuration import Configuration
from ..board import Board
from . import card_finder
import copy


def parse_board(image: np.ndarray, conf: Configuration) -> Board:
    squares = card_finder.get_field_squares(
        image, conf.field_adjustment, count_x=13, count_y=8)
    squares = [card_finder.simplify(square)[0] for square in squares]
    square_rows = [squares[13 * i:13 * (i + 1)] for i in range(8)]
    empty_square = np.full(
        shape=(conf.field_adjustment.w,
               conf.field_adjustment.h),
        fill_value=card_finder.GREYSCALE_COLOR[card_finder.Cardcolor.Background],
        dtype=np.uint8)
    assert empty_square.shape == squares[0].shape
    result: Board = Board()
    for row_id, square_row in enumerate(square_rows):
        for square in square_row:
            fitting_square, _ = card_finder.find_square(
                square, [empty_square] + [x[0] for x in conf.catalogue])
            if np.array_equal(fitting_square, empty_square):
                print("empty")
                break
            for cat_square, cardtype in conf.catalogue:
                if np.array_equal(fitting_square, cat_square):
                    print(cardtype)
                    result.field[row_id].append(cardtype)
                    break
            else:
                print("did not find image")

    return result
