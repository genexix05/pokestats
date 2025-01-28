import easyocr
import pyautogui
import numpy as np
import cv2

class OCRProcessor:
    def __init__(self, language='es'):
        self.reader = easyocr.Reader([language], gpu=False)
    
    def capture_and_recognize(self, region):
        # Capturar la pantalla y convertirla en un array de NumPy
        screenshot = pyautogui.screenshot(region=region)
        screenshot_np = np.array(screenshot)

        # Convertir de RGB a BGR
        screenshot_np = screenshot_np[:, :, ::-1]

        # Convertir a escala de grises
        gray = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        height, width = blurred.shape[:2]
        scale_factor = 2  # Ajusta si quieres más (x3) o menos (x1.5)
        resized = cv2.resize(blurred, (width * scale_factor, height * scale_factor),
                             interpolation=cv2.INTER_LINEAR)

        # Aplicar umbralización
        _, thresh = cv2.threshold(resized, 150, 255, cv2.THRESH_BINARY)

        # Pasar la imagen procesada a la función readtext
        result = self.reader.readtext(thresh, detail=0)
        return result
