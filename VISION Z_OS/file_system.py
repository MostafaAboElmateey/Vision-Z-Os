"""
Virtual File System - Enhanced with Advanced Features
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
import copy


class FileSystemNode:
    """Represents a node in the virtual filesystem"""
    
    def __init__(self, name: str, node_type: str, content: str = ""):
        self.name = name
        self.type = node_type  # "file" or "directory"
        self.content = content
        self.children: Dict[str, 'FileSystemNode'] = {}
        self.created = datetime.now()
        self.modified = datetime.now()
        self.size = len(content) if node_type == "file" else 0
        self.permissions = "rwxr-xr-x"  # Unix-like permissions
        self.owner = "user"
        self.hidden = False
        
    def to_dict(self) -> dict:
        """Convert node to dictionary for JSON serialization"""
        return {
            "type": self.type,
            "content": self.content,
            "children": {
                name: child.to_dict() for name, child in self.children.items()
            } if self.type == "directory" else {},
            "created": self.created.isoformat(),
            "modified": self.modified.isoformat(),
            "size": self.size,
            "permissions": self.permissions,
            "owner": self.owner,
            "hidden": self.hidden
        }
    
    @classmethod
    def from_dict(cls, name: str, data: dict) -> 'FileSystemNode':
        """Create node from dictionary"""
        node = cls(
            name=name,
            node_type=data.get("type", "file"),
            content=data.get("content", "")
        )
        
        # Restore metadata
        try:
            node.created = datetime.fromisoformat(data.get("created", datetime.now().isoformat()))
            node.modified = datetime.fromisoformat(data.get("modified", datetime.now().isoformat()))
        except:
            pass
            
        node.size = data.get("size", 0)
        node.permissions = data.get("permissions", "rwxr-xr-x")
        node.owner = data.get("owner", "user")
        node.hidden = data.get("hidden", False)
        
        # Restore children for directories
        if node.type == "directory":
            for child_name, child_data in data.get("children", {}).items():
                node.children[child_name] = cls.from_dict(child_name, child_data)
        
        return node


class FileSystem:
    """Enhanced virtual file system with per-user isolation"""
    
    def __init__(self, username: str):
        """
        Initialize filesystem for a specific user
        
        Args:
            username: Username for user isolation
        """
        self.username = username
        self.current_path = "/"
        self.root: Optional[FileSystemNode] = None
        self.history = []  # Navigation history
        self.history_index = -1
        self.clipboard = None  # For copy/paste operations
        self.clipboard_operation = None  # "copy" or "cut"
        
        # Load or create filesystem
        self.load_filesystem()
        
    def get_user_path(self) -> str:
        """Get user's data file path"""
        return f"data/users/{self.username}/filesystem.json"
    
    def get_backup_path(self) -> str:
        """Get backup file path"""
        return f"data/users/{self.username}/filesystem.backup.json"
    
    def load_filesystem(self):
        """Load user's filesystem from storage with backup recovery"""
        try:
            with open(self.get_user_path(), 'r') as f:
                data = json.load(f)
                
            # Convert from old format if necessary
            if isinstance(data, dict):
                if "type" in data and data["type"] == "directory":
                    # Already in correct format
                    self.root = FileSystemNode.from_dict("/", data)
                else:
                    # Old format: create root with children
                    self._migrate_from_old_format(data)
            else:
                self._create_default_filesystem()
                
            print(f"[FileSystem] Loaded filesystem for {self.username}")
            
        except FileNotFoundError:
            # Try to recover from backup
            if os.path.exists(self.get_backup_path()):
                print(f"[FileSystem] Recovering from backup for {self.username}")
                shutil.copy2(self.get_backup_path(), self.get_user_path())
                self.load_filesystem()
            else:
                self._create_default_filesystem()
                
        except (json.JSONDecodeError, Exception) as e:
            print(f"[FileSystem] Error loading filesystem: {e}")
            # Try backup
            if os.path.exists(self.get_backup_path()):
                print(f"[FileSystem] Recovering from backup")
                shutil.copy2(self.get_backup_path(), self.get_user_path())
                try:
                    self.load_filesystem()
                    return
                except:
                    pass
            self._create_default_filesystem()
    
    def _create_default_filesystem(self):
        """Create default filesystem structure"""
        print(f"[FileSystem] Creating default filesystem for {self.username}")
        self.root = FileSystemNode("/", "directory")
        
        # Create default directories
        default_dirs = ["Desktop", "Documents", "Downloads", "Pictures", "Music", "Videos"]
        for dir_name in default_dirs:
            self.create_directory(dir_name, "/")
        
        # Create welcome file
        welcome_content = f"""Welcome to Vision Z OS, {self.username}!

Your virtual file system is ready.

Quick Tips:
- Right-click on desktop for menu options
- Use File Explorer to manage your files
- Terminal supports commands like: ls, cd, mkdir, rm, cat, echo

Enjoy your experience!
"""
        self.create_file("Welcome.txt", welcome_content, "/")
        
        # Create readme in Documents
        readme_content = """Documents Folder
Use this folder to store your documents and files.

Supported operations:
- Create, edit, and delete files
- Create folders to organize your work
- Drag and drop to move files
"""
        self.create_file("README.txt", readme_content, "/Documents")
        
        self.save_filesystem()
    
    def _migrate_from_old_format(self, old_data: dict):
        """Migrate from old filesystem format"""
        print(f"[FileSystem] Migrating from old format")
        self.root = FileSystemNode("/", "directory")
        
        # Convert old children format
        if "children" in old_data:
            for name, child_data in old_data["children"].items():
                self.root.children[name] = FileSystemNode.from_dict(name, child_data)
        
        self.save_filesystem()
    
    def save_filesystem(self, create_backup: bool = True):
        """
        Save user's filesystem to storage
        
        Args:
            create_backup: If True, create a backup before saving
        """
        try:
            # Create backup of current file if it exists
            if create_backup and os.path.exists(self.get_user_path()):
                shutil.copy2(self.get_user_path(), self.get_backup_path())
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.get_user_path()), exist_ok=True)
            
            # Save new filesystem
            with open(self.get_user_path(), 'w') as f:
                json.dump(self.root.to_dict(), f, indent=2)
                
        except Exception as e:
            print(f"[FileSystem] Error saving filesystem: {e}")
            raise
    
    def resolve_path(self, path: str) -> Optional[FileSystemNode]:
        """
        Resolve path to actual node
        
        Args:
            path: Absolute or relative path
            
        Returns:
            FileSystemNode if found, None otherwise
        """
        if not path:
            return None
            
        # Normalize path
        if path == "/":
            return self.root
            
        # Handle relative paths
        if not path.startswith('/'):
            path = self.current_path.rstrip('/') + '/' + path
        
        # Split and clean path parts
        parts = [p for p in path.split('/') if p]
        
        current = self.root
        for part in parts:
            if not current or current.type != "directory":
                return None
            if part == "..":
                # For simplicity, we can't go above root
                continue
            if part not in current.children:
                return None
            current = current.children[part]
        
        return current
    
    def get_parent_node(self, path: str) -> Optional[FileSystemNode]:
        """Get the parent node of a path"""
        if path == "/" or not path:
            return None
            
        parent_path = '/'.join(path.split('/')[:-1]) or "/"
        return self.resolve_path(parent_path)
    
    def get_node_name(self, path: str) -> str:
        """Get the name part of a path"""
        if path == "/":
            return "/"
        return path.split('/')[-1]
    
    def list_directory(self, path: str = None, show_hidden: bool = False) -> Optional[List[str]]:
        """
        List contents of directory
        
        Args:
            path: Directory path (uses current_path if None)
            show_hidden: Include hidden files/directories
            
        Returns:
            List of item names or None if directory doesn't exist
        """
        target = path if path else self.current_path
        node = self.resolve_path(target)
        
        if not node or node.type != "directory":
            return None
        
        items = list(node.children.keys())
        
        if not show_hidden:
            items = [item for item in items if not node.children[item].hidden]
        
        # Sort: directories first, then files, alphabetical
        items.sort(key=lambda x: (
            not node.children[x].type == "directory",  # Directories first
            x.lower()  # Case-insensitive alphabetical
        ))
        
        return items
    
    def list_directory_details(self, path: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        List contents of directory with details
        
        Returns:
            List of dictionaries with file details
        """
        target = path if path else self.current_path
        node = self.resolve_path(target)
        
        if not node or node.type != "directory":
            return None
        
        details = []
        for name, child in node.children.items():
            details.append({
                "name": name,
                "type": child.type,
                "size": child.size,
                "modified": child.modified,
                "created": child.created,
                "permissions": child.permissions,
                "owner": child.owner,
                "hidden": child.hidden
            })
        
        # Sort: directories first, then by name
        details.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
        
        return details
    
    def create_directory(self, name: str, path: str = None) -> bool:
        """
        Create a new directory
        
        Args:
            name: Directory name
            path: Parent directory path
            
        Returns:
            True if successful, False otherwise
        """
        if not name or '/' in name or '\\' in name:
            return False
            
        parent_path = path if path else self.current_path
        parent_node = self.resolve_path(parent_path)
        
        if not parent_node or parent_node.type != "directory":
            return False
        
        if name in parent_node.children:
            return False
        
        # Create new directory
        parent_node.children[name] = FileSystemNode(name, "directory")
        parent_node.modified = datetime.now()
        
        self.save_filesystem()
        return True
    
    def create_file(self, name: str, content: str = "", path: str = None) -> bool:
        """
        Create a new file
        
        Args:
            name: File name
            content: Initial file content
            path: Parent directory path
            
        Returns:
            True if successful, False otherwise
        """
        if not name or '/' in name or '\\' in name:
            return False
            
        parent_path = path if path else self.current_path
        parent_node = self.resolve_path(parent_path)
        
        if not parent_node or parent_node.type != "directory":
            return False
        
        if name in parent_node.children:
            return False
        
        # Create new file
        new_file = FileSystemNode(name, "file", content)
        new_file.size = len(content)
        parent_node.children[name] = new_file
        parent_node.modified = datetime.now()
        
        self.save_filesystem()
        return True
    
    def delete_item(self, name: str, path: str = None) -> bool:
        """
        Delete a file or directory
        
        Args:
            name: Item name
            path: Parent directory path
            
        Returns:
            True if successful, False otherwise
        """
        parent_path = path if path else self.current_path
        parent_node = self.resolve_path(parent_path)
        
        if not parent_node or parent_node.type != "directory":
            return False
        
        if name not in parent_node.children:
            return False
        
        # Check if directory is empty
        node = parent_node.children[name]
        if node.type == "directory" and node.children:
            # Directory not empty - could add recursive delete option
            return False
        
        del parent_node.children[name]
        parent_node.modified = datetime.now()
        
        self.save_filesystem()
        return True
    
    def delete_recursive(self, name: str, path: str = None) -> bool:
        """
        Delete a file or directory recursively
        
        Args:
            name: Item name
            path: Parent directory path
            
        Returns:
            True if successful, False otherwise
        """
        parent_path = path if path else self.current_path
        parent_node = self.resolve_path(parent_path)
        
        if not parent_node or parent_node.type != "directory":
            return False
        
        if name not in parent_node.children:
            return False
        
        del parent_node.children[name]
        parent_node.modified = datetime.now()
        
        self.save_filesystem()
        return True
    
    def copy_item(self, source_name: str, source_path: str = None) -> bool:
        """
        Copy an item to clipboard
        
        Args:
            source_name: Name of item to copy
            source_path: Source directory path
            
        Returns:
            True if successful
        """
        parent_path = source_path if source_path else self.current_path
        parent_node = self.resolve_path(parent_path)
        
        if not parent_node or parent_node.type != "directory":
            return False
        
        if source_name not in parent_node.children:
            return False
        
        # Deep copy the node
        self.clipboard = copy.deepcopy(parent_node.children[source_name])
        self.clipboard_operation = "copy"
        return True
    
    def cut_item(self, source_name: str, source_path: str = None) -> bool:
        """
        Cut an item to clipboard
        
        Args:
            source_name: Name of item to cut
            source_path: Source directory path
            
        Returns:
            True if successful
        """
        if self.copy_item(source_name, source_path):
            self.clipboard_operation = "cut"
            return True
        return False
    
    def paste_item(self, dest_path: str = None) -> bool:
        """
        Paste item from clipboard
        
        Args:
            dest_path: Destination directory path
            
        Returns:
            True if successful
        """
        if not self.clipboard:
            return False
        
        parent_path = dest_path if dest_path else self.current_path
        parent_node = self.resolve_path(parent_path)
        
        if not parent_node or parent_node.type != "directory":
            return False
        
        # Generate unique name if exists
        new_name = self.clipboard.name
        counter = 1
        original_name = new_name
        
        while new_name in parent_node.children:
            if '.' in original_name:
                name_part, ext = original_name.rsplit('.', 1)
                new_name = f"{name_part} ({counter}).{ext}"
            else:
                new_name = f"{original_name} ({counter})"
            counter += 1
        
        # Paste the item
        new_node = copy.deepcopy(self.clipboard)
        new_node.name = new_name
        new_node.created = datetime.now()
        new_node.modified = datetime.now()
        parent_node.children[new_name] = new_node
        
        # Clear clipboard if cut
        if self.clipboard_operation == "cut":
            self.clipboard = None
            self.clipboard_operation = None
        
        self.save_filesystem()
        return True
    
    def rename_item(self, old_name: str, new_name: str, path: str = None) -> bool:
        """
        Rename a file or directory
        
        Args:
            old_name: Current name
            new_name: New name
            path: Parent directory path
            
        Returns:
            True if successful
        """
        if not new_name or '/' in new_name or '\\' in new_name:
            return False
            
        parent_path = path if path else self.current_path
        parent_node = self.resolve_path(parent_path)
        
        if not parent_node or parent_node.type != "directory":
            return False
        
        if old_name not in parent_node.children:
            return False
        
        if new_name in parent_node.children:
            return False
        
        # Rename by creating new entry and removing old
        node = parent_node.children[old_name]
        node.name = new_name
        node.modified = datetime.now()
        parent_node.children[new_name] = node
        del parent_node.children[old_name]
        
        self.save_filesystem()
        return True
    
    def move_item(self, item_name: str, source_path: str, dest_path: str) -> bool:
        """
        Move an item from source to destination
        
        Args:
            item_name: Name of item to move
            source_path: Source directory path
            dest_path: Destination directory path
            
        Returns:
            True if successful
        """
        source_node = self.resolve_path(source_path)
        dest_node = self.resolve_path(dest_path)
        
        if not source_node or not dest_node:
            return False
        if source_node.type != "directory" or dest_node.type != "directory":
            return False
        if item_name not in source_node.children:
            return False
        if item_name in dest_node.children:
            return False
        
        # Move the item
        dest_node.children[item_name] = source_node.children[item_name]
        del source_node.children[item_name]
        dest_node.children[item_name].modified = datetime.now()
        
        self.save_filesystem()
        return True
    
    def change_directory(self, path: str) -> bool:
        """
        Change current directory
        
        Args:
            path: Target directory path
            
        Returns:
            True if successful
        """
        if path == "..":
            if self.current_path != "/":
                # Add to history
                self._add_to_history()
                self.current_path = '/'.join(self.current_path.split('/')[:-1]) or "/"
            return True
        
        node = self.resolve_path(path)
        if node and node.type == "directory":
            self._add_to_history()
            
            if path.startswith('/'):
                self.current_path = path
            else:
                self.current_path = self.current_path.rstrip('/') + '/' + path
            
            # Normalize path
            self.current_path = os.path.normpath(self.current_path).replace('\\', '/')
            return True
        
        return False
    
    def _add_to_history(self):
        """Add current path to navigation history"""
        # Remove future history if we navigated back
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(self.current_path)
        self.history_index = len(self.history) - 1
    
    def navigate_back(self) -> bool:
        """Navigate back in history"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_path = self.history[self.history_index]
            return True
        return False
    
    def navigate_forward(self) -> bool:
        """Navigate forward in history"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_path = self.history[self.history_index]
            return True
        return False
    
    def get_current_path(self) -> str:
        """Get current working directory"""
        return self.current_path
    
    def read_file(self, file_path: str) -> Optional[str]:
        """
        Read file content
        
        Args:
            file_path: Path to file
            
        Returns:
            File content or None if not found
        """
        node = self.resolve_path(file_path)
        if node and node.type == "file":
            return node.content
        return None
    
    def write_file(self, file_path: str, content: str) -> bool:
        """
        Write content to file
        
        Args:
            file_path: Path to file
            content: New content
            
        Returns:
            True if successful
        """
        node = self.resolve_path(file_path)
        if node and node.type == "file":
            node.content = content
            node.size = len(content)
            node.modified = datetime.now()
            self.save_filesystem()
            return True
        return False
    
    def append_file(self, file_path: str, content: str) -> bool:
        """
        Append content to file
        
        Args:
            file_path: Path to file
            content: Content to append
            
        Returns:
            True if successful
        """
        node = self.resolve_path(file_path)
        if node and node.type == "file":
            node.content += content
            node.size = len(node.content)
            node.modified = datetime.now()
            self.save_filesystem()
            return True
        return False
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists"""
        node = self.resolve_path(path)
        return node is not None and node.type == "file"
    
    def directory_exists(self, path: str) -> bool:
        """Check if directory exists"""
        node = self.resolve_path(path)
        return node is not None and node.type == "directory"
    
    def get_file_size(self, path: str) -> Optional[int]:
        """Get file size in bytes"""
        node = self.resolve_path(path)
        if node:
            return node.size
        return None
    
    def get_file_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Get detailed file information"""
        node = self.resolve_path(path)
        if node:
            return {
                "name": node.name,
                "type": node.type,
                "size": node.size,
                "created": node.created,
                "modified": node.modified,
                "permissions": node.permissions,
                "owner": node.owner,
                "hidden": node.hidden
            }
        return None
    
    def set_hidden(self, path: str, hidden: bool = True) -> bool:
        """Set hidden attribute on file/directory"""
        node = self.resolve_path(path)
        if node:
            node.hidden = hidden
            self.save_filesystem()
            return True
        return False
    
    def get_directory_size(self, path: str = "/") -> int:
        """Calculate total size of directory recursively"""
        node = self.resolve_path(path)
        if not node:
            return 0
        
        if node.type == "file":
            return node.size
        
        total_size = 0
        for child in node.children.values():
            total_size += self.get_directory_size(
                path.rstrip('/') + '/' + child.name
            )
        
        return total_size
    
    def search_files(self, query: str, path: str = "/") -> List[str]:
        """
        Search for files and directories
        
        Args:
            query: Search query (case-insensitive)
            path: Starting path for search
            
        Returns:
            List of matching paths
        """
        results = []
        node = self.resolve_path(path)
        
        if not node or node.type == "file":
            return results
        
        query_lower = query.lower()
        
        for name, child in node.children.items():
            full_path = path.rstrip('/') + '/' + name
            
            # Check if name matches
            if query_lower in name.lower():
                results.append(full_path)
            
            # Recurse into directories
            if child.type == "directory":
                results.extend(self.search_files(query, full_path))
        
        return results
    
    def get_tree(self, path: str = "/", indent: str = "") -> str:
        """
        Get directory tree as string
        
        Args:
            path: Starting path
            indent: Current indentation
            
        Returns:
            Formatted tree string
        """
        node = self.resolve_path(path)
        if not node or node.type != "directory":
            return ""
        
        tree = ""
        items = list(node.children.items())
        
        for i, (name, child) in enumerate(items):
            is_last = i == len(items) - 1
            prefix = "└── " if is_last else "├── "
            
            tree += f"{indent}{prefix}{name}"
            if child.type == "file":
                size_str = self._format_size(child.size)
                tree += f" ({size_str})"
            tree += "\n"
            
            if child.type == "directory":
                next_indent = indent + ("    " if is_last else "│   ")
                tree += self.get_tree(path.rstrip('/') + '/' + name, next_indent)
        
        return tree
    
    def _format_size(self, size: int) -> str:
        """Format file size to human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def export_filesystem(self, export_path: str = None) -> bool:
        """
        Export filesystem to JSON file
        
        Args:
            export_path: Path to export file
            
        Returns:
            True if successful
        """
        if not export_path:
            export_path = f"data/exports/{self.username}_filesystem_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            with open(export_path, 'w') as f:
                json.dump(self.root.to_dict(), f, indent=2)
            return True
        except Exception as e:
            print(f"[FileSystem] Export error: {e}")
            return False
    
    def import_filesystem(self, import_path: str) -> bool:
        """
        Import filesystem from JSON file
        
        Args:
            import_path: Path to import file
            
        Returns:
            True if successful
        """
        try:
            with open(import_path, 'r') as f:
                data = json.load(f)
            
            self.root = FileSystemNode.from_dict("/", data)
            self.current_path = "/"
            self.save_filesystem()
            return True
        except Exception as e:
            print(f"[FileSystem] Import error: {e}")
            return False