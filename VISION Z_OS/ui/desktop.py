"""
Desktop Environment - Complete desktop with wallpaper support (FIXED WALLPAPER ISSUE)
"""

from PyQt5.QtWidgets import (QMainWindow, QDesktopWidget, QMenu, QAction, 
                             QFileDialog, QMessageBox, QVBoxLayout, QWidget,
                             QPushButton, QGridLayout, QScrollArea, QLabel,
                             QInputDialog, QApplication)
from PyQt5.QtCore import Qt, QPoint, QSize, QTimer
from PyQt5.QtGui import QPixmap, QColor, QPalette, QBrush, QIcon, QPainter, QFont
from PyQt5.QtGui import QPixmap, QColor, QPalette, QBrush, QIcon, QPainter, QFont, QLinearGradient
from ui.taskbar import Taskbar
from ui.file_explorer import FileExplorer
from ui.terminal_ui import TerminalUI
from ui.task_manager import TaskManagerWindow
from ui.settings_panel import SettingsPanel
from file_system import FileSystem
import os


class DesktopIcon(QPushButton):
    """Desktop application icon with drag support"""
    
    def __init__(self, name, icon_text, app_function, parent=None):
        super().__init__(parent)
        self.name = name
        self.icon_text = icon_text
        self.app_function = app_function
        self.drag_start_position = None
        
        self.setFixedSize(110, 110)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip(f"Open {name}")
        
        # جعل الأيقونة شفافة لظهور الخلفية
        self.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 46, 0.7);
                border: 1px solid rgba(0, 255, 204, 0.5);
                border-radius: 12px;
                color: white;
                font-size: 12px;
                font-weight: bold;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 204, 0.3);
                border: 2px solid #00ffcc;
            }
            QPushButton:pressed {
                background-color: rgba(0, 255, 204, 0.5);
                border: 2px solid #ffffff;
            }
        """)
        
        self.setText(f"{icon_text}\n{name}")
        self.clicked.connect(self.launch_app)
        
    def launch_app(self):
        """Launch the associated application with visual feedback"""
        if self.app_function:
            self.app_function()


class Desktop(QMainWindow):
    """Main desktop environment with icons and wallpaper support"""
    
    def __init__(self, username, kernel):
        super().__init__()
        self.username = username
        self.kernel = kernel
        self.running_windows = []
        self.current_wallpaper = "default"
        self._wallpaper_pixmap = QPixmap()
        self.desktop_fs = FileSystem(username)
        self.desktop_icons = []
        
        # تحميل الخلفية المحفوظة
        self.load_saved_wallpaper()
        
        # 🔥 مهم: إعداد الواجهة أولاً
        self.init_ui()
        
        # إنشاء مجلد Desktop
        self.ensure_desktop_directory()
        
    def load_saved_wallpaper(self):
        """Load saved wallpaper from user settings"""
        try:
            if hasattr(self.kernel.user_manager, 'db_manager'):
                settings = self.kernel.user_manager.db_manager.get_user_settings(self.username)
                if settings and settings.get('wallpaper') and settings['wallpaper'] != 'default':
                    saved_wallpaper = settings['wallpaper']
                    if os.path.exists(saved_wallpaper):
                        self.current_wallpaper = saved_wallpaper
                        print(f"[Desktop] Loaded saved wallpaper: {saved_wallpaper}")
                    else:
                        self.current_wallpaper = "default"
                else:
                    self.current_wallpaper = "default"
        except Exception as e:
            print(f"[Desktop] Could not load saved wallpaper: {e}")
            self.current_wallpaper = "default"
        
    def ensure_desktop_directory(self):
        """Ensure Desktop directory exists"""
        try:
            if not self.desktop_fs.resolve_path("/Desktop"):
                self.desktop_fs.create_directory("Desktop", "/")
                print("[Desktop] Created Desktop directory")
        except Exception as e:
            print(f"[Desktop] Error ensuring Desktop directory: {e}")
        
    def init_ui(self):
        """Initialize desktop UI"""
        self.setWindowTitle(f"Vision Z OS - {self.username}")
        self.setWindowState(Qt.WindowMaximized)
        
        # 🔥 المهم: جعل النافذة الرئيسية شفافة
        self.setAttribute(Qt.WA_TranslucentBackground, False)  # النافذة الرئيسية ليست شفافة
        
        # 🔥 تعيين الخلفية أولاً
        self.set_wallpaper(self.current_wallpaper)
        
        # 🔥 إنشاء Central Widget شفاف
        central_widget = QWidget()
        central_widget.setObjectName("central_widget")
        # 🔥 جعل الـ central widget شفاف ليظهر الـ painEvent
        central_widget.setAttribute(Qt.WA_TranslucentBackground)
        central_widget.setAutoFillBackground(False)
        # 🔥 مهم: إزالة أي لون خلفية
        central_widget.setStyleSheet("""
            QWidget#central_widget {
                background: transparent;
                border: none;
            }
        """)
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 0)
        main_layout.setSpacing(0)
        
        # 🔥 Scroll area شفاف بالكامل
        scroll_area = QScrollArea()
        scroll_area.setObjectName("scroll_area")
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # 🔥 جعل scroll area شفاف
        scroll_area.setAttribute(Qt.WA_TranslucentBackground)
        scroll_area.setAutoFillBackground(False)
        scroll_area.viewport().setAttribute(Qt.WA_TranslucentBackground)
        scroll_area.viewport().setAutoFillBackground(False)
        scroll_area.setFrameShape(QScrollArea.NoFrame)  # إزالة الإطار
        
        scroll_area.setStyleSheet("""
            QScrollArea#scroll_area {
                background: transparent;
                border: none;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background-color: rgba(0, 0, 0, 0.3);
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(0, 255, 204, 0.6);
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(0, 255, 204, 0.8);
            }
            QScrollBar:horizontal {
                background-color: rgba(0, 0, 0, 0.3);
                height: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:horizontal {
                background-color: rgba(0, 255, 204, 0.6);
                border-radius: 6px;
                min-width: 30px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                width: 0px;
                height: 0px;
            }
        """)
        
        # 🔥 Icons container - شفاف بالكامل
        icons_widget = QWidget()
        icons_widget.setObjectName("icons_widget")
        icons_widget.setAttribute(Qt.WA_TranslucentBackground)
        icons_widget.setAutoFillBackground(False)
        icons_widget.setStyleSheet("""
            QWidget#icons_widget {
                background: transparent;
                border: none;
            }
        """)
        
        self.icons_layout = QGridLayout(icons_widget)
        self.icons_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.icons_layout.setSpacing(25)
        self.icons_layout.setContentsMargins(20, 20, 20, 20)
        
        # Add desktop icons
        self.add_desktop_icons()
        
        scroll_area.setWidget(icons_widget)
        main_layout.addWidget(scroll_area)
        
        # Create taskbar
        self.taskbar = Taskbar(self)
        self.taskbar.show()
        
        # Enable context menu
        central_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        central_widget.customContextMenuRequested.connect(self.show_desktop_menu)
        
        # Enable drag and drop for wallpaper
        self.setAcceptDrops(True)
        
    def add_desktop_icons(self):
        """Add application icons to desktop"""
        apps = [
            ("File Explorer", "📁", self.open_file_explorer),
            ("Terminal", "💻", self.open_terminal),
            ("Task Manager", "⚙️", self.open_task_manager),
            ("Settings", "🔧", self.open_settings),
        ]
        
        # إزالة الأيقونات القديمة
        for icon in self.desktop_icons:
            self.icons_layout.removeWidget(icon)
            icon.deleteLater()
        self.desktop_icons.clear()
        
        for i, (name, icon, function) in enumerate(apps):
            row = i // 4
            col = i % 4
            icon_btn = DesktopIcon(name, icon, function)
            self.desktop_icons.append(icon_btn)
            self.icons_layout.addWidget(icon_btn, row, col)
        
    def set_wallpaper(self, wallpaper_source):
        """تغيير خلفية سطح المكتب مع إصلاح مشكلة الجزء الأسود"""
        try:
            print(f"[Desktop] Setting wallpaper: {wallpaper_source}")

            if wallpaper_source == "default" or wallpaper_source == "":
                # خلفية افتراضية
                pixmap = QPixmap(1920, 1080)
                pixmap.fill(QColor(30, 30, 46))
                
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                
                # رسم تدرج لوني جميل
                gradient = QLinearGradient(0, 0, 1920, 1080)
                gradient.setColorAt(0, QColor(30, 30, 46))
                gradient.setColorAt(0.5, QColor(40, 40, 60))
                gradient.setColorAt(1, QColor(30, 30, 46))
                painter.fillRect(pixmap.rect(), gradient)
                
                painter.setPen(QColor(0, 255, 204))
                painter.setFont(QFont("Arial", 48, QFont.Bold))
                painter.drawText(pixmap.rect(), Qt.AlignCenter, "Vision Z OS")
                
                painter.setFont(QFont("Arial", 12))
                painter.setPen(QColor(255, 255, 255, 150))
                painter.drawText(
                    pixmap.rect().adjusted(0, 60, 0, 0),
                    Qt.AlignCenter,
                    f"Welcome, {self.username}"
                )
                painter.end()
                
                self.current_wallpaper = "default"
            else:
                if os.path.exists(wallpaper_source):
                    pixmap = QPixmap(wallpaper_source)
                    if pixmap.isNull():
                        print(f"[Desktop] Invalid image file: {wallpaper_source}")
                        return self.set_wallpaper("default")
                    self.current_wallpaper = wallpaper_source
                else:
                    print(f"[Desktop] Wallpaper file not found: {wallpaper_source}")
                    return self.set_wallpaper("default")

            # 🔥 تصغير الصورة لتناسب الشاشة
            screen_geometry = QDesktopWidget().availableGeometry()
            screen_size = QApplication.primaryScreen().size()
            
            # استخدام حجم الشاشة الكامل
            self._wallpaper_pixmap = pixmap.scaled(
                screen_size.width(),
                screen_size.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            )
            
            # 🔥 قص الصورة لتتناسب مع الشاشة
            if (self._wallpaper_pixmap.width() != screen_size.width() or 
                self._wallpaper_pixmap.height() != screen_size.height()):
                # قص من المنتصف
                x = (self._wallpaper_pixmap.width() - screen_size.width()) // 2
                y = (self._wallpaper_pixmap.height() - screen_size.height()) // 2
                self._wallpaper_pixmap = self._wallpaper_pixmap.copy(
                    x, y, 
                    screen_size.width(), 
                    screen_size.height()
                )

            # حفظ الإعدادات
            self.save_wallpaper_setting()

            # 🔥 تحديث الواجهة بالكامل
            self.update()
            self.repaint()  # فرض إعادة رسم فورية
            
            print(f"[Desktop] Wallpaper applied successfully: {self.current_wallpaper}")

        except Exception as e:
            print(f"[Desktop] Error setting wallpaper: {e}")
            if wallpaper_source != "default":
                self.set_wallpaper("default")
    
    def save_wallpaper_setting(self):
        """Save wallpaper setting to user profile"""
        try:
            if hasattr(self, 'username') and hasattr(self, 'kernel'):
                if hasattr(self.kernel.user_manager, 'db_manager'):
                    self.kernel.user_manager.db_manager.update_user_settings(
                        self.username, {'wallpaper': self.current_wallpaper}
                    )
                    print("[Desktop] Wallpaper setting saved")
        except Exception as e:
            print(f"[Desktop] Could not save wallpaper setting: {e}")

    def paintEvent(self, event):
        """🔥 رسم الخلفية مباشرة على النافذة الرئيسية"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        if hasattr(self, '_wallpaper_pixmap') and not self._wallpaper_pixmap.isNull():
            # رسم الصورة على كامل النافذة
            painter.drawPixmap(self.rect(), self._wallpaper_pixmap)
        else:
            # رسم خلفية افتراضية إذا لم تكن الصورة موجودة
            painter.fillRect(self.rect(), QColor(30, 30, 46))
            painter.setPen(QColor(0, 255, 204))
            painter.setFont(QFont("Arial", 48, QFont.Bold))
            painter.drawText(self.rect(), Qt.AlignCenter, "Vision Z OS")
        
        painter.end()
    
    def resizeEvent(self, event):
        """إعادة تحجيم الخلفية عند تغيير حجم النافذة"""
        super().resizeEvent(event)
        # إعادة تحميل الخلفية لتناسب الحجم الجديد
        if hasattr(self, 'current_wallpaper'):
            self.set_wallpaper(self.current_wallpaper)
    
    def dragEnterEvent(self, event):
        """Handle drag enter for wallpaper files"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """Handle dropping image files as wallpaper"""
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                self.set_wallpaper(file_path)
                if hasattr(self.kernel, 'notification_system'):
                    self.kernel.notification_system.show_notification(
                        "🖼️ Wallpaper Changed",
                        f"New wallpaper applied",
                        "success"
                    )
                break
        
    def show_desktop_menu(self, position):
        """Show right-click context menu on desktop"""
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(30, 30, 46, 0.95);
                color: white;
                border: 1px solid #00ffcc;
                border-radius: 8px;
                padding: 5px;
                min-width: 200px;
            }
            QMenu::item {
                padding: 10px 30px;
                margin: 2px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #00ffcc;
                color: #1a1a2e;
                font-weight: bold;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3a3a5a;
                margin: 5px 10px;
            }
        """)
        
        # New submenu
        new_menu = QMenu("✨ New", menu)
        new_menu.setStyleSheet(menu.styleSheet())
        
        create_file_action = QAction("📄 Text File", self)
        create_file_action.triggered.connect(lambda: self.create_file_on_desktop(".txt"))
        new_menu.addAction(create_file_action)
        
        create_folder_action = QAction("📁 Folder", self)
        create_folder_action.triggered.connect(self.create_folder_on_desktop)
        new_menu.addAction(create_folder_action)
        
        menu.addMenu(new_menu)
        menu.addSeparator()
        
        change_wallpaper_action = QAction("🖼️ Change Wallpaper", self)
        change_wallpaper_action.triggered.connect(self.change_wallpaper_dialog)
        menu.addAction(change_wallpaper_action)
        
        reset_wallpaper_action = QAction("🔄 Reset Wallpaper", self)
        reset_wallpaper_action.triggered.connect(lambda: self.set_wallpaper("default"))
        menu.addAction(reset_wallpaper_action)
        
        menu.addSeparator()
        
        refresh_action = QAction("🔄 Refresh Desktop", self)
        refresh_action.triggered.connect(self.refresh_desktop)
        menu.addAction(refresh_action)
        
        personalize_action = QAction("🎨 Personalize", self)
        personalize_action.triggered.connect(self.open_settings)
        menu.addAction(personalize_action)
        
        menu.addSeparator()
        
        file_explorer_action = QAction("📂 File Explorer", self)
        file_explorer_action.triggered.connect(self.open_file_explorer)
        menu.addAction(file_explorer_action)
        
        terminal_action = QAction("💻 Terminal", self)
        terminal_action.triggered.connect(self.open_terminal)
        menu.addAction(terminal_action)
        
        task_manager_action = QAction("⚙️ Task Manager", self)
        task_manager_action.triggered.connect(self.open_task_manager)
        menu.addAction(task_manager_action)
        
        menu.exec_(self.mapToGlobal(position))
    
    def change_wallpaper_dialog(self):
        """Open file dialog to select wallpaper"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Wallpaper",
            os.path.expanduser("~"),
            "Images (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.set_wallpaper(file_path)
            if hasattr(self.kernel, 'notification_system'):
                self.kernel.notification_system.show_notification(
                    "🖼️ Wallpaper Updated",
                    "Desktop wallpaper has been changed",
                    "success"
                )
        
    def create_file_on_desktop(self, extension=".txt"):
        """Create new file on desktop"""
        name, ok = QInputDialog.getText(
            self,
            "Create File",
            "Enter file name:",
            text=f"NewFile{extension}"
        )
        if ok and name:
            if '.' not in name:
                name += extension
            if self.desktop_fs.create_file(name, "", "/Desktop"):
                if hasattr(self.kernel, 'notification_system'):
                    self.kernel.notification_system.show_notification(
                        "✅ File Created",
                        f"Created: {name} on Desktop",
                        "success"
                    )
                self.refresh_file_explorers()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Cannot create file: {name}"
                )
                
    def create_folder_on_desktop(self):
        """Create new folder on desktop"""
        name, ok = QInputDialog.getText(
            self,
            "Create Folder",
            "Enter folder name:",
            text="NewFolder"
        )
        if ok and name:
            if self.desktop_fs.create_directory(name, "/Desktop"):
                if hasattr(self.kernel, 'notification_system'):
                    self.kernel.notification_system.show_notification(
                        "✅ Folder Created",
                        f"Created folder: {name} on Desktop",
                        "success"
                    )
                self.refresh_file_explorers()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Cannot create folder: {name}"
                )
    
    def refresh_file_explorers(self):
        """Refresh all open file explorer windows"""
        for window in self.running_windows:
            if isinstance(window, FileExplorer):
                try:
                    window.refresh_files()
                except Exception as e:
                    print(f"[Desktop] Error refreshing file explorer: {e}")
            
    def refresh_desktop(self):
        """Refresh desktop view"""
        self.update()
        self.repaint()
        if hasattr(self.kernel, 'notification_system'):
            self.kernel.notification_system.show_notification(
                "🔄 Desktop Refreshed",
                "Desktop has been refreshed",
                "info"
            )
        
    def open_file_explorer(self):
        """Open file explorer window"""
        process_id = self.kernel.process_manager.create_process("File Explorer", "app")
        explorer = FileExplorer(self.username, self.kernel)
        explorer.process_id = process_id
        explorer.show()
        self.running_windows.append(explorer)
        
        if hasattr(self, 'taskbar'):
            self.taskbar.add_running_app("File Explorer", explorer)
            
        original_close = explorer.closeEvent
        def handle_close(event, window=explorer):
            if window in self.running_windows:
                self.running_windows.remove(window)
            if hasattr(self, 'taskbar'):
                self.taskbar.remove_running_app("File Explorer")
            original_close(event)
        explorer.closeEvent = handle_close
        
        if hasattr(self.kernel, 'notification_system'):
            self.kernel.notification_system.show_notification(
                "🚀 Application Launched",
                "File Explorer started",
                "info"
            )
        
    def open_terminal(self):
        """Open terminal window"""
        process_id = self.kernel.process_manager.create_process("Terminal", "app")
        terminal = TerminalUI(self.username, self.kernel)
        terminal.process_id = process_id
        terminal.show()
        self.running_windows.append(terminal)
        
        if hasattr(self, 'taskbar'):
            self.taskbar.add_running_app("Terminal", terminal)
            
        original_close = terminal.closeEvent
        def handle_close(event, window=terminal):
            if window in self.running_windows:
                self.running_windows.remove(window)
            if hasattr(self, 'taskbar'):
                self.taskbar.remove_running_app("Terminal")
            original_close(event)
        terminal.closeEvent = handle_close
        
        if hasattr(self.kernel, 'notification_system'):
            self.kernel.notification_system.show_notification(
                "🚀 Application Launched",
                "Terminal started",
                "info"
            )
        
    def open_settings(self):
        """Open settings panel"""
        settings = SettingsPanel(self)
        if settings.exec_():
            # تحديث الخلفية إذا تغيرت
            self.load_saved_wallpaper()
            self.set_wallpaper(self.current_wallpaper)
            self.refresh_desktop()
        
    def open_task_manager(self):
        """Open task manager window"""
        task_manager = TaskManagerWindow(self.kernel.process_manager, self)
        task_manager.show()
        self.running_windows.append(task_manager)
        
        if hasattr(self, 'taskbar'):
            self.taskbar.add_running_app("Task Manager", task_manager)
        
    def closeEvent(self, event):
        """Handle desktop close event"""
        reply = QMessageBox.question(
            self,
            'Shutdown Vision Z OS',
            'Are you sure you want to shutdown Vision Z OS?\n\nAll unsaved work will be lost.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            for window in self.running_windows[:]:
                try:
                    window.close()
                except Exception as e:
                    print(f"[Desktop] Error closing window: {e}")
                    
            if hasattr(self, 'taskbar'):
                try:
                    self.taskbar.close()
                except Exception as e:
                    print(f"[Desktop] Error closing taskbar: {e}")
                    
            event.accept()
        else:
            event.ignore()