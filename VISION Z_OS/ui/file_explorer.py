"""
File Explorer - Complete file management with working operations (FIXED for new FileSystem)
"""

from PyQt5.QtWidgets import (QMainWindow, QTreeWidget, QTreeWidgetItem, 
                             QVBoxLayout, QHBoxLayout, QWidget, QToolBar, 
                             QAction, QPushButton, QLineEdit, QMenu, 
                             QInputDialog, QMessageBox, QSplitter, QLabel,
                             QTextEdit, QDialog, QDialogButtonBox, QFormLayout)
from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QKeySequence
from file_system import FileSystem
from datetime import datetime
import os


class SearchThread(QThread):
    """Thread for searching files without blocking UI"""
    search_complete = pyqtSignal(list)
    search_progress = pyqtSignal(str)
    
    def __init__(self, filesystem, query, path="/"):
        super().__init__()
        self.filesystem = filesystem
        self.query = query
        self.path = path
    
    def run(self):
        """Perform search in background"""
        try:
            self.search_progress.emit("Searching...")
            results = self.filesystem.search_files(self.query, self.path)
            self.search_progress.emit(f"Found {len(results)} items")
            self.search_complete.emit(results)
        except Exception as e:
            self.search_progress.emit(f"Search error: {str(e)}")
            self.search_complete.emit([])


