import numpy as np
import cv2
from shenzhen_solitaire.card_detection.configuration import Configuration

def main() -> None:
    """Generate a configuration"""
    with open("pictures/20190809172213_1.jpg", 'rb') as png_file:
        img_str = png_file.read()
    nparr = np.frombuffer(img_str, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    generated_config = Configuration.generate(image)
    generated_config.save('test_config.zip')
 