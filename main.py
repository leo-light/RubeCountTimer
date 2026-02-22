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
                             QFrame, QSpacerItem, QSizePolicy, QDialog, QFormLayout, 
                             QLineEdit, QDoubleSpinBox, QDialogButtonBox, QMessageBox, QCheckBox,
                             QTabWidget, QGroupBox, QMenu, QComboBox)
from PyQt6.QtCore import Qt, QTimer, QUrl, pyqtSignal
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QCursor, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

TRANSLATIONS = {
    "en": {
        "window_title": "Rube Countdown Timer ver1.2",
        "presets_group": "Presets (Normal Countdowns)",
        "circled_group": "CircleD Settings",
        "global_group": "Global Control",
        "language_group": "Language Settings",
        "preset_name_label": "Preset {} Name:",
        "loop_time": "Loop Time (s):",
        "first_time": "First Time (s):",
        "hotkey": "Hotkey:",
        "start_hotkey": "START Hotkey:",
        "enable_start": "Enable START Hotkey",
        "enable_circled": "Enable CircleD Hotkey",
        "language_label": "Select Language:",
        "start_btn": "START",
        "stop_btn": "STOP",
        "circled_btn": "CircleD",
        "latency_label": "Latency Adjust",
        "volume_label": "Volume",
        "settings": "Settings",
        "running": "RUNNING",
        "ok": "OK",
        "cancel": "Cancel"
    },
    "ja": {
        "window_title": "ルベカウントタイマー ver1.2",
        "presets_group": "プリセット設定 (通常カウントダウン)",
        "circled_group": "サークルD設定",
        "global_group": "システム制御",
        "language_group": "言語設定",
        "preset_name_label": "プリセット {} 名前:",
        "loop_time": "ループ時間 (秒):",
        "first_time": "初回時間 (秒):",
        "hotkey": "ホットキー:",
        "start_hotkey": "開始ホットキー:",
        "enable_start": "STARTホットキーを有効にする",
        "enable_circled": "CircleDホットキーを有効にする",
        "language_label": "言語を選択:",
        "start_btn": "スタート",
        "stop_btn": "ストップ",
        "circled_btn": "サークルD",
        "latency_label": "タイム補正",
        "volume_label": "音量",
        "settings": "設定",
        "running": "計測中",
        "ok": "保存",
        "cancel": "キャンセル"
    }
}

class PresetEditDialog(QDialog):
    def __init__(self, current_label, current_time, current_first_time, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Preset")
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
        
        layout.addRow("Label:", self.label_edit)
        layout.addRow("Loop Time (s):", self.time_edit)
        layout.addRow("First Time (s):", self.first_time_edit)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)


class HotkeyEditDialog(QDialog):
    def __init__(self, current_hotkey, current_enabled, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit START Hotkey")
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
            QPushButton#CaptureBtn[active="true"] {
                border-color: #ffaa00;
                color: #ffaa00;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        self.info_label = QLabel("Current Hotkey:")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        
        self.capture_btn = QPushButton(str(self.new_hotkey).upper())
        self.capture_btn.setObjectName("CaptureBtn")
        self.capture_btn.setProperty("active", "false")
        self.capture_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.capture_btn.clicked.connect(self.start_capture)
        layout.addWidget(self.capture_btn)
        
        self.enable_chk = QCheckBox("Enable Global Shortcut")
        self.enable_chk.setChecked(self.new_enabled)
        layout.addWidget(self.enable_chk)
        
        # Optional fields for time editing (used by CircleD)
        self.has_time_edit = False
        self.time_edit_loop = None
        self.time_edit_first = None
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)
        
        self.listener = None
        
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
        form_layout.addRow("Loop Time (s):", self.time_edit_loop)
        
        self.time_edit_first = QDoubleSpinBox()
        self.time_edit_first.setDecimals(2)
        self.time_edit_first.setMaximum(9999.99)
        self.time_edit_first.setSingleStep(1.0)
        self.time_edit_first.setValue(first_val)
        form_layout.addRow("First Time (s):", self.time_edit_first)
        
        # Add the form layout before the enable_chk and button box
        layout = self.layout()
        layout.insertLayout(3, form_layout)
        
    def start_capture(self):
        self.capture_btn.setText("Press any key...")
        self.capture_btn.setProperty("active", "true")
        self.capture_btn.style().unpolish(self.capture_btn)
        self.capture_btn.style().polish(self.capture_btn)
        
        if self.listener is not None:
            self.listener.stop()
            
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
    def on_press(self, key):
        try:
            # Alphabetic keys
            key_name = key.char
        except AttributeError:
            # Special keys (e.g., F9, Space, Enter)
            key_name = key.name
            
        self.new_hotkey = str(key_name).lower()
        
        # Stop listener and update UI via thread-safe invoke (though it's usually fine here for simple text)
        QTimer.singleShot(0, self.finish_capture)
        return False # Stop listener
        
    def finish_capture(self):
        self.capture_btn.setText(self.new_hotkey.upper())
        self.capture_btn.setProperty("active", "false")
        self.capture_btn.style().unpolish(self.capture_btn)
        self.capture_btn.style().polish(self.capture_btn)
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
            
    def closeEvent(self, event):
        if self.listener is not None:
            self.listener.stop()
        super().closeEvent(event)

