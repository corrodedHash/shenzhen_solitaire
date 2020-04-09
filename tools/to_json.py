from shenzhen_solitaire.card_detection.board_parser import parse_to_json
import shenzhen_solitaire.card_detection.configuration as configuration
import cv2
import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Give filename pls")
        return
    image = cv2.imread(str(sys.argv[1]))

    conf = configuration.load("test_config.zip")

    print(parse_to_json(image, conf))


if __name__ == "__main__":
    main()
