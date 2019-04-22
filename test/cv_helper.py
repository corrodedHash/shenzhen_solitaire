from .context import shenzhen_solitaire
from shenzhen_solitaire.cv import adjustment
from shenzhen_solitaire.cv import card_finder
from typing import Tuple, List, Dict
import cv2
import numpy
import itertools

A = cv2.imread("Solitaire.png")


def pixelcount(image: numpy.ndarray) -> List[Tuple[Tuple[int, int, int], int]]:
    p: Dict[Tuple[int, int, int], int] = {(0, 0, 0): 0}
    for pixel in itertools.chain.from_iterable(image):
        x = tuple(pixel)
        if x in p:
            p[x] += 1
        else:
            p[x] = 1
    B = sorted(p.items(), key=lambda x: x[1])
    return B

def simplify(image: numpy.ndarray) -> None:
    cv2.imshow("Window", image)
    cv2.waitKey(0)
    cv2.destroyWindow("Window")
    print(*card_finder.simplify(image).items(), sep='\n')
    cv2.imshow("Window", image)
    cv2.waitKey(0)
    cv2.destroyWindow("Window")


def main() -> None:
    adj = adjustment.adjust_field(A)
    image_squares = card_finder.get_field_squares(A, adj)
    for img in image_squares:
        print(*pixelcount(img), sep='\n')
        cv2.imshow("Window", img)
        cv2.waitKey(0)
        cv2.destroyWindow("Window")
        print()


if __name__ == "__main__":
    main()
