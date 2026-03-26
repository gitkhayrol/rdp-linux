#!/usr/bin/env python3
import sys
import os
import subprocess
import json
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QComboBox, 
                           QSpinBox, QGroupBox, QFileDialog, QMessageBox, 
                           QTabWidget, QCheckBox, QFrame, QSizePolicy, 
                           QStackedWidget, QLineEdit, QTextEdit)
from PyQt6.QtCore import Qt, QProcess, QPropertyAnimation, QEasingCurve, QPoint, QSettings
from PyQt6.QtGui import QFont, QIcon, QPixmap, QColor, QPalette, QAction

class ArchRDPTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arch RDP Professional | @DevidLuice")
        self.setGeometry(100, 100, 850, 650)
        
        # Config paths for Arch Linux
        self.config_dir = Path.home() / ".config" / "arch-rdp-tool"
        self.config_file = self.config_dir / "settings.json"
        self.rdp_connections_file = self.config_dir / "connections.json"
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize RDP process
        self.rdp_process = None
        
        # Setup UI
        self.setup_palette()
        self.init_ui()
        
        # Ensure shared directory exists
        shared_folder = self.settings.get("shared_folder", str(Path.home() / "RDP_Shared"))
        os.makedirs(shared_folder, exist_ok=True)
    
    def load_settings(self):
        """Load settings from config file with defaults"""
        defaults = {
            "server_ip": "20.27.222.193",
            "username": "madtiger",
            "password": "",
            "shared_folder": str(Path.home() / "RDP_Shared"),
            "resolution": "Fullscreen",
            "gfx_mode": "Auto",
            "quality": "High",
            "clipboard": True,
            "audio": False,
            "printers": False,
            "smartcard": False,
            "drive": False,
            "nla": True,
            "validate_cert": False,
            "panel_always_visible": True,
            "window_management": True,
            "keyboard_layout": "us",
            "multi_monitor": False
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    return {**defaults, **loaded}
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return defaults
    
    def save_settings(self):
        """Save current settings to config file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def setup_palette(self):
        """Configure a modern dark theme palette"""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(25, 25, 25))
        palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197).lighter())
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        self.setPalette(palette)
        
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #fff;
            }
            QTabWidget::pane {
                border: 1px solid #444;
                border-radius: 3px;
                padding: 5px;
            }
            QTabBar::tab {
                background: #353535;
                color: #fff;
                padding: 8px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #5a5a5a;
                border-bottom: 2px solid #8e2dc5;
            }
            QPushButton {
                background-color: #5a5a5a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #6a6a6a;
            }
            QPushButton:pressed {
                background-color: #8e2dc5;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background: #454545;
                color: white;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
            }
        """)
    
    def init_ui(self):
        # Create menu bar
        self.create_menu_bar()
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # Header
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        # Logo and title
        title = QLabel("Arch Linux RDP Professional | Khayrol Islam ")
        title.setFont(QFont("Noto Sans", 16, QFont.Weight.Bold))
        header_layout.addWidget(title)
        
        # System info
        sys_info = QLabel(self.get_system_info())
        sys_info.setFont(QFont("Noto Sans", 9))
        header_layout.addWidget(sys_info, alignment=Qt.AlignmentFlag.AlignRight)
        
        main_layout.addWidget(header)
        
        # Tab widget
        self.tabs = QTabWidget()
        self.tabs.setFont(QFont("Noto Sans", 10))
        
        # Create tabs
        self.setup_connection_tab()
        self.setup_display_tab()
        self.setup_file_transfer_tab()
        self.setup_advanced_tab()
        self.setup_tools_tab()
        self.setup_monitoring_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
    
    def get_system_info(self):
        """Get Arch Linux system information"""
        try:
            with open("/etc/os-release") as f:
                os_info = f.read()
            arch = [line.split("=")[1].strip('"') 
                    for line in os_info.splitlines() 
                    if line.startswith("PRETTY_NAME")][0]
            
            kernel = subprocess.check_output(["uname", "-r"]).decode().strip()
            return f"{arch} | Kernel: {kernel}"
        except:
            return "Arch Linux"
    
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        new_action = QAction("New Connection", self)
        save_action = QAction("Save Settings", self)
        save_action.triggered.connect(self.save_settings)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(new_action)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")
        
        monitor_action = QAction("Performance Monitor", self)
        keymap_action = QAction("Keyboard Mapper", self)
        screenshot_action = QAction("Take Screenshot", self)
        
        tools_menu.addAction(monitor_action)
        tools_menu.addAction(keymap_action)
        tools_menu.addAction(screenshot_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("Help")
        
        about_action = QAction("About", self)
        docs_action = QAction("Documentation", self)
        
        help_menu.addAction(about_action)
        help_menu.addAction(docs_action)
    
    def setup_connection_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Connection Settings
        conn_group = QGroupBox("Connection Settings")
        conn_layout = QVBoxLayout()
        
        # Server Info
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("Server:"))
        self.server_input = QLineEdit(self.settings["server_ip"])
        self.server_input.textChanged.connect(lambda: self.update_setting("server_ip", self.server_input.text()))
        server_layout.addWidget(self.server_input)
        
        # Username
        user_layout = QHBoxLayout()
        user_layout.addWidget(QLabel("Username:"))
        self.user_input = QLineEdit(self.settings["username"])
        self.user_input.textChanged.connect(lambda: self.update_setting("username", self.user_input.text()))
        user_layout.addWidget(self.user_input)
        
        # Password
        pass_layout = QHBoxLayout()
        pass_layout.addWidget(QLabel("Password:"))
        self.pass_input = QLineEdit(self.settings["password"])
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.textChanged.connect(lambda: self.update_setting("password", self.pass_input.text()))
        pass_layout.addWidget(self.pass_input)
        
        # Shared Folder
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(QLabel("Shared Folder:"))
        self.folder_input = QLineEdit(self.settings["shared_folder"])
        self.folder_input.textChanged.connect(lambda: self.update_setting("shared_folder", self.folder_input.text()))
        folder_btn = QPushButton("Browse...")
        folder_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(folder_btn)
        
        conn_layout.addLayout(server_layout)
        conn_layout.addLayout(user_layout)
        conn_layout.addLayout(pass_layout)
        conn_layout.addLayout(folder_layout)
        conn_group.setLayout(conn_layout)
        layout.addWidget(conn_group)
        
        # Connection Buttons
        btn_frame = QFrame()
        btn_layout = QHBoxLayout(btn_frame)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.setStyleSheet("background-color: #2ecc71;")
        self.connect_btn.clicked.connect(self.start_rdp)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.setStyleSheet("background-color: #e74c3c;")
        self.disconnect_btn.clicked.connect(self.stop_rdp)
        self.disconnect_btn.setEnabled(False)
        
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.disconnect_btn)
        layout.addWidget(btn_frame)
        
        self.tabs.addTab(tab, "Connection")
    
    def setup_display_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Display Settings
        display_group = QGroupBox("Display Settings")
        display_layout = QVBoxLayout()
        
        # Resolution
        res_layout = QHBoxLayout()
        res_layout.addWidget(QLabel("Resolution:"))
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems(["Fullscreen", "1024x768", "1280x720", "1366x768", 
                                      "1600x900", "1920x1080", "2560x1440", "Custom"])
        self.resolution_combo.setCurrentText(self.settings["resolution"])
        self.resolution_combo.currentTextChanged.connect(lambda: self.update_setting("resolution", self.resolution_combo.currentText()))
        res_layout.addWidget(self.resolution_combo)
        
        # Custom Resolution
        self.custom_res_group = QWidget()
        custom_layout = QHBoxLayout(self.custom_res_group)
        custom_layout.addWidget(QLabel("Custom:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(800, 7680)
        self.width_spin.setValue(1024)
        custom_layout.addWidget(self.width_spin)
        custom_layout.addWidget(QLabel("x"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(600, 4320)
        self.height_spin.setValue(768)
        custom_layout.addWidget(self.height_spin)
        self.custom_res_group.setVisible(False)
        
        # Multi-monitor
        self.multi_monitor_cb = QCheckBox("Span across multiple monitors")
        self.multi_monitor_cb.setChecked(self.settings["multi_monitor"])
        self.multi_monitor_cb.stateChanged.connect(lambda: self.update_setting("multi_monitor", self.multi_monitor_cb.isChecked()))
        
        display_layout.addLayout(res_layout)
        display_layout.addWidget(self.custom_res_group)
        display_layout.addWidget(self.multi_monitor_cb)
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Graphics Settings
        graphics_group = QGroupBox("Graphics Settings")
        graphics_layout = QVBoxLayout()
        
        # Graphics Mode
        gfx_layout = QHBoxLayout()
        gfx_layout.addWidget(QLabel("Graphics Mode:"))
        self.gfx_combo = QComboBox()
        self.gfx_combo.addItems(["Auto", "H.264", "RFX", "RemoteFX"])
        self.gfx_combo.setCurrentText(self.settings["gfx_mode"])
        self.gfx_combo.currentTextChanged.connect(lambda: self.update_setting("gfx_mode", self.gfx_combo.currentText()))
        gfx_layout.addWidget(self.gfx_combo)
        
        # Quality
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["Auto", "Low", "Medium", "High", "Ultra"])
        self.quality_combo.setCurrentText(self.settings["quality"])
        self.quality_combo.currentTextChanged.connect(lambda: self.update_setting("quality", self.quality_combo.currentText()))
        quality_layout.addWidget(self.quality_combo)
        
        graphics_layout.addLayout(gfx_layout)
        graphics_layout.addLayout(quality_layout)
        graphics_group.setLayout(graphics_layout)
        layout.addWidget(graphics_group)
        
        self.tabs.addTab(tab, "Display")
    
    def setup_file_transfer_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File Transfer Group
        transfer_group = QGroupBox("File Transfer")
        transfer_layout = QVBoxLayout()
        
        # Transfer Buttons
        btn_layout = QHBoxLayout()
        self.upload_btn = QPushButton("Upload to Remote")
        self.upload_btn.clicked.connect(self.upload_file)
        self.download_btn = QPushButton("Download from Remote")
        self.download_btn.clicked.connect(self.download_file)
        btn_layout.addWidget(self.upload_btn)
        btn_layout.addWidget(self.download_btn)
        
        # Transfer Log
        self.transfer_log = QTextEdit()
        self.transfer_log.setReadOnly(True)
        self.transfer_log.setPlaceholderText("File transfer log will appear here...")
        
        transfer_layout.addLayout(btn_layout)
        transfer_layout.addWidget(self.transfer_log)
        transfer_group.setLayout(transfer_layout)
        layout.addWidget(transfer_group)
        
        self.tabs.addTab(tab, "File Transfer")
    
    def setup_advanced_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Redirection Options
        redirect_group = QGroupBox("Redirection Options")
        redirect_layout = QVBoxLayout()
        
        self.clipboard_cb = QCheckBox("Clipboard Redirection")
        self.clipboard_cb.setChecked(self.settings["clipboard"])
        self.clipboard_cb.stateChanged.connect(lambda: self.update_setting("clipboard", self.clipboard_cb.isChecked()))
        
        self.audio_cb = QCheckBox("Audio Redirection")
        self.audio_cb.setChecked(self.settings["audio"])
        self.audio_cb.stateChanged.connect(lambda: self.update_setting("audio", self.audio_cb.isChecked()))
        
        self.printer_cb = QCheckBox("Printer Redirection")
        self.printer_cb.setChecked(self.settings["printers"])
        self.printer_cb.stateChanged.connect(lambda: self.update_setting("printers", self.printer_cb.isChecked()))
        
        self.smartcard_cb = QCheckBox("Smart Card Redirection")
        self.smartcard_cb.setChecked(self.settings["smartcard"])
        self.smartcard_cb.stateChanged.connect(lambda: self.update_setting("smartcard", self.smartcard_cb.isChecked()))
        
        self.drive_cb = QCheckBox("Drive Redirection")
        self.drive_cb.setChecked(self.settings["drive"])
        self.drive_cb.stateChanged.connect(lambda: self.update_setting("drive", self.drive_cb.isChecked()))
        
        redirect_layout.addWidget(self.clipboard_cb)
        redirect_layout.addWidget(self.audio_cb)
        redirect_layout.addWidget(self.printer_cb)
        redirect_layout.addWidget(self.smartcard_cb)
        redirect_layout.addWidget(self.drive_cb)
        redirect_group.setLayout(redirect_layout)
        layout.addWidget(redirect_group)
        
        # Security Options
        security_group = QGroupBox("Security Settings")
        security_layout = QVBoxLayout()
        
        self.nla_cb = QCheckBox("Network Level Authentication (NLA)")
        self.nla_cb.setChecked(self.settings["nla"])
        self.nla_cb.stateChanged.connect(lambda: self.update_setting("nla", self.nla_cb.isChecked()))
        
        self.validate_cert_cb = QCheckBox("Validate Server Certificate")
        self.validate_cert_cb.setChecked(self.settings["validate_cert"])
        self.validate_cert_cb.stateChanged.connect(lambda: self.update_setting("validate_cert", self.validate_cert_cb.isChecked()))
        
        security_layout.addWidget(self.nla_cb)
        security_layout.addWidget(self.validate_cert_cb)
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # Window Management
        window_group = QGroupBox("Window Management")
        window_layout = QVBoxLayout()
        
        self.panel_cb = QCheckBox("Keep Control Panel Always Visible")
        self.panel_cb.setChecked(self.settings["panel_always_visible"])
        self.panel_cb.stateChanged.connect(lambda: self.update_setting("panel_always_visible", self.panel_cb.isChecked()))
        
        self.window_management_cb = QCheckBox("Enable Window Management")
        self.window_management_cb.setChecked(self.settings["window_management"])
        self.window_management_cb.stateChanged.connect(lambda: self.update_setting("window_management", self.window_management_cb.isChecked()))
        
        window_layout.addWidget(self.panel_cb)
        window_layout.addWidget(self.window_management_cb)
        window_group.setLayout(window_layout)
        layout.addWidget(window_group)
        
        self.tabs.addTab(tab, "Advanced")
    
    def setup_tools_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Keyboard Tools
        keyboard_group = QGroupBox("Keyboard Tools")
        keyboard_layout = QVBoxLayout()
        
        self.keyboard_combo = QComboBox()
        self.keyboard_combo.addItems(["us", "gb", "fr", "de", "es", "it", "jp"])
        self.keyboard_combo.setCurrentText(self.settings["keyboard_layout"])
        self.keyboard_combo.currentTextChanged.connect(lambda: self.update_setting("keyboard_layout", self.keyboard_combo.currentText()))
        
        keyboard_layout.addWidget(QLabel("Keyboard Layout:"))
        keyboard_layout.addWidget(self.keyboard_combo)
        
        keyboard_btn = QPushButton("Apply Keyboard Layout")
        keyboard_btn.clicked.connect(self.apply_keyboard_layout)
        keyboard_layout.addWidget(keyboard_btn)
        
        keyboard_group.setLayout(keyboard_layout)
        layout.addWidget(keyboard_group)
        
        # Screenshot Tools
        screenshot_group = QGroupBox("Screenshot Tools")
        screenshot_layout = QVBoxLayout()
        
        screenshot_btn = QPushButton("Take Screenshot")
        screenshot_btn.clicked.connect(self.take_screenshot)
        screenshot_layout.addWidget(screenshot_btn)
        
        screenshot_group.setLayout(screenshot_layout)
        layout.addWidget(screenshot_group)
        
        # Performance Tools
        perf_group = QGroupBox("Performance Tools")
        perf_layout = QVBoxLayout()
        
        monitor_btn = QPushButton("Start Performance Monitor")
        monitor_btn.clicked.connect(self.start_performance_monitor)
        perf_layout.addWidget(monitor_btn)
        
        perf_group.setLayout(perf_layout)
        layout.addWidget(perf_group)
        
        self.tabs.addTab(tab, "Tools")
    
    def setup_monitoring_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Connection Monitor
        monitor_group = QGroupBox("Connection Monitor")
        monitor_layout = QVBoxLayout()
        
        self.monitor_output = QTextEdit()
        self.monitor_output.setReadOnly(True)
        self.monitor_output.setPlaceholderText("Connection statistics will appear here...")
        
        monitor_layout.addWidget(self.monitor_output)
        monitor_group.setLayout(monitor_layout)
        layout.addWidget(monitor_group)
        
        # Resource Monitor
        resource_group = QGroupBox("Resource Usage")
        resource_layout = QVBoxLayout()
        
        self.resource_output = QTextEdit()
        self.resource_output.setReadOnly(True)
        self.resource_output.setPlaceholderText("Resource usage will appear here...")
        
        resource_layout.addWidget(self.resource_output)
        resource_group.setLayout(resource_layout)
        layout.addWidget(resource_group)
        
        self.tabs.addTab(tab, "Monitoring")
    
    def update_setting(self, key, value):
        """Update a setting and save to config"""
        self.settings[key] = value
        self.save_settings()
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Shared Folder")
        if folder:
            self.folder_input.setText(folder)
    
    def start_rdp(self):
        """Start RDP connection with all settings"""
        cmd = [
            "/v:" + self.settings["server_ip"],
            "/u:" + self.settings["username"],
            "/p:" + self.settings["password"],
            "/drive:shared," + self.settings["shared_folder"],
            "/cert:ignore" if not self.settings["validate_cert"] else "",
            "+auto-reconnect",
            "/gdi:sw",
            "/rfx",
            "-wallpaper"
        ]
        
        # Add display settings
        if self.settings["resolution"] == "Fullscreen":
            cmd.append("/f")
        elif self.settings["resolution"] == "Custom":
            cmd.append(f"/size:{self.width_spin.value()}x{self.height_spin.value()}")
        else:
            cmd.append(f"/size:{self.settings['resolution']}")
        
        if self.settings["multi_monitor"]:
            cmd.append("/multimon")
        
        # Add graphics settings
        if self.settings["gfx_mode"] == "H.264":
            cmd.append("/gfx:avc444")
        elif self.settings["gfx_mode"] in ["RFX", "RemoteFX"]:
            cmd.append("/rfx")
        
        # Add quality settings
        if self.settings["quality"] == "Low":
            cmd.append("/network:modem")
        elif self.settings["quality"] == "Medium":
            cmd.append("/network:broadband")
        elif self.settings["quality"] == "High":
            cmd.append("/network:broadband-high")
        elif self.settings["quality"] == "Ultra":
            cmd.append("/network:lan")
        
        # Add redirection options
        if self.settings["clipboard"]:
            cmd.extend(["+clipboard", "/clipboard"])
        
        if self.settings["audio"]:
            cmd.append("/sound")
        
        if self.settings["printers"]:
            cmd.append("/printer")
        
        if self.settings["smartcard"]:
            cmd.append("/smartcard")
        
        if self.settings["drive"]:
            cmd.append(f"/drive:home,{os.path.expanduser('~')}")
        
        if self.settings["nla"]:
            cmd.append("/sec:nla")
        
        if self.settings["panel_always_visible"]:
            cmd.append("/floatbar:sticky:on")
        
        if self.settings["window_management"]:
            cmd.extend(["/window-drag", "/menu-anims"])
        
        # Filter out empty arguments
        cmd = [arg for arg in cmd if arg]
        
        try:
            self.rdp_process = QProcess()
            print("Executing command:", "xfreerdp " + " ".join(cmd))  # Debug output
            self.rdp_process.start("xfreerdp", cmd)  # Pass program and args separately
            if not self.rdp_process.waitForStarted(3000):  # Wait 3 seconds for start
                raise Exception(f"Process failed to start: {self.rdp_process.errorString()}")
            self.rdp_process.readyReadStandardOutput.connect(self.update_monitor)
            self.rdp_process.readyReadStandardError.connect(self.update_monitor)
            
            self.connect_btn.setEnabled(False)
            self.disconnect_btn.setEnabled(True)
            self.status_bar.showMessage("Connected to remote desktop")
            
            # Start monitoring
            self.start_connection_monitor()
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Failed to start RDP: {str(e)}")
            self.status_bar.showMessage("Connection failed")
    
    def stop_rdp(self):
        """Stop RDP connection"""
        if self.rdp_process:
            self.rdp_process.terminate()
            self.rdp_process = None
            
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.status_bar.showMessage("Disconnected")
            
            # Stop monitoring
            self.stop_connection_monitor()
    
    def upload_file(self):
        """Upload file to remote via shared folder"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Upload", "", "All Files (*)"
        )
        
        if file_path:
            try:
                dest = os.path.join(self.settings["shared_folder"], os.path.basename(file_path))
                subprocess.run(["cp", file_path, dest], check=True)
                self.transfer_log.append(f"[UPLOAD] {os.path.basename(file_path)}")
            except Exception as e:
                self.transfer_log.append(f"[ERROR] Upload failed: {str(e)}")
    
    def download_file(self):
        """Download file from remote via shared folder"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File From Remote", "", "All Files (*)"
        )
        
        if file_path:
            try:
                src = os.path.join(self.settings["shared_folder"], os.path.basename(file_path))
                subprocess.run(["cp", src, file_path], check=True)
                self.transfer_log.append(f"[DOWNLOAD] {os.path.basename(file_path)}")
            except Exception as e:
                self.transfer_log.append(f"[ERROR] Download failed: {str(e)}")
    
    def apply_keyboard_layout(self):
        """Apply selected keyboard layout"""
        layout = self.settings["keyboard_layout"]
        try:
            subprocess.run(["setxkbmap", layout], check=True)
            self.status_bar.showMessage(f"Keyboard layout set to {layout}")
        except Exception as e:
            self.status_bar.showMessage(f"Failed to set keyboard layout: {str(e)}")
    
    def take_screenshot(self):
        """Take screenshot of remote session"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Screenshot", "", "PNG Images (*.png)"
        )
        
        if file_path:
            try:
                subprocess.run(["scrot", file_path], check=True)
                self.status_bar.showMessage(f"Screenshot saved to {file_path}")
            except Exception as e:
                self.status_bar.showMessage(f"Failed to take screenshot: {str(e)}")
    
    def start_performance_monitor(self):
        """Start performance monitoring"""
        try:
            self.perf_process = QProcess()
            self.perf_process.start("top", ["-b"])
            self.perf_process.readyReadStandardOutput.connect(self.update_resource_monitor)
            self.status_bar.showMessage("Performance monitor started")
        except Exception as e:
            self.status_bar.showMessage(f"Failed to start monitor: {str(e)}")
    
    def start_connection_monitor(self):
        """Start connection monitoring"""
        self.monitor_output.clear()
        self.monitor_output.append("Connection monitoring started...")
    
    def stop_connection_monitor(self):
        """Stop connection monitoring"""
        self.monitor_output.append("Connection monitoring stopped")
    
    def update_monitor(self):
        """Update connection monitor with output"""
        if self.rdp_process:
            output = self.rdp_process.readAllStandardOutput().data().decode()
            error = self.rdp_process.readAllStandardError().data().decode()
            
            if output:
                self.monitor_output.append(output)
            if error:
                self.monitor_output.append(f"ERROR: {error}")
            if not output and not error:
                self.monitor_output.append("No output from process yet...")
    
    def update_resource_monitor(self):
        """Update resource monitor with output"""
        if hasattr(self, 'perf_process'):
            output = self.perf_process.readAllStandardOutput().data().decode()
            self.resource_output.append(output)

if __name__ == "__main__":
    # Check for dependencies on Arch Linux
    try:
        subprocess.run(["which", "xfreerdp"], check=True, stdout=subprocess.PIPE)
        subprocess.run(["which", "setxkbmap"], check=True, stdout=subprocess.PIPE)
        subprocess.run(["which", "scrot"], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print("Missing dependencies. Please install:")
        print("sudo pacman -S freerdp setxkbmap scrot")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application font for Arch Linux
    font = QFont("Noto Sans", 10)
    app.setFont(font)
    
    window = ArchRDPTool()
    window.show()
    sys.exit(app.exec())
