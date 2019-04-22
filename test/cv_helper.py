from .context import shenzhen_solitaire
from shenzhen_solitaire.cv import adjustment
from shenzhen_solitaire.cv import card_finder
from typing import Tuple, List, Dict
import cv2
import numpy
import itertools


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
    image = cv2.imread("Solitaire.png")
    image2 = cv2.imread("Solitaire2.png")
    image2 = cv2.resize(image2, (1000, 629))

    adj = adjustment.adjust_field(image)
    squares = card_finder.get_simplified_squares(image, adj)
    print("Simplified")

    adj.x -= 2
    adj.y -= 2
    adj.w += 5
    adj.h += 5

    image_squares = card_finder.get_field_squares(image2, adj)
    for i in range(10,20):
        image_squares[i], _ = card_finder.simplify(image_squares[i])
        print("Finding...")
        found_image, certainty = card_finder.find_square(image_squares[i], squares)


if __name__ == "__main__":
    main()
