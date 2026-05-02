"""
Settings Panel - System configuration with working wallpaper changer
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QFileDialog, QCheckBox,
                             QTabWidget, QWidget, QSlider, QGroupBox,
                             QListWidget, QListWidgetItem, QMessageBox)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QFont, QPalette, QBrush, QPainter, QLinearGradient, QColor
import os
import shutil
import time

class SettingsPanel(QDialog):
    """System settings configuration with wallpaper support"""
    
    def __init__(self, desktop):
        super().__init__(desktop)
        self.desktop = desktop
        self.init_ui()
        
    def init_ui(self):
        """Initialize settings UI"""
        self.setWindowTitle("⚙️ Vision Z Settings")
        self.setGeometry(300, 300, 750, 650)
        self.setMinimumSize(650, 550)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d3d;
            }
            QTabWidget::pane {
                background-color: #1e1e2e;
                border: 2px solid #00ffcc;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #3d3d4d;
                color: #ffffff;
                padding: 10px 25px;
                margin: 2px;
                border-radius: 8px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #00ffcc;
                color: #1a1a2e;
                font-weight: bold;
            }
            QGroupBox {
                color: #00ffcc;
                border: 1px solid #00ffcc;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px;
            }
            QLabel {
                color: #ffffff;
                padding: 5px;
                font-size: 12px;
            }
            QComboBox {
                background-color: #1e1e2e;
                color: #ffffff;
                border: 1px solid #00ffcc;
                padding: 8px;
                border-radius: 5px;
                min-width: 150px;
            }
            QPushButton {
                background-color: #00ffcc;
                color: #1a1a2e;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00e6b8;
            }
            QPushButton#danger {
                background-color: #ff4444;
                color: white;
            }
            QPushButton#danger:hover {
                background-color: #ff6666;
            }
            QListWidget {
                background-color: #1e1e2e;
                color: #ffffff;
                border: 1px solid #00ffcc;
                border-radius: 5px;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 5px;
            }
            QListWidget::item:selected {
                background-color: #00ffcc;
                color: #1a1a2e;
            }
            QListWidget::item:hover {
                background-color: #3d3d4d;
            }
            QSlider::groove:horizontal {
                border: 1px solid #00ffcc;
                height: 6px;
                background: #1e1e2e;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #00ffcc;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QCheckBox {
                color: #ffffff;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid #00ffcc;
            }
            QCheckBox::indicator:checked {
                background-color: #00ffcc;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("⚙️ Vision Z Settings")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 20, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00ffcc; margin: 15px;")
        layout.addWidget(title_label)
        
        # Tab widget
        tabs = QTabWidget()
        
        # Personalization tab (Wallpaper)
        personalization_tab = self.create_personalization_tab()
        tabs.addTab(personalization_tab, "🎨 Personalization")
        
        # System tab
        system_tab = self.create_system_tab()
        tabs.addTab(system_tab, "⚙️ System")
        
        # About tab
        about_tab = self.create_about_tab()
        tabs.addTab(about_tab, "ℹ️ About")
        
        layout.addWidget(tabs)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setFixedHeight(40)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
    def create_personalization_tab(self):
        """Create personalization tab with wallpaper changer"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        # Wallpaper section
        wallpaper_group = QGroupBox("Desktop Wallpaper")
        wallpaper_layout = QVBoxLayout(wallpaper_group)
        
        # Preview
        preview_label = QLabel("Current Wallpaper Preview:")
        preview_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        wallpaper_layout.addWidget(preview_label)
        
        self.preview_frame = QLabel()
        self.preview_frame.setFixedSize(350, 220)
        self.preview_frame.setStyleSheet("""
            border: 2px solid #00ffcc;
            border-radius: 10px;
            background-color: #1e1e2e;
        """)
        self.preview_frame.setAlignment(Qt.AlignCenter)
        wallpaper_layout.addWidget(self.preview_frame)
        
        # Update preview with current wallpaper
        self.update_wallpaper_preview()
        
        # Buttons for wallpaper selection
        buttons_layout = QHBoxLayout()
        
        # Built-in wallpapers
        builtin_btn = QPushButton("🎨 Built-in Wallpapers")
        builtin_btn.clicked.connect(self.show_builtin_wallpapers)
        buttons_layout.addWidget(builtin_btn)
        
        # Custom wallpaper from file
        custom_btn = QPushButton("📁 Choose from Computer")
        custom_btn.clicked.connect(self.choose_custom_wallpaper)
        buttons_layout.addWidget(custom_btn)
        
        wallpaper_layout.addLayout(buttons_layout)
        
        # Built-in wallpapers list
        self.wallpaper_list = QListWidget()
        self.wallpaper_list.setMaximumHeight(150)
        self.wallpaper_list.setVisible(False)
        self.wallpaper_list.itemClicked.connect(self.apply_builtin_wallpaper)
        wallpaper_layout.addWidget(self.wallpaper_list)
        
        layout.addWidget(wallpaper_group)
        
        # Theme selection
        theme_group = QGroupBox("Theme")
        theme_layout = QHBoxLayout(theme_group)
        
        theme_label = QLabel("Color Theme:")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark (Default)", "Light", "Blue Neon", "Green Matrix", "Purple Haze"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        
        theme_layout.addStretch()
        layout.addWidget(theme_group)
        
        layout.addStretch()
        return tab
        
    def create_system_tab(self):
        """Create system tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Sound settings
        sound_group = QGroupBox("Sound")
        sound_layout = QVBoxLayout(sound_group)
        
        self.sound_checkbox = QCheckBox("Enable System Sounds")
        self.sound_checkbox.setChecked(True)
        sound_layout.addWidget(self.sound_checkbox)
        
        # Volume slider
        volume_label = QLabel("Volume:")
        sound_layout.addWidget(volume_label)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        sound_layout.addWidget(self.volume_slider)
        
        self.volume_value_label = QLabel("70%")
        self.volume_value_label.setAlignment(Qt.AlignCenter)
        sound_layout.addWidget(self.volume_value_label)
        
        layout.addWidget(sound_group)
        
        # Notifications
        notif_group = QGroupBox("Notifications")
        notif_layout = QVBoxLayout(notif_group)
        
        self.notifications_checkbox = QCheckBox("Show Notifications")
        self.notifications_checkbox.setChecked(True)
        notif_layout.addWidget(self.notifications_checkbox)
        
        layout.addWidget(notif_group)
        
        # Reset section
        reset_group = QGroupBox("Reset Options")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_wallpaper_btn = QPushButton("Reset to Default Wallpaper")
        reset_wallpaper_btn.setObjectName("danger")
        reset_wallpaper_btn.clicked.connect(self.reset_wallpaper)
        reset_layout.addWidget(reset_wallpaper_btn)
        
        layout.addWidget(reset_group)
        
        layout.addStretch()
        return tab
        
    def create_about_tab(self):
        """Create about tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        about_text = QLabel("""
        <div style='text-align: center;'>
            <h1 style='color: #00ffcc; font-size: 36px;'>Vision Z OS</h1>
            <p style='color: #ffffff; font-size: 18px;'>Version 2.0</p>
            <br>
            <p style='color: #00ffcc; font-size: 14px;'>Developed by Abu El-Maati OS Team</p>
            <br>
            <h3 style='color: #ffffff;'>👥 Team Members:</h3>
            <p style='color: #cccccc;'>
            Mostafa Abu El-Maati
                            , Youssef Tarek
                            , Omar Tarek
                            , Hossam Mohamed
                            ,<br>
            Marwan
                            , Abdullah
                            , Hussein
                            , Youssef Hussein
                            , Amir
                            , Michael Medhat
                            ,<br>
            Mohamed, Ibrahim, Saeed , Roa Abu El-Magd, Solafa, Sara,<br>
            Rawan, Malak, Maha, Mena
            </p>
            <br>
            <p style='color: #888888;'>Vision Z OS - All Rights Reserved</p>
        </div>
        """)
        about_text.setWordWrap(True)
        about_text.setAlignment(Qt.AlignTop)
        layout.addWidget(about_text)
        
        layout.addStretch()
        return tab
        
    def update_wallpaper_preview(self):
        """Update wallpaper preview - FIXED"""
        try:
            current_wallpaper = getattr(self.desktop, 'current_wallpaper', 'default')
            print(f"[Settings] Current wallpaper: {current_wallpaper}")
            
            if current_wallpaper == 'default':
                self.preview_frame.setText("🎨\nDefault Wallpaper")
                self.preview_frame.setStyleSheet("""
                    border: 2px solid #00ffcc;
                    border-radius: 10px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                              stop:0 #1a1a2e, stop:1 #16213e);
                    font-size: 16px;
                    color: #00ffcc;
                """)
                self.preview_frame.setPixmap(QPixmap())
            else:
                # Try to load the image
                pixmap = QPixmap(current_wallpaper)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(350, 220, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.preview_frame.setPixmap(scaled)
                    self.preview_frame.setText("")
                    self.preview_frame.setStyleSheet("border: 2px solid #00ffcc; border-radius: 10px;")
                else:
                    self.preview_frame.setText("❌\nPreview not available")
                    self.preview_frame.setStyleSheet("""
                        border: 2px solid #ff4444;
                        border-radius: 10px;
                        font-size: 14px;
                        color: #ff4444;
                    """)
        except Exception as e:
            print(f"[Settings] Preview error: {e}")
            
    def show_builtin_wallpapers(self):
        """Show built-in wallpapers list"""
        self.wallpaper_list.setVisible(True)
        self.wallpaper_list.clear()
        
        builtins = [
            ("🌌 Galaxy", "galaxy"),
            ("🌄 Sunset", "sunset"),
            ("🌲 Forest", "forest"),
            ("🌊 Ocean", "ocean"),
            ("🎨 Abstract", "abstract"),
            ("⭐ Stars", "stars"),
        ]
        
        for name, value in builtins:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, value)
            self.wallpaper_list.addItem(item)
            
    def apply_builtin_wallpaper(self, item):
        """Apply built-in wallpaper - FIXED"""
        try:
            wallpaper_name = item.data(Qt.UserRole)
            print(f"[Settings] Applying built-in wallpaper: {wallpaper_name}")
            
            # Create gradient wallpaper
            self.create_gradient_wallpaper(wallpaper_name)
            
            # Get full path
            wallpaper_path = f"resources/wallpapers/{wallpaper_name}.jpg"
            
            # Apply to desktop
            self.desktop.set_wallpaper(wallpaper_path)
            
            # Update preview
            self.update_wallpaper_preview()
            
            # Show notification
            self.desktop.kernel.notification_system.show_notification(
                "Wallpaper Changed", 
                f"Applied '{item.text()}' wallpaper", 
                "success"
            )
            
            # Hide list after selection
            self.wallpaper_list.setVisible(False)
            
            QMessageBox.information(self, "Success", f"Wallpaper changed to '{item.text()}'!")
            
        except Exception as e:
            print(f"[Settings] Error applying wallpaper: {e}")
            QMessageBox.warning(self, "Error", f"Could not apply wallpaper: {str(e)}")
        
    def create_gradient_wallpaper(self, name):
        """Create gradient wallpaper programmatically - FIXED"""
        try:
            pixmap = QPixmap(1920, 1080)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            gradient = QLinearGradient(0, 0, 1920, 1080)
            
            # Preset gradients
            gradients = {
                "galaxy": [(0, QColor(25, 0, 51)), (0.5, QColor(75, 0, 130)), (1, QColor(138, 43, 226))],
                "sunset": [(0, QColor(255, 94, 77)), (0.5, QColor(255, 154, 0)), (1, QColor(255, 213, 0))],
                "forest": [(0, QColor(0, 51, 0)), (0.5, QColor(0, 100, 0)), (1, QColor(34, 139, 34))],
                "ocean": [(0, QColor(0, 51, 102)), (0.5, QColor(0, 102, 204)), (1, QColor(0, 153, 255))],
                "abstract": [(0, QColor(255, 0, 102)), (0.5, QColor(255, 0, 255)), (1, QColor(102, 0, 204))],
                "stars": [(0, QColor(10, 10, 30)), (0.5, QColor(20, 20, 50)), (1, QColor(30, 30, 70))]
            }
            
            if name in gradients:
                for pos, color in gradients[name]:
                    gradient.setColorAt(pos, color)
            else:
                # Default gradient
                gradient.setColorAt(0, QColor(30, 30, 46))
                gradient.setColorAt(1, QColor(22, 33, 62))
            
            painter.fillRect(pixmap.rect(), gradient)
            painter.end()
            
            # Ensure directory exists
            os.makedirs("resources/wallpapers", exist_ok=True)
            
            # Save the image
            save_path = f"resources/wallpapers/{name}.jpg"
            pixmap.save(save_path, "JPG", 90)
            print(f"[Settings] Created wallpaper: {save_path}")
            
        except Exception as e:
            print(f"[Settings] Error creating gradient: {e}")
        
    def choose_custom_wallpaper(self):
        """Choose custom wallpaper from computer - FIXED"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Choose Wallpaper", 
                "", 
                "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
            )
            
            if file_path:
                print(f"[Settings] Selected custom wallpaper: {file_path}")
                
                # Create resources directory if not exists
                os.makedirs("resources/wallpapers", exist_ok=True)
                
                # Generate unique filename
                timestamp = int(time.time())
                filename = f"custom_{timestamp}_{os.path.basename(file_path)}"
                dest_path = os.path.join("resources/wallpapers", filename)
                
                # Copy the file
                shutil.copy2(file_path, dest_path)
                
                # Apply wallpaper
                self.desktop.set_wallpaper(dest_path)
                
                # Update preview
                self.update_wallpaper_preview()
                
                # Show notification
                self.desktop.kernel.notification_system.show_notification(
                    "Wallpaper Changed", 
                    "Custom wallpaper applied successfully!", 
                    "success"
                )
                
                QMessageBox.information(self, "Success", "Wallpaper changed successfully!")
                
        except Exception as e:
            print(f"[Settings] Error choosing custom wallpaper: {e}")
            QMessageBox.warning(self, "Error", f"Could not set wallpaper: {str(e)}")
                
    def reset_wallpaper(self):
        """Reset to default wallpaper - FIXED"""
        try:
            print("[Settings] Resetting to default wallpaper")
            self.desktop.set_wallpaper("default")
            self.update_wallpaper_preview()
            self.desktop.kernel.notification_system.show_notification(
                "Wallpaper Reset", 
                "Default wallpaper applied", 
                "info"
            )
            QMessageBox.information(self, "Reset", "Wallpaper reset to default!")
        except Exception as e:
            print(f"[Settings] Error resetting wallpaper: {e}")
            QMessageBox.warning(self, "Error", f"Could not reset wallpaper: {str(e)}")
        
    def change_theme(self, theme):
        """Change system theme"""
        if theme == "Dark (Default)":
            self.desktop.set_dark_theme()
        elif theme == "Light":
            # Simple light theme
            light_palette = self.palette()
            light_palette.setColor(QPalette.Window, Qt.white)
            light_palette.setColor(QPalette.WindowText, Qt.black)
            self.desktop.setPalette(light_palette)
            
        self.desktop.kernel.notification_system.show_notification(
            "Theme Changed", f"Applied {theme} theme", "info"
        )
        
    def on_volume_changed(self, value):
        """Handle volume change"""
        self.volume_value_label.setText(f"{value}%")