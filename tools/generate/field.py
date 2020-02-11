import numpy as np
import cv2
import shenzhen_solitaire.card_detection.configuration as configuration


def main() -> None:
    """Generate a configuration"""
    image = cv2.imread("pictures/20190809172213_1.jpg")

    generated_config = configuration.generate(image)
    configuration.save(generated_config, "test_config.zip")


if __name__ == "__main__":
    main()
