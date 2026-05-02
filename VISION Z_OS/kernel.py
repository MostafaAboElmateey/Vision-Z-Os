"""
Vision Z OS Kernel - Updated with process tracking
"""

import sys
from PyQt5.QtWidgets import QSplashScreen, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from user_manager import UserManager
from process_manager import ProcessManager
from ui.login_window import LoginWindow
from ui.desktop import Desktop
from ui.notification_system import NotificationSystem

class Kernel:
    """Main kernel class - heart of Vision Z OS"""
    
    def __init__(self):
        self.current_user = None
        self.user_manager = UserManager()
        self.process_manager = ProcessManager()
        self.desktop = None
        self.notification_system = NotificationSystem()
        self.boot_screen = None
        
        # Create system processes
        self.create_system_processes()
        
    def create_system_processes(self):
        """Create essential system processes"""
        self.process_manager.create_process("System Kernel", "system")
        self.process_manager.create_process("Window Manager", "system")
        self.process_manager.create_process("Process Manager", "system")
        
    def show_boot_screen(self):
        """Display boot screen with logo"""
        self.boot_screen = QSplashScreen()
        self.boot_screen.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        # Create boot screen content
        label = QLabel()
        label.setStyleSheet("""
            QLabel {
                background-color: #1a1a2e;
                color: #00ffcc;
                font-size: 48px;
                font-weight: bold;
                padding: 50px;
            }
        """)
        label.setText("""
        <div style='text-align: center;'>
            <h1 style='color: #00ffcc; font-size: 72px;'>Vision Z</h1>
            <h2 style='color: #ffffff;'>Operating System</h2>
            <p style='color: #888888; margin-top: 50px;'>Loading...</p>
            <p style='color: #00ffcc; font-size: 14px;'>Developed by Abu El-Maati OS Team</p>
        </div>
        """)
        label.setAlignment(Qt.AlignCenter)
        self.boot_screen.setPixmap(QPixmap(label.size()))
        self.boot_screen.show()
        
        # Update boot screen text
        QTimer.singleShot(1000, lambda: self.update_boot_status("Initializing kernel..."))
        QTimer.singleShot(1500, lambda: self.update_boot_status("Loading services..."))
        QTimer.singleShot(2000, lambda: self.update_boot_status("Starting process manager..."))
        QTimer.singleShot(2500, lambda: self.update_boot_status("Preparing desktop environment..."))
        
    def update_boot_status(self, message):
        """Update boot screen status"""
        if self.boot_screen:
            self.boot_screen.showMessage(message, Qt.AlignBottom | Qt.AlignCenter, Qt.white)
        
    def start_os(self):
        """Start the operating system"""
        self.boot_screen.close()
        self.show_login_screen()
        
    def show_login_screen(self):
        """Display login window"""
        self.login_window = LoginWindow(self.user_manager, self)
        self.login_window.show()
        
    def login_user(self, username, password):
        """Authenticate and login user — called ONLY from LoginWindow after auth passed"""
        self.current_user = username
        self.start_desktop()
        
    def register_user(self, username, password):
        """Register new user"""
        return self.user_manager.create_user(username, password)
        
    def start_desktop(self):
        """Launch desktop environment for current user"""
        # Create desktop process
        process_id = self.process_manager.create_process("Desktop Environment", "system")
        
        self.desktop = Desktop(self.current_user, self)
        self.desktop.process_id = process_id
        self.desktop.show()
        
        self.notification_system.show_notification(
            "Welcome to Vision Z OS",
            f"Welcome back, {self.current_user}!",
            "success"
        )
        
        # Auto-launch essential apps
        self.auto_launch_applications()
        
    def auto_launch_applications(self):
        """Auto-launch applications on desktop"""
        # These launch automatically when desktop starts
        QTimer.singleShot(1000, lambda: self.notification_system.show_notification(
            "System Ready", "Vision Z OS is ready to use", "info"
        ))
        
    def logout(self):
        """Logout current user"""
        if self.desktop:
            # Terminate user processes
            for process in self.process_manager.get_all_processes():
                if process.type != "system":
                    self.process_manager.terminate_process(process.pid)
            self.desktop.close()
        self.current_user = None
        self.show_login_screen()
        
    def shutdown(self):
        """Shutdown the system"""
        # Terminate all processes
        for process in self.process_manager.get_all_processes():
            self.process_manager.terminate_process(process.pid)
        QTimer.singleShot(0, lambda: sys.exit(0))