class FilePropertiesDialog(QDialog):
    """Dialog for viewing file properties"""
    
    def __init__(self, file_info, parent=None):
        super().__init__(parent)
        self.file_info = file_info
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f"Properties - {self.file_info.get('name', 'Unknown')}")
        self.setFixedSize(400, 300)
        
        layout = QFormLayout()
        
        layout.addRow("Name:", QLabel(self.file_info.get('name', 'Unknown')))
        layout.addRow("Type:", QLabel(self.file_info.get('type', 'unknown').capitalize()))
        layout.addRow("Size:", QLabel(self._format_size(self.file_info.get('size', 0))))
        layout.addRow("Created:", QLabel(str(self.file_info.get('created', 'N/A'))))
        layout.addRow("Modified:", QLabel(str(self.file_info.get('modified', 'N/A'))))
        layout.addRow("Owner:", QLabel(self.file_info.get('owner', 'user')))
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addRow(buttons)
        
        self.setLayout(layout)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2d2d3d;
                color: white;
            }
            QLabel {
                color: #00ffcc;
                padding: 5px;
            }
            QPushButton {
                background-color: #4d4d5d;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00ffcc;
                color: #1a1a2e;
            }
        """)
    
    def _format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class FileExplorer(QMainWindow):
    """Enhanced file explorer for browsing and managing files"""
    
    def __init__(self, username, kernel):
        super().__init__()
        self.username = username
        self.kernel = kernel
        self.filesystem = FileSystem(username)
        self.current_path = "/"
        self._nav_history = ["/"]
        self._history_index = 0
        self.selected_items = []
        self.search_thread = None
        
        self.init_ui()
        self.setup_shortcuts()
        
    def init_ui(self):
        """Initialize enhanced file explorer UI"""
        self.setWindowTitle(f"📂 File Explorer - {self.username}@VisionZ")
        self.setGeometry(100, 100, 1200, 750)
        self.setMinimumSize(800, 500)
        
        # Set modern dark theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a2e;
            }
            QToolBar {
                background-color: #16213e;
                border: none;
                border-bottom: 2px solid #0f3460;
                padding: 5px;
                spacing: 5px;
            }
            QPushButton {
                background-color: #0f3460;
                color: #e0e0e0;
                border: 1px solid #1a1a4e;
                padding: 8px 15px;
                margin: 2px;
                border-radius: 5px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00ffcc;
                color: #1a1a2e;
                border-color: #00ffcc;
            }
            QPushButton:pressed {
                background-color: #00ccaa;
            }
            QPushButton:disabled {
                background-color: #2d2d3d;
                color: #666;
            }
            QLineEdit {
                background-color: #0f3460;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                padding: 8px 12px;
                border-radius: 5px;
                font-size: 12px;
                font-family: 'Courier New', monospace;
            }
            QLineEdit:focus {
                border: 2px solid #00ffcc;
                background-color: #1a1a4e;
            }
            QTreeWidget {
                background-color: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #0f3460;
                outline: none;
                font-size: 12px;
                alternate-background-color: #16213e;
            }
            QTreeWidget::item {
                padding: 6px;
                border-bottom: 1px solid #0f3460;
            }
            QTreeWidget::item:hover {
                background-color: #2d4a7a;
            }
            QTreeWidget::item:selected {
                background-color: #00ffcc;
                color: #1a1a2e;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #0f3460;
                color: #00ffcc;
                padding: 8px;
                border: 1px solid #1a1a4e;
                font-weight: bold;
                font-size: 12px;
            }
            QTextEdit {
                background-color: #1a1a2e;
                color: #00ffcc;
                border: 1px solid #00ffcc;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                padding: 10px;
                border-radius: 5px;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Toolbar
        toolbar = self.create_toolbar()
        main_layout.addWidget(toolbar)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search files...")
        self.search_box.returnPressed.connect(self.perform_search)
        search_layout.addWidget(self.search_box)
        
        search_btn = QPushButton("🔍 Search")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)
        
        clear_search_btn = QPushButton("✖ Clear")
        clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(clear_search_btn)
        
        main_layout.addLayout(search_layout)
        
        # Main content splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Sidebar (directory tree)
        sidebar_container = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_container)
        sidebar_layout.setContentsMargins(5, 5, 5, 5)
        
        sidebar_label = QLabel("📁 Folders")
        sidebar_label.setFont(QFont("Arial", 11, QFont.Bold))
        sidebar_label.setStyleSheet("color: #00ffcc; padding: 5px;")
        sidebar_layout.addWidget(sidebar_label)
        
        self.sidebar = QTreeWidget()
        self.sidebar.setHeaderHidden(True)
        self.sidebar.setMaximumWidth(280)
        self.sidebar.itemClicked.connect(self.sidebar_clicked)
        self.sidebar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sidebar.customContextMenuRequested.connect(self.show_sidebar_context_menu)
        sidebar_layout.addWidget(self.sidebar)
        
        splitter.addWidget(sidebar_container)
        
        # Main content
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # File view
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Type", "Size", "Modified"])
        self.file_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.file_tree.itemDoubleClicked.connect(self.item_double_clicked)
        self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.file_tree.setColumnWidth(0, 350)
        self.file_tree.setColumnWidth(1, 100)
        self.file_tree.setColumnWidth(2, 100)
        self.file_tree.setColumnWidth(3, 150)
        content_layout.addWidget(self.file_tree)
        
        # Preview area
        preview_label = QLabel("📄 Preview")
        preview_label.setFont(QFont("Arial", 10, QFont.Bold))
        preview_label.setStyleSheet("color: #00ffcc; padding: 5px;")
        content_layout.addWidget(preview_label)
        
        self.preview_area = QTextEdit()
        self.preview_area.setMaximumHeight(180)
        self.preview_area.setPlaceholderText("File preview will appear here...")
        self.preview_area.setReadOnly(True)
        content_layout.addWidget(self.preview_area)
        
        splitter.addWidget(content_widget)
        splitter.setSizes([280, 920])
        
        main_layout.addWidget(splitter, 1)
        
        # Status bar
        status_widget = QWidget()
        status_layout = QHBoxLayout(status_widget)
        status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #00ffcc; padding: 5px; font-weight: bold;")
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        self.path_label = QLabel(f"📍 {self.current_path}")
        self.path_label.setStyleSheet("color: #e0e0e0; padding: 5px;")
        status_layout.addWidget(self.path_label)
        
        main_layout.addWidget(status_widget)
        
        # Load initial content
        self.refresh_sidebar()
        self.refresh_files()
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Delete shortcut
        delete_action = QAction(self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete_selected)
        self.addAction(delete_action)
        
        # Refresh shortcut
        refresh_action = QAction(self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.refresh_files)
        self.addAction(refresh_action)
        
        # New folder shortcut
        new_folder_action = QAction(self)
        new_folder_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_folder_action.triggered.connect(self.create_new_folder)
        self.addAction(new_folder_action)

    def create_toolbar(self):
        """Create toolbar with actions"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        
        # Navigation buttons
        back_btn = QPushButton("← Back")
        back_btn.clicked.connect(self.go_back)
        back_btn.setToolTip("Go back (Alt+Left)")
        toolbar.addWidget(back_btn)
        
        forward_btn = QPushButton("Forward →")
        forward_btn.clicked.connect(self.go_forward)
        forward_btn.setToolTip("Go forward (Alt+Right)")
        toolbar.addWidget(forward_btn)
        
        up_btn = QPushButton("↑ Up")
        up_btn.clicked.connect(self.go_up)
        up_btn.setToolTip("Go to parent directory")
        toolbar.addWidget(up_btn)
        
        toolbar.addSeparator()
        
        refresh_btn = QPushButton("⟳ Refresh")
        refresh_btn.clicked.connect(self.refresh_files)
        refresh_btn.setToolTip("Refresh (F5)")
        toolbar.addWidget(refresh_btn)
        
        toolbar.addSeparator()
        
        # Address bar
        path_label = QLabel("📍")
        path_label.setStyleSheet("color: #00ffcc; font-weight: bold;")
        toolbar.addWidget(path_label)
        
        self.address_bar = QLineEdit()
        self.address_bar.setText(self.current_path)
        self.address_bar.returnPressed.connect(self.navigate_to_address)
        self.address_bar.setMinimumWidth(300)
        toolbar.addWidget(self.address_bar)
        
        go_btn = QPushButton("Go")
        go_btn.clicked.connect(self.navigate_to_address)
        toolbar.addWidget(go_btn)
        
        toolbar.addSeparator()
        
        # File operations
        new_folder_btn = QPushButton("📁 New Folder")
        new_folder_btn.clicked.connect(self.create_new_folder)
        new_folder_btn.setToolTip("Create new folder (Ctrl+Shift+N)")
        toolbar.addWidget(new_folder_btn)
        
        new_file_btn = QPushButton("📄 New File")
        new_file_btn.clicked.connect(self.create_new_file)
        toolbar.addWidget(new_file_btn)
        
        toolbar.addSeparator()
        
        copy_btn = QPushButton("📋 Copy")
        copy_btn.clicked.connect(self.copy_selected)
        toolbar.addWidget(copy_btn)
        
        cut_btn = QPushButton("✂ Cut")
        cut_btn.clicked.connect(self.cut_selected)
        toolbar.addWidget(cut_btn)
        
        paste_btn = QPushButton("📌 Paste")
        paste_btn.clicked.connect(self.paste_selected)
        toolbar.addWidget(paste_btn)
        
        toolbar.addSeparator()
        
        delete_btn = QPushButton("🗑 Delete")
        delete_btn.clicked.connect(self.delete_selected)
        delete_btn.setToolTip("Delete selected (Delete)")
        toolbar.addWidget(delete_btn)
        
        rename_btn = QPushButton("✏️ Rename")
        rename_btn.clicked.connect(self.rename_item)
        toolbar.addWidget(rename_btn)
        
        toolbar.addSeparator()
        
        properties_btn = QPushButton("ℹ️ Properties")
        properties_btn.clicked.connect(self.show_properties)
        toolbar.addWidget(properties_btn)
        
        return toolbar
        
    def refresh_sidebar(self):
        """Refresh directory tree in sidebar"""
        self.sidebar.clear()
        
        # 🎯 استخدام كائن FileSystemNode بدلاً من القاموس
        root_node = self.filesystem.root
        
        if not root_node:
            return
            
        root_item = QTreeWidgetItem(self.sidebar)
        root_item.setText(0, "🖥️ My Computer")
        root_item.setData(0, Qt.UserRole, "/")
        
        # إضافة المجلدات الفرعية
        if root_node.type == "directory":
            self.add_directory_items(root_item, "/", root_node)
        
        self.sidebar.expandAll()
        
    def add_directory_items(self, parent_item, path, node):
        """Add directory items recursively - 🎯 استخدام كائنات FileSystemNode"""
        if node.type != "directory":
            return
            
        # ترتيب: المجلدات أولاً
        children = sorted(
            node.children.items(),
            key=lambda x: (x[1].type != "directory", x[0].lower())
        )
        
        for child_name, child_node in children:
            if child_node.type == "directory":
                child_path = f"{path}/{child_name}" if path != "/" else f"/{child_name}"
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, f"📁 {child_name}")
                child_item.setData(0, Qt.UserRole, child_path)
                # تكرار للمجلدات الفرعية
                self.add_directory_items(child_item, child_path, child_node)
                    
    def refresh_files(self):
        """Refresh file listing"""
        self.file_tree.clear()
        
        # 🎯 استخدام list_directory من نظام الملفات الجديد
        items = self.filesystem.list_directory(self.current_path)
        
        if items is None:
            self.status_label.setText("❌ Cannot access directory")
            return
        
        # Add parent directory if not at root
        if self.current_path != "/":
            parent_item = QTreeWidgetItem(self.file_tree)
            parent_item.setText(0, "⬆ ..")
            parent_item.setText(1, "Parent Directory")
            parent_item.setText(2, "-")
            parent_item.setText(3, "-")
            parent_item.setData(0, Qt.UserRole, "parent")
            font = parent_item.font(0)
            font.setBold(True)
            parent_item.setFont(0, font)
        
        # 🎯 الحصول على تفاصيل الملفات
        details = self.filesystem.list_directory_details(self.current_path)
        
        if details:
            for item_detail in details:
                file_item = QTreeWidgetItem(self.file_tree)
                
                # أيقونة حسب النوع
                if item_detail['type'] == "directory":
                    icon = "📁"
                    type_text = "Folder"
                    size_text = "-"
                else:
                    icon = "📄"
                    type_text = "File"
                    size_text = self._format_size(item_detail['size'])
                
                file_item.setText(0, f"{icon} {item_detail['name']}")
                file_item.setText(1, type_text)
                file_item.setText(2, size_text)
                
                # تنسيق التاريخ
                try:
                    if isinstance(item_detail['modified'], datetime):
                        modified_text = item_detail['modified'].strftime("%Y-%m-%d %H:%M")
                    else:
                        modified_text = str(item_detail['modified']).split("T")[0]
                except:
                    modified_text = "N/A"
                    
                file_item.setText(3, modified_text)
                
                file_item.setData(0, Qt.UserRole, item_detail['type'])
                file_item.setData(1, Qt.UserRole, item_detail['name'])
                
                # تلوين المجلدات
                if item_detail['type'] == "directory":
                    file_item.setForeground(0, QColor(0, 200, 255))
        
        self.address_bar.setText(self.current_path)
        self.path_label.setText(f"📍 {self.current_path}")
        self.update_status()
        
    def _format_size(self, size):
        """Format file size to human-readable format"""
        if size == 0:
            return "0 B"
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
        
    def update_status(self):
        """Update status bar"""
        details = self.filesystem.list_directory_details(self.current_path)
        if details is not None:
            folders = sum(1 for d in details if d['type'] == 'directory')
            files = sum(1 for d in details if d['type'] == 'file')
            self.status_label.setText(f"📊 {folders} folders | {files} files")
        else:
            self.status_label.setText("❌ Error loading directory")
        
    def sidebar_clicked(self, item, column):
        """Handle sidebar click"""
        path = item.data(0, Qt.UserRole)
        if path:
            self._push_history(path)
            self.refresh_files()
            
    def show_sidebar_context_menu(self, position):
        """Show context menu for sidebar"""
        item = self.sidebar.itemAt(position)
        if not item:
            return
            
        path = item.data(0, Qt.UserRole)
        if not path:
            return
            
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d3d;
                color: white;
                border: 1px solid #00ffcc;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #00ffcc;
                color: #1a1a2e;
            }
        """)
        
        new_folder_action = QAction("📁 New Folder Here", self)
        new_folder_action.triggered.connect(lambda: self.create_new_folder_in_path(path))
        menu.addAction(new_folder_action)
        
        new_file_action = QAction("📄 New File Here", self)
        new_file_action.triggered.connect(lambda: self.create_new_file_in_path(path))
        menu.addAction(new_file_action)
        
        menu.exec_(self.sidebar.mapToGlobal(position))
            
    def item_double_clicked(self, item, column):
        """Handle double click on file/folder"""
        item_type = item.data(0, Qt.UserRole)
        item_name = item.data(1, Qt.UserRole)
        
        if item_type == "parent":
            self.go_up()
        elif item_type == "directory":
            new_path = f"{self.current_path}/{item_name}" if self.current_path != "/" else f"/{item_name}"
            self._push_history(new_path)
            self.refresh_files()
            self.refresh_sidebar()
        elif item_type == "file":
            # Preview file
            self.preview_file(item_name)
            
    def preview_file(self, filename):
        """Preview file content"""
        file_path = f"{self.current_path}/{filename}" if self.current_path != "/" else f"/{filename}"
        content = self.filesystem.read_file(file_path)
        if content is not None:
            self.preview_area.setPlainText(content)
            self.status_label.setText(f"📄 Previewing: {filename}")
        else:
            self.preview_area.setPlainText("[Cannot preview this file type]")
            
    def _push_history(self, path):
        """Push path to navigation history"""
        self._nav_history = self._nav_history[:self._history_index + 1]
        if path != self.current_path:
            self._nav_history.append(path)
            self._history_index = len(self._nav_history) - 1
        self.current_path = path

    def go_back(self):
        """Go back in navigation history"""
        if self._history_index > 0:
            self._history_index -= 1
            self.current_path = self._nav_history[self._history_index]
            self.refresh_files()
            self.refresh_sidebar()

    def go_forward(self):
        """Go forward in navigation history"""
        if self._history_index < len(self._nav_history) - 1:
            self._history_index += 1
            self.current_path = self._nav_history[self._history_index]
            self.refresh_files()
            self.refresh_sidebar()
        
    def go_up(self):
        """Go to parent directory"""
        if self.current_path != "/":
            parent = '/'.join(self.current_path.split('/')[:-1]) or "/"
            self._push_history(parent)
            self.refresh_files()
            self.refresh_sidebar()
            
    def navigate_to_address(self):
        """Navigate to entered address"""
        path = self.address_bar.text()
        if self.filesystem.resolve_path(path):
            self._push_history(path)
            self.refresh_files()
            self.refresh_sidebar()
        else:
            QMessageBox.warning(self, "Error", f"Path not found: {path}")
            
    def perform_search(self):
        """Perform file search"""
        query = self.search_box.text().strip()
        if not query:
            self.clear_search()
            return
            
        self.status_label.setText(f"🔍 Searching for: {query}...")
        
        # Use search thread
        self.search_thread = SearchThread(self.filesystem, query, "/")
        self.search_thread.search_complete.connect(self.display_search_results)
        self.search_thread.search_progress.connect(self.status_label.setText)
        self.search_thread.start()
    
    def display_search_results(self, results):
        """Display search results"""
        self.file_tree.clear()
        
        if not results:
            self.file_tree.addTopLevelItem(
                QTreeWidgetItem(["No results found"])
            )
        else:
            for path in results:
                # 🎯 استخدام كائن FileSystemNode
                node = self.filesystem.resolve_path(path)
                if node:
                    item = QTreeWidgetItem(self.file_tree)
                    icon = "📁" if node.type == "directory" else "📄"
                    item.setText(0, f"{icon} {node.name}")
                    item.setText(1, f"📍 {path}")
                    item.setText(2, node.type.capitalize())
                    item.setData(0, Qt.UserRole, node.type)
                    item.setData(1, Qt.UserRole, node.name)
                    
        self.status_label.setText(f"✅ Found {len(results)} items")
    
    def clear_search(self):
        """Clear search results"""
        self.search_box.clear()
        self.refresh_files()
        self.status_label.setText("Ready")
            
    def create_new_folder(self):
        """Create new folder"""
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            if self.filesystem.create_directory(name, self.current_path):
                if hasattr(self.kernel, 'notification_system'):
                    self.kernel.notification_system.show_notification(
                        "✅ Folder Created", f"Created folder: {name}", "success"
                    )
                self.refresh_files()
                self.refresh_sidebar()
            else:
                QMessageBox.warning(self, "Error", f"Cannot create folder: {name}")
    
    def create_new_folder_in_path(self, path):
        """Create new folder in specific path"""
        name, ok = QInputDialog.getText(self, "New Folder", "Enter folder name:")
        if ok and name:
            if self.filesystem.create_directory(name, path):
                self.refresh_sidebar()
                if path == self.current_path:
                    self.refresh_files()
                
    def create_new_file(self):
        """Create new file"""
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            if '.' not in name:
                name += ".txt"
            if self.filesystem.create_file(name, "", self.current_path):
                if hasattr(self.kernel, 'notification_system'):
                    self.kernel.notification_system.show_notification(
                        "✅ File Created", f"Created file: {name}", "success"
                    )
                self.refresh_files()
            else:
                QMessageBox.warning(self, "Error", f"Cannot create file: {name}")
    
    def create_new_file_in_path(self, path):
        """Create new file in specific path"""
        name, ok = QInputDialog.getText(self, "New File", "Enter file name:")
        if ok and name:
            if '.' not in name:
                name += ".txt"
            if self.filesystem.create_file(name, "", path):
                if path == self.current_path:
                    self.refresh_files()
                
    def delete_selected(self):
        """Delete selected items"""
        selected = self.file_tree.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select items to delete")
            return
        
        # Collect items to delete
        items_to_delete = []
        for item in selected:
            item_name = item.data(1, Qt.UserRole)
            if item_name and item_name != "parent":
                items_to_delete.append(item_name)
        
        if not items_to_delete:
            return
        
        # Confirm deletion
        msg = f"Are you sure you want to delete {len(items_to_delete)} item(s)?\n\n"
        msg += "\n".join(items_to_delete[:5])
        if len(items_to_delete) > 5:
            msg += f"\n... and {len(items_to_delete) - 5} more"
            
        reply = QMessageBox.question(
            self, 'Confirm Delete', msg,
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            deleted = 0
            for item_name in items_to_delete:
                if self.filesystem.delete_item(item_name, self.current_path):
                    deleted += 1
            
            if deleted > 0:
                if hasattr(self.kernel, 'notification_system'):
                    self.kernel.notification_system.show_notification(
                        "🗑 Deleted", f"Deleted {deleted} item(s)", "warning"
                    )
                self.refresh_files()
                self.refresh_sidebar()
            else:
                QMessageBox.warning(self, "Error", "Could not delete items")
    
    def copy_selected(self):
        """Copy selected items"""
        selected = self.file_tree.selectedItems()
        if not selected:
            return
        
        self.selected_items = []
        for item in selected:
            item_name = item.data(1, Qt.UserRole)
            if item_name and item_name != "parent":
                self.selected_items.append(item_name)
                self.filesystem.copy_item(item_name, self.current_path)
        
        if self.selected_items:
            self.status_label.setText(f"📋 Copied {len(self.selected_items)} item(s) to clipboard")
    
    def cut_selected(self):
        """Cut selected items"""
        selected = self.file_tree.selectedItems()
        if not selected:
            return
        
        self.selected_items = []
        for item in selected:
            item_name = item.data(1, Qt.UserRole)
            if item_name and item_name != "parent":
                self.selected_items.append(item_name)
                self.filesystem.cut_item(item_name, self.current_path)
        
        if self.selected_items:
            self.status_label.setText(f"✂ Cut {len(self.selected_items)} item(s) to clipboard")
    
    def paste_selected(self):
        """Paste items from clipboard"""
        if not self.selected_items:
            self.status_label.setText("❌ Nothing to paste")
            return
        
        pasted = 0
        for item_name in self.selected_items:
            if self.filesystem.paste_item(self.current_path):
                pasted += 1
        
        if pasted > 0:
            self.status_label.setText(f"📌 Pasted {pasted} item(s)")
            self.refresh_files()
            self.refresh_sidebar()
            self.selected_items = []
        else:
            self.status_label.setText("❌ Paste failed")
                
    def rename_item(self):
        """Rename selected item"""
        current_item = self.file_tree.currentItem()
        if not current_item:
            return
            
        old_name = current_item.data(1, Qt.UserRole)
        if not old_name or old_name == "parent":
            return
            
        new_name, ok = QInputDialog.getText(
            self, "Rename", "Enter new name:", text=old_name
        )
        if ok and new_name and new_name != old_name:
            if self.filesystem.rename_item(old_name, new_name, self.current_path):
                if hasattr(self.kernel, 'notification_system'):
                    self.kernel.notification_system.show_notification(
                        "✏️ Renamed", f"{old_name} → {new_name}", "info"
                    )
                self.refresh_files()
                self.refresh_sidebar()
            else:
                QMessageBox.warning(self, "Error", "Cannot rename item")
    
    def show_properties(self):
        """Show properties of selected item"""
        current_item = self.file_tree.currentItem()
        if not current_item:
            return
            
        item_name = current_item.data(1, Qt.UserRole)
        if not item_name or item_name == "parent":
            return
        
        # 🎯 استخدام get_file_info من نظام الملفات الجديد
        file_path = f"{self.current_path}/{item_name}" if self.current_path != "/" else f"/{item_name}"
        file_info = self.filesystem.get_file_info(file_path)
        
        if file_info:
            dialog = FilePropertiesDialog(file_info, self)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "Cannot get file information")
                
    def show_context_menu(self, position):
        """Show context menu for file operations"""
        menu = QMenu()
        menu.setStyleSheet("""
            QMenu {
                background-color: #2d2d3d;
                color: white;
                border: 1px solid #00ffcc;
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: #00ffcc;
                color: #1a1a2e;
            }
            QMenu::separator {
                height: 1px;
                background-color: #4d4d5d;
                margin: 5px;
            }
        """)
        
        # Open action (if file)
        current_item = self.file_tree.currentItem()
        if current_item:
            item_type = current_item.data(0, Qt.UserRole)
            if item_type == "file":
                open_action = QAction("📂 Open", self)
                open_action.triggered.connect(lambda: self.item_double_clicked(current_item, 0))
                menu.addAction(open_action)
                menu.addSeparator()
        
        copy_action = QAction("📋 Copy", self)
        copy_action.triggered.connect(self.copy_selected)
        menu.addAction(copy_action)
        
        cut_action = QAction("✂ Cut", self)
        cut_action.triggered.connect(self.cut_selected)
        menu.addAction(cut_action)
        
        paste_action = QAction("📌 Paste", self)
        paste_action.triggered.connect(self.paste_selected)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        rename_action = QAction("✏️ Rename", self)
        rename_action.triggered.connect(self.rename_item)
        menu.addAction(rename_action)
        
        delete_action = QAction("🗑 Delete", self)
        delete_action.triggered.connect(self.delete_selected)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        properties_action = QAction("ℹ️ Properties", self)
        properties_action.triggered.connect(self.show_properties)
        menu.addAction(properties_action)
        
        menu.addSeparator()
        
        new_folder_action = QAction("📁 New Folder", self)
        new_folder_action.triggered.connect(self.create_new_folder)
        menu.addAction(new_folder_action)
        
        new_file_action = QAction("📄 New File", self)
        new_file_action.triggered.connect(self.create_new_file)
        menu.addAction(new_file_action)
        
        menu.exec_(self.file_tree.mapToGlobal(position))
        
    def closeEvent(self, event):
        """Handle close event"""
        if hasattr(self.kernel, 'desktop') and hasattr(self.kernel.desktop, 'taskbar'):
            self.kernel.desktop.taskbar.remove_running_app("File Explorer")
        event.accept()