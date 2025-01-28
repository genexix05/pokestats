from gui.emulator_selection import EmulatorSelection
from gui.main_window import MainWindow
from PyQt6 import QtWidgets
import sys
import threading



def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Ventana de selección de emulador
    emulator_selection = EmulatorSelection()
    emulator_selection.show()
    app.exec()
    
    if emulator_selection.selected_emulator is None:
        print("No se seleccionó ningún emulador.")
        sys.exit()
    
    # Ventana principal
    main_window = MainWindow(emulator_selection.selected_emulator)
    main_window.show()
    
    # Iniciar hilos o procesos necesarios
    main_window.start_capture_thread()
    
    sys.exit(app.exec())

    self.setWindowIcon(QtGui.QIcon('assets/icons/pokemon_icon.ico'))


if __name__ == '__main__':
    main()
