"""
Digital DNA - Desktop GUI
3-Phase Workflow: Monitor -> Train -> Authenticate
Clean Monochrome (Black & White) Design with Scrollable Non-Overlapping Layout
"""

import sys
import os
import time
import json
import threading
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTabWidget, QLineEdit,
    QCheckBox, QSpinBox, QMessageBox, QGroupBox, QComboBox, QTextEdit,
    QFrame, QScrollArea, QSizePolicy
)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPen

from core.profile_manager import ProfileManager
from core.enrollment import EnrollmentManager
from core.auth_engine import ContinuousAuthEngine
from core.config import config
from collectors.desktop.main_collector import DesktopCollector
from features.feature_pipeline import FeaturePipeline


# --------------------- Monochrome Color Palette ---------------------
COLORS = {
    "bg_dark": "#0a0a0a",
    "bg_card": "#141414",
    "bg_card_hover": "#1c1c1c",
    "bg_input": "#0d0d0d",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
    "text_muted": "#606060",
    "border": "#282828",
    "border_light": "#404040",
    "border_focus": "#ffffff",
    "progress_bg": "#161616",
    "progress_chunk": "#ffffff",
}

STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['bg_dark']};
}}
QWidget {{
    background-color: transparent;
    color: {COLORS['text_primary']};
    font-family: 'Segoe UI', 'Inter', 'Roboto', sans-serif;
}}
QLabel {{
    color: {COLORS['text_primary']};
    background: transparent;
}}
QGroupBox {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 18px;
    padding-top: 16px;
    padding-bottom: 14px;
    padding-left: 14px;
    padding-right: 14px;
    background-color: {COLORS['bg_card']};
    font-weight: 600;
    font-size: 13px;
    color: {COLORS['text_primary']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: 2px;
    padding: 0 6px;
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    font-weight: bold;
}}
QPushButton {{
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #ffffff;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}}
QPushButton:hover {{
    background-color: #d9d9d9;
    border-color: #d9d9d9;
}}
QPushButton:pressed {{
    background-color: #bfbfbf;
    border-color: #bfbfbf;
}}
QPushButton:disabled {{
    background-color: #1a1a1a;
    color: #555555;
    border: 1px solid #282828;
}}
QProgressBar {{
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    height: 16px;
    background-color: {COLORS['progress_bg']};
    text-align: center;
    color: {COLORS['text_primary']};
    font-size: 11px;
    font-weight: bold;
}}
QProgressBar::chunk {{
    border-radius: 5px;
    background-color: {COLORS['progress_chunk']};
}}
QTextEdit {{
    background-color: {COLORS['bg_input']};
    color: #dcdcdc;
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
    font-family: 'Cascadia Code', 'Consolas', monospace;
    font-size: 11px;
    selection-background-color: #333333;
}}
QLineEdit {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
}}
QLineEdit:focus {{
    border-color: {COLORS['border_focus']};
}}
QComboBox {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
}}
QComboBox:focus {{
    border-color: {COLORS['border_focus']};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    selection-background-color: #282828;
}}
QCheckBox {{
    color: {COLORS['text_primary']};
    spacing: 8px;
    font-size: 13px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid {COLORS['border_light']};
    background-color: {COLORS['bg_input']};
}}
QCheckBox::indicator:checked {{
    background-color: #ffffff;
    border-color: #ffffff;
}}
QSpinBox {{
    background-color: {COLORS['bg_input']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 13px;
}}
QSpinBox:focus {{
    border-color: {COLORS['border_focus']};
}}
QTabWidget::pane {{
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    background: #101010;
}}
QTabBar::tab {{
    background: {COLORS['bg_card']};
    color: {COLORS['text_secondary']};
    border: 1px solid {COLORS['border']};
    border-bottom: none;
    padding: 9px 20px;
    font-size: 12px;
    font-weight: bold;
    margin-right: 4px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{
    background: #101010;
    color: #ffffff;
    border-top: 2px solid #ffffff;
}}
QTabBar::tab:hover {{
    background: {COLORS['bg_card_hover']};
    color: #cccccc;
}}
QScrollBar:vertical {{
    background: #0d0d0d;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical {{
    background: #333333;
    min-height: 24px;
    border-radius: 4px;
}}
QScrollBar::handle:vertical:hover {{
    background: #555555;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

PRIMARY_BTN_STYLE = """
QPushButton {
    background-color: #ffffff;
    color: #000000;
    border: 1px solid #ffffff;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #d9d9d9;
    border-color: #d9d9d9;
}
QPushButton:pressed {
    background-color: #bfbfbf;
    border-color: #bfbfbf;
}
QPushButton:disabled {
    background-color: #1a1a1a;
    color: #555555;
    border: 1px solid #282828;
}
"""

SECONDARY_BTN_STYLE = """
QPushButton {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px solid #444444;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #282828;
    border-color: #666666;
}
QPushButton:pressed {
    background-color: #222222;
    border-color: #888888;
}
QPushButton:disabled {
    background-color: #141414;
    color: #555555;
    border: 1px solid #282828;
}
"""

ACTIVE_BTN_STYLE = """
QPushButton {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px solid #ffffff;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #282828;
    border-color: #ffffff;
}
"""

DANGER_BTN_STYLE = """
QPushButton {
    background-color: #1a0d0d;
    color: #ff5555;
    border: 1px solid #772222;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #2e1414;
    border-color: #ff5555;
    color: #ffffff;
}
QPushButton:pressed {
    background-color: #401818;
    border-color: #ff3333;
}
QPushButton:disabled {
    background-color: #141414;
    color: #555555;
    border: 1px solid #282828;
}
"""


class PulsingDot(QWidget):
    """Monochrome animated activity indicator."""
    def __init__(self, color: str = "#ffffff", size: int = 10, parent=None):
        super().__init__(parent)
        self._color = QColor(color)
        self._size = size
        self._opacity = 1.0
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._pulse)
        self._pulse_dir = -0.05
        self.setFixedSize(size + 4, size + 4)
        self._active = False

    def set_active(self, active: bool):
        self._active = active
        if active:
            self._opacity = 1.0
            self._pulse_timer.start(50)
        else:
            self._pulse_timer.stop()
            self._opacity = 0.3
        self.update()

    def set_color(self, color: str):
        self._color = QColor(color)
        self.update()

    def _pulse(self):
        self._opacity += self._pulse_dir
        if self._opacity <= 0.3:
            self._pulse_dir = 0.05
        elif self._opacity >= 1.0:
            self._pulse_dir = -0.05
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        c = QColor(self._color)
        c.setAlphaF(self._opacity if self._active else 0.3)
        painter.setBrush(c)
        painter.setPen(Qt.PenStyle.NoPen)
        x = (self.width() - self._size) // 2
        y = (self.height() - self._size) // 2
        painter.drawEllipse(x, y, self._size, self._size)
        painter.end()


class PhaseIndicator(QWidget):
    """Step indicator in pure black & white: 1. Monitor -> 2. Train -> 3. Authenticate"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(72)
        self._current_phase = 0
        self._phase_labels = ["1. Monitor", "2. Train", "3. Authenticate"]

    def set_phase(self, phase: int):
        self._current_phase = phase
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        margin = 80
        step_width = (w - 2 * margin) / 2 if w > 2 * margin else 100
        cy = 24
        radius = 14

        for i in range(3):
            cx = margin + i * step_width
            is_active = (i + 1) == self._current_phase
            is_done = (i + 1) < self._current_phase

            # Connecting lines
            if i < 2:
                line_color = QColor(255, 255, 255) if is_done else QColor(50, 50, 50)
                pen = QPen(line_color, 2)
                painter.setPen(pen)
                painter.drawLine(int(cx + radius + 4), cy, int(cx + step_width - radius - 4), cy)

            # Circle styling
            if is_done:
                painter.setBrush(QColor(30, 30, 30))
                painter.setPen(QPen(QColor(255, 255, 255), 2))
            elif is_active:
                painter.setBrush(QColor(255, 255, 255))
                painter.setPen(QPen(QColor(255, 255, 255), 2))
            else:
                painter.setBrush(QColor(18, 18, 18))
                painter.setPen(QPen(QColor(60, 60, 60), 1))

            painter.drawEllipse(int(cx - radius), int(cy - radius), radius * 2, radius * 2)

            # Circle text
            font = QFont("Segoe UI", 10, QFont.Weight.Bold)
            painter.setFont(font)
            if is_active:
                painter.setPen(QColor(0, 0, 0))
                painter.drawText(int(cx - radius), int(cy - radius), radius * 2, radius * 2, Qt.AlignmentFlag.AlignCenter, str(i + 1))
            elif is_done:
                painter.setPen(QColor(255, 255, 255))
                painter.drawText(int(cx - radius), int(cy - radius), radius * 2, radius * 2, Qt.AlignmentFlag.AlignCenter, "OK")
            else:
                painter.setPen(QColor(90, 90, 90))
                painter.drawText(int(cx - radius), int(cy - radius), radius * 2, radius * 2, Qt.AlignmentFlag.AlignCenter, str(i + 1))

            # Label below
            font_label = QFont("Segoe UI", 9, QFont.Weight.Bold if is_active else QFont.Weight.Normal)
            painter.setFont(font_label)
            label_color = QColor(255, 255, 255) if (is_active or is_done) else QColor(90, 90, 90)
            painter.setPen(label_color)
            painter.drawText(int(cx - 60), cy + 18, 120, 20, Qt.AlignmentFlag.AlignCenter, self._phase_labels[i])

        painter.end()


class DigitalDNAGUI(QMainWindow):
    tick_signal = pyqtSignal(dict)
    continuous_update_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital DNA - Behavioral Biometrics Authentication")
        self.resize(920, 720)
        self.setMinimumSize(780, 560)
        self.setStyleSheet(STYLESHEET)

        self.tray_manager = None
        self._last_notified_decision = None
        self.profile_manager = ProfileManager()
        self.current_user_id = "user_001"
        self.profile_manager.ensure_default_profile(self.current_user_id)

        self.tick_signal.connect(self._handle_engine_tick)
        self.continuous_update_signal.connect(self._handle_continuous_update)

        self.auth_engine = ContinuousAuthEngine(
            user_id=self.current_user_id,
            profile_manager=self.profile_manager,
            on_tick=lambda res: self.tick_signal.emit(res),
            on_continuous_update=lambda info: self.continuous_update_signal.emit(info),
            auto_lock_system=False
        )
        self.enrollment_manager = EnrollmentManager(
            user_id=self.current_user_id,
            profile_manager=self.profile_manager
        )

        # Monitoring state
        self._is_monitoring = False
        self._monitoring_start_time = None
        self._monitoring_windows_collected = 0
        self._monitoring_keystroke_count = 0
        self._monitoring_mouse_count = 0
        self._standalone_collector = None

        # Auth state
        self._is_authenticating = False

        self._build_ui()
        self._setup_timers()

        # Load profile data if exists
        self._load_profile_data(self.current_user_id)

    # --------------------- Tab Scroll Helper ---------------------

    def _create_scrollable_tab(self) -> tuple[QScrollArea, QVBoxLayout]:
        """Wrap tab contents in a smooth QScrollArea so elements never overlap."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        container = QWidget()
        container.setObjectName("scrollContainer")
        container.setStyleSheet("#scrollContainer { background-color: transparent; }")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(14)

        scroll.setWidget(container)
        return scroll, layout

    # --------------------- UI Build ---------------------

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        central.setStyleSheet(f"#centralWidget {{ background-color: {COLORS['bg_dark']}; }}")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(18, 14, 18, 14)
        main_layout.setSpacing(10)

        # Title row
        title_row = QHBoxLayout()
        title_row.setSpacing(10)

        title_text = QVBoxLayout()
        title_text.setSpacing(2)
        title_lbl = QLabel("DIGITAL DNA")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #ffffff; letter-spacing: 1px;")
        subtitle_lbl = QLabel("Continuous Behavioral Biometrics Authentication")
        subtitle_lbl.setFont(QFont("Segoe UI", 9))
        subtitle_lbl.setStyleSheet("color: #888888;")
        title_text.addWidget(title_lbl)
        title_text.addWidget(subtitle_lbl)

        title_row.addLayout(title_text)
        title_row.addStretch()

        # Status badge
        status_box = QFrame()
        status_box.setObjectName("statusBox")
        status_box.setStyleSheet("#statusBox { background-color: #141414; border: 1px solid #282828; border-radius: 6px; padding: 2px 10px; }")
        status_layout = QHBoxLayout(status_box)
        status_layout.setContentsMargins(8, 4, 8, 4)
        status_layout.setSpacing(8)

        self.status_dot = PulsingDot("#555555", size=10)
        self.status_text = QLabel("IDLE")
        self.status_text.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self.status_text.setStyleSheet("color: #888888;")
        status_layout.addWidget(self.status_dot)
        status_layout.addWidget(self.status_text)
        title_row.addWidget(status_box)

        main_layout.addLayout(title_row)

        # Phase indicator
        self.phase_indicator = PhaseIndicator()
        main_layout.addWidget(self.phase_indicator)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs, stretch=1)

        self.monitor_scroll, self.monitor_layout = self._create_scrollable_tab()
        self.train_scroll, self.train_layout = self._create_scrollable_tab()
        self.auth_scroll, self.auth_layout = self._create_scrollable_tab()
        self.settings_scroll, self.settings_layout = self._create_scrollable_tab()

        self.tabs.addTab(self.monitor_scroll, "1. Monitor")
        self.tabs.addTab(self.train_scroll, "2. Train")
        self.tabs.addTab(self.auth_scroll, "3. Authenticate")
        self.tabs.addTab(self.settings_scroll, "Settings")

        self._build_monitor_tab()
        self._build_train_tab()
        self._build_auth_tab()
        self._build_settings_tab()

        # Activity log docked at bottom
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        log_layout.setContentsMargins(10, 10, 10, 10)
        self.log_feed = QTextEdit()
        self.log_feed.setReadOnly(True)
        self.log_feed.setFixedHeight(85)
        self.log_feed.append("[SYSTEM] Digital DNA initialized. Ready to begin.")
        log_layout.addWidget(self.log_feed)
        main_layout.addWidget(log_group)

    def _build_monitor_tab(self):
        layout = self.monitor_layout

        # Instructions
        info_group = QGroupBox("Phase 1 - Natural Usage Recording")
        info_layout = QVBoxLayout(info_group)
        info_lbl = QLabel(
            "Start monitoring to capture your natural typing and mouse behavior.\n"
            "Use your computer normally (browse, code, type, work). The system learns your unique\n"
            "interaction rhythm without storing actual keystroke contents or sensitive text."
        )
        info_lbl.setWordWrap(True)
        info_lbl.setFont(QFont("Segoe UI", 10))
        info_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        info_layout.addWidget(info_lbl)
        layout.addWidget(info_group)

        # Profile ID
        id_group = QGroupBox("Profile Setup")
        id_layout = QHBoxLayout(id_group)
        id_lbl = QLabel("Profile Name:")
        id_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.monitor_user_input = QLineEdit("user_001")
        self.monitor_user_input.setMinimumWidth(200)
        id_layout.addWidget(id_lbl)
        id_layout.addWidget(self.monitor_user_input)
        id_layout.addStretch()
        layout.addWidget(id_group)

        # Stats
        stats_group = QGroupBox("Collection Statistics")
        stats_layout = QVBoxLayout(stats_group)
        stats_layout.setSpacing(10)

        self.monitor_time_lbl = QLabel("Recording Duration: 0:00")
        self.monitor_time_lbl.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        stats_layout.addWidget(self.monitor_time_lbl)

        stat_row = QHBoxLayout()
        self.monitor_windows_lbl = QLabel("Windows Collected: 0")
        self.monitor_keys_lbl = QLabel("Keystrokes: 0")
        self.monitor_mouse_lbl = QLabel("Mouse Events: 0")
        for lbl in [self.monitor_windows_lbl, self.monitor_keys_lbl, self.monitor_mouse_lbl]:
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
            stat_row.addWidget(lbl)
        stats_layout.addLayout(stat_row)

        self.monitor_progress = QProgressBar()
        self.monitor_progress.setRange(0, 100)
        self.monitor_progress.setValue(0)
        self.monitor_progress.setFormat(f"Target: {config.window.min_training_windows} windows - %v%")
        stats_layout.addWidget(self.monitor_progress)

        self.monitor_quality_lbl = QLabel("Quality: Waiting for data...")
        self.monitor_quality_lbl.setFont(QFont("Segoe UI", 10))
        self.monitor_quality_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        stats_layout.addWidget(self.monitor_quality_lbl)

        layout.addWidget(stats_group)

        # Controls
        ctrl_box = QHBoxLayout()
        ctrl_box.setSpacing(12)

        self.btn_start_monitor = QPushButton("Start Monitoring")
        self.btn_start_monitor.setFixedHeight(40)
        self.btn_start_monitor.setStyleSheet(PRIMARY_BTN_STYLE)
        self.btn_start_monitor.clicked.connect(self._toggle_monitoring)

        self.btn_stop_and_save = QPushButton("Stop && Save Data")
        self.btn_stop_and_save.setFixedHeight(40)
        self.btn_stop_and_save.setEnabled(False)
        self.btn_stop_and_save.setStyleSheet(SECONDARY_BTN_STYLE)
        self.btn_stop_and_save.clicked.connect(self._stop_monitoring_and_save)

        self.btn_clear_all = QPushButton("Clear All Data && Models")
        self.btn_clear_all.setFixedHeight(40)
        self.btn_clear_all.setStyleSheet(DANGER_BTN_STYLE)
        self.btn_clear_all.clicked.connect(self._confirm_and_clear_all)

        ctrl_box.addWidget(self.btn_start_monitor)
        ctrl_box.addWidget(self.btn_stop_and_save)
        ctrl_box.addWidget(self.btn_clear_all)
        layout.addLayout(ctrl_box)
        layout.addStretch()

    def _build_train_tab(self):
        layout = self.train_layout

        info_group = QGroupBox("Phase 2 - Behavioral Model Training")
        info_layout = QVBoxLayout(info_group)
        info_lbl = QLabel(
            "Train your personalized biometric model from recorded interaction data.\n"
            "The model learns your typing timing distributions and mouse trajectory features\n"
            "to authenticate you and detect impostor activity."
        )
        info_lbl.setWordWrap(True)
        info_lbl.setFont(QFont("Segoe UI", 10))
        info_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        info_layout.addWidget(info_lbl)
        layout.addWidget(info_group)

        # Profile selector
        profile_group = QGroupBox("Select Profile to Train")
        profile_layout = QHBoxLayout(profile_group)
        self.train_profile_combo = QComboBox()
        self.train_profile_combo.setMinimumWidth(180)
        self._refresh_train_profiles()
        self.train_profile_combo.currentTextChanged.connect(self._on_train_profile_changed)

        btn_load_data = QPushButton("Load Profile Data")
        btn_load_data.setFixedHeight(34)
        btn_load_data.setStyleSheet(SECONDARY_BTN_STYLE)
        btn_load_data.clicked.connect(lambda: self._load_profile_data(self.train_profile_combo.currentText()))

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFixedHeight(34)
        btn_refresh.setFixedWidth(80)
        btn_refresh.setStyleSheet(SECONDARY_BTN_STYLE)
        btn_refresh.clicked.connect(self._refresh_train_profiles)

        profile_layout.addWidget(QLabel("Profile:"))
        profile_layout.addWidget(self.train_profile_combo)
        profile_layout.addWidget(btn_load_data)
        profile_layout.addWidget(btn_refresh)
        profile_layout.addStretch()
        layout.addWidget(profile_group)

        # Data summary
        data_group = QGroupBox("Collected Data Summary")
        data_layout = QVBoxLayout(data_group)
        self.train_data_summary = QLabel("No data collected yet. Go to Phase 1 first or select a profile above.")
        self.train_data_summary.setFont(QFont("Segoe UI", 10))
        self.train_data_summary.setWordWrap(True)
        data_layout.addWidget(self.train_data_summary)
        layout.addWidget(data_group)

        # Training controls
        train_group = QGroupBox("Model Training")
        train_layout = QVBoxLayout(train_group)
        train_layout.setSpacing(10)

        self.train_progress = QProgressBar()
        self.train_progress.setRange(0, 100)
        self.train_progress.setValue(0)
        self.train_progress.setFormat("Ready to train")
        train_layout.addWidget(self.train_progress)

        self.train_status_lbl = QLabel("Status: Waiting")
        self.train_status_lbl.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.train_status_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")
        train_layout.addWidget(self.train_status_lbl)

        self.btn_train = QPushButton("Train Model")
        self.btn_train.setFixedHeight(40)
        self.btn_train.setStyleSheet(PRIMARY_BTN_STYLE)
        self.btn_train.clicked.connect(self._train_model)
        train_layout.addWidget(self.btn_train)

        layout.addWidget(train_group)
        layout.addStretch()

    def _build_auth_tab(self):
        layout = self.auth_layout

        info_group = QGroupBox("Phase 3 - Real-Time Identity Verification")
        info_layout = QVBoxLayout(info_group)
        info_lbl = QLabel(
            "Start continuous authentication to verify in real-time whether the current user matches\n"
            "the trained behavioral profile. If anomalous behavior is detected, alerts and locks trigger."
        )
        info_lbl.setWordWrap(True)
        info_lbl.setFont(QFont("Segoe UI", 10))
        info_lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
        info_layout.addWidget(info_lbl)
        layout.addWidget(info_group)

        # Profile selection
        auth_profile_group = QGroupBox("Active Profile")
        auth_profile_layout = QHBoxLayout(auth_profile_group)
        self.auth_profile_combo = QComboBox()
        self.auth_profile_combo.setMinimumWidth(180)
        self._refresh_auth_profiles()
        self.auth_profile_combo.currentTextChanged.connect(self._on_auth_profile_changed)

        btn_refresh = QPushButton("Refresh")
        btn_refresh.setFixedHeight(34)
        btn_refresh.setFixedWidth(80)
        btn_refresh.setStyleSheet(SECONDARY_BTN_STYLE)
        btn_refresh.clicked.connect(self._refresh_auth_profiles)

        auth_profile_layout.addWidget(QLabel("Verify against:"))
        auth_profile_layout.addWidget(self.auth_profile_combo)
        auth_profile_layout.addWidget(btn_refresh)
        auth_profile_layout.addStretch()
        layout.addWidget(auth_profile_group)

        # Trust score display
        score_group = QGroupBox("Continuous Trust Score")
        score_layout = QVBoxLayout(score_group)
        score_layout.setSpacing(8)

        self.score_label = QLabel("--")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setFont(QFont("Segoe UI", 42, QFont.Weight.Bold))
        self.score_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        score_layout.addWidget(self.score_label)

        self.score_bar = QProgressBar()
        self.score_bar.setRange(0, 100)
        self.score_bar.setValue(0)
        self.score_bar.setTextVisible(False)
        self.score_bar.setFixedHeight(14)
        score_layout.addWidget(self.score_bar)

        self.auth_status_label = QLabel("Status: Not Running")
        self.auth_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.auth_status_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self.auth_status_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        score_layout.addWidget(self.auth_status_label)
        layout.addWidget(score_group)

        # Modality details
        detail_group = QGroupBox("Modality Breakdown")
        detail_layout = QVBoxLayout(detail_group)
        self.k_score_lbl = QLabel("Keystroke Similarity: --")
        self.m_score_lbl = QLabel("Mouse Similarity: --")
        self.violations_lbl = QLabel("Consecutive Violations: 0")
        for lbl in [self.k_score_lbl, self.m_score_lbl, self.violations_lbl]:
            lbl.setFont(QFont("Segoe UI", 10))
            lbl.setStyleSheet(f"color: {COLORS['text_secondary']};")
            detail_layout.addWidget(lbl)
        layout.addWidget(detail_group)

        # Controls
        ctrl_box = QHBoxLayout()
        ctrl_box.setSpacing(12)

        self.btn_start_auth = QPushButton("Start Authentication")
        self.btn_start_auth.setFixedHeight(40)
        self.btn_start_auth.setStyleSheet(PRIMARY_BTN_STYLE)
        self.btn_start_auth.clicked.connect(self._toggle_auth)

        self.btn_lock_now = QPushButton("Lock Workstation")
        self.btn_lock_now.setFixedHeight(40)
        self.btn_lock_now.setStyleSheet(SECONDARY_BTN_STYLE)
        self.btn_lock_now.clicked.connect(self.auth_engine._lock_workstation)

        ctrl_box.addWidget(self.btn_start_auth)
        ctrl_box.addWidget(self.btn_lock_now)
        layout.addLayout(ctrl_box)
        layout.addStretch()

    def _build_settings_tab(self):
        layout = self.settings_layout

        gen_group = QGroupBox("General Settings")
        gen_layout = QVBoxLayout(gen_group)
        self.chk_auto_lock = QCheckBox("Automatically lock workstation when impostor detected")
        self.chk_auto_lock.toggled.connect(self._on_auto_lock_toggled)
        gen_layout.addWidget(self.chk_auto_lock)
        layout.addWidget(gen_group)

        thresh_group = QGroupBox("Authentication Thresholds")
        thresh_layout = QVBoxLayout(thresh_group)
        thresh_layout.setSpacing(10)

        allow_box = QHBoxLayout()
        allow_lbl = QLabel("Allow Threshold (score >=):")
        allow_lbl.setFont(QFont("Segoe UI", 10))
        self.spin_allow = QSpinBox()
        self.spin_allow.setRange(50, 95)
        self.spin_allow.setValue(int(config.fusion.threshold_allow))
        self.spin_allow.valueChanged.connect(self._on_threshold_changed)
        allow_box.addWidget(allow_lbl)
        allow_box.addWidget(self.spin_allow)
        allow_box.addStretch()
        thresh_layout.addLayout(allow_box)

        warn_box = QHBoxLayout()
        warn_lbl = QLabel("Warn Threshold (score >=):")
        warn_lbl.setFont(QFont("Segoe UI", 10))
        self.spin_warn = QSpinBox()
        self.spin_warn.setRange(20, 80)
        self.spin_warn.setValue(int(config.fusion.threshold_warn))
        self.spin_warn.valueChanged.connect(self._on_threshold_changed)
        warn_box.addWidget(warn_lbl)
        warn_box.addWidget(self.spin_warn)
        warn_box.addStretch()
        thresh_layout.addLayout(warn_box)

        layout.addWidget(thresh_group)

        window_group = QGroupBox("Monitoring Window Configuration")
        window_layout = QVBoxLayout(window_group)
        win_info = QLabel(
            f"Window Duration: {config.window.window_duration_seconds}s  |  "
            f"Step Duration: {config.window.step_duration_seconds}s\n"
            f"Min Keystrokes/Window: {config.window.min_keystrokes_per_window}  |  "
            f"Min Mouse Events/Window: {config.window.min_mouse_events_per_window}"
        )
        win_info.setFont(QFont("Segoe UI", 10))
        win_info.setStyleSheet(f"color: {COLORS['text_secondary']};")
        win_info.setWordWrap(True)
        window_layout.addWidget(win_info)
        layout.addWidget(window_group)

        # Danger Zone
        danger_group = QGroupBox("Danger Zone - Data & Model Reset")
        danger_layout = QVBoxLayout(danger_group)
        danger_desc = QLabel(
            "Permanently delete all recorded interaction data, session files, and trained models.\n"
            "Use this if you want to wipe the system and re-record completely from scratch."
        )
        danger_desc.setFont(QFont("Segoe UI", 10))
        danger_desc.setStyleSheet(f"color: {COLORS['text_secondary']};")
        danger_desc.setWordWrap(True)
        danger_layout.addWidget(danger_desc)

        btn_settings_clear = QPushButton("Delete All Profiles, Models && Data")
        btn_settings_clear.setFixedHeight(38)
        btn_settings_clear.setStyleSheet(DANGER_BTN_STYLE)
        btn_settings_clear.clicked.connect(self._confirm_and_clear_all)
        danger_layout.addWidget(btn_settings_clear)
        layout.addWidget(danger_group)

        layout.addStretch()

    # --------------------- Timers ---------------------

    def _setup_timers(self):
        self.monitor_timer = QTimer(self)
        self.monitor_timer.timeout.connect(self._on_monitor_tick)

        self.monitor_ui_timer = QTimer(self)
        self.monitor_ui_timer.timeout.connect(self._update_monitor_duration)

    # --------------------- Phase 1: Monitor ---------------------

    def _toggle_monitoring(self):
        if self._is_monitoring:
            self._stop_monitoring_and_save()
        else:
            self._start_monitoring()

    def _start_monitoring(self):
        user_id = self.monitor_user_input.text().strip() or "user_001"
        self.current_user_id = user_id

        self._standalone_collector = DesktopCollector(user_id=user_id)
        self._standalone_collector.start()

        self.enrollment_manager = EnrollmentManager(
            user_id=user_id,
            profile_manager=self.profile_manager
        )

        self._is_monitoring = True
        self._monitoring_start_time = time.time()
        self._monitoring_windows_collected = 0
        self._monitoring_keystroke_count = 0
        self._monitoring_mouse_count = 0

        # UI updates in black & white
        self.btn_start_monitor.setText("Monitoring Active...")
        self.btn_start_monitor.setStyleSheet(ACTIVE_BTN_STYLE)
        self.btn_stop_and_save.setEnabled(True)
        self.monitor_user_input.setEnabled(False)

        self.status_dot.set_color("#ffffff")
        self.status_dot.set_active(True)
        self.status_text.setText("RECORDING")
        self.status_text.setStyleSheet("color: #ffffff;")
        self.phase_indicator.set_phase(1)

        interval_ms = int(config.window.step_duration_seconds * 1000)
        self.monitor_timer.start(interval_ms)
        self.monitor_ui_timer.start(1000)

        self.log_feed.append(f"[MONITOR] Started recording behavioral data for '{user_id}'. Use your computer normally.")

    def _on_monitor_tick(self):
        if not self._is_monitoring or self._standalone_collector is None:
            return

        window_data = self._standalone_collector.collect_window()
        self.enrollment_manager.add_window(window_data)

        raw = window_data.get("raw_events", {})
        k_count = len(raw.get("keystroke", []))
        m_count = len(raw.get("mouse", []))
        self._monitoring_keystroke_count += k_count
        self._monitoring_mouse_count += m_count

        k_samples = len(self.enrollment_manager.keystroke_samples)
        m_samples = len(self.enrollment_manager.mouse_samples)
        self._monitoring_windows_collected = min(k_samples, m_samples)

        # Update stats
        self.monitor_windows_lbl.setText(f"Windows Collected: {self._monitoring_windows_collected} (K:{k_samples}, M:{m_samples})")
        self.monitor_keys_lbl.setText(f"Keystrokes: {self._monitoring_keystroke_count}")
        self.monitor_mouse_lbl.setText(f"Mouse Events: {self._monitoring_mouse_count}")

        target_windows = config.window.min_training_windows
        pct = min(100, int((self._monitoring_windows_collected / target_windows) * 100))
        self.monitor_progress.setValue(pct)
        if self._monitoring_windows_collected >= target_windows:
            self.monitor_progress.setFormat(f"Target Met: {self._monitoring_windows_collected}/{target_windows} windows (Ready to Train)")
            self.monitor_quality_lbl.setText("Quality: High-Accuracy Dataset Ready - Proceed to Train")
            self.monitor_quality_lbl.setStyleSheet("color: #ffffff;")
        elif self._monitoring_windows_collected >= 10:
            self.monitor_progress.setFormat(f"Good Progress: {self._monitoring_windows_collected}/{target_windows} windows")
            self.monitor_quality_lbl.setText(f"Quality: Good ({self._monitoring_windows_collected}/{target_windows}) - 30+ recommended for best accuracy")
            self.monitor_quality_lbl.setStyleSheet("color: #aaaaaa;")
        else:
            self.monitor_progress.setFormat(f"Collecting: {self._monitoring_windows_collected}/{target_windows} windows")
            self.monitor_quality_lbl.setText("Quality: Need more interaction data")
            self.monitor_quality_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")

        if k_count > 0 or m_count > 0:
            self.log_feed.append(
                f"[MONITOR] Window #{k_samples + m_samples}: {k_count} keys, {m_count} mouse events captured"
            )

    def _update_monitor_duration(self):
        if self._monitoring_start_time is None:
            return
        elapsed = int(time.time() - self._monitoring_start_time)
        mins = elapsed // 60
        secs = elapsed % 60
        self.monitor_time_lbl.setText(f"Recording Duration: {mins}:{secs:02d}")

    def _stop_monitoring_and_save(self):
        if not self._is_monitoring:
            return

        self._is_monitoring = False
        self.monitor_timer.stop()
        self.monitor_ui_timer.stop()

        if self._standalone_collector is not None:
            self._standalone_collector.stop()
            self._standalone_collector = None

        self.btn_start_monitor.setText("Start Monitoring")
        self.btn_start_monitor.setStyleSheet(PRIMARY_BTN_STYLE)
        self.btn_stop_and_save.setEnabled(False)
        self.monitor_user_input.setEnabled(True)

        self.status_dot.set_color("#555555")
        self.status_dot.set_active(False)
        self.status_text.setText("IDLE")
        self.status_text.setStyleSheet("color: #888888;")

        k_count = len(self.enrollment_manager.keystroke_samples)
        m_count = len(self.enrollment_manager.mouse_samples)

        try:
            self.enrollment_manager.save_samples()
            self.log_feed.append(f"[DATA] Saved feature samples to disk for profile '{self.enrollment_manager.user_id}'.")
        except Exception as e:
            self.log_feed.append(f"[DATA] Warning: Could not save samples: {e}")

        self.log_feed.append(
            f"[MONITOR] Stopped. Total: {k_count} keystroke windows, {m_count} mouse windows recorded."
        )

        self._refresh_train_profiles()
        self._refresh_auth_profiles()
        self._update_train_data_summary()

        target_windows = config.window.min_training_windows
        if min(k_count, m_count) >= target_windows:
            self.phase_indicator.set_phase(2)
            self.log_feed.append(f"[MONITOR] Target data collected ({min(k_count, m_count)} windows). Proceed to Phase 2: Train Model.")
            self.tabs.setCurrentIndex(1)
        elif min(k_count, m_count) >= 10:
            self.phase_indicator.set_phase(2)
            self.log_feed.append(f"[MONITOR] Sufficient data collected ({min(k_count, m_count)} windows). Proceed to Phase 2: Train Model ({target_windows}+ recommended for high accuracy).")
            self.tabs.setCurrentIndex(1)
        else:
            self.log_feed.append(f"[MONITOR] Notice: Only {min(k_count, m_count)}/{target_windows} windows recorded. For high accuracy, record {target_windows}+ windows.")

    # --------------------- Reset / Clear All ---------------------

    def _confirm_and_clear_all(self):
        reply = QMessageBox.question(
            self,
            "Confirm Delete All Data & Models",
            "Are you sure you want to delete ALL captured data, trained models, and profiles?\n\n"
            "This will permanently delete:\n"
            "  • All recorded keystroke and mouse sample files\n"
            "  • All raw session JSONL logs\n"
            "  • All trained biometric models (.joblib)\n"
            "  • Profile metadata and history\n\n"
            "You will be able to start recording and training completely from scratch.\n\n"
            "Do you want to proceed?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._execute_clear_all()

    def _execute_clear_all(self):
        import shutil

        # Stop active monitoring if running
        if self._is_monitoring:
            self._is_monitoring = False
            self.monitor_timer.stop()
            self.monitor_ui_timer.stop()
            if self._standalone_collector is not None:
                self._standalone_collector.stop()
                self._standalone_collector = None
            self.btn_start_monitor.setText("Start Monitoring")
            self.btn_start_monitor.setStyleSheet(PRIMARY_BTN_STYLE)
            self.btn_stop_and_save.setEnabled(False)
            self.monitor_user_input.setEnabled(True)

        # Stop active authentication if running
        if self._is_authenticating:
            self._is_authenticating = False
            self.auth_engine.stop()
            self.btn_start_auth.setText("Start Authentication")
            self.btn_start_auth.setStyleSheet(PRIMARY_BTN_STYLE)

        # Permanently delete all profile directories
        profiles_dir = config.paths.profiles_dir
        if profiles_dir.exists():
            for p_dir in list(profiles_dir.iterdir()):
                if p_dir.is_dir():
                    try:
                        shutil.rmtree(p_dir, ignore_errors=True)
                    except Exception as e:
                        self.log_feed.append(f"[RESET] Warning deleting {p_dir.name}: {e}")

        # Delete any files in raw and processed dirs
        for folder in [config.paths.raw_dir, config.paths.processed_dir]:
            if folder.exists():
                for item in list(folder.iterdir()):
                    try:
                        if item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                        else:
                            item.unlink(missing_ok=True)
                    except Exception:
                        pass

        # Reset EnrollmentManager in-memory data
        user_id = self.monitor_user_input.text().strip() or "user_001"
        self.enrollment_manager.reset_session(user_id)

        # Reset counters & UI elements
        self._monitoring_windows_collected = 0
        self._monitoring_keystroke_count = 0
        self._monitoring_mouse_count = 0
        self._monitoring_start_time = None

        self.monitor_time_lbl.setText("Recording Duration: 0:00")
        self.monitor_windows_lbl.setText("Windows Collected: 0")
        self.monitor_keys_lbl.setText("Keystrokes: 0")
        self.monitor_mouse_lbl.setText("Mouse Events: 0")
        self.monitor_progress.setValue(0)
        self.monitor_progress.setFormat(f"Target: {config.window.min_training_windows} windows - %v%")
        self.monitor_quality_lbl.setText("Quality: Waiting for data...")
        self.monitor_quality_lbl.setStyleSheet(f"color: {COLORS['text_muted']};")

        self.phase_indicator.set_phase(1)
        self.status_dot.set_color("#555555")
        self.status_dot.set_active(False)
        self.status_text.setText("IDLE")
        self.status_text.setStyleSheet("color: #888888;")

        # Reset Auth Engine state & GUI indicators
        self.auth_engine.keystroke_model = None
        self.auth_engine.mouse_model = None
        self.auth_engine.trust_engine.reset(50.0)
        self.auth_engine.decision_engine.reset()
        self.score_bar.setValue(50)
        self.score_label.setText("50.0")
        self.score_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.auth_status_label.setText("Status: Not Running")
        self.auth_status_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.k_score_lbl.setText("Keystroke Similarity: --")
        self.m_score_lbl.setText("Mouse Similarity: --")
        self.violations_lbl.setText("Consecutive Violations: 0")

        # Refresh dropdowns and summaries
        self._refresh_train_profiles()
        self._refresh_auth_profiles()
        self._update_train_data_summary()

        self.log_feed.append("[SYSTEM] All previous data, sessions, and trained models deleted. Ready to capture from scratch.")
        QMessageBox.information(
            self,
            "Reset Complete",
            "All previous data, models, and profiles have been successfully deleted.\n\n"
            "You can now start recording from scratch in Phase 1."
        )

    # --------------------- Phase 2: Train ---------------------

    def _refresh_train_profiles(self):
        current = self.train_profile_combo.currentText()
        self.train_profile_combo.blockSignals(True)
        self.train_profile_combo.clear()
        profiles = self.profile_manager.list_profiles()
        if not profiles:
            profiles = [self.current_user_id]
        self.train_profile_combo.addItems(profiles)
        if current and current in profiles:
            self.train_profile_combo.setCurrentText(current)
        elif self.current_user_id in profiles:
            self.train_profile_combo.setCurrentText(self.current_user_id)
        self.train_profile_combo.blockSignals(False)

    def _on_train_profile_changed(self, user_id: str):
        if not user_id:
            return
        self._load_profile_data(user_id)

    def _load_profile_data(self, user_id: str):
        if not user_id:
            return
        self.enrollment_manager = EnrollmentManager(
            user_id=user_id,
            profile_manager=self.profile_manager
        )
        loaded = self.enrollment_manager.load_samples()
        k_count = len(self.enrollment_manager.keystroke_samples)
        m_count = len(self.enrollment_manager.mouse_samples)
        if loaded:
            self.log_feed.append(f"[TRAIN] Loaded existing training data for '{user_id}' ({k_count} keys, {m_count} mouse).")
        self._update_train_data_summary()

    def _update_train_data_summary(self):
        user_id = self.enrollment_manager.user_id
        k_count = len(self.enrollment_manager.keystroke_samples)
        m_count = len(self.enrollment_manager.mouse_samples)

        p_dir = self.profile_manager.get_profile_path(user_id)
        has_models = (p_dir / "keystroke_model.joblib").exists() and (p_dir / "mouse_model.joblib").exists()

        if k_count == 0 and m_count == 0:
            status_text = f"Profile: {user_id}\nNo new data in memory."
            if has_models:
                status_text += " [Prebuilt trained models are already ready on disk!]"
                self.phase_indicator.set_phase(3)
            else:
                status_text += " Go to Phase 1 to record behavioral data or click 'Load Profile Data'."
            self.train_data_summary.setText(status_text)
            self.btn_train.setEnabled(False)
        else:
            target_min = config.window.min_training_windows
            ready = min(k_count, m_count) >= 10
            is_full = min(k_count, m_count) >= target_min
            model_info = " | Prebuilt Model: Present on disk" if has_models else " | Prebuilt Model: None"
            if is_full:
                ready_str = f"Yes - High-Accuracy Dataset Ready ({min(k_count, m_count)} windows)"
            elif ready:
                ready_str = f"Yes ({min(k_count, m_count)} windows, {target_min}+ recommended for best accuracy)"
            else:
                ready_str = f"Need more data ({min(k_count, m_count)}/10 min, {target_min} recommended)"

            self.train_data_summary.setText(
                f"Profile: {user_id}{model_info}\n"
                f"Keystroke Windows: {k_count}  |  Mouse Windows: {m_count}\n"
                f"Ready to train: {ready_str}"
            )
            self.btn_train.setEnabled(ready)

    def _train_model(self):
        self.btn_train.setEnabled(False)
        self.train_status_lbl.setText("Status: Training in progress...")
        self.train_status_lbl.setStyleSheet("color: #cccccc;")
        self.train_progress.setValue(10)
        self.log_feed.append("[TRAIN] Starting model training...")
        QApplication.processEvents()

        try:
            self.train_progress.setValue(30)
            self.train_progress.setFormat("Fitting keystroke model...")
            QApplication.processEvents()

            meta = self.enrollment_manager.train_and_save()

            self.train_progress.setValue(80)
            self.train_progress.setFormat("Saving models...")
            QApplication.processEvents()

            self.train_progress.setValue(100)
            self.train_progress.setFormat("Training complete!")
            self.train_status_lbl.setText(f"Status: Model trained successfully for '{meta['user_id']}'")
            self.train_status_lbl.setStyleSheet("color: #ffffff;")

            self._refresh_auth_profiles()
            self._refresh_train_profiles()

            self.auth_engine.user_id = meta['user_id']
            self.auth_engine.reload_models()
            self.current_user_id = meta['user_id']

            self.log_feed.append(
                f"[TRAIN] Successfully trained profile '{meta['user_id']}' "
                f"(K: {meta['keystroke_samples_count']} samples, M: {meta['mouse_samples_count']} samples)"
            )

            self.phase_indicator.set_phase(3)

            QMessageBox.information(
                self, "Training Complete",
                f"Successfully trained behavioral model for '{meta['user_id']}'!\n\n"
                f"You can now start real-time authentication in Phase 3."
            )

            self.tabs.setCurrentIndex(2)

        except Exception as e:
            self.train_status_lbl.setText(f"Status: Training failed: {str(e)}")
            self.train_status_lbl.setStyleSheet("color: #888888;")
            self.train_progress.setValue(0)
            self.train_progress.setFormat("Training failed")
            self.log_feed.append(f"[TRAIN] Error: {str(e)}")
            self.btn_train.setEnabled(True)

    # --------------------- Phase 3: Authenticate ---------------------

    def _refresh_auth_profiles(self):
        current = self.auth_profile_combo.currentText()
        self.auth_profile_combo.blockSignals(True)
        self.auth_profile_combo.clear()
        profiles = self.profile_manager.list_profiles()
        if not profiles:
            profiles = [self.current_user_id]
        self.auth_profile_combo.addItems(profiles)
        if current in profiles:
            self.auth_profile_combo.setCurrentText(current)
        elif self.current_user_id in profiles:
            self.auth_profile_combo.setCurrentText(self.current_user_id)
        self.auth_profile_combo.blockSignals(False)

    def _on_auth_profile_changed(self, new_user_id: str):
        if not new_user_id:
            return
        self.current_user_id = new_user_id
        self.auth_engine.user_id = new_user_id
        self.auth_engine.reload_models()
        self.log_feed.append(f"[AUTH] Switched verification profile to '{new_user_id}'.")

    def _toggle_auth(self):
        if self._is_authenticating:
            self._stop_auth()
        else:
            self._start_auth()

    def _start_auth(self):
        user_id = self.auth_profile_combo.currentText()
        if not user_id:
            QMessageBox.warning(self, "No Profile", "Please select or create a profile first.")
            return

        p_dir = self.profile_manager.get_profile_path(user_id)
        if not (p_dir / "keystroke_model.joblib").exists() or not (p_dir / "mouse_model.joblib").exists():
            QMessageBox.warning(
                self, "No Trained Model",
                f"No trained model found for '{user_id}'.\n"
                "Please complete Phase 1 (Monitor) and Phase 2 (Train) first."
            )
            return

        self.auth_engine.user_id = user_id
        self.auth_engine.reload_models()
        self.auth_engine.start()
        self._is_authenticating = True

        self.btn_start_auth.setText("Stop Authentication")
        self.btn_start_auth.setStyleSheet(ACTIVE_BTN_STYLE)

        self.status_dot.set_color("#ffffff")
        self.status_dot.set_active(True)
        self.status_text.setText("AUTHENTICATING")
        self.status_text.setStyleSheet("color: #ffffff;")
        self.phase_indicator.set_phase(3)

        self.log_feed.append(f"[AUTH] Real-time authentication started for '{user_id}'.")

    def _stop_auth(self):
        self.auth_engine.stop()
        self._is_authenticating = False

        self.btn_start_auth.setText("Start Authentication")
        self.btn_start_auth.setStyleSheet(PRIMARY_BTN_STYLE)

        self.status_dot.set_color("#555555")
        self.status_dot.set_active(False)
        self.status_text.setText("IDLE")
        self.status_text.setStyleSheet("color: #888888;")

        self.score_label.setText("--")
        self.score_label.setStyleSheet(f"color: {COLORS['text_muted']};")
        self.auth_status_label.setText("Status: Not Running")
        self.auth_status_label.setStyleSheet(f"color: {COLORS['text_muted']};")

        self.log_feed.append("[AUTH] Authentication stopped.")

    def _handle_engine_tick(self, result: dict):
        score = result["trust_score"]
        self.score_label.setText(f"{score:.1f}")
        self.score_bar.setValue(int(score))

        is_idle = result.get("is_idle", False)
        decision = result["decision"]

        if is_idle:
            self.score_label.setStyleSheet("color: #777777;")
            self.auth_status_label.setText("Status: IDLE - Awaiting Interaction")
            self.auth_status_label.setStyleSheet("color: #777777; font-weight: bold;")
            self.score_bar.setStyleSheet("""
                QProgressBar { border: 1px solid #282828; border-radius: 6px; height: 14px; background-color: #161616; }
                QProgressBar::chunk { border-radius: 5px; background-color: #555555; }
            """)
            self.status_dot.set_color("#555555")
        elif decision == "ALLOW":
            self.score_label.setStyleSheet("color: #ffffff;")
            self.auth_status_label.setText("Status: AUTHENTICATED - User Verified")
            self.auth_status_label.setStyleSheet("color: #ffffff; font-weight: bold;")
            self.score_bar.setStyleSheet("""
                QProgressBar { border: 1px solid #282828; border-radius: 6px; height: 14px; background-color: #161616; }
                QProgressBar::chunk { border-radius: 5px; background-color: #ffffff; }
            """)
            self.status_dot.set_color("#ffffff")
        elif decision == "WARN":
            self.score_label.setStyleSheet("color: #cccccc;")
            self.auth_status_label.setText("Status: WARNING - Suspicious Behavior")
            self.auth_status_label.setStyleSheet("color: #cccccc; font-weight: bold;")
            self.score_bar.setStyleSheet("""
                QProgressBar { border: 1px solid #282828; border-radius: 6px; height: 14px; background-color: #161616; }
                QProgressBar::chunk { border-radius: 5px; background-color: #999999; }
            """)
            self.status_dot.set_color("#aaaaaa")
            if self.tray_manager and self._last_notified_decision != "WARN":
                self.tray_manager.notify("Digital DNA Warning", "Suspicious behavior detected.", is_warning=True)
                self._last_notified_decision = "WARN"
        else:  # LOCK
            self.score_label.setStyleSheet("color: #ffffff;")
            self.auth_status_label.setText("Status: ALERT - IMPOSTOR DETECTED [SYSTEM LOCKED]")
            self.auth_status_label.setStyleSheet("color: #ffffff; background-color: #222222; border: 1px solid #ffffff; padding: 4px; border-radius: 4px; font-weight: bold;")
            self.score_bar.setStyleSheet("""
                QProgressBar { border: 1px solid #282828; border-radius: 6px; height: 14px; background-color: #161616; }
                QProgressBar::chunk { border-radius: 5px; background-color: #ffffff; }
            """)
            self.status_dot.set_color("#ffffff")
            if self.tray_manager and self._last_notified_decision != "LOCK":
                self.tray_manager.notify("Digital DNA Alert", "Impostor detected! System locking.", is_warning=True)
                self._last_notified_decision = "LOCK"

        if decision == "ALLOW":
            self._last_notified_decision = None

        k_s = result["modality_scores"]["keystroke"]
        m_s = result["modality_scores"]["mouse"]
        self.k_score_lbl.setText(f"Keystroke Similarity: {k_s:.2f}" if k_s is not None else "Keystroke: Idle")
        self.m_score_lbl.setText(f"Mouse Similarity: {m_s:.2f}" if m_s is not None else "Mouse: Idle")
        self.violations_lbl.setText(f"Consecutive Violations: {result['consecutive_violations']}")

        t_str = time.strftime("%H:%M:%S")
        if is_idle:
            self.log_feed.append(f"[{t_str}] AUTH: IDLE (Trust={score:.1f})")
        else:
            k_disp = f"{k_s:.2f}" if k_s is not None else "--"
            m_disp = f"{m_s:.2f}" if m_s is not None else "--"
            self.log_feed.append(f"[{t_str}] AUTH: Key={k_disp}, Mouse={m_disp} | Trust={score:.1f} ({decision})")

    def _handle_continuous_update(self, info: dict):
        v = info.get("version", 2)
        samples = info.get("total_samples", 0)
        t_str = time.strftime("%H:%M:%S")
        self.log_feed.append(f"[{t_str}] [CONTINUOUS LEARNING] Model automatically retrained to v{v} with {samples} confirmed genuine samples. Profile improved!")

    # --------------------- Settings ---------------------

    def _on_auto_lock_toggled(self, checked: bool):
        self.auth_engine.auto_lock_system = checked
        self.log_feed.append(f"[CONFIG] Auto-lock {'enabled' if checked else 'disabled'}.")

    def _on_threshold_changed(self):
        self.auth_engine.decision_engine.threshold_allow = float(self.spin_allow.value())
        self.auth_engine.decision_engine.threshold_warn = float(self.spin_warn.value())

    # --------------------- Cleanup ---------------------

    def closeEvent(self, event):
        self.auth_engine.stop()
        if self._standalone_collector is not None:
            self._standalone_collector.stop()
        self.monitor_timer.stop()
        self.monitor_ui_timer.stop()
        event.accept()


def launch():
    app = QApplication(sys.argv)
    window = DigitalDNAGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    launch()
