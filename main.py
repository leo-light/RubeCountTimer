import sys
import json
import os
from pynput import keyboard

def get_bundle_dir():
    return getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

def get_external_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QSlider, QProgressBar, 
                             QFrame, QSpacerItem, QSizePolicy, QDialog, QFormLayout, QGridLayout, 
                             QLineEdit, QDoubleSpinBox, QDialogButtonBox, QMessageBox, QCheckBox,
                             QTabWidget, QGroupBox, QMenu, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QCursor, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

TRANSLATIONS = {
    "en": {
        "window_title": "Rube Countdown Timer ver1.6",
        "presets_group": "Presets (Normal Countdowns)",
        "circlec_group": "CircleC Settings",
        "global_group": "START Button Settings",
        "language_group": "Language Settings",
        "preset_name_label": "Preset {} Name:",
        "loop_time": "Loop Time (s):",
        "first_time": "First Time (s):",
        "hotkey": "Hotkey:",
        "start_hotkey": "START Hotkey:",
        "enable_start": "Enable START Hotkey",
        "enable_circlec": "Enable CircleC Hotkey",
        "language_label": "Select Language:",
        "start_btn": "START",
        "stop_btn": "STOP",
        "circlec_btn": "CircleC",
        "latency_label": "Latency Adjust",
        "volume_label": "Volume",
        "settings": "Settings",
        "running": "RUNNING",
        "press_any_key": "Press any key...",
        "edit_preset_title": "Edit Preset",
        "edit_hotkey_title": "Edit START Hotkey",
        "label_label": "Label:",
        "current_hotkey_label": "Current Hotkey:",
        "enable_global_shortcut": "Enable Global Shortcut",
        "loop_a": "Loop A (s):",
        "loop_b": "Loop B (s):",
        "start_yellow": "Loop Time (Yellow):",
        "start_rainbow": "Loop Time (Rainbow):",
        "circlec_slow": "Slow Floor:",
        "circlec_fast": "Fast Floor:",
        "circled_ab": "Label 3 CircleD (A/B):",
        "start_ab": "Label 3 START (A/B):",
        "ok": "OK",
        "cancel": "Cancel"
    },
    "ja": {
        "window_title": "ルベカウントタイマー ver1.6",
        "presets_group": "プリセット設定 (通常カウントダウン)",
        "circlec_group": "サークルC設定",
        "global_group": "STARTボタンの設定",
        "language_group": "言語設定",
        "preset_name_label": "プリセット {} 名前:",
        "loop_time": "ループ時間 (秒):",
        "first_time": "初回時間 (秒):",
        "hotkey": "ホットキー:",
        "start_hotkey": "開始ホットキー:",
        "enable_start": "STARTホットキーを有効にする",
        "enable_circlec": "CircleCホットキーを有効にする",
        "language_label": "言語を選択:",
        "start_btn": "スタート",
        "stop_btn": "ストップ",
        "circlec_btn": "サークルC",
        "latency_label": "タイム補正",
        "volume_label": "音量",
        "settings": "設定",
        "running": "計測中",
        "press_any_key": "キーを押してください...",
        "edit_preset_title": "プリセット編集",
        "edit_hotkey_title": "開始ホットキー編集",
        "label_label": "ラベル:",
        "current_hotkey_label": "現在のホットキー:",
        "enable_global_shortcut": "グローバルホットキーを有効にする",
        "loop_a": "ループ A (秒):",
        "loop_b": "ループ B (秒):",
        "start_yellow": "ループ時間(黄色):",
        "start_rainbow": "ループ時間(虹):",
        "circlec_slow": "遅い床(秒):",
        "circlec_fast": "早い床(秒):",
        "first_time_input": "初回設定時間(秒):",
        "loop_time_input": "ループ時間(秒):",
        "circled_ab": "ラベル3 サークルD A/B:",
        "start_ab": "ラベル3 スタート A/B:",
        "ok": "保存",
        "cancel": "キャンセル"
    }
}

class KeyCaptureButton(QPushButton):
    keyChanged = pyqtSignal(str)

    def __init__(self, current_key, parent_dialog=None):
        super().__init__(str(current_key).upper())
        self.parent_dialog = parent_dialog
        self.key_name = str(current_key).lower()
        self.listener = None
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self.start_capture)
        
        # Style will be handled by parent dialog or globally
        self.setProperty("active", "false")

    def start_capture(self):
        # Update text to "Press any key..." using translation from parent dialog if available
        msg = "Press any key..."
        if self.parent_dialog and hasattr(self.parent_dialog, "tr"):
            msg = self.parent_dialog.tr("press_any_key")
            
        self.setText(msg)
        self.setProperty("active", "true")
        self.style().unpolish(self)
        self.style().polish(self)
        
        if self.listener is not None:
            self.listener.stop()
            
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
    def on_press(self, key):
        try:
            key_name = key.char
        except AttributeError:
            key_name = key.name
            
        self.key_name = str(key_name).lower()
        QTimer.singleShot(0, self.finish_capture)
        return False # Stop listener
        
    def finish_capture(self):
        self.setText(self.key_name.upper())
        self.setProperty("active", "false")
        self.style().unpolish(self)
        self.style().polish(self)
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
        self.keyChanged.emit(self.key_name)

    def stop_listener(self):
        if self.listener is not None:
            self.listener.stop()
            self.listener = None

class PresetEditDialog(QDialog):
    def __init__(self, current_label, current_time, current_first_time, index, parent=None):
        super().__init__(parent)
        self.preset_index = index
        self.app_ref = None
        # Try to find the app reference for language
        p = parent
        while p:
            if hasattr(p, 'language'):
                self.app_ref = p
                break
            p = p.parent()
            
        self.setWindowTitle(self.tr("edit_preset_title"))
        self.setFixedSize(300, 190)
        
        self.setStyleSheet("""
            QDialog { background-color: #22252a; color: white; }
            QLabel { color: white; }
            QLineEdit { 
                background-color: #111317; 
                color: white; 
                border: 1px solid #3ca4ff; 
                padding: 5px; 
            }
            QDoubleSpinBox { 
                background-color: #111317; 
                color: white; 
                border: 1px solid #3ca4ff; 
            }
            QDoubleSpinBox::up-button {
                width: 20px;
            }
            QDoubleSpinBox::down-button {
                width: 20px;
            }
            QPushButton {
                background-color: #2b2e35;
                color: white;
                border: 1px solid #3c4049;
                padding: 5px 15px;
            }
            QPushButton:hover { background-color: #353a42; }
        """)
        
        layout = QFormLayout(self)
        self.label_edit = QLineEdit(current_label)
        self.time_edit = QDoubleSpinBox()
        self.time_edit.setDecimals(2)
        self.time_edit.setMaximum(9999.99)
        self.time_edit.setSingleStep(1.0)
        self.time_edit.setValue(current_time)
        
        self.first_time_edit = QDoubleSpinBox()
        self.first_time_edit.setDecimals(2)
        self.first_time_edit.setMaximum(9999.99)
        self.first_time_edit.setSingleStep(1.0)
        self.first_time_edit.setValue(current_first_time)
        
        layout.addRow(self.tr("label_label"), self.label_edit)
        if self.preset_index != 2:
            layout.addRow(self.tr("loop_time"), self.time_edit)
        layout.addRow(self.tr("first_time"), self.first_time_edit)
        
        # New: Label 3 phasing in individual edit dialog
        if self.preset_index == 2:
            self.setFixedSize(300, 240) # Smaller height since floors are removed
            
            self.st_a_edit = QDoubleSpinBox()
            self.st_a_edit.setDecimals(2)
            self.st_a_edit.setValue(parent.label3_start_phases[0])
            self.st_b_edit = QDoubleSpinBox()
            self.st_b_edit.setDecimals(2)
            self.st_b_edit.setValue(parent.label3_start_phases[1])
            
            layout.addRow(self.tr("start_yellow"), self.st_a_edit)
            layout.addRow(self.tr("start_rainbow"), self.st_b_edit)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def tr(self, key):
        lang = "en"
        if self.app_ref:
            lang = self.app_ref.language
        return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)


