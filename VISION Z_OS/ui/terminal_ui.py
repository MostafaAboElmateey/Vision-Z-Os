"""
Terminal UI - Vision Z OS Terminal Emulator (USING Terminal Engine)
"""

from PyQt5.QtWidgets import (QMainWindow, QTextEdit, QLineEdit, QVBoxLayout, 
                             QWidget, QScrollBar)
from PyQt5.QtCore import Qt, QProcess, QTimer
from PyQt5.QtGui import QFont, QColor, QTextCursor, QKeySequence
from file_system import FileSystem
from terminal import Terminal  # ✅ استيراد المحرك
import os
import traceback


class TerminalUI(QMainWindow):
    """Vision Z OS Terminal Emulator"""
    
    def __init__(self, username, kernel):
        super().__init__()
        self.username = username
        self.kernel = kernel
        
        # ✅ استخدام نظام الملفات الجديد
        self.filesystem = FileSystem(username)
        
        # ✅ إنشاء محرك التيرمينال
        self.terminal = Terminal(
            filesystem=self.filesystem,
            process_manager=kernel.process_manager if hasattr(kernel, 'process_manager') else None
        )
        
        self.command_history = []
        self.history_index = -1
        
        self.init_ui()
        self.show_welcome()
        
    def init_ui(self):
        """Initialize terminal UI"""
        self.setWindowTitle(f"💻 Terminal - {self.username}@VisionZ")
        self.setGeometry(150, 150, 900, 600)
        self.setMinimumSize(600, 400)
        
        # Modern dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0a0a0f;
            }
            QTextEdit {
                background-color: #0a0a0f;
                color: #00ffcc;
                border: none;
                font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                padding: 10px;
                selection-background-color: #00ffcc;
                selection-color: #0a0a0f;
            }
            QLineEdit {
                background-color: #0d0d1a;
                color: #00ffcc;
                border: none;
                border-top: 1px solid #1a1a3a;
                font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                padding: 10px;
            }
            QLineEdit:focus {
                border-top: 1px solid #00ffcc;
            }
            QScrollBar:vertical {
                background-color: #0a0a0f;
                width: 10px;
            }
            QScrollBar::handle:vertical {
                background-color: #00ffcc;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Terminal output area
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        layout.addWidget(self.output_area)
        
        # Command input
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type command here...")
        self.command_input.returnPressed.connect(self.execute_command)
        layout.addWidget(self.command_input)
        
        # Setup command history navigation
        self.command_input.keyPressEvent = self.custom_key_press
        
        # Focus on input
        QTimer.singleShot(100, self.command_input.setFocus)
        
    def custom_key_press(self, event):
        """Handle special key presses"""
        key = event.key()
        
        if key == Qt.Key_Up:
            if self.history_index > 0:
                self.history_index -= 1
                self.command_input.setText(self.command_history[self.history_index])
            elif self.history_index == -1 and self.command_history:
                self.history_index = len(self.command_history) - 1
                self.command_input.setText(self.command_history[self.history_index])
            return
            
        elif key == Qt.Key_Down:
            if self.history_index >= 0 and self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_input.setText(self.command_history[self.history_index])
            else:
                self.history_index = -1
                self.command_input.clear()
            return
            
        QLineEdit.keyPressEvent(self.command_input, event)
        
    def show_welcome(self):
        """Display welcome message"""
        welcome_text = f"""
<span style="color: #00ffcc; font-weight: bold;">
╔══════════════════════════════════════════════════════════════╗
║           Vision Z OS Terminal v2.0                          ║
║           Developed by Abu El-Maati OS Team                  ║
╚══════════════════════════════════════════════════════════════╝
</span>

<span style="color: #888;">
Type 'help' for available commands.
</span>
"""
        self.output_area.append(welcome_text)
        self.show_prompt()
        
    def show_prompt(self):
        """Show command prompt"""
        current_path = self.filesystem.get_current_path()
        prompt = (
            f"<span style='color: #00ff88; font-weight: bold;'>{self.username}@VisionZ</span>"
            f":<span style='color: #00aaff;'>{current_path}</span>$ "
        )
        self.output_area.append(prompt)
        self.output_area.moveCursor(QTextCursor.End)
        
    def execute_command(self):
        """Execute entered command"""
        command = self.command_input.text().strip()
        
        if not command:
            self.show_prompt()
            return
            
        # Add to GUI history
        if not self.command_history or command != self.command_history[-1]:
            self.command_history.append(command)
        self.history_index = -1
        
        # Display command
        self.output_area.append(f"<span style='color: #ffffff;'>{command}</span>")
        
        # ✅ استخدام محرك التيرمينال للتنفيذ
        try:
            result = self.terminal.execute_command(command)
            
            if result == "CLEAR_SCREEN":
                self.output_area.clear()
            elif result:
                # عرض النتيجة - استبدال newlines بـ <br> عشان HTML
                formatted_result = result.replace('\n', '<br>')
                self.output_area.append(f"<span style='color: #e0e0e0;'>{formatted_result}</span>")
                
        except Exception as e:
            self.output_area.append(f"<span style='color: #ff4444;'>Error: {str(e)}</span>")
            traceback.print_exc()
            
        self.command_input.clear()
        self.show_prompt()
        
    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self.kernel, 'desktop') and hasattr(self.kernel.desktop, 'taskbar'):
            self.kernel.desktop.taskbar.remove_running_app("Terminal")
        event.accept()