"""
Taskbar - Windows-like taskbar with start menu and running apps
"""

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QPushButton, QLabel, 
                             QMenu, QAction, QScrollArea, QFrame)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QFont

class Taskbar(QWidget):
    """Taskbar with start menu and running applications"""
    
    def __init__(self, desktop):
        super().__init__()
        self.desktop = desktop
        self.running_app_buttons = []
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFixedHeight(60)  # أكبر شوية
        
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2f;
                border-top: 2px solid #00ffcc;
            }
            QPushButton {
                background-color: #2a2a3b;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                margin: 5px;
                border-radius: 5px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #00ffcc;
                color: #1a1a2e;
            }
            QPushButton[highlight="true"] {
                background-color: #00ffcc;
                color: #1a1a2e;
                border: 1px solid #ffffff;
            }
            QLabel {
                color: #ffffff;
                padding: 10px;
                font-size: 14px;
            }
            QFrame {
                background-color: #2a2a3b;
                border-radius: 5px;
            }
        """)
        
        self.init_ui()
        self.position_taskbar()
        self.show()
        
        # Update time every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
    def init_ui(self):
        """Initialize taskbar UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Start button (أكبر)
        self.start_btn = QPushButton("◉ Vision Z")
        self.start_btn.setFixedHeight(45)
        self.start_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.start_btn.clicked.connect(self.show_start_menu)
        layout.addWidget(self.start_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFixedWidth(2)
        layout.addWidget(separator)
        
        # Running apps area ( Scroll area for many apps)
        apps_widget = QWidget()
        apps_layout = QHBoxLayout(apps_widget)
        apps_layout.setContentsMargins(0, 0, 0, 0)
        apps_layout.setSpacing(5)
        
        self.apps_container = apps_widget
        layout.addWidget(apps_widget, 1)  # Takes all available space
        
        layout.addStretch()
        
        # System tray icons
        self.notify_btn = QPushButton("🔔")
        self.notify_btn.setFixedSize(40, 45)
        self.notify_btn.clicked.connect(self.show_notifications)
        layout.addWidget(self.notify_btn)
        
        # Time display
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setFont(QFont("Arial", 11))
        self.time_label.setFixedWidth(120)
        self.update_time()
        layout.addWidget(self.time_label)
        
        # Shutdown button
        shutdown_btn = QPushButton("⏻")
        shutdown_btn.setFixedSize(50, 45)
        shutdown_btn.setFont(QFont("Arial", 14))
        shutdown_btn.clicked.connect(self.shutdown_system)
        layout.addWidget(shutdown_btn)
        
        self.setLayout(layout)
        
    def position_taskbar(self):
        """Position taskbar at bottom of screen"""
        screen_geometry = self.desktop.screen().geometry()
        self.setGeometry(0, screen_geometry.height() - 60, 
                        screen_geometry.width(), 60)
        
    def add_running_app(self, app_name, app_window):
        """Add a running application to taskbar"""
        # Check if already exists
        for btn in self.running_app_buttons:
            if btn.app_name == app_name:
                return
                
        app_btn = QPushButton(f"📌 {app_name}")
        app_btn.setFixedHeight(40)
        app_btn.setMinimumWidth(120)
        app_btn.app_name = app_name
        app_btn.app_window = app_window
        
        # Highlight on click
        app_btn.clicked.connect(lambda: self.bring_to_front(app_window, app_btn))
        
        # Add to layout
        self.apps_container.layout().addWidget(app_btn)
        self.running_app_buttons.append(app_btn)
        
    def remove_running_app(self, app_name):
        """Remove app from taskbar when closed"""
        for btn in self.running_app_buttons:
            if btn.app_name == app_name:
                btn.deleteLater()
                self.running_app_buttons.remove(btn)
                break
                
    def bring_to_front(self, window, button):
        """Bring window to front and highlight button"""
        # Reset all buttons highlight
        for btn in self.running_app_buttons:
            btn.setProperty("highlight", "false")
            btn.setStyleSheet("")
            
        # Highlight selected button
        button.setProperty("highlight", "true")
        button.setStyleSheet("""
            QPushButton {
                background-color: #00ffcc;
                color: #1a1a2e;
                border: 1px solid #ffffff;
            }
        """)
        
        # Bring window to front
        if window:
            window.raise_()
            window.activateWindow()
            
    def show_start_menu(self):
        """Display start menu"""
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e2f;
                color: #ffffff;
                border: 1px solid #00ffcc;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 30px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #00ffcc;
                color: #1a1a2e;
            }
        """)
        
        # Applications section
        apps_menu = menu.addMenu("📱 Applications")
        
        file_explorer_action = QAction("📁 File Explorer", self)
        file_explorer_action.triggered.connect(self.desktop.open_file_explorer)
        apps_menu.addAction(file_explorer_action)
        
        terminal_action = QAction("💻 Terminal", self)
        terminal_action.triggered.connect(self.desktop.open_terminal)
        apps_menu.addAction(terminal_action)
        
        task_manager_action = QAction("⚙️ Task Manager", self)
        task_manager_action.triggered.connect(self.desktop.open_task_manager)
        apps_menu.addAction(task_manager_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("🔧 Settings", self)
        settings_action.triggered.connect(self.desktop.open_settings)
        menu.addAction(settings_action)
        
        menu.addSeparator()
        
        # User info
        user_action = QAction(f"👤 {self.desktop.username}", self)
        user_action.setEnabled(False)
        menu.addAction(user_action)
        
        menu.addSeparator()
        
        # Logout
        logout_action = QAction("🚪 Logout", self)
        logout_action.triggered.connect(self.logout_system)
        menu.addAction(logout_action)
        
        # Show menu at button position
        menu.exec_(self.start_btn.mapToGlobal(self.start_btn.rect().bottomLeft()))
        
    def show_notifications(self):
        """Show notifications panel"""
        # Simplified for now
        self.desktop.kernel.notification_system.show_notification(
            "Notifications", "No new notifications", "info"
        )
        
    def update_time(self):
        """Update time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M %p")
        current_date = datetime.now().strftime("%Y-%m-%d")
        self.time_label.setText(f"{current_date}\n{current_time}")
        
    def shutdown_system(self):
        """Shutdown the system"""
        self.desktop.close()
        
    def logout_system(self):
        """Logout current user"""
        self.desktop.kernel.logout()