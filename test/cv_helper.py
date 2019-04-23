import itertools
from typing import Tuple, List, Dict
import zipfile
import io
import json
import dataclasses

import numpy as np  # type: ignore
import cv2  # type: ignore

from .context import shenzhen_solitaire
from shenzhen_solitaire.cv import adjustment
from shenzhen_solitaire.cv import card_finder


def pixelcount(image: np.ndarray) -> List[Tuple[Tuple[int, int, int], int]]:
    p: Dict[Tuple[int, int, int], int] = {(0, 0, 0): 0}
    for pixel in itertools.chain.from_iterable(image):
        x = tuple(pixel)
        if x in p:
            p[x] += 1
        else:
            p[x] = 1
    B = sorted(p.items(), key=lambda x: x[1])
    return B


def simplify(image: np.ndarray) -> None:
    cv2.imshow("Window", image)
    cv2.waitKey(0)
    cv2.destroyWindow("Window")
    print(*card_finder.simplify(image)[1].items(), sep='\n')
    cv2.imshow("Window", image)
    cv2.waitKey(0)
    cv2.destroyWindow("Window")

def calibrate(image: np.ndarray) -> None:
    adj = adjustment.adjust_field(image)
    squares = card_finder.get_field_squares(image, adj)
    catalogue = card_finder.catalague_cards(squares)
    simplified_catalogue = []
    for square, card in catalogue:
        simplified_catalogue.append((card_finder.simplify(square), card))

    zip_stream = io.BytesIO()
    with zipfile.ZipFile(zip_stream, "w") as zip_file:
        zip_file.writestr('adjustment.json', json.dumps(dataclasses.asdict(adj)))

        file_stream = io.BytesIO()
        np.save(file_stream, squares[0], allow_pickle=False)
        print(file_stream.getvalue())
        zip_file.writestr('0.dat', file_stream.getvalue())
    print()
    print(zip_stream.getvalue())
    with open('myzip.zip', 'wb') as fd:
        fd.write(zip_stream.getvalue())


def main() -> None:
    with open("Solitaire.png", 'rb') as fd:
        img_str = fd.read()
    nparr = np.frombuffer(img_str, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    #print(squares[0])



def main2() -> None:
    file_stream = None
    with zipfile.ZipFile('myzip.zip', "r") as zip_file:
        file_stream = io.BytesIO(zip_file.read('0.dat'))

    A = np.load(file_stream)
    print(A)


if __name__ == "__main__":
    main()
    main2()
