import sys
from PyQt6.QtWidgets import QApplication
from .gui import DigitalDNAGUI
from .tray_icon import SystemTrayManager

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = DigitalDNAGUI()
    tray = SystemTrayManager(window)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
