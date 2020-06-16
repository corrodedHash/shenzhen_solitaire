import shenzhen_solitaire.card_detection.configuration as configuration
from shenzhen_solitaire.board import NumberCard, SpecialCard

import cv2

import numpy as np
from typing import Any, Tuple


def prepare_image(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # edge_image = cv2.Canny(gray_image, 120, 160)
    ret, edge_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY_INV)
    contours2, hierarchy = cv2.findContours(
        edge_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    cnt2 = max(contours2, key=cv2.contourArea)

    mask = np.zeros(edge_image.shape, dtype=edge_image.dtype)
    contim = cv2.drawContours(mask, [cnt2], 0, 1, cv2.FILLED)
    crop = np.multiply(edge_image, contim)
    return crop


def match_template(image, template):
    image_cont, hierarchy = cv2.findContours(
        image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    imcont = max(image_cont, key=cv2.contourArea)
    template_cont, hierarchy = cv2.findContours(
        template, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    temcont = max(template_cont, key=cv2.contourArea)
    return [
        cv2.matchShapes(imcont, temcont, mode, 0.0)
        for mode in (
            cv2.CONTOURS_MATCH_I1,
            cv2.CONTOURS_MATCH_I2,
            cv2.CONTOURS_MATCH_I3,
        )
    ]


def type_fine(one, other) -> bool:
    if isinstance(one, SpecialCard):
        return one == other
    assert isinstance(one, NumberCard)
    if not isinstance(other, NumberCard):
        return False
    return one.number == other.number


def debug_match(image, image_type, catalogue):
    img1 = prepare_image(image)
    i1_matches = []
    for index, (template_image, template_type) in enumerate(catalogue):
        img2 = prepare_image(template_image)
        i1_matches.append((template_type, match_template(img1, img2)[0], index))
    i1_matches = sorted(i1_matches, key=lambda x: x[1])
    if not type_fine(i1_matches[0][0], image_type):
        correct_index = 0
        for list_type, list_value, _ in i1_matches:
            if type_fine(list_type, image_type):
                correct_value = list_value
                break
            correct_index += 1
        print(
            f"{str(image_type):>20} matched as {str(i1_matches[0][0]):>20} {i1_matches[0][1]:.05f}, "
            f"correct in pos {correct_index:02d} val {correct_value:.05f}"
        )
        cv2.imshow("one", prepare_image(catalogue[i1_matches[0][2]][0]))
        cv2.imshow("two", img1)
        cv2.imshow("three", prepare_image(catalogue[i1_matches[correct_index][2]][0]))
        cv2.waitKey(0)
        return
    for list_type, list_value, list_index in i1_matches:
        if not type_fine(list_type, i1_matches[0][0]):
            if list_value * 0.6 < i1_matches[0][1]:
                print(
                    f"{str(image_type):>20} {i1_matches[0][1]:.05f} very close"
                    f" match with {str(list_type):>20} {list_value:.05f}"
                )
            return

    if i1_matches[0][1] > 1:
        print(f"{image_type} with value {i1_matches[0][1]}")


def main() -> None:
    pc = configuration.load("test_config.zip")
    laptop = configuration.load("laptop_conf.zip")
    bla = [(i, t) for i, t in pc.catalogue if t == SpecialCard.Hua]
    bla = pc.catalogue
    for pc_image, pc_card_type in bla:
        debug_match(pc_image, pc_card_type, laptop.catalogue)


if __name__ == "__main__":
    main()
