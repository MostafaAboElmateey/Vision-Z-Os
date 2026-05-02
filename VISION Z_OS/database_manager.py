"""
Database Manager - Handles data persistence
"""

import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    """Manages SQLite database for user data storage"""
    
    def __init__(self, db_path="vision_z_os.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT,
                settings TEXT
            )
        ''')
        
        # Files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                path TEXT NOT NULL,
                file_type TEXT NOT NULL,
                content TEXT,
                created_at TEXT,
                modified_at TEXT,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')
        
        # Settings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                username TEXT PRIMARY KEY,
                theme TEXT DEFAULT 'dark',
                wallpaper TEXT DEFAULT 'default',
                sound_enabled INTEGER DEFAULT 1,
                notifications_enabled INTEGER DEFAULT 1,
                FOREIGN KEY (username) REFERENCES users(username)
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def create_user(self, username, password_hash):
        """Create new user in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, created_at)
                VALUES (?, ?, ?)
            ''', (username, password_hash, datetime.now().isoformat()))
            
            # Create default settings for user
            cursor.execute('''
                INSERT INTO settings (username, theme, wallpaper, sound_enabled, notifications_enabled)
                VALUES (?, 'dark', 'default', 1, 1)
            ''', (username,))
            
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
            
    def get_user(self, username):
        """Get user information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        conn.close()
        return user
        
    def get_all_users(self):
        """Get all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT username, password_hash FROM users')
        users = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return users
        
    def create_user_file(self, username, path, file_type, content=""):
        """Create a file or directory for user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO files (username, path, file_type, content, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (username, path, file_type, content, 
              datetime.now().isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
    def get_user_files(self, username):
        """Get all files for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT path, file_type, content FROM files WHERE username = ?', (username,))
        files = cursor.fetchall()
        
        conn.close()
        return files
        
    def update_user_settings(self, username, settings):
        """Update user settings — merges with existing values"""
        existing = self.get_user_settings(username) or {
            'theme': 'dark', 'wallpaper': 'default',
            'sound_enabled': True, 'notifications_enabled': True
        }
        merged = {**existing, **settings}

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO settings (username, theme, wallpaper, sound_enabled, notifications_enabled)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                theme=excluded.theme,
                wallpaper=excluded.wallpaper,
                sound_enabled=excluded.sound_enabled,
                notifications_enabled=excluded.notifications_enabled
        ''', (username,
              merged.get('theme', 'dark'),
              merged.get('wallpaper', 'default'),
              int(merged.get('sound_enabled', True)),
              int(merged.get('notifications_enabled', True))))
        conn.commit()
        conn.close()
        
    def get_user_settings(self, username):
        """Get user settings"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT theme, wallpaper, sound_enabled, notifications_enabled FROM settings WHERE username=?', (username,))
        settings = cursor.fetchone()
        
        conn.close()
        
        if settings:
            return {
                'theme': settings[0],
                'wallpaper': settings[1],
                'sound_enabled': bool(settings[2]),
                'notifications_enabled': bool(settings[3])
            }
        return None