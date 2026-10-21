import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Also ensure app/desktop directory is in sys.path if run directly
DESKTOP_DIR = Path(__file__).resolve().parent
if str(DESKTOP_DIR) not in sys.path:
    sys.path.insert(0, str(DESKTOP_DIR))

from PyQt6.QtWidgets import QApplication

try:
    from app.desktop.gui import DigitalDNAGUI
    from app.desktop.tray_icon import SystemTrayManager
except (ImportError, ModuleNotFoundError):
    from gui import DigitalDNAGUI
    try:
        from tray_icon import SystemTrayManager
    except (ImportError, ModuleNotFoundError):
        SystemTrayManager = None

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = DigitalDNAGUI()
    if SystemTrayManager is not None:
        tray = SystemTrayManager(window)
        window.tray_manager = tray
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
