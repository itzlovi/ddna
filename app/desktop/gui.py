import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QProgressBar, QTabWidget, QLineEdit,
    QCheckBox, QSpinBox, QMessageBox, QGroupBox
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont, QColor
from core.profile_manager import ProfileManager
from core.enrollment import EnrollmentManager
from core.auth_engine import ContinuousAuthEngine
from core.config import config

class DigitalDNAGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Digital DNA - Continuous Behavioral Biometrics")
        self.resize(720, 560)

        self.profile_manager = ProfileManager()
        self.current_user_id = "user_001"
        self.auth_engine: ContinuousAuthEngine = ContinuousAuthEngine(
            user_id=self.current_user_id,
            profile_manager=self.profile_manager,
            on_tick=self._handle_engine_tick,
            auto_lock_system=False
        )
        self.enrollment_manager: EnrollmentManager = EnrollmentManager(
            user_id=self.current_user_id,
            profile_manager=self.profile_manager
        )
        self.is_enrolling = False

        self._build_ui()
        self._setup_timer()

    def _build_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.dashboard_tab = QWidget()
        self.enrollment_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.enrollment_tab, "Enrollment")
        self.tabs.addTab(self.settings_tab, "Settings")

        self._build_dashboard_tab()
        self._build_enrollment_tab()
        self._build_settings_tab()

    def _build_dashboard_tab(self):
        layout = QVBoxLayout(self.dashboard_tab)

        user_box = QHBoxLayout()
        user_lbl = QLabel("Active User Profile:")
        user_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.user_display = QLabel(self.current_user_id)
        self.user_display.setFont(QFont("Arial", 11))
        user_box.addWidget(user_lbl)
        user_box.addWidget(self.user_display)
        user_box.addStretch()
        layout.addLayout(user_box)

        gauge_group = QGroupBox("Behavioral Trust Score")
        gauge_layout = QVBoxLayout(gauge_group)

        self.score_label = QLabel("85.0")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setFont(QFont("Arial", 42, QFont.Weight.Bold))
        self.score_label.setStyleSheet("color: #27ae60;")
        gauge_layout.addWidget(self.score_label)

        self.score_bar = QProgressBar()
        self.score_bar.setRange(0, 100)
        self.score_bar.setValue(85)
        self.score_bar.setTextVisible(False)
        self.score_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                height: 24px;
                background-color: #ecf0f1;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                border-radius: 6px;
            }
        """)
        gauge_layout.addWidget(self.score_bar)

        self.status_label = QLabel("Status: AUTHENTICATED (ALLOW)")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 13, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #2c3e50;")
        gauge_layout.addWidget(self.status_label)

        layout.addWidget(gauge_group)

        details_group = QGroupBox("Modality Telemetry")
        details_layout = QVBoxLayout(details_group)
        self.k_score_lbl = QLabel("Keystroke Similarity: --")
        self.m_score_lbl = QLabel("Mouse Dynamics Similarity: --")
        self.violations_lbl = QLabel("Consecutive Low-Confidence Windows: 0")
        details_layout.addWidget(self.k_score_lbl)
        details_layout.addWidget(self.m_score_lbl)
        details_layout.addWidget(self.violations_lbl)
        layout.addWidget(details_group)

        ctrl_box = QHBoxLayout()
        self.btn_toggle_monitoring = QPushButton("Start Continuous Monitoring")
        self.btn_toggle_monitoring.setFixedHeight(38)
        self.btn_toggle_monitoring.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_toggle_monitoring.clicked.connect(self._toggle_monitoring)

        self.btn_lock_now = QPushButton("Lock Workstation Now")
        self.btn_lock_now.setFixedHeight(38)
        self.btn_lock_now.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold; border-radius: 4px;")
        self.btn_lock_now.clicked.connect(self.auth_engine._lock_workstation)

        ctrl_box.addWidget(self.btn_toggle_monitoring)
        ctrl_box.addWidget(self.btn_lock_now)
        layout.addLayout(ctrl_box)

    def _build_enrollment_tab(self):
        layout = QVBoxLayout(self.enrollment_tab)

        info_lbl = QLabel("Type naturally in the box below and move your mouse to build your baseline behavioral biometric model.")
        info_lbl.setWordWrap(True)
        layout.addWidget(info_lbl)

        id_box = QHBoxLayout()
        id_lbl = QLabel("Enroll as User ID:")
        self.enroll_user_input = QLineEdit(self.current_user_id)
        id_box.addWidget(id_lbl)
        id_box.addWidget(self.enroll_user_input)
        layout.addLayout(id_box)

        self.enroll_prompt_input = QLineEdit()
        self.enroll_prompt_input.setPlaceholderText("Type sentences here (e.g. 'The quick brown fox jumps over the lazy dog')...")
        self.enroll_prompt_input.setFixedHeight(50)
        layout.addWidget(self.enroll_prompt_input)

        self.enroll_progress_bar = QProgressBar()
        self.enroll_progress_bar.setRange(0, 10)
        self.enroll_progress_bar.setValue(0)
        layout.addWidget(self.enroll_progress_bar)

        self.enroll_status_lbl = QLabel("Samples collected: 0 / 10")
        layout.addWidget(self.enroll_status_lbl)

        btn_box = QHBoxLayout()
        self.btn_start_enroll = QPushButton("Start Enrollment Capture")
        self.btn_start_enroll.setFixedHeight(38)
        self.btn_start_enroll.clicked.connect(self._start_enrollment)

        self.btn_finish_enroll = QPushButton("Train & Save Models")
        self.btn_finish_enroll.setFixedHeight(38)
        self.btn_finish_enroll.clicked.connect(self._finish_enrollment)
        self.btn_finish_enroll.setEnabled(False)

        btn_box.addWidget(self.btn_start_enroll)
        btn_box.addWidget(self.btn_finish_enroll)
        layout.addLayout(btn_box)
        layout.addStretch()

    def _build_settings_tab(self):
        layout = QVBoxLayout(self.settings_tab)

        self.chk_auto_lock = QCheckBox("Automatically lock workstation when score drops below threshold")
        self.chk_auto_lock.toggled.connect(self._on_auto_lock_toggled)
        layout.addWidget(self.chk_auto_lock)

        allow_box = QHBoxLayout()
        allow_lbl = QLabel("Allow Threshold (Score >= ):")
        self.spin_allow = QSpinBox()
        self.spin_allow.setRange(50, 95)
        self.spin_allow.setValue(int(config.fusion.threshold_allow))
        self.spin_allow.valueChanged.connect(self._on_threshold_changed)
        allow_box.addWidget(allow_lbl)
        allow_box.addWidget(self.spin_allow)
        layout.addLayout(allow_box)

        warn_box = QHBoxLayout()
        warn_lbl = QLabel("Warn Threshold (Score >= ):")
        self.spin_warn = QSpinBox()
        self.spin_warn.setRange(20, 80)
        self.spin_warn.setValue(int(config.fusion.threshold_warn))
        self.spin_warn.valueChanged.connect(self._on_threshold_changed)
        warn_box.addWidget(warn_lbl)
        warn_box.addWidget(self.spin_warn)
        layout.addLayout(warn_box)

        layout.addStretch()

    def _setup_timer(self):
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self._on_enrollment_tick)
        self.ui_timer.start(1000)

    def _toggle_monitoring(self):
        if self.auth_engine._running:
            self.auth_engine.stop()
            self.btn_toggle_monitoring.setText("Start Continuous Monitoring")
            self.btn_toggle_monitoring.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; border-radius: 4px;")
        else:
            self.current_user_id = self.enroll_user_input.text().strip() or "user_001"
            self.user_display.setText(self.current_user_id)
            self.auth_engine.user_id = self.current_user_id
            self.auth_engine.reload_models()
            self.auth_engine.start()
            self.btn_toggle_monitoring.setText("Stop Continuous Monitoring")
            self.btn_toggle_monitoring.setStyleSheet("background-color: #e67e22; color: white; font-weight: bold; border-radius: 4px;")

    def _handle_engine_tick(self, result: dict):
        score = result["trust_score"]
        self.score_label.setText(f"{score:.1f}")
        self.score_bar.setValue(int(score))

        decision = result["decision"]
        if decision == "ALLOW":
            self.score_label.setStyleSheet("color: #27ae60;")
            self.status_label.setText("Status: AUTHENTICATED (ALLOW)")
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        elif decision == "WARN":
            self.score_label.setStyleSheet("color: #f39c12;")
            self.status_label.setText("Status: SUSPICIOUS BEHAVIOR (WARN)")
            self.status_label.setStyleSheet("color: #f39c12; font-weight: bold;")
        else:
            self.score_label.setStyleSheet("color: #c0392b;")
            self.status_label.setText("Status: IMPOSTOR DETECTED (LOCK)")
            self.status_label.setStyleSheet("color: #c0392b; font-weight: bold;")

        k_s = result["modality_scores"]["keystroke"]
        m_s = result["modality_scores"]["mouse"]
        self.k_score_lbl.setText(f"Keystroke Similarity: {k_s:.2f}" if k_s is not None else "Keystroke Similarity: Idle")
        self.m_score_lbl.setText(f"Mouse Dynamics Similarity: {m_s:.2f}" if m_s is not None else "Mouse Dynamics Similarity: Idle")
        self.violations_lbl.setText(f"Consecutive Low-Confidence Windows: {result['consecutive_violations']}")

    def _start_enrollment(self):
        uid = self.enroll_user_input.text().strip() or "user_001"
        self.enrollment_manager = EnrollmentManager(user_id=uid, profile_manager=self.profile_manager)
        self.auth_engine.collector.start()
        self.is_enrolling = True
        self.btn_start_enroll.setEnabled(False)
        self.enroll_prompt_input.setFocus()

    def _on_enrollment_tick(self):
        if not self.is_enrolling:
            return
        window_data = self.auth_engine.collector.collect_window()
        self.enrollment_manager.add_window(window_data)
        count = min(len(self.enrollment_manager.keystroke_samples), len(self.enrollment_manager.mouse_samples))
        self.enroll_progress_bar.setValue(min(10, count))
        self.enroll_status_lbl.setText(f"Samples collected: {count} / 10")
        if count >= 5:
            self.btn_finish_enroll.setEnabled(True)

    def _finish_enrollment(self):
        self.is_enrolling = False
        self.auth_engine.collector.stop()
        meta = self.enrollment_manager.train_and_save()
        self.btn_start_enroll.setEnabled(True)
        self.btn_finish_enroll.setEnabled(False)
        QMessageBox.information(self, "Enrollment Complete", f"Successfully trained and saved profile for {meta['user_id']}!")
        self.auth_engine.reload_models()

    def _on_auto_lock_toggled(self, checked: bool):
        self.auth_engine.auto_lock_system = checked

    def _on_threshold_changed(self):
        self.auth_engine.decision_engine.threshold_allow = float(self.spin_allow.value())
        self.auth_engine.decision_engine.threshold_warn = float(self.spin_warn.value())

    def closeEvent(self, event):
        self.auth_engine.stop()
        event.accept()

def launch():
    app = QApplication(sys.argv)
    window = DigitalDNAGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    launch()
