import shenzhen_solitaire.card_detection.configuration as configuration
from shenzhen_solitaire.board import NumberCard, SpecialCard

import cv2

import numpy as np
from typing import Any, Tuple


def border_image(image, size=1, color=0):
    for ring in range(size):
        for x in range(ring, image.shape[0] - ring):
            image[x][ring] = color
            image[x][image.shape[1] - 1 - ring] = color
        for y in range(ring, image.shape[1] - ring):
            image[ring][y] = color
            image[image.shape[0] - 1 - ring][y] = color


def prepare_image(image):
    cnt = get_contour(image)
    mask = np.zeros(image.shape[:2], dtype=image.dtype)
    contim = cv2.drawContours(mask, [cnt], 0, 255, cv2.FILLED)
    # crop = np.multiply(edge_image, contim)
    return contim


def get_contour(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, edge_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY_INV)
    border_image(edge_image, size=0)
    contours, hierarchy = cv2.findContours(
        edge_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    cnt = max(contours, key=cv2.contourArea)
    return cnt


def matchScaleInvShape(cont1, cont2):
    m1 = cv2.moments(cont1)
    m2 = cv2.moments(cont2)
    moments = [
        (m1[moment], m2[moment]) for moment in m1 if str(moment).startswith("nu")
    ]
    return sum([abs((nu1) - (nu2)) for nu1, nu2 in moments])


def match_template(image, template):
    image_cont, hierarchy = cv2.findContours(
        image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    imcont = max(image_cont, key=cv2.contourArea)
    template_cont, hierarchy = cv2.findContours(
        template, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
    )
    temcont = max(template_cont, key=cv2.contourArea)
    return [matchScaleInvShape(imcont, temcont)]


def type_fine(one, other) -> bool:
    if isinstance(one, SpecialCard):
        return one == other
    assert isinstance(one, NumberCard)
    if not isinstance(other, NumberCard):
        return False
    return one.number == other.number

def check_type(matches, should_type):
    if not type_fine(matches[0][0], should_type):
        correct_index = 0
        for list_type, list_value, _ in matches:
            if type_fine(list_type, should_type):
                correct_value = list_value
                break
            correct_index += 1
        print(
            f"{str(should_type):>20} matched as {str(matches[0][0]):>20} {matches[0][1]:.05f}, "
            f"correct in pos {correct_index:02d} val {correct_value:.05f}"
        )
        cv2.imshow("one", prepare_image(catalogue[matches[0][2]][0]))
        cv2.imshow("two", img1)
        cv2.imshow("three", prepare_image(catalogue[matches[correct_index][2]][0]))
        cv2.waitKey(0)
        return True
    return False

def debug_match(image, image_type, catalogue):
    cnt1 = prepare_image(image)
    i1_matches = []
    for index, (template_image, template_type) in enumerate(catalogue):
        cnt2 = prepare_image(template_image)
        i1_matches.append((template_type, matchScaleInvShape(cnt1, cnt2), index))
    i1_matches = sorted(i1_matches, key=lambda x: x[1])
    
    for list_type, list_value, list_index in i1_matches:
        if not type_fine(list_type, i1_matches[0][0]):
            if list_value * 0.4 < i1_matches[0][1]:
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
