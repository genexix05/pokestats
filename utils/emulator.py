# utils/emulator.py

import pyautogui
import re

def get_emulator_region(emulator_name):
    """
    Busca la ventana del emulador, la activa y devuelve una tupla con
    (left, top, width, height) que representa ÚNICAMENTE el 25% superior
    de la ventana.
    """
    # Palabras clave o patrones regex para identificar el emulador
    window_patterns = {
        'Desmume': r'DeSmuME.*',
        'VisualBoyAdvance': r'VisualBoyAdvance.*',
        'Citra': r'Citra.*',
        'Yuzu': r'yuzu.*',
    }

    pattern = window_patterns.get(emulator_name)
    if not pattern:
        print(f"No se encontró el patrón para el emulador {emulator_name}")
        return None

    windows = pyautogui.getAllWindows()
    for window in windows:
        if re.match(pattern, window.title, re.IGNORECASE):
            # Asegurarnos de que la ventana está visible y activarla
            if window.isMinimized:
                window.restore()
            window.activate()

            # Capturamos los bordes totales de la ventana
            full_left   = window.left
            full_top    = window.top
            full_width  = window.width
            full_height = window.height

            # Calculamos la región que representa el 25% superior de la ventana
            new_height = int(full_height * 0.25)
            region = (full_left, full_top, full_width, new_height)

            print(f"Ventana del emulador encontrada: '{window.title}'")
            print(f"Región devuelta (25% superior): {region}")

            return region

    print(f"No se encontró la ventana del emulador {emulator_name} que coincida con el patrón '{pattern}'")
    return None
