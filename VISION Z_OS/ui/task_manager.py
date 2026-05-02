"""
Task Manager - FULL FIXED VERSION (Stable & Working)
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QWidget, QHeaderView,
    QLabel, QHBoxLayout, QMessageBox, QProgressBar, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont


class TaskManagerWindow(QMainWindow):
    # Protected processes list as class constant
    PROTECTED_PROCESSES = {
        "system kernel",
        "window manager",
        "process manager",
        "desktop environment"
    }
    
    def __init__(self, process_manager, desktop):
        super().__init__()
        self.process_manager = process_manager
        self.desktop = desktop
        self.refresh_rate = 1000  # ms (1 second)
        self.is_updating = False  # Prevent concurrent updates

        self.init_ui()

        # تحديث كل ثانية
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_process_list)
        self.timer.start(self.refresh_rate)

    def init_ui(self):
        self.setWindowTitle("⚙️ Vision Z Task Manager")
        self.setGeometry(200, 200, 1100, 700)
        self.setMinimumSize(800, 500)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)

        # عنوان رئيسي
        title = QLabel("🖥️ Vision Z Task Manager")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        layout.addWidget(title)

        # إحصائيات النظام
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        # CPU Stats
        cpu_layout = QVBoxLayout()
        cpu_label = QLabel("🖥️ CPU Usage")
        cpu_label.setAlignment(Qt.AlignCenter)
        cpu_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)
        self.cpu_progress.setTextVisible(True)
        self.cpu_progress.setFormat("%p%")
        self.cpu_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #27ae60, stop:0.5 #f1c40f, stop:1 #e74c3c);
                border-radius: 3px;
            }
        """)
        cpu_layout.addWidget(cpu_label)
        cpu_layout.addWidget(self.cpu_progress)

        # Memory Stats
        memory_layout = QVBoxLayout()
        memory_label = QLabel("🧠 Memory Usage")
        memory_label.setAlignment(Qt.AlignCenter)
        memory_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setTextVisible(True)
        self.memory_progress.setFormat("%p%")
        self.memory_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:0.5 #f39c12, stop:1 #e74c3c);
                border-radius: 3px;
            }
        """)
        memory_layout.addWidget(memory_label)
        memory_layout.addWidget(self.memory_progress)

        stats_layout.addLayout(cpu_layout)
        stats_layout.addLayout(memory_layout)
        layout.addLayout(stats_layout)

        # عدد العمليات
        self.process_count_label = QLabel("📊 Total Processes: 0")
        self.process_count_label.setFont(QFont("Arial", 10))
        self.process_count_label.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.process_count_label)

        # جدول العمليات
        self.process_table = QTableWidget()
        self.process_table.setColumnCount(7)
        self.process_table.setHorizontalHeaderLabels(
            ["PID", "Name", "Type", "CPU%", "RAM (MB)", "Status", "Uptime"]
        )
        self.process_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.process_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.process_table.setSelectionMode(QTableWidget.SingleSelection)
        self.process_table.setAlternatingRowColors(True)
        self.process_table.setSortingEnabled(True)
        self.process_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #bdc3c7;
                gridline-color: #dcdde1;
                background-color: #f5f6fa;
                alternate-background-color: #ebedf0;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 8px;
                font-weight: bold;
                border: 1px solid #34495e;
            }
        """)
        layout.addWidget(self.process_table)

        # أزرار التحكم
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.end_btn = QPushButton("🗑 End Task")
        self.end_btn.clicked.connect(self.end_selected_task)
        self.end_btn.setMinimumHeight(40)
        self.end_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)

        refresh_btn = QPushButton("🔄 Refresh Now")
        refresh_btn.clicked.connect(self.update_process_list)
        refresh_btn.setMinimumHeight(40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)

        # Refresh Rate Control
        rate_label = QLabel("Refresh Rate:")
        rate_label.setFont(QFont("Arial", 10))
        
        self.slow_btn = QPushButton("🐢 2s")
        self.slow_btn.clicked.connect(lambda: self.set_refresh_rate(2000))
        self.slow_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        
        self.normal_btn = QPushButton("🐇 1s")
        self.normal_btn.clicked.connect(lambda: self.set_refresh_rate(1000))
        self.normal_btn.setEnabled(False)
        self.normal_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:disabled {
                background-color: #27ae60;
                color: white;
            }
        """)
        
        self.fast_btn = QPushButton("⚡ 500ms")
        self.fast_btn.clicked.connect(lambda: self.set_refresh_rate(500))
        self.fast_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)

        btn_layout.addWidget(self.end_btn)
        btn_layout.addWidget(refresh_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(rate_label)
        btn_layout.addWidget(self.slow_btn)
        btn_layout.addWidget(self.normal_btn)
        btn_layout.addWidget(self.fast_btn)

        layout.addLayout(btn_layout)

        # شريط الحالة
        self.status_label = QLabel("✅ Ready - Auto-refreshing every 1 second")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                padding: 5px;
                background-color: #ecf0f1;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.status_label)

    def set_refresh_rate(self, ms):
        """تغيير معدل التحديث"""
        self.refresh_rate = max(500, ms)
        self.timer.start(self.refresh_rate)
        
        # تحديث حالة الأزرار
        self.slow_btn.setEnabled(ms != 2000)
        self.normal_btn.setEnabled(ms != 1000)
        self.fast_btn.setEnabled(ms != 500)
        
        rate_text = f"{ms/1000:.1f}s" if ms >= 1000 else f"{ms}ms"
        self.status_label.setText(f"✅ Auto-refreshing every {rate_text}")

    def _set_table_item(self, row, col, text, color=None):
        """مساعد لتحديث خلايا الجدول بكفاءة"""
        if row >= self.process_table.rowCount():
            return
            
        item = self.process_table.item(row, col)
        if item is None:
            item = QTableWidgetItem()
            self.process_table.setItem(row, col, item)
        
        if item.text() != text:
            item.setText(text)
        
        if color:
            item.setForeground(color)
        
        # جعل الخلايا للقراءة فقط
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)

    def update_process_list(self):
        """تحديث قائمة العمليات"""
        if self.is_updating:
            return
            
        self.is_updating = True
        
        try:
            processes = self.process_manager.get_all_processes()
            stats = self.process_manager.get_system_stats()

            # تحديث شريط CPU مع لون متغير حسب الاستخدام
            cpu_percent = stats.get("cpu_percent", 0)
            self.cpu_progress.setValue(int(cpu_percent))
            
            # تحديث شريط الذاكرة مع لون متغير
            memory_percent = stats.get("memory_percent", 0)
            self.memory_progress.setValue(int(memory_percent))
            
            # تحديث عداد العمليات
            self.process_count_label.setText(f"📊 Total Processes: {len(processes)}")

            # تحسين: تحديث الصفوف الموجودة فقط
            current_rows = self.process_table.rowCount()
            new_count = len(processes)
            
            if new_count != current_rows:
                self.process_table.setRowCount(new_count)

            for i, p in enumerate(processes):
                # PID
                self._set_table_item(i, 0, str(p.pid))
                
                # Name
                name = getattr(p, 'name', 'Unknown')
                self._set_table_item(i, 1, name)
                
                # Type
                proc_type = getattr(p, 'type', 'Unknown')
                self._set_table_item(i, 2, proc_type)
                
                # CPU Usage
                cpu = getattr(p, "cpu_usage", 0)
                if isinstance(cpu, float):
                    cpu_text = f"{cpu:.1f}%"
                else:
                    cpu_text = f"{cpu}%"
                
                # تلوين CPU حسب الاستخدام
                cpu_color = QColor(39, 174, 96)  # أخضر
                if cpu > 50:
                    cpu_color = QColor(231, 76, 60)  # أحمر
                elif cpu > 25:
                    cpu_color = QColor(241, 196, 15)  # أصفر
                    
                self._set_table_item(i, 3, cpu_text, cpu_color)
                
                # Memory Usage
                mem = getattr(p, "memory_usage", 0)
                if isinstance(mem, float):
                    mem_text = f"{mem:.1f}"
                else:
                    mem_text = f"{mem}"
                    
                # تلوين الذاكرة حسب الاستخدام
                mem_color = QColor(52, 152, 219)  # أزرق
                if mem > 500:
                    mem_color = QColor(231, 76, 60)  # أحمر
                elif mem > 200:
                    mem_color = QColor(243, 156, 18)  # برتقالي
                    
                self._set_table_item(i, 4, mem_text, mem_color)
                
                # Status
                running = getattr(p, "running", True)
                status = "🟢 Running" if running else "🔴 Stopped"
                status_color = QColor(0, 150, 0) if running else QColor(200, 0, 0)
                self._set_table_item(i, 5, status, status_color)
                
                # Uptime
                try:
                    import datetime
                    if hasattr(p, 'start_time') and isinstance(p.start_time, datetime.datetime):
                        now = datetime.datetime.now()
                        uptime_delta = now - p.start_time
                        hours = uptime_delta.seconds // 3600
                        minutes = (uptime_delta.seconds % 3600) // 60
                        seconds = uptime_delta.seconds % 60
                        uptime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                    else:
                        uptime = "N/A"
                except:
                    uptime = "N/A"
                    
                self._set_table_item(i, 6, uptime)
                
        except Exception as e:
            self.status_label.setText(f"❌ Error updating: {str(e)}")
        finally:
            self.is_updating = False

    def end_selected_task(self):
        """إنهاء العملية المحددة"""
        row = self.process_table.currentRow()
        
        if row < 0:
            QMessageBox.warning(self, "⚠️ Error", "Please select a process first!")
            return

        try:
            pid_item = self.process_table.item(row, 0)
            name_item = self.process_table.item(row, 1)
            
            if not pid_item or not name_item:
                QMessageBox.warning(self, "⚠️ Error", "Invalid process selection!")
                return
                
            pid = int(pid_item.text())
            name = name_item.text()

            # حماية العمليات النظامية
            if name.lower() in self.PROTECTED_PROCESSES:
                QMessageBox.warning(
                    self,
                    "🔒 Protected Process",
                    f"Cannot terminate '{name}'!\n\n"
                    "This is a system-critical process that keeps the OS running."
                )
                return

            # التأكيد
            confirm = QMessageBox.question(
                self,
                "⚠️ Confirm Termination",
                f"Are you sure you want to end '{name}' (PID: {pid})?\n\n"
                "⚠️ Warning: This may cause data loss!",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if confirm != QMessageBox.Yes:
                return

            # إنهاء العملية
            success = self.process_manager.terminate_process(pid)

            if not success:
                QMessageBox.warning(
                    self,
                    "❌ Failed",
                    f"Could not terminate {name}.\n"
                    "The process may have already ended."
                )
                return

            # إغلاق النوافذ المرتبطة
            windows_closed = 0
            for w in list(self.desktop.running_windows):
                if getattr(w, "process_id", None) == pid:
                    try:
                        w.close()
                        windows_closed += 1
                    except Exception as e:
                        print(f"Error closing window: {e}")
                    if w in self.desktop.running_windows:
                        self.desktop.running_windows.remove(w)

            # تحديث القائمة
            self.update_process_list()
            
            # عرض النتيجة
            status_msg = f"✅ {name} (PID: {pid}) terminated successfully"
            if windows_closed > 0:
                status_msg += f"\n📋 {windows_closed} window(s) closed"
                
            self.status_label.setText(status_msg)
            QMessageBox.information(self, "✅ Success", status_msg)

        except ValueError:
            QMessageBox.critical(self, "❌ Error", "Invalid PID format!")
        except Exception as e:
            QMessageBox.critical(
                self,
                "❌ Unexpected Error",
                f"An error occurred:\n{str(e)}"
            )
            self.status_label.setText(f"❌ Error: {str(e)}")

      
    def closeEvent(self, event):
        """تنظيف عند إغلاق النافذة"""
        try:
            if hasattr(self, 'timer') and self.timer is not None:
                self.timer.stop()
                self.timer.deleteLater()
        except:
            pass
        
        try:
            self.is_updating = False
        except:
            pass
        
        event.accept()