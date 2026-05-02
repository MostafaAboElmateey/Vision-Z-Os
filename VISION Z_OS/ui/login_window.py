"""
Login Window - User authentication interface
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QTabWidget, 
                             QWidget, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

class LoginWindow(QDialog):
    """Login and registration window"""
    
    def __init__(self, user_manager, kernel):
        super().__init__()
        self.user_manager = user_manager
        self.kernel = kernel
        self.init_ui()
        
    def init_ui(self):
        """Initialize login UI"""
        self.setWindowTitle("Vision Z OS - Login")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        
        # Set window style
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                                          stop:0 #1a1a2e, stop:1 #16213e);
            }
            QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 2px solid #00ffcc;
                border-radius: 5px;
                background-color: #0f3460;
                color: #ffffff;
            }
            QPushButton {
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                background-color: #00ffcc;
                color: #1a1a2e;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00e6b8;
            }
            QTabWidget::pane {
                border: 1px solid #00ffcc;
                border-radius: 5px;
                background-color: rgba(15, 52, 96, 0.5);
            }
            QTabBar::tab {
                background-color: #0f3460;
                color: #ffffff;
                padding: 10px;
                margin: 5px;
                border-radius: 5px;
            }
            QTabBar::tab:selected {
                background-color: #00ffcc;
                color: #1a1a2e;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Vision Z OS")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont("Arial", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #00ffcc; margin: 20px;")
        layout.addWidget(title_label)
        
        # Tab widget for login/register
        tabs = QTabWidget()
        
        # Login tab
        login_tab = QWidget()
        login_layout = QVBoxLayout()
        
        username_label = QLabel("Username:")
        login_layout.addWidget(username_label)
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Enter username")
        login_layout.addWidget(self.login_username)
        
        password_label = QLabel("Password:")
        login_layout.addWidget(password_label)
        
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Enter password")
        login_layout.addWidget(self.login_password)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        login_layout.addWidget(login_btn)
        
        login_tab.setLayout(login_layout)
        
        # Register tab
        register_tab = QWidget()
        register_layout = QVBoxLayout()
        
        reg_username_label = QLabel("Username:")
        register_layout.addWidget(reg_username_label)
        
        self.reg_username = QLineEdit()
        self.reg_username.setPlaceholderText("Choose username")
        register_layout.addWidget(self.reg_username)
        
        reg_password_label = QLabel("Password:")
        register_layout.addWidget(reg_password_label)
        
        self.reg_password = QLineEdit()
        self.reg_password.setEchoMode(QLineEdit.Password)
        self.reg_password.setPlaceholderText("Choose password")
        register_layout.addWidget(self.reg_password)
        
        reg_confirm_label = QLabel("Confirm Password:")
        register_layout.addWidget(reg_confirm_label)
        
        self.reg_confirm = QLineEdit()
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        self.reg_confirm.setPlaceholderText("Confirm password")
        register_layout.addWidget(self.reg_confirm)
        
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register)
        register_layout.addWidget(register_btn)
        
        register_tab.setLayout(register_layout)
        
        tabs.addTab(login_tab, "Login")
        tabs.addTab(register_tab, "Register")
        
        layout.addWidget(tabs)
        
        # Info label
        info_label = QLabel("Developed by Abu El-Maati OS Team")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #888888; margin: 10px;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
        
    def login(self):
        """Handle login attempt"""
        username = self.login_username.text()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
            
        if self.user_manager.authenticate_user(username, password):
            self.login_password.clear()
            self.kernel.login_user(username, password)
            self.accept()
        else:
            self.login_password.clear()
            QMessageBox.critical(self, "Error", "Invalid username or password")
            
    def register(self):
        """Handle registration attempt"""
        username = self.reg_username.text()
        password = self.reg_password.text()
        confirm = self.reg_confirm.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please enter username and password")
            return
            
        if password != confirm:
            QMessageBox.warning(self, "Error", "Passwords do not match")
            return
            
        if self.user_manager.create_user(username, password):
            QMessageBox.information(self, "Success", 
                                   f"User {username} created successfully!\nPlease login.")
            self.login_username.setText(username)
            self.login_password.setText("")
            # Switch to login tab
            self.findChild(QTabWidget).setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "Error", "Username already exists")