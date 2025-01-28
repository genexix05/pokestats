# gui/emulator_selection.py

from PyQt6 import QtWidgets, QtGui, QtCore
import sys
import os

class ClickableLabel(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton and self.isEnabled():
            self.clicked.emit()
        super().mouseReleaseEvent(event)

class EmulatorSelection(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('assets/icons/pokemon_icon.ico'))
        self.selected_emulator = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Selecciona tu Emulador')
        self.setFixedSize(400, 300)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Etiqueta de instrucción
        label = QtWidgets.QLabel('Elige el emulador que estás utilizando:')
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        font = QtGui.QFont()
        font.setPointSize(12)
        label.setFont(font)
        main_layout.addWidget(label)

        main_layout.addSpacing(20)

        # Crear un layout para los logos
        logos_layout = QtWidgets.QGridLayout()
        logos_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(logos_layout)

        emulators = [
            {'name': 'Desmume', 'logo': 'desmume.png'},
            {'name': 'VisualBoyAdvance', 'logo': 'visualboyadvance.png'},
            {'name': 'Citra', 'logo': 'citra.png'},
            {'name': 'Yuzu', 'logo': 'yuzu.png'}
        ]

        logos_path = 'assets/icons/'
        columns = 2
        row = 0
        col = 0

        for emulator in emulators:
            label_logo = ClickableLabel()
            label_logo.setFixedSize(150, 100)
            label_logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

            # Cargar la imagen del logo
            logo_path = os.path.join(logos_path, emulator['logo'])
            pixmap = QtGui.QPixmap(logo_path)
            pixmap = pixmap.scaled(label_logo.size(),
                                   QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                                   QtCore.Qt.TransformationMode.SmoothTransformation)
            label_logo.setPixmap(pixmap)

            label_logo.emulator_name = emulator['name']

            # Habilitar solo si es Desmume
            if emulator['name'].lower() == 'desmume':
                # Conectar el click al método select_emulator
                label_logo.clicked.connect(self.select_emulator)
                label_logo.setEnabled(True)
            else:
                # Deshabilitar el resto de emuladores
                label_logo.setEnabled(False)

            # Añadir al layout
            logos_layout.addWidget(label_logo, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        self.setLayout(main_layout)

    def select_emulator(self):
        sender = self.sender()
        self.selected_emulator = sender.emulator_name
        self.close()

# Código de prueba
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = EmulatorSelection()
    window.show()
    app.exec()
    print(f"Emulador seleccionado: {window.selected_emulator}")
