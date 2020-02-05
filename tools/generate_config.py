import numpy as np
import cv2
from shenzhen_solitaire.card_detection.configuration import Configuration

def main() -> None:
    """Generate a configuration"""
    image = cv2.imread("pictures/20190809172213_1.jpg")

    generated_config = Configuration.generate(image)
    generated_config.save('test_config.zip')

if __name__ == "__main__":
    main()
 