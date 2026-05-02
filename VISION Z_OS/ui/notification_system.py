"""
Notification System - Popup notifications
"""

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont

class Notification(QWidget):
    """Individual notification popup"""
    
    def __init__(self, title, message, notif_type="info", parent=None):
        super().__init__(parent)
        self.title = title
        self.message = message
        self.notif_type = notif_type
        self.init_ui()
        
        # Auto-close after 5 seconds
        QTimer.singleShot(5000, self.close_animation)
        
    def init_ui(self):
        """Initialize notification UI"""
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Set style based on type
        colors = {
            "info": "#00ffcc",
            "success": "#00ff00",
            "warning": "#ffaa00",
            "error": "#ff4444"
        }
        
        color = colors.get(self.notif_type, "#00ffcc")
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: #2d2d3d;
                border-left: 4px solid {color};
                border-radius: 5px;
            }}
            QLabel {{
                color: #ffffff;
                padding: 5px;
            }}
            QLabel#title {{
                font-weight: bold;
                color: {color};
            }}
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(self.title)
        title_label.setObjectName("title")
        layout.addWidget(title_label)
        
        # Message
        msg_label = QLabel(self.message)
        msg_label.setWordWrap(True)
        layout.addWidget(msg_label)
        
        self.setLayout(layout)
        self.setFixedSize(300, 80)
        
    def show_animation(self):
        """Animate notification appearance"""
        self.show()
        
    def close_animation(self):
        """Animate notification disappearance"""
        self.close()

class NotificationSystem:
    """Manages system notifications"""
    
    def __init__(self):
        self.notifications = []
        
    def show_notification(self, title, message, notif_type="info"):
        """Display a notification"""
        notification = Notification(title, message, notif_type)
        notification.show_animation()
        self.notifications.append(notification)
        
        # Position notification at bottom right
        from PyQt5.QtWidgets import QDesktopWidget
        screen_geometry = QDesktopWidget().availableGeometry()
        offset = (len(self.notifications) - 1) * (notification.height() + 5)
        notification.move(
            screen_geometry.width() - notification.width() - 15,
            screen_geometry.height() - notification.height() - 15 - offset
        )
        # Clean up closed notifications
        self.notifications = [n for n in self.notifications if n.isVisible()]