import sys
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor

class SystemTrayManager:
    def __init__(self, main_window):
        self.main_window = main_window
        self.tray_icon = QSystemTrayIcon(main_window)
        self.tray_icon.setIcon(self._create_icon())

        menu = QMenu()
        show_action = menu.addAction("Open Digital DNA")
        show_action.triggered.connect(self._show_window)

        lock_action = menu.addAction("Lock Workstation")
        lock_action.triggered.connect(self.main_window.auth_engine._lock_workstation)

        menu.addSeparator()
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(QApplication.instance().quit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

    def _create_icon(self) -> QIcon:
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(0, 0, 0, 0))
        painter = QPainter(pixmap)
        painter.setBrush(QColor(41, 128, 185))
        painter.setPen(QColor(255, 255, 255))
        painter.drawEllipse(2, 2, 28, 28)
        painter.drawText(8, 21, "DNA")
        painter.end()
        return QIcon(pixmap)

    def _show_window(self):
        self.main_window.show()
        self.main_window.activateWindow()
