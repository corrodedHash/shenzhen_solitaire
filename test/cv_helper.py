import itertools
from typing import Tuple, List, Dict
import numpy as np  # type: ignore
import cv2  # type: ignore
import zipfile

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


def main() -> None:
    #image = cv2.imread("Solitaire.png")
    with open("Solitaire.png", 'rb') as fd:
        img_str = fd.read()
    nparr = np.frombuffer(img_str, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #image2 = cv2.imread("Solitaire2.png")
    #image2 = cv2.resize(image2, (1000, 629))
    image2 = cv2.imread("Solitaire.png")

    adj = adjustment.adjust_field(image)
    squares = card_finder.get_field_squares(image, adj)
    print(squares[0])
    np.save('0.dat', squares[0], allow_pickle=False)
    assert 0
    with open("0.dat", 'wb') as fd:
        fd.write(squares[0].tobytes())
    catalogue = card_finder.catalague_cards(squares[:5])
    my_zip = zipfile.ZipFile('myzip.zip', mode='w')
    for index, x in enumerate(catalogue):
        my_zip.writestr(f"{index}.dat", x[0].tobytes())
    my_zip.close()
    assert 0

    squares = card_finder.get_simplified_squares(image, adj)
    print("Simplified")

    adj.x -= 2
    adj.y -= 2
    adj.w += 5
    adj.h += 5

    image_squares = card_finder.get_field_squares(image2, adj)
    for i in range(10, 20):
        image_squares[i], _ = card_finder.simplify(image_squares[i])
        print("Finding...")
        found_image, certainty = card_finder.find_square(
            image_squares[i], squares)
        print(certainty)


def main2() -> None:
    A = np.load('0.dat.npy')
    print(A)


if __name__ == "__main__":
    main2()