class HotkeyEditDialog(QDialog):
    def __init__(self, current_hotkey, current_enabled, parent=None):
        super().__init__(parent)
        self.app_ref = None
        # Try to find the app reference for language
        p = parent
        while p:
            if hasattr(p, 'language'):
                self.app_ref = p
                break
            p = p.parent()

        self.setWindowTitle(self.tr("edit_hotkey_title"))
        self.setFixedSize(300, 180)
        self.new_hotkey = current_hotkey
        self.new_enabled = current_enabled
        
        self.setStyleSheet("""
            QDialog { background-color: #22252a; color: white; }
            QLabel { color: white; font-size: 14px; }
            QPushButton {
                background-color: #2b2e35;
                color: #3ca4ff;
                border: 2px solid #3c4049;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #353a42; }
            QPushButton[active="true"] {
                border-color: #ffaa00;
                color: #ffaa00;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        self.info_label = QLabel(self.tr("current_hotkey_label"))
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        self.capture_btn = KeyCaptureButton(self.new_hotkey, parent_dialog=self)
        self.capture_btn.keyChanged.connect(self.on_key_changed)
        layout.addWidget(self.capture_btn)
        
        self.enable_chk = QCheckBox(self.tr("enable_global_shortcut"))
        self.enable_chk.setChecked(self.new_enabled)
        layout.addWidget(self.enable_chk)
        
        # Optional fields for time editing (used by CircleC)
        self.has_time_edit = False
        self.time_edit_loop = None
        self.time_edit_first = None
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
    def add_time_editors(self, loop_val, first_val):
        self.has_time_edit = True
        self.setFixedSize(300, 260) # Make dialog taller to fit the inputs
        
        self.setStyleSheet(self.styleSheet() + """
            QDoubleSpinBox { 
                background-color: #111317; 
                color: white; 
                border: 1px solid #3ca4ff; 
            }
            QDoubleSpinBox::up-button { width: 20px; }
            QDoubleSpinBox::down-button { width: 20px; }
        """)
        
        # Insert them right before the buttons
        form_layout = QFormLayout()
        
        self.time_edit_loop = QDoubleSpinBox()
        self.time_edit_loop.setDecimals(2)
        self.time_edit_loop.setMaximum(9999.99)
        self.time_edit_loop.setSingleStep(1.0)
        self.time_edit_loop.setValue(loop_val)
        form_layout.addRow(self.tr("loop_time"), self.time_edit_loop)
        
        self.time_edit_first = QDoubleSpinBox()
        self.time_edit_first.setDecimals(2)
        self.time_edit_first.setMaximum(9999.99)
        self.time_edit_first.setSingleStep(1.0)
        self.time_edit_first.setValue(first_val)
        form_layout.addRow(self.tr("first_time"), self.time_edit_first)
        
        # Add the form layout before the enable_chk and button box
        layout = self.layout()
        layout.insertLayout(3, form_layout)
        
    def on_key_changed(self, new_key):
        self.new_hotkey = new_key

    def tr(self, key):
        lang = "en"
        if self.app_ref:
            lang = self.app_ref.language
        return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, key)
            
    def closeEvent(self, event):
        self.capture_btn.stop_listener()
        super().closeEvent(event)

class CircleCSettingsDialog(QDialog):
    def __init__(self, parent_app, parent=None):
        super().__init__(parent)
        self.app_ref = parent_app
        self.setWindowTitle(self.tr("circlec_group"))
        self.setFixedWidth(450)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # 1. Timings Group
        time_group = QGroupBox(self.tr("circlec_group"))
        time_form = QFormLayout(time_group)
        time_form.setSpacing(15)
        time_form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        def create_sb(val):
            sb = QDoubleSpinBox()
            sb.setDecimals(2)
            sb.setRange(0, 9999.99)
            sb.setFixedWidth(120)
            sb.setValue(val)
            return sb

        if self.app_ref.current_preset_index == 2:
            # Label 3: Slow/Fast Floor
            self.p3_cd_a = create_sb(self.app_ref.label3_circled_phases[0])
            self.p3_cd_b = create_sb(self.app_ref.label3_circled_phases[1])
            self.circlec_first = create_sb(self.app_ref.circlec_first_time)
            
            time_form.addRow(self.tr("circlec_slow"), self.p3_cd_a)
            time_form.addRow(self.tr("circlec_fast"), self.p3_cd_b)
            # Add a small spacer
            time_form.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
            time_form.addRow(self.tr("first_time_input"), self.circlec_first)
        else:
            # Regular CircleC
            self.cc_loop = create_sb(self.app_ref.circlec_loop_time)
            self.cc_first = create_sb(self.app_ref.circlec_first_time)
            
            time_form.addRow(self.tr("loop_time_input"), self.cc_loop)
            time_form.addRow(self.tr("first_time_input"), self.cc_first)
            
        layout.addWidget(time_group)
        
        # 2. Hotkey Group
        hk_group = QGroupBox(self.tr("global_group"))
        hk_form = QFormLayout(hk_group)
        hk_form.setSpacing(15)
        
        self.hk_btn = KeyCaptureButton(self.app_ref.circlec_hotkey, parent_dialog=self)
        self.hk_chk = QCheckBox(self.tr("enable_circlec"))
        self.hk_chk.setChecked(self.app_ref.circlec_hotkey_enabled)
        
        hk_form.addRow(self.tr("hotkey"), self.hk_btn)
        hk_form.addRow("", self.hk_chk)
        layout.addWidget(hk_group)
        
        # Buttons
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.button(QDialogButtonBox.StandardButton.Ok).setText(self.tr("ok"))
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText(self.tr("cancel"))
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def tr(self, key):
        return TRANSLATIONS.get(self.app_ref.language, TRANSLATIONS["en"]).get(key, key)
    
    def get_data(self):
        data = {
            "hotkey": self.hk_btn.key_name,
            "enabled": self.hk_chk.isChecked()
        }
        if self.app_ref.current_preset_index == 2:
            data["label3_circled_phases"] = [self.p3_cd_a.value(), self.p3_cd_b.value()]
            data["circlec_first_time"] = self.circlec_first.value()
        else:
            data["circlec_loop_time"] = self.cc_loop.value()
            data["circlec_first_time"] = self.cc_first.value()
        return data

class GlobalSettingsDialog(QDialog):
    def __init__(self, parent_app, parent=None):
        super().__init__(parent)
        self.app_ref = parent_app
        self.setWindowTitle("Global Settings")
        self.setFixedSize(850, 880)
        
        self.setStyleSheet("""
            QDialog { background-color: #22252a; color: white; }
            QGroupBox { 
                font-weight: bold; 
                border: 1px solid #3ca4ff; 
                border-radius: 5px; 
                margin-top: 10px;
                padding-top: 15px; 
            }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 5px; color: #3ca4ff; }
            QLabel { color: white; font-size: 13px; }
            QLineEdit, QDoubleSpinBox { 
                background-color: #111317; 
                color: white; 
                border: 1px solid #3c4049; 
                padding: 4px; 
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button { width: 16px; }
            QPushButton {
                background-color: #2b2e35;
                color: white;
                border: 1px solid #3c4049;
                padding: 6px 15px;
            }
            QPushButton:hover { background-color: #353a42; border-color: #3ca4ff; }
        """)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(25)
        
        # 1. Presets Settings
        preset_group = QGroupBox(self.tr("presets_group"))
        preset_vbox = QVBoxLayout(preset_group)
        preset_vbox.setSpacing(25) 
        
        self.preset_inputs = []
        for i, preset in enumerate(self.app_ref.presets):
            preset_block = QWidget()
            # Use QGridLayout for the entire block for maximum control
            block_grid = QGridLayout(preset_block)
            block_grid.setContentsMargins(15, 0, 15, 0)
            block_grid.setSpacing(10)
            
            # Row 0: Preset Name Label and LineEdit
            name_label = QLabel(self.tr("preset_name_label").format(i+1))
            name_label.setMinimumWidth(120)
            le_label = QLineEdit(preset['label'])
            le_label.setMinimumWidth(250)
            
            block_grid.addWidget(name_label, 0, 0, Qt.AlignmentFlag.AlignRight)
            block_grid.addWidget(le_label, 0, 1, 1, 3) # Span across
            
            def create_sb(val):
                sb = QDoubleSpinBox()
                sb.setDecimals(2)
                sb.setRange(0, 9999.99)
                sb.setFixedWidth(120)
                sb.setValue(val)
                return sb

            sb_loop = create_sb(float(preset['time']))
            sb_first = create_sb(float(preset.get('first_time', 5.00)))
            
            if i == 2:
                # Label 3: START timings (Yellow/Rainbow/First)
                self.p3_st_a = create_sb(self.app_ref.label3_start_phases[0])
                self.p3_st_b = create_sb(self.app_ref.label3_start_phases[1])
                
                # Row 1: Yellow Loop and Rainbow Loop
                block_grid.addWidget(QLabel(self.tr("start_yellow")), 1, 0, Qt.AlignmentFlag.AlignRight)
                block_grid.addWidget(self.p3_st_a, 1, 1)
                block_grid.addWidget(QLabel(self.tr("start_rainbow")), 1, 2, Qt.AlignmentFlag.AlignRight)
                block_grid.addWidget(self.p3_st_b, 1, 3)
                
                # Row 2: First Time
                block_grid.addWidget(QLabel(self.tr("first_time_input")), 2, 0, Qt.AlignmentFlag.AlignRight)
                block_grid.addWidget(sb_first, 2, 1)
            else:
                # Row 1: Loop Time and First Time
                block_grid.addWidget(QLabel(self.tr("loop_time_input")), 1, 0, Qt.AlignmentFlag.AlignRight)
                block_grid.addWidget(sb_loop, 1, 1)
                block_grid.addWidget(QLabel(self.tr("first_time_input")), 1, 2, Qt.AlignmentFlag.AlignRight)
                block_grid.addWidget(sb_first, 1, 3)
                
            preset_vbox.addWidget(preset_block)
            self.preset_inputs.append({'label': le_label, 'time': sb_loop, 'first_time': sb_first})
            
        main_layout.addWidget(preset_group)
        
        circlec_group = QGroupBox(self.tr("circlec_group"))
        circlec_grid = QGridLayout(circlec_group)
        circlec_grid.setContentsMargins(20, 15, 20, 15)
        circlec_grid.setSpacing(15)
        
        # Row 0: Loop and First Time
        self.circlec_loop_input = create_sb(self.app_ref.circlec_loop_time)
        self.circlec_first_input = create_sb(self.app_ref.circlec_first_time)
        
        circlec_grid.addWidget(QLabel(self.tr("loop_time_input")), 0, 0, Qt.AlignmentFlag.AlignRight)
        circlec_grid.addWidget(self.circlec_loop_input, 0, 1)
        circlec_grid.addWidget(QLabel(self.tr("first_time_input")), 0, 2, Qt.AlignmentFlag.AlignRight)
        circlec_grid.addWidget(self.circlec_first_input, 0, 3)
        
        # Row 1: Slow and Fast Floor
        self.p3_cd_a = create_sb(self.app_ref.label3_circled_phases[0])
        self.p3_cd_b = create_sb(self.app_ref.label3_circled_phases[1])
        
        circlec_grid.addWidget(QLabel(self.tr("circlec_slow")), 1, 0, Qt.AlignmentFlag.AlignRight)
        circlec_grid.addWidget(self.p3_cd_a, 1, 1)
        circlec_grid.addWidget(QLabel(self.tr("circlec_fast")), 1, 2, Qt.AlignmentFlag.AlignRight)
        circlec_grid.addWidget(self.p3_cd_b, 1, 3)
        
        # Row 2: Hotkey
        self.circlec_hotkey_btn = KeyCaptureButton(self.app_ref.circlec_hotkey, parent_dialog=self)
        self.enable_circlec_hk_chk = QCheckBox(self.tr("enable_circlec"))
        self.enable_circlec_hk_chk.setChecked(self.app_ref.circlec_hotkey_enabled)
        
        circlec_grid.addWidget(QLabel(self.tr("hotkey")), 2, 0, Qt.AlignmentFlag.AlignRight)
        circlec_grid.addWidget(self.circlec_hotkey_btn, 2, 1)
        circlec_grid.addWidget(self.enable_circlec_hk_chk, 2, 2, 1, 2)

        main_layout.addWidget(circlec_group)
        
        # 3. Global Hotkey Settings
        hotkey_group = QGroupBox(self.tr("global_group"))
        hotkey_layout = QFormLayout(hotkey_group)
        
        self.start_hotkey_btn = KeyCaptureButton(self.app_ref.start_hotkey, parent_dialog=self)
        self.start_hotkey_btn.setFixedWidth(140) # Match CircleC button weight (v1.7.0)
        
        self.enable_start_hk_chk = QCheckBox(self.tr("enable_start"))
        self.enable_start_hk_chk.setChecked(self.app_ref.start_hotkey_enabled)
        
        hotkey_layout.addRow(self.tr("start_hotkey"), self.start_hotkey_btn)
        hotkey_layout.addRow("", self.enable_start_hk_chk)
        main_layout.addWidget(hotkey_group)
        
        # 4. Language Settings
        lang_group = QGroupBox(self.tr("language_group"))
        lang_layout = QHBoxLayout(lang_group)
        lang_layout.addWidget(QLabel(self.tr("language_label")))
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItem("English", "en")
        self.lang_combo.addItem("日本語", "ja")
        
        index = self.lang_combo.findData(self.app_ref.language)
        if index >= 0:
            self.lang_combo.setCurrentIndex(index)
            
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        main_layout.addWidget(lang_group)
        
        # Dialog Buttons
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.button(QDialogButtonBox.StandardButton.Ok).setText(self.tr("ok"))
        btn_box.button(QDialogButtonBox.StandardButton.Cancel).setText(self.tr("cancel"))
        
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        main_layout.addWidget(btn_box)

    def tr(self, key):
        return TRANSLATIONS.get(self.app_ref.language, TRANSLATIONS["en"]).get(key, key)

    def get_data(self):
        presets_data = []
        for inputs in self.preset_inputs:
            presets_data.append({
                'label': inputs['label'].text(),
                'time': inputs['time'].value(),
                'first_time': inputs['first_time'].value()
            })
            
        return {
            'presets': presets_data,
            'language': self.lang_combo.currentData(),
            'circlec_loop_time': self.circlec_loop_input.value(),
            'circlec_first_time': self.circlec_first_input.value(),
            'circlec_hotkey': self.circlec_hotkey_btn.key_name,
            'circlec_hotkey_enabled': self.enable_circlec_hk_chk.isChecked(),
            'start_hotkey': self.start_hotkey_btn.key_name,
            'start_hotkey_enabled': self.enable_start_hk_chk.isChecked(),
            'label3_circled_phases': [self.p3_cd_a.value(), self.p3_cd_b.value()],
            'label3_start_phases': [self.p3_st_a.value(), self.p3_st_b.value()]
        }

    def closeEvent(self, event):
        self.circlec_hotkey_btn.stop_listener()
        self.start_hotkey_btn.stop_listener()
        super().closeEvent(event)

class CountdownTimerApp(QMainWindow):
    hotkey_pressed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("ルベカウントタイマー ver1.6")
        self.setFixedSize(600, 390)
        self.setObjectName("MainWindow")
        
        # Set Window Icon
        icon_path = os.path.join(get_bundle_dir(), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        elif os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        
        # Default Presets
        self.presets = [
            {'label': '1', 'time': 20.0, 'first_time': 5.0},
            {'label': '2', 'time': 17.75, 'first_time': 5.0},
            {'label': '3', 'time': 23.75, 'first_time': 5.0} # New default Yellow
        ]
        self.language = 'ja'
        self.circlec_loop_time = 19.15
        self.circlec_first_time = 5.00
        self.start_hotkey = 'f9'
        self.circlec_hotkey = 'f8'
        self.start_hotkey_enabled = True
        self.circlec_hotkey_enabled = True
        self.language = "ja"
        
        # Audio Defaults
        self.audio_settings = {
            "warning_5s_red": "sounds/warning_5s_red.wav",
            "warning_5s_yellow": "sounds/warning_5s_yellow.wav",
            "warning_5s_circlec": "sounds/warning_5s_circleC.wav",
            "warning_5s_slow": "sounds/warning_5s_slow.wav",
            "warning_5s_fast": "sounds/warning_5s_fast.wav",
            "warning_5s_rainbow": "sounds/warning_5s_rainbow.wav",
            "count_321": "sounds/count.wav",
            "end_0s": "sounds/end.wav"
        }
        
        # State variables
        self.timer_mode = "normal" # "normal" or "circlec"
        self.current_preset_index = 0
        self.time_left = 0.0
        self.initial_time = 0.0
        self.is_running = False
        
        self.loop_count = 1  # 1st: Red, 2nd: Red, 3rd: Yellow -> loop back to 1
        
        self.warning_triggered = False
        self.count_3_triggered = False
        self.count_2_triggered = False
        self.count_1_triggered = False
        self._slider_start_val = 0.0
        
        self.timer = QTimer()
        self.timer.setInterval(10) # 10ms for 0.01s precision
        self.timer.timeout.connect(self.update_timer)
        
        self.load_settings()
        
        # Setup hotkey signal slot
        self.hotkey_pressed.connect(self.handle_hotkey_trigger, Qt.ConnectionType.QueuedConnection)
        
        self.keyboard_listener = None
        self.register_hotkey()
        
        # Audio Setup
        self.player_5s_red = QMediaPlayer()
        self.audio_out_5s_red = QAudioOutput()
        self.player_5s_red.setAudioOutput(self.audio_out_5s_red)
        
        self.player_5s_yellow = QMediaPlayer()
        self.audio_out_5s_yellow = QAudioOutput()
        self.player_5s_yellow.setAudioOutput(self.audio_out_5s_yellow)
        
        self.player_5s_circlec = QMediaPlayer()
        self.audio_out_5s_circlec = QAudioOutput()
        self.player_5s_circlec.setAudioOutput(self.audio_out_5s_circlec)
        
        self.player_5s_slow = QMediaPlayer()
        self.audio_out_5s_slow = QAudioOutput()
        self.player_5s_slow.setAudioOutput(self.audio_out_5s_slow)
        
        self.player_5s_fast = QMediaPlayer()
        self.audio_out_5s_fast = QAudioOutput()
        self.player_5s_fast.setAudioOutput(self.audio_out_5s_fast)
        
        self.player_5s_rainbow = QMediaPlayer()
        self.audio_out_5s_rainbow = QAudioOutput()
        self.player_5s_rainbow.setAudioOutput(self.audio_out_5s_rainbow)
        
        self.player_count = QMediaPlayer()
        self.audio_out_count = QAudioOutput()
        self.player_count.setAudioOutput(self.audio_out_count)
        
        self.player_end = QMediaPlayer()
        self.audio_out_end = QAudioOutput()
        self.player_end.setAudioOutput(self.audio_out_end)
        
        self.init_ui()
        self.load_audio_files()
        
        # Select Preset 3 by default if it exists (index 2)
        if len(self.presets) >= 3:
            self.select_preset(2)
        elif self.presets:
            self.select_preset(0)
            
        # Set initial volume
        self.update_volume(self.vol_slider.value())

    def load_settings(self):
        settings_path = os.path.join(get_external_dir(), 'settings.json')
        if not os.path.exists(settings_path):
            return
            
        try:
            # Try loading as UTF-8 first
            with open(settings_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except UnicodeDecodeError:
            try:
                # Fallback to CP932 (Japanese Windows default) if UTF-8 fails
                with open(settings_path, 'r', encoding='cp932') as f:
                    data = json.load(f)
            except Exception:
                print("Failed to decode settings.json with UTF-8 or CP932")
                return
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"settings.json missing or invalid! {e}")
            return
        except Exception as e:
            print(f"Unexpected error loading settings: {e}")
            return

        try:
            self.presets = data.get('presets', [])
            
            # Upgrade presets to have 'first_time' if missing, or enforce 5.00 if user requests 
            for p in self.presets:
                # To satisfy user request, we enforce 5.00 if it was the old default of 6.00
                if 'first_time' not in p or p['first_time'] == 6.00:
                    p['first_time'] = 5.00
                    
            self.audio_settings = data.get('audio', {})
            self.start_hotkey = data.get('start_hotkey', 'f9')
            # Handle migration from disaster_hotkey/circled_hotkey to circlec_hotkey
            self.circlec_hotkey = data.get('circlec_hotkey', data.get('disaster_hotkey', data.get('circled_hotkey', 'f8')))
            
            self.circlec_loop_time = float(data.get('circlec_loop_time', data.get('circled_loop_time', 19.15)))
            self.circlec_first_time = float(data.get('circlec_first_time', data.get('circled_first_time', 5.00)))
            
            # Individual hotkey flags
            self.start_hotkey_enabled = data.get('start_hotkey_enabled', data.get('hotkey_enabled', True))
            self.circlec_hotkey_enabled = data.get('circlec_hotkey_enabled', data.get('circled_hotkey_enabled', data.get('hotkey_enabled', True)))
            self.language = data.get('language', 'en')
            
            # Label 3 Multi-phase settings
            p3 = self.presets[2] if len(self.presets) > 2 else {}
            self.label3_circled_phases = data.get('label3_circled_phases', [23.50, 21.00]) # Updated v1.6.9
            self.label3_start_phases = data.get('label3_start_phases', [23.75, 23.50]) # New defaults
        except Exception as e:
            print(f"Error parsing loaded settings: {e}")

    def save_settings(self):
        settings_path = os.path.join(get_external_dir(), 'settings.json')
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                data = {
                    "start_hotkey": self.start_hotkey,
                    "circlec_hotkey": self.circlec_hotkey,
                    "circlec_loop_time": self.circlec_loop_time,
                    "circlec_first_time": self.circlec_first_time,
                    "start_hotkey_enabled": self.start_hotkey_enabled,
                    "circlec_hotkey_enabled": self.circlec_hotkey_enabled,
                    "language": self.language,
                    "presets": self.presets,
                    "audio": self.audio_settings,
                    "label3_circled_phases": self.label3_circled_phases,
                    "label3_start_phases": self.label3_start_phases
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_audio_files(self):
        ext_dir = get_external_dir()
        path_5s_red = os.path.join(ext_dir, self.audio_settings.get("warning_5s_red", "sounds/warning_5s_red.wav"))
        path_5s_yellow = os.path.join(ext_dir, self.audio_settings.get("warning_5s_yellow", "sounds/warning_5s_yellow.wav"))
        path_5s_circlec = os.path.join(ext_dir, self.audio_settings.get("warning_5s_circlec", "sounds/warning_5s_circleC.wav"))
        path_5s_slow = os.path.join(ext_dir, self.audio_settings.get("warning_5s_slow", "sounds/warning_5s_slow.wav"))
        path_5s_fast = os.path.join(ext_dir, self.audio_settings.get("warning_5s_fast", "sounds/warning_5s_fast.wav"))
        path_5s_rainbow = os.path.join(ext_dir, self.audio_settings.get("warning_5s_rainbow", "sounds/warning_5s_rainbow.wav"))
        
        # Standard fallback for all 5s warnings
        std_fallback = os.path.join(ext_dir, "sounds/warning_5s.wav")
        
        def set_p_source(player, path):
            if os.path.exists(path):
                player.setSource(QUrl.fromLocalFile(path))
            elif os.path.exists(std_fallback):
                player.setSource(QUrl.fromLocalFile(std_fallback))

        set_p_source(self.player_5s_red, path_5s_red)
        set_p_source(self.player_5s_yellow, path_5s_yellow)
        set_p_source(self.player_5s_circlec, path_5s_circlec)
        set_p_source(self.player_5s_slow, path_5s_slow)
        set_p_source(self.player_5s_fast, path_5s_fast)
        set_p_source(self.player_5s_rainbow, path_5s_rainbow)
        
        path_count = os.path.join(ext_dir, self.audio_settings.get("count_321", "sounds/count.wav"))
        path_end = os.path.join(ext_dir, self.audio_settings.get("end_0s", "sounds/end.wav"))
        
        if os.path.exists(path_count): self.player_count.setSource(QUrl.fromLocalFile(path_count))
        if os.path.exists(path_end): self.player_end.setSource(QUrl.fromLocalFile(path_end))

    def init_ui(self):
        central_widget = QWidget()
        central_widget.setObjectName("CentralWidget")
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # --- Top Row: Presets ---
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        top_layout.addStretch()
        
        self.preset_buttons = []
        for i, preset in enumerate(self.presets):
            if i == 2:
                # Label 3: Show dual phases at startup (v1.7.1)
                btn_text = f"{preset['label']} ({self.label3_start_phases[0]:.2f}/{self.label3_start_phases[1]:.2f})"
            else:
                btn_text = f"{preset['label']} ({preset['time']:.2f}s)"
            btn = QPushButton(btn_text)
            btn.setObjectName("PresetButton")
            btn.setProperty("active", "false")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            # Context menu for right click
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(lambda pos, idx=i: self.show_preset_context_menu(idx))
            
            top_layout.addWidget(btn)
            self.preset_buttons.append(btn)
            
        top_layout.addStretch()
        main_layout.addLayout(top_layout)
        
        # --- Middle Row: Volume, Display ---
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(0, 5, 0, 5)
        
        # Volume Column
        vol_layout = QVBoxLayout()
        self.vol_title_label = QLabel(self.tr("volume_label"))
        self.vol_title_label.setObjectName("SmallLabel")
        self.vol_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.vol_slider = QSlider(Qt.Orientation.Vertical)
        self.vol_slider.setObjectName("VolumeSlider")
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(50)
        
        vol_icon = QLabel("🔈")
        vol_icon.setObjectName("IconLabel")
        vol_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        vol_layout.addWidget(self.vol_title_label)
        vol_layout.addWidget(self.vol_slider, alignment=Qt.AlignmentFlag.AlignHCenter)
        vol_layout.addWidget(vol_icon)
        
        middle_layout.addLayout(vol_layout)
        middle_layout.addStretch()
        
        # Main Display Frame
        self.display_frame = QFrame()
        self.display_frame.setObjectName("DisplayFrame")
        self.display_frame.setFixedSize(450, 150)
        self.display_frame.setProperty("warning", "none")
        
        display_layout = QVBoxLayout(self.display_frame)
        display_layout.setContentsMargins(10, 10, 10, 10)
        
        self.time_label = QLabel("00.00")
        self.time_label.setObjectName("TimeLabel")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setProperty("warning", "none")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("ProgressBar")
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 1000)
        self.progress_bar.setValue(1000)
        self.progress_bar.setProperty("warning", "none")
        
        display_layout.addWidget(self.time_label)
        display_layout.addWidget(self.progress_bar)
        
        middle_layout.addWidget(self.display_frame)
        middle_layout.addStretch()
        
        main_layout.addLayout(middle_layout)
        
        # --- Bottom Row: Start/Stop, Latency ---
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        bottom_layout.addStretch(1)
        
        # Start/Stop Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.start_btn = QPushButton("START")
        self.start_btn.setToolTip(f"Hotkey: {self.start_hotkey} (Right-click to edit)")
        self.start_btn.setObjectName("StartButton")
        self.start_btn.setFixedSize(100, 100)
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Start button context menu
        self.start_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.start_btn.customContextMenuRequested.connect(self.open_hotkey_edit_start)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("StopButton")
        self.stop_btn.setFixedSize(80, 80)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 2. CircleC Setup
        self.circlec_btn = QPushButton()
        self.circlec_btn.setObjectName("CircleCButton")
        self.circlec_btn.setFixedSize(140, 60)
        self.circlec_btn.clicked.connect(self.start_circlec_timer)
        self.circlec_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.circlec_btn.customContextMenuRequested.connect(self.show_circlec_context_menu)
        self.circlec_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_circlec_info_label()
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        btn_layout.addWidget(self.circlec_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        
        bottom_layout.addLayout(btn_layout)
        bottom_layout.addStretch(1)
        
        # Latency Column
        latency_layout = QVBoxLayout()
        self.latency_title_label = QLabel(self.tr("latency_label"))
        self.latency_title_label.setObjectName("SmallLabel")
        self.latency_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Latency Slider (-500 to 500 mapping to -5.00 to +5.00)
        self.latency_slider = QSlider(Qt.Orientation.Horizontal)
        self.latency_slider.setObjectName("LatencySlider")
        self.latency_slider.setRange(-500, 500)
        self.latency_slider.setValue(0)
        self.latency_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.latency_slider.setTickInterval(100)
        self.latency_slider.setMinimumWidth(160) # Make slider larger
        self.latency_slider.setEnabled(False) # Disabled initially
        
        self.latency_val_label = QLabel("0.00")
        self.latency_val_label.setObjectName("LatencyValue")
        self.latency_val_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        slider_row = QHBoxLayout()
        slider_row.addWidget(QLabel("-5"))
        slider_row.addWidget(self.latency_slider)
        slider_row.addWidget(QLabel("+5"))
        
        latency_layout.addWidget(self.latency_title_label)
        latency_layout.addLayout(slider_row)
        latency_layout.addWidget(self.latency_val_label)
        
        bottom_layout.addLayout(latency_layout)
        
        main_layout.addLayout(bottom_layout)
        
        # Initialize labels
        self.retranslate_ui()
        
        # Event bindings
        for i, btn in enumerate(self.preset_buttons):
            btn.clicked.connect(lambda checked, idx=i: self.select_preset(idx))
            
        self.start_btn.clicked.connect(self.start_timer)
        self.stop_btn.clicked.connect(self.stop_timer)
        self.vol_slider.valueChanged.connect(self.update_volume)
        self.latency_slider.valueChanged.connect(self.update_latency_label)
        self.latency_slider.sliderPressed.connect(self.record_latency_start)
        self.latency_slider.sliderReleased.connect(self.apply_latency)

    def record_latency_start(self):
        self._slider_start_val = self.latency_slider.value() / 100.0

    def trigger_hotkey_signal(self, key_name):
        self.hotkey_pressed.emit(key_name)

    def contextMenuEvent(self, event):
        # Open global settings on right click of the main window empty space
        if self.is_running:
            return
            
        menu = QMenu(self)
        settings_action = menu.addAction("Settings")
        
        action = menu.exec(event.globalPos())
        
        if action == settings_action:
            self.stop_keyboard_listener()
                
            dialog = GlobalSettingsDialog(self, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_data = dialog.get_data()
                
                self.presets = new_data['presets']
                self.circlec_loop_time = float(new_data['circlec_loop_time'])
                self.circlec_first_time = float(new_data['circlec_first_time'])
                self.circlec_hotkey = str(new_data['circlec_hotkey'])
                self.start_hotkey = str(new_data['start_hotkey'])
                self.start_hotkey_enabled = bool(new_data['start_hotkey_enabled'])
                self.circlec_hotkey_enabled = bool(new_data['circlec_hotkey_enabled'])
                self.language = str(new_data['language'])
                self.label3_circled_phases = new_data['label3_circled_phases']
                self.label3_start_phases = new_data['label3_start_phases']
                
                self.save_settings()
                self.retranslate_ui()
                
                # Update UI to reflect new settings
                self.start_btn.setToolTip(f"Hotkey: {self.start_hotkey.upper()} (Right-click to edit)")
                self.circlec_btn.setToolTip(f"Hotkey: {self.circlec_hotkey.upper()} (Right-click to edit)")
                
                for i, p in enumerate(self.presets):
                    if i < len(self.preset_buttons):
                        self.preset_buttons[i].setText(f"{p['label']} ({float(p['time']):.2f}s)")
                    
                # If stopped, re-select current preset to update display
                self.select_preset(self.current_preset_index)
                self.update_circlec_info_label()
                
            self.register_hotkey()

    def register_hotkey(self):
        self.stop_keyboard_listener()
            
        try:
            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()
        except Exception as e:
            print(f"Failed to catch keys: {e}")

    def stop_keyboard_listener(self):
        if self.keyboard_listener is not None:
            try:
                self.keyboard_listener.stop()
            except:
                pass
            self.keyboard_listener = None

    def on_press(self, key):
        try:
            key_name = key.char
        except AttributeError:
            key_name = key.name
            
        key_str = str(key_name).lower()
        # Priority resolution
        if key_str == self.start_hotkey:
            self.trigger_hotkey_signal(key_str)
        elif key_str == self.circlec_hotkey:
            self.trigger_hotkey_signal(key_str)

    def handle_hotkey_trigger(self, key_name):
        if key_name == self.start_hotkey and self.start_hotkey_enabled:
            self.start_timer()
        elif key_name == self.circlec_hotkey and self.circlec_hotkey_enabled:
            self.start_circlec_timer()

    def closeEvent(self, event):
        self.stop_keyboard_listener()
        super().closeEvent(event)

    def open_hotkey_edit_start(self):
        if self.is_running:
            return
            
        self.stop_keyboard_listener()
            
        dialog = HotkeyEditDialog(self.start_hotkey, self.start_hotkey_enabled, self)
        dialog.setWindowTitle(self.tr("start_btn") + " " + self.tr("settings"))
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_hotkey = dialog.new_hotkey.strip().lower()
            self.start_hotkey_enabled = dialog.enable_chk.isChecked()
            
            if new_hotkey:
                self.start_hotkey = new_hotkey
                self.save_settings()
                self.start_btn.setToolTip(f"Hotkey: {self.start_hotkey.upper()} (Right-click to edit)")
                
        # Re-enable main listener
        self.register_hotkey()

    def open_hotkey_edit_circlec(self):
        if self.is_running:
            return
            
        self.stop_keyboard_listener()
            
        dialog = HotkeyEditDialog(self.circlec_hotkey, self.circlec_hotkey_enabled, parent=self)
        dialog.setWindowTitle(self.tr("circlec_btn") + " " + self.tr("settings"))
        dialog.add_time_editors(self.circlec_loop_time, self.circlec_first_time)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.circlec_hotkey = dialog.new_hotkey
            self.circlec_hotkey_enabled = dialog.enable_chk.isChecked()
            if dialog.has_time_edit:
                self.circlec_loop_time = dialog.time_edit_loop.value()
                self.circlec_first_time = dialog.time_edit_first.value()
            self.save_settings()
            self.register_hotkey()
            self.update_circlec_info_label()
            self.update_display()

    def show_preset_context_menu(self, index):
        if self.is_running:
            return 
            
        preset = self.presets[index]
        dialog = PresetEditDialog(
            preset['label'], 
            float(preset['time']), 
            float(preset.get('first_time', 6.00)),
            index,
            self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_label = dialog.label_edit.text()
            new_time = dialog.time_edit.value()
            new_first_time = dialog.first_time_edit.value()
            
            # Update data
            self.presets[index]['label'] = new_label
            self.presets[index]['time'] = new_time
            self.presets[index]['first_time'] = new_first_time
            
            if index == 2:
                self.label3_start_phases = [dialog.st_a_edit.value(), dialog.st_b_edit.value()]
                # Update main loop time for display to match first phase or average?
                # User said "move yellow/rainbow here", maybe just keep existing time or use yellow.
                # Let's use avg for the button label but keep logic as is.
                new_time = dialog.st_a_edit.value() 
                self.presets[index]['time'] = new_time
            
            self.save_settings()
            
            # Update UI button
            btn = self.preset_buttons[index]
            if index == 2:
                btn.setText(f"{new_label} ({self.label3_start_phases[0]:.2f}/{self.label3_start_phases[1]:.2f})")
            else:
                btn.setText(f"{new_label} ({new_time:.2f}s)")
            
            # If current preset, update display
            if self.current_preset_index == index:
                self.initial_time = new_time
                self.time_left = new_time
                self.update_display()

    def show_circlec_context_menu(self, pos):
        if self.is_running:
            return 
            
        dialog = CircleCSettingsDialog(self, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.circlec_hotkey = data["hotkey"]
            self.circlec_hotkey_enabled = data["enabled"]
            if self.current_preset_index == 2:
                self.label3_circled_phases = data["label3_circled_phases"]
                self.circlec_first_time = data["circlec_first_time"]
            else:
                self.circlec_loop_time = data["circlec_loop_time"]
                self.circlec_first_time = data["circlec_first_time"]
            
            self.save_settings()
            self.register_hotkey() # Refresh hotkey listener
            self.update_circlec_info_label()

    def select_preset(self, index):
        if self.is_running:
            return 
            
        self.current_preset_index = index
        preset = self.presets[index]
        self.initial_time = float(preset['time'])
        
        # Display the loop time when selected/not running
        self.time_left = self.initial_time
        self.loop_count = 1 
        self.reset_triggers()
        self.latency_slider.setValue(0)
        self.update_display()
        
        # Update button styles
        for i, btn in enumerate(self.preset_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            
        # Update Start button text
        self.start_btn.setText(f"{self.tr('start_btn')}\n({preset['time']:.2f}s)")
        
        self.update_circlec_info_label()

    def update_circlec_info_label(self):
        if not self.is_running or self.timer_mode != "circlec":
            if self.current_preset_index == 2:
                # Label 3: Show dual times with 2 decimals (v1.6.9)
                self.circlec_btn.setText(f"{self.tr('circlec_btn')}\n({self.label3_circled_phases[0]:.2f}/{self.label3_circled_phases[1]:.2f})")
            else:
                self.circlec_btn.setText(f"{self.tr('circlec_btn')}\n({self.circlec_loop_time:.2f}s)")
        else:
            self.circlec_btn.setText("C-RUN")

    def tr(self, key):
        return TRANSLATIONS.get(self.language, TRANSLATIONS["en"]).get(key, key)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("window_title"))
        if not self.is_running:
            self.start_btn.setText(self.tr("start_btn"))
        self.stop_btn.setText(self.tr("stop_btn"))
        self.latency_title_label.setText(self.tr("latency_label"))
        self.vol_title_label.setText(self.tr("volume_label"))
        self.update_circlec_info_label()

    def reset_triggers(self):
        self.warning_triggered = False
        self.count_3_triggered = False
        self.count_2_triggered = False
        self.count_1_triggered = False
        self.set_warning_visuals("none")

    def update_latency_label(self, value):
        float_val = value / 100.0
        sign = "+" if float_val > 0 else ""
        self.latency_val_label.setText(f"{sign}{float_val:.2f}")

    def apply_latency(self):
        current_val = self.latency_slider.value() / 100.0
        diff = current_val - self._slider_start_val
        if diff != 0 and self.is_running:
            self.time_left += diff
            self.update_display()
            if self.time_left > 5.0 and self.warning_triggered:
                self.warning_triggered = False
                self.set_warning_visuals("none")
            if self.time_left > 3.0: self.count_3_triggered = False
            if self.time_left > 2.0: self.count_2_triggered = False
            if self.time_left > 1.0: self.count_1_triggered = False
            
        # Update the start value so subsequent tweaks work correctly without needing to re-click
        self._slider_start_val = current_val

    def update_volume(self, value):
        vol = value / 100.0
        self.audio_out_5s_red.setVolume(vol)
        self.audio_out_5s_yellow.setVolume(vol)
        self.audio_out_5s_circlec.setVolume(vol)
        self.audio_out_5s_slow.setVolume(vol)
        self.audio_out_5s_fast.setVolume(vol)
        self.audio_out_5s_rainbow.setVolume(vol)
        self.audio_out_count.setVolume(vol)
        self.audio_out_end.setVolume(vol)

    def start_timer(self):
        # NORMAL start interrupts circlec if it's running
        was_circlec = (self.is_running and self.timer_mode == "circlec")
        
        if not self.is_running or was_circlec:
            self.is_running = True
            self.timer_mode = "normal"
            
            preset = self.presets[self.current_preset_index]
            self.initial_time = float(preset['time'])
            
            # If completely fresh OR interrupting circlec, apply normal first_time
            fresh_start = (self.loop_count == 1 and abs(self.time_left - self.initial_time) < 0.001)
            if fresh_start or was_circlec:
                self.time_left = float(preset.get('first_time', 5.00))
                self.loop_count = 1
                self.reset_triggers()
                self.update_display()
            
            # Reset latency slider strictly upon START tracking
            self.latency_slider.setValue(0)
            self.latency_slider.setEnabled(True)
            self._slider_start_val = 0.0
            
            self.start_btn.setText(self.tr("running"))
            self.start_btn.setStyleSheet("color: #ffffff; border-color: #ffffff;")
            self.update_circlec_info_label()
            self.circlec_btn.setStyleSheet("")
            self.timer.start()

    def start_circlec_timer(self):
        if not self.is_running and self.time_left > 0:
            self.is_running = True
            self.timer_mode = "circlec"
            
            self.initial_time = self.circlec_loop_time
            self.time_left = self.circlec_first_time
            self.loop_count = 1
            self.reset_triggers()
            self.update_display()
            
            self.latency_slider.setValue(0)
            self.latency_slider.setEnabled(True)
            self._slider_start_val = 0.0
            
            self.circlec_btn.setText("C-RUN")
            self.circlec_btn.setStyleSheet("border-color: #ffffff;") # Maintain neon yellow text from QSS, just white border
            self.start_btn.setText("START")
            self.start_btn.setStyleSheet("")
            self.timer.start()

    def stop_timer(self):
        self.is_running = False
        self.timer_mode = "normal"
        self.timer.stop()
        self.start_btn.setText("START")
        self.start_btn.setStyleSheet("") 
        self.update_circlec_info_label()
        self.circlec_btn.setStyleSheet("") 
        
        # Revert to loop time when stopped (as requested v1.6.6)
        preset = self.presets[self.current_preset_index]
        self.initial_time = float(preset['time'])
        self.time_left = self.initial_time
        self.loop_count = 1
        self.reset_triggers()
        self.latency_slider.setValue(0)
        self.latency_slider.setEnabled(False)
        self.set_warning_visuals("none") # Clear color warnings
        self.update_display()
        self.update_circlec_info_label()

    def update_timer(self):
        self.time_left -= 0.01
        
        # Audio Triggers
        # Slightly larger buffer (5.05) to ensure trigger if starting exactly at 5.0
        if self.time_left <= 5.05 and not self.warning_triggered:
            self.warning_triggered = True
            
            # Label 3 specific logic (Highest priority)
            if self.current_preset_index == 2:
                if self.timer_mode == "circlec":
                    # CircleD (CircleC) Logic: Phase 1 (5s), Phase 2 (Slow), Phase 3 (Fast)
                    if self.loop_count == 1:
                        self.set_warning_visuals("red")
                        self.player_5s_circlec.setPosition(0)
                        self.player_5s_circlec.play()
                    elif self.loop_count % 2 == 0:
                        self.set_warning_visuals("yellow")
                        self.player_5s_slow.setPosition(0)
                        self.player_5s_slow.play()
                    else:
                        self.set_warning_visuals("red")
                        self.player_5s_fast.setPosition(0)
                        self.player_5s_fast.play()
                else:
                    # START Logic: Phase 1 (Red), Phase 2 (Yellow), Phase 3 (Rainbow)
                    if self.loop_count == 1:
                        self.set_warning_visuals("red")
                        self.player_5s_red.setPosition(0)
                        self.player_5s_red.play()
                    elif self.loop_count % 2 == 0:
                        self.set_warning_visuals("yellow")
                        self.player_5s_yellow.setPosition(0)
                        self.player_5s_yellow.play()
                    else:
                        self.set_warning_visuals("red") # Visual is red as requested
                        self.player_5s_red.setPosition(0)
                        self.player_5s_red.play()
            
            # Global default logic for other presets
            elif self.timer_mode == "circlec":
                self.set_warning_visuals("red")
                self.player_5s_circlec.setPosition(0)
                self.player_5s_circlec.play()
            else:
                # Presets 1 & 2: 3-loop cycle (Red -> Red -> Yellow)
                mod_val = self.loop_count % 3
                if mod_val == 1 or mod_val == 2:
                    self.set_warning_visuals("red")
                    self.player_5s_red.setPosition(0)
                    self.player_5s_red.play()
                else:
                    self.set_warning_visuals("yellow")
                    self.player_5s_yellow.setPosition(0)
                    self.player_5s_yellow.play()
            
        if self.time_left <= 3.01 and not self.count_3_triggered:
            self.count_3_triggered = True
            self.player_count.setPosition(0)
            self.player_count.play()
            
        if self.time_left <= 2.01 and not self.count_2_triggered:
            self.count_2_triggered = True
            self.player_count.setPosition(0)
            self.player_count.play()
            
        if self.time_left <= 1.01 and not self.count_1_triggered:
            self.count_1_triggered = True
            self.player_count.setPosition(0)
            self.player_count.play()

        # End of countdown
        if self.time_left <= 0:
            self.time_left = 0
            self.player_end.setPosition(0)
            self.player_end.play()
            self.update_display()
            self.restart_countdown()
            return
            
        self.update_display()

    def restart_countdown(self):
        self.loop_count += 1 
        
        if self.current_preset_index == 2:
            # Multi-phase logic for Label 3
            if self.timer_mode == "circlec":
                # CircleD: alternating A and B
                self.initial_time = self.label3_circled_phases[0] if self.loop_count % 2 == 0 else self.label3_circled_phases[1]
            else:
                # START: alternating A and B
                self.initial_time = self.label3_start_phases[0] if self.loop_count % 2 == 0 else self.label3_start_phases[1]
        
        self.time_left = self.initial_time
        self.reset_triggers()
        self.latency_slider.setValue(0)
        self.update_display()

    def set_warning_visuals(self, status):
        self.display_frame.setProperty("warning", status)
        self.time_label.setProperty("warning", status)
        self.progress_bar.setProperty("warning", status)
        
        self.display_frame.style().unpolish(self.display_frame)
        self.display_frame.style().polish(self.display_frame)
        self.time_label.style().unpolish(self.time_label)
        self.time_label.style().polish(self.time_label)
        self.progress_bar.style().unpolish(self.progress_bar)
        self.progress_bar.style().polish(self.progress_bar)

    def update_display(self):
        if self.time_left < 0:
            self.time_left = 0
        self.time_label.setText(f"{self.time_left:05.2f}")
        
        # We need to compute progress base on whether it's the very first loop or subsequent loops
        # If we are stopped and at the start, max_time matches what is displayed (initial_time)
        if self.loop_count == 1:
            if not self.is_running:
                max_time = self.time_left # Full bar at idle
            elif self.timer_mode == "circlec":
                max_time = self.circlec_first_time
            else:
                preset = self.presets[self.current_preset_index]
                max_time = float(preset.get('first_time', 5.00))
        else:
            max_time = self.initial_time
        
        if max_time > 0:
            progress_val = int((self.time_left / max_time) * 1000)
            self.progress_bar.setValue(progress_val)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    try:
        qss_path = os.path.join(get_bundle_dir(), 'style.qss')
        with open(qss_path, 'r') as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        print("style.qss not found!")
        
    window = CountdownTimerApp()
    window.show()
    sys.exit(app.exec())
