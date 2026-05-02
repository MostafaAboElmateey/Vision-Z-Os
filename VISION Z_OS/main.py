"""
Vision Z OS - Main Entry Point
Complete Operating System Simulator
Developed by Abu El-Maati OS Team
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from kernel import Kernel

# Create necessary directories
os.makedirs("data/users", exist_ok=True)
os.makedirs("resources/wallpapers", exist_ok=True)

def main():
    """Main entry point for Vision Z OS"""
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Initialize kernel
    kernel = Kernel()
    
    # Show boot screen
    kernel.show_boot_screen()
    
    # Start OS after boot delay
    QTimer.singleShot(3000, kernel.start_os)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()