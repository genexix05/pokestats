from PyQt6 import QtWidgets, QtGui, QtCore
from utils.ocr import OCRProcessor
from utils.emulator import get_emulator_region
from utils.pokeapi import get_pokemon_stats, get_pokemon_names
from fuzzywuzzy import process
import threading
import sys
import time
import re

# Palabras irrelevantes para descartar del OCR
IRRELEVANT_WORDS = {
    'file', 'view', 'config', 'tools', 'help',
    'desmume', 'mgba', 'yuzu', 'citra',
    'fps:60/30', 'fps:60/33', 'fps:0/30',
    'viex', 'ccnfig', 'helr', 'texto', 'valido', 'detectado',
    'qpa', 'window', 'failed',  # etc. las que veas
}

class MainWindow(QtWidgets.QWidget):

    

    update_stats_signal = QtCore.pyqtSignal(str, dict, str)

    def __init__(self, selected_emulator):
        super().__init__()
        self.selected_emulator = selected_emulator
        
        # Cargar nombres de Pokémon
        self.pokemon_names = get_pokemon_names()

        # Inicializar OCR, región y control de detección
        self.emulator_region = None
        self.ocr_processor = OCRProcessor()
        self.detection_enabled = False  # Inicia sin buscar
        self.paused = False  # Control de "Parar" y "Recargar"

        # Señal para actualizar stats
        self.update_stats_signal.connect(self.update_stats)

        # Construcción de la interfaz
        self.init_ui()
        
        # Obtener la región del emulador
        self.get_emulator_region()
        
        # Iniciar el hilo de OCR (aunque detection_enabled=False)
        self.start_capture_thread()

    def init_ui(self):
        self.setWindowIcon(QtGui.QIcon('assets/icons/pokemon_icon.ico'))
        self.setWindowTitle('Estadísticas del Pokémon')
        self.setFixedSize(450, 500)

        # Mantener la ventana encima
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.WindowStaysOnTopHint)

        # Ajusta el icono de la ventana
        self.setWindowIcon(QtGui.QIcon('assets/icons/pokemon_icon.png'))

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Etiqueta principal
        self.title_label = QtWidgets.QLabel('Pulsa "Empezar" para buscar Pokémon...')
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.title_label.setFont(font)
        self.title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Imagen del Pokémon
        self.pokemon_image_label = QtWidgets.QLabel()
        self.pokemon_image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.pokemon_image_label)

        # Espacio
        layout.addSpacing(10)

        # Layout para stats con barras y valores
        self.stats_layout = QtWidgets.QFormLayout()
        layout.addLayout(self.stats_layout)

        # Mapeo de stats desde la API
        self.stat_mapping = {
            'hp': 'HP',
            'attack': 'Attack',
            'defense': 'Defense',
            'special-attack': 'Special-Attack',
            'special-defense': 'Special-Defense',
            'speed': 'Speed'
        }

        # Crear barras de progreso y etiquetas para stats
        self.stats_bars = {}
        for stat_api, stat_label in self.stat_mapping.items():
            bar_layout = QtWidgets.QHBoxLayout()
            bar = QtWidgets.QProgressBar()
            bar.setRange(0, 255)  # Rango máximo de stats base
            bar.setValue(0)
            bar.setTextVisible(False)  # Ocultar porcentaje
            label = QtWidgets.QLabel("0")  # Muestra el valor de la stat
            bar_layout.addWidget(bar)
            bar_layout.addWidget(label)
            self.stats_layout.addRow(f"{stat_label}:", bar_layout)
            self.stats_bars[stat_api] = (bar, label)

        # Botón "Empezar"
        self.start_button = QtWidgets.QPushButton("Empezar")
        self.start_button.clicked.connect(self.on_start_clicked)
        layout.addWidget(self.start_button)

        # Botón "Recargar"/"Parar"
        self.reload_button = QtWidgets.QPushButton("Recargar")
        self.reload_button.clicked.connect(self.on_reload_clicked)
        layout.addWidget(self.reload_button)

        # Botón "Cerrar"
        self.close_button = QtWidgets.QPushButton("Cerrar")
        self.close_button.clicked.connect(self.close_application)
        layout.addWidget(self.close_button)

    def on_start_clicked(self):
        """Activa la detección al pulsar "Empezar" y oculta el botón."""
        self.detection_enabled = True
        self.paused = False
        self.title_label.setText("Buscando Pokémon...")
        self.start_button.hide()

    def on_reload_clicked(self):
        """Alterna entre "Recargar" y "Parar"."""
        if self.reload_button.text() == "Recargar":
            self.detection_enabled = True
            self.paused = False
            self.title_label.setText("Buscando Pokémon...")
            self.pokemon_image_label.clear()
            for bar, label in self.stats_bars.values():
                bar.setValue(0)
                label.setText("0")
            self.reload_button.setText("Parar")
        else:
            self.detection_enabled = False
            self.paused = True
            self.title_label.setText("Detenido (pulsa 'Recargar' para continuar)")
            self.reload_button.setText("Recargar")

    def get_emulator_region(self):
        """Obtiene la región de la ventana del emulador."""
        reg = get_emulator_region(self.selected_emulator)
        if not reg:
            QtWidgets.QMessageBox.critical(self, "Error", "No se encontró la ventana del emulador.")
            self.close()
            sys.exit()
        self.emulator_region = reg

    def start_capture_thread(self):
        """Arranca el hilo que realiza OCR continuamente."""
        self.capture_thread = threading.Thread(target=self.run_capture, daemon=True)
        self.capture_thread.start()

    def run_capture(self):
        """Bucle que realiza OCR mientras detection_enabled=True."""
        last_text = None
        while True:
            if not self.detection_enabled or self.paused:
                time.sleep(0.1)
                continue

            recognized_texts = self.ocr_processor.capture_and_recognize(self.emulator_region)
            if not recognized_texts:
                time.sleep(0.1)
                continue

            for res in recognized_texts:
                text = res[1] if isinstance(res, tuple) else res
                text = text.lower().strip()

                # Filtrar texto irrelevante
                if len(text) < 3 or text in IRRELEVANT_WORDS or not re.match(r'^[a-z0-9\-]+$', text) or text == last_text:
                    continue
                last_text = text

                # Coincidencia exacta o fuzzy matching
                if text in self.pokemon_names:
                    stats, sprite_url = get_pokemon_stats(text)
                    if stats:
                        self.update_stats_signal.emit(text, stats, sprite_url)
                        self.detection_enabled = False
                        self.reload_button.setText("Recargar")
                        break
                else:
                    best_match, score = process.extractOne(text, self.pokemon_names)
                    if score >= 80:
                        stats, sprite_url = get_pokemon_stats(best_match)
                        if stats:
                            self.update_stats_signal.emit(best_match, stats, sprite_url)
                            self.detection_enabled = False
                            self.reload_button.setText("Recargar")
                            break

            time.sleep(0.1)

    @QtCore.pyqtSlot(str, dict, str)
    def update_stats(self, pokemon_name, stats, sprite_url):
        """Actualiza las barras y muestra el sprite del Pokémon."""
        self.title_label.setText(f"Estadísticas de {pokemon_name.capitalize()}:")
        data = self.download_image(sprite_url)
        if data:
            img = QtGui.QImage()
            img.loadFromData(QtCore.QByteArray(data))
            pix = QtGui.QPixmap.fromImage(img)
            self.pokemon_image_label.setPixmap(pix.scaled(128, 128, QtCore.Qt.AspectRatioMode.KeepAspectRatio))

        # Actualizar las barras con los valores de stats
        for api_stat, value in stats.items():
            if api_stat in self.stats_bars:
                bar, label = self.stats_bars[api_stat]
                bar.setValue(value)
                label.setText(str(value))

    def download_image(self, url):
        """Descarga el sprite del Pokémon."""
        import requests
        try:
            resp = requests.get(url)
            if resp.status_code == 200:
                return resp.content
        except Exception as e:
            print(f"Error al descargar sprite: {e}")
        return b''

    def close_application(self):
        """Cierra la aplicación."""
        self.close()
        sys.exit()
