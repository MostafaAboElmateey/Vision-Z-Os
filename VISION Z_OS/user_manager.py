"""
User Manager - Handles user authentication and isolation
"""

import hashlib
import json
import os
from database_manager import DatabaseManager

class UserManager:
    """Manages user accounts and authentication"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.current_users = {}
        self.load_users()
        
    def load_users(self):
        """Load users from database"""
        self.current_users = self.db_manager.get_all_users()
        
    def hash_password(self, password):
        """Hash password for security"""
        return hashlib.sha256(password.encode()).hexdigest()
        
    def create_user(self, username, password):
        """Create a new user account"""
        if username in self.current_users:
            return False
            
        hashed_pw = self.hash_password(password)
        self.db_manager.create_user(username, hashed_pw)
        self.current_users[username] = hashed_pw
        return True
        
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        if username not in self.current_users:
            return False
            
        hashed_pw = self.hash_password(password)
        return self.current_users[username] == hashed_pw
        
    def user_exists(self, username):
        """Check if user exists"""
        return username in self.current_users