class GlobalSettingsDialog(QDialog):
    def __init__(self, parent_app, parent=None):
        super().__init__(parent)
        self.app_ref = parent_app
        self.setWindowTitle("Global Settings")
        self.setFixedSize(500, 780)
        
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
        
        # 1. Presets Settings
        preset_group = QGroupBox(self.tr("presets_group"))
        preset_vbox = QVBoxLayout(preset_group)
        preset_vbox.setSpacing(15) 
        
        self.preset_inputs = []
        for i, preset in enumerate(self.app_ref.presets):
            preset_block = QVBoxLayout()
            
            # Label row: Name
            label_row = QHBoxLayout()
            label_row.addWidget(QLabel(self.tr("preset_name_label").format(i+1)))
            le_label = QLineEdit(preset['label'])
            le_label.setMinimumWidth(200)
            label_row.addWidget(le_label)
            label_row.addStretch()
            preset_block.addLayout(label_row)
            
            # Times row: Loop and First
            times_row = QHBoxLayout()
            times_row.addSpacing(20)
            
            sb_loop = QDoubleSpinBox()
            sb_loop.setDecimals(2)
            sb_loop.setMaximum(9999.99)
            sb_loop.setSingleStep(1.0)
            sb_loop.setValue(float(preset['time']))
            
            sb_first = QDoubleSpinBox()
            sb_first.setDecimals(2)
            sb_first.setMaximum(9999.99)
            sb_first.setSingleStep(1.0)
            sb_first.setValue(float(preset.get('first_time', 5.00)))
            
            times_row.addWidget(QLabel(self.tr("loop_time")))
            times_row.addWidget(sb_loop)
            times_row.addSpacing(10)
            times_row.addWidget(QLabel(self.tr("first_time")))
            times_row.addWidget(sb_first)
            times_row.addStretch()
            
            preset_block.addLayout(times_row)
            preset_vbox.addLayout(preset_block)
            self.preset_inputs.append({'label': le_label, 'time': sb_loop, 'first_time': sb_first})
            
        main_layout.addWidget(preset_group)
        
        # 2. CircleD Settings
        circled_group = QGroupBox(self.tr("circled_group"))
        circled_layout = QFormLayout(circled_group)
        circled_layout.setSpacing(10)
        
        self.cd_loop = QDoubleSpinBox()
        self.cd_loop.setDecimals(2)
        self.cd_loop.setMaximum(9999.99)
        self.cd_loop.setSingleStep(1.0)
        self.cd_loop.setValue(self.app_ref.circled_loop_time)
        
        self.cd_first = QDoubleSpinBox()
        self.cd_first.setDecimals(2)
        self.cd_first.setMaximum(9999.99)
        self.cd_first.setSingleStep(1.0)
        self.cd_first.setValue(self.app_ref.circled_first_time)
        
        self.cd_hotkey = QLineEdit(self.app_ref.disaster_hotkey)
        self.cd_hotkey.setMaximumWidth(100)
        
        self.enable_circled_hk_chk = QCheckBox(self.tr("enable_circled"))
        self.enable_circled_hk_chk.setChecked(self.app_ref.circled_hotkey_enabled)
        
        circled_layout.addRow(self.tr("loop_time"), self.cd_loop)
        circled_layout.addRow(self.tr("first_time"), self.cd_first)
        circled_layout.addRow(self.tr("hotkey"), self.cd_hotkey)
        circled_layout.addRow("", self.enable_circled_hk_chk)
        main_layout.addWidget(circled_group)
        
        # 3. Global Hotkey Settings
        hotkey_group = QGroupBox(self.tr("global_group"))
        hotkey_layout = QFormLayout(hotkey_group)
        
        self.start_hotkey_input = QLineEdit(self.app_ref.start_hotkey)
        self.start_hotkey_input.setMaximumWidth(100)
        
        self.enable_start_hk_chk = QCheckBox(self.tr("enable_start"))
        self.enable_start_hk_chk.setChecked(self.app_ref.start_hotkey_enabled)
        
        hotkey_layout.addRow(self.tr("start_hotkey"), self.start_hotkey_input)
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
            'circled_loop': self.cd_loop.value(),
            'circled_first': self.cd_first.value(),
            'circled_hotkey': self.cd_hotkey.text().strip().lower(),
            'start_hotkey': self.start_hotkey_input.text().strip().lower(),
            'start_hotkey_enabled': self.enable_start_hk_chk.isChecked(),
            'circled_hotkey_enabled': self.enable_circled_hk_chk.isChecked(),
            'language': self.lang_combo.currentData()
        }

class CountdownTimerApp(QMainWindow):
    hotkey_pressed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("ルベカウントタイマー ver1.2")
        self.setFixedSize(600, 390)
        self.setObjectName("MainWindow")
        
        # Set Window Icon
        icon_path = os.path.join(get_bundle_dir(), "icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        elif os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
        
        self.presets = []
        self.audio_settings = {}
        self.start_hotkey = "f9"
        self.start_hotkey_enabled = True
        self.disaster_hotkey = "f8"
        self.circled_hotkey_enabled = True
        self.circled_loop_time = 19.15
        self.circled_first_time = 5.00
        self.language = "en"
        
        # State variables
        self.timer_mode = "normal" # "normal" or "disaster"
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
        
        self.player_5s_disaster = QMediaPlayer()
        self.audio_out_5s_disaster = QAudioOutput()
        self.player_5s_disaster.setAudioOutput(self.audio_out_5s_disaster)
        
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
            self.disaster_hotkey = data.get('disaster_hotkey', 'f8')
            self.circled_loop_time = float(data.get('circled_loop_time', 19.15))
            self.circled_first_time = float(data.get('circled_first_time', 5.00))
            # Individual hotkey flags
            self.start_hotkey_enabled = data.get('start_hotkey_enabled', data.get('hotkey_enabled', True))
            self.circled_hotkey_enabled = data.get('circled_hotkey_enabled', data.get('hotkey_enabled', True))
            self.language = data.get('language', 'en')
        except Exception as e:
            print(f"Error parsing loaded settings: {e}")

    def save_settings(self):
        settings_path = os.path.join(get_external_dir(), 'settings.json')
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                data = {
                    "start_hotkey": self.start_hotkey,
                    "disaster_hotkey": self.disaster_hotkey,
                    "circled_loop_time": self.circled_loop_time,
                    "circled_first_time": self.circled_first_time,
                    "start_hotkey_enabled": self.start_hotkey_enabled,
                    "circled_hotkey_enabled": self.circled_hotkey_enabled,
                    "language": self.language,
                    "presets": self.presets,
                    "audio": self.audio_settings
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def load_audio_files(self):
        ext_dir = get_external_dir()
        path_5s_red = os.path.join(ext_dir, self.audio_settings.get("warning_5s_red", "sounds/warning_5s_red.wav"))
        path_5s_yellow = os.path.join(ext_dir, self.audio_settings.get("warning_5s_yellow", "sounds/warning_5s_yellow.wav"))
        path_5s_disaster = os.path.join(ext_dir, self.audio_settings.get("warning_5s_disaster", "sounds/warning_5s_disaster.wav"))
        path_count = os.path.join(ext_dir, self.audio_settings.get("count_321", "sounds/count.wav"))
        path_end = os.path.join(ext_dir, self.audio_settings.get("end_0s", "sounds/end.wav"))
        
        if os.path.exists(path_5s_red): self.player_5s_red.setSource(QUrl.fromLocalFile(path_5s_red))
        if os.path.exists(path_5s_yellow): self.player_5s_yellow.setSource(QUrl.fromLocalFile(path_5s_yellow))
        if os.path.exists(path_5s_disaster): self.player_5s_disaster.setSource(QUrl.fromLocalFile(path_5s_disaster))
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
            btn = QPushButton(f"{preset['label']} ({preset['time']:.2f}s)")
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
        self.start_btn.customContextMenuRequested.connect(self.show_hotkey_context_menu)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("StopButton")
        self.stop_btn.setFixedSize(80, 80)
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.disaster_btn = QPushButton(f"CircleD\n({self.circled_loop_time:.2f}s)")
        self.disaster_btn.setToolTip(f"Hotkey: {self.disaster_hotkey} (Right-click to edit)")
        self.disaster_btn.setObjectName("DisasterButton")
        self.disaster_btn.setFixedSize(85, 60) # Taller to fit two lines
        self.disaster_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.disaster_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.disaster_btn.customContextMenuRequested.connect(self.show_disaster_hotkey_context_menu)
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        btn_layout.addWidget(self.disaster_btn, alignment=Qt.AlignmentFlag.AlignVCenter)
        
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
        self.disaster_btn.clicked.connect(self.start_disaster_timer)
        self.vol_slider.valueChanged.connect(self.update_volume)
        self.latency_slider.valueChanged.connect(self.update_latency_label)
        self.latency_slider.sliderPressed.connect(self.record_latency_start)
        self.latency_slider.sliderReleased.connect(self.apply_latency)

    def record_latency_start(self):
        self._slider_start_val = self.latency_slider.value() / 100.0

    def trigger_hotkey_signal(self):
        self.hotkey_pressed.emit()

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
                self.circled_loop_time = float(new_data['circled_loop'])
                self.circled_first_time = float(new_data['circled_first'])
                self.disaster_hotkey = str(new_data['circled_hotkey'])
                self.start_hotkey = str(new_data['start_hotkey'])
                self.start_hotkey_enabled = bool(new_data['start_hotkey_enabled'])
                self.circled_hotkey_enabled = bool(new_data['circled_hotkey_enabled'])
                self.language = str(new_data['language'])
                
                self.save_settings()
                self.retranslate_ui()
                
                # Update UI to reflect new settings
                self.start_btn.setToolTip(f"Hotkey: {self.start_hotkey.upper()} (Right-click to edit)")
                self.disaster_btn.setToolTip(f"Hotkey: {self.disaster_hotkey.upper()} (Right-click to edit)")
                
                for i, p in enumerate(self.presets):
                    if i < len(self.preset_buttons):
                        self.preset_buttons[i].setText(f"{p['label']} ({float(p['time']):.2f}s)")
                    
                # If stopped, re-select current preset to update display
                self.select_preset(self.current_preset_index)
                self.update_circled_info_label()
                
            self.register_hotkey()

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
            self.trigger_hotkey_signal()
        elif key_str == self.disaster_hotkey:
            self.trigger_hotkey_signal_disaster()

    def trigger_hotkey_signal_disaster(self):
        # We need another signal or just thread-safe invoke (since signal is already queued, we can just use QTimer)
        QTimer.singleShot(0, self.handle_disaster_hotkey_trigger)

    def register_hotkey(self):
        self.stop_keyboard_listener()
            
        try:
            self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
            self.keyboard_listener.start()
        except Exception as e:
            print(f"Failed to catch keys: {e}")

    def handle_hotkey_trigger(self):
        if not self.start_hotkey_enabled:
            return
            
        # Hotkey only starts the timer, does not toggle STOP
        # If disaster is running, start_timer() will interrupt it.
        # If it's not running, it will just start.
        self.start_timer()
        
    def handle_disaster_hotkey_trigger(self):
        if not self.circled_hotkey_enabled:
            return
            
        # If NOT running normal mode, we can start disaster
        # If already running normal, we do NOT interrupt normal with disaster.
        if not self.is_running or self.timer_mode == "disaster":
            self.start_disaster_timer()

    def closeEvent(self, event):
        self.stop_keyboard_listener()
        super().closeEvent(event)

    def show_hotkey_context_menu(self, pos):
        if self.is_running:
            return
            
        self.stop_keyboard_listener()
            
        dialog = HotkeyEditDialog(self.start_hotkey, self.start_hotkey_enabled, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_hotkey = dialog.new_hotkey.strip().lower()
            self.start_hotkey_enabled = dialog.enable_chk.isChecked()
            
            if new_hotkey:
                self.start_hotkey = new_hotkey
                self.save_settings()
                self.start_btn.setToolTip(f"Hotkey: {self.start_hotkey.upper()} (Right-click to edit)")
                
        # Re-enable main listener
        self.register_hotkey()

    def show_disaster_hotkey_context_menu(self, pos):
        if self.is_running:
            return
            
        self.stop_keyboard_listener()
            
        dialog = HotkeyEditDialog(self.disaster_hotkey, self.circled_hotkey_enabled, self)
        dialog.setWindowTitle("Edit CircleD Setup")
        dialog.add_time_editors(self.circled_loop_time, self.circled_first_time)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_hotkey = dialog.new_hotkey.strip().lower()
            self.circled_hotkey_enabled = dialog.enable_chk.isChecked()
            self.circled_loop_time = dialog.time_edit_loop.value()
            self.circled_first_time = dialog.time_edit_first.value()
            
            if new_hotkey:
                self.disaster_hotkey = new_hotkey
                self.save_settings()
                self.update_circled_info_label()
                self.disaster_btn.setToolTip(f"Hotkey: {self.disaster_hotkey.upper()} (Right-click to edit)")
                
        self.register_hotkey()

    def show_preset_context_menu(self, index):
        if self.is_running:
            return 
            
        preset = self.presets[index]
        dialog = PresetEditDialog(
            preset['label'], 
            float(preset['time']), 
            float(preset.get('first_time', 6.00)),
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
            self.save_settings()
            
            # Update UI button (hide first loop time for cleaner UI)
            btn = self.preset_buttons[index]
            btn.setText(f"{new_label} ({new_time:.2f}s)")
            
            # If current preset, update display
            if self.current_preset_index == index:
                self.initial_time = new_time
                self.time_left = new_time
                self.update_display()

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
            
        self.update_circled_info_label()

    def update_circled_info_label(self):
        if not self.is_running or self.timer_mode != "disaster":
            self.disaster_btn.setText(f"{self.tr('circled_btn')}\n({self.circled_loop_time:.2f}s)")
        else:
            self.disaster_btn.setText("C-RUN")

    def tr(self, key):
        return TRANSLATIONS.get(self.language, TRANSLATIONS["en"]).get(key, key)

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("window_title"))
        if not self.is_running:
            self.start_btn.setText(self.tr("start_btn"))
        self.stop_btn.setText(self.tr("stop_btn"))
        self.latency_title_label.setText(self.tr("latency_label"))
        self.vol_title_label.setText(self.tr("volume_label"))
        self.update_circled_info_label()

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
        self.audio_out_count.setVolume(vol)
        self.audio_out_end.setVolume(vol)

    def start_timer(self):
        # NORMAL start interrupts disaster if it's running
        was_disaster = (self.is_running and self.timer_mode == "disaster")
        
        if not self.is_running or was_disaster:
            self.is_running = True
            self.timer_mode = "normal"
            
            preset = self.presets[self.current_preset_index]
            self.initial_time = float(preset['time'])
            
            # If completely fresh OR interrupting disaster, apply normal first_time
            fresh_start = (self.loop_count == 1 and abs(self.time_left - self.initial_time) < 0.001)
            if fresh_start or was_disaster:
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
            self.update_circled_info_label()
            self.disaster_btn.setStyleSheet("")
            self.timer.start()

    def start_disaster_timer(self):
        if not self.is_running and self.time_left > 0:
            self.is_running = True
            self.timer_mode = "disaster"
            
            self.initial_time = self.circled_loop_time
            self.time_left = self.circled_first_time
            self.loop_count = 1
            self.reset_triggers()
            self.update_display()
            
            self.latency_slider.setValue(0)
            self.latency_slider.setEnabled(True)
            self._slider_start_val = 0.0
            
            self.disaster_btn.setText("C-RUN")
            self.disaster_btn.setStyleSheet("color: #ffffff; border-color: #ffffff;")
            self.start_btn.setText("START")
            self.start_btn.setStyleSheet("")
            self.timer.start()

    def stop_timer(self):
        self.is_running = False
        self.timer_mode = "normal"
        self.timer.stop()
        self.start_btn.setText("START")
        self.start_btn.setStyleSheet("") 
        self.update_circled_info_label()
        self.disaster_btn.setStyleSheet("") 
        
        # Fully reset timer and loop count as requested
        preset = self.presets[self.current_preset_index]
        self.initial_time = float(preset['time'])
        self.time_left = self.initial_time
        self.loop_count = 1
        self.reset_triggers()
        self.latency_slider.setValue(0)
        self.latency_slider.setEnabled(False)
        self.update_display()

    def update_timer(self):
        self.time_left -= 0.01
        
        # Audio Triggers
        if self.time_left <= 5.01 and not self.warning_triggered:
            self.warning_triggered = True
            
            if self.timer_mode == "disaster":
                self.set_warning_visuals("red")
                self.player_5s_disaster.setPosition(0)
                self.player_5s_disaster.play()
            else:
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
        self.time_left = self.initial_time
        self.loop_count += 1 
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
        if not self.is_running and self.loop_count == 1:
            max_time = self.initial_time
        else:
            if self.timer_mode == "disaster":
                max_time = self.circled_first_time if self.loop_count == 1 else self.circled_loop_time
            else:
                preset = self.presets[self.current_preset_index]
                # First loop uses 'first_time', subsequent loops use 'initial_time' (normal time)
                max_time = float(preset.get('first_time', 5.00)) if self.loop_count == 1 else self.initial_time
        
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
