"""
Terminal Emulator - Linux-like command interface with advanced commands (FIXED)
"""

import os
from file_system import FileSystem
from datetime import datetime
import random
import platform

class Terminal:
    """Linux-like terminal emulator with command parsing"""
    
    def __init__(self, filesystem, process_manager=None):
        self.filesystem = filesystem
        self.process_manager = process_manager
        self.command_history = []
        self.permissions = {}
        
    def execute_command(self, command_line):
        """Parse and execute a command"""
        if not command_line.strip():
            return ""
        
        # Save to history
        self.command_history.append(command_line)
        if len(self.command_history) > 50:
            self.command_history.pop(0)
            
        parts = command_line.strip().split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        commands = {
            # Basic commands
            'ls': self.cmd_ls,
            'cd': self.cmd_cd,
            'mkdir': self.cmd_mkdir,
            'touch': self.cmd_touch,
            'rm': self.cmd_rm,
            'pwd': self.cmd_pwd,
            'clear': self.cmd_clear,
            'cat': self.cmd_cat,
            'echo': self.cmd_echo,
            'help': self.cmd_help,
            'whoami': self.cmd_whoami,
            'date': self.cmd_date,
            'tree': self.cmd_tree,
            'mv': self.cmd_mv,
            'cp': self.cmd_cp,
            'find': self.cmd_find,
            'grep': self.cmd_grep,
            'history': self.cmd_history,
            
            # Permission commands
            'chmod': self.cmd_chmod,
            'chown': self.cmd_chown,
            'ls-l': self.cmd_ls_l,
            'stat': self.cmd_stat,
            
            # Network commands
            'ipconfig': self.cmd_ipconfig,
            'ifconfig': self.cmd_ipconfig,
            'ping': self.cmd_ping,
            'netstat': self.cmd_netstat,
            'hostname': self.cmd_hostname,
            
            # Process commands
            'ps': self.cmd_ps,
            'kill': self.cmd_kill,
            'top': self.cmd_top,
            
            # System commands
            'uname': self.cmd_uname,
            'uptime': self.cmd_uptime,
            'who': self.cmd_who,
            'users': self.cmd_users,
            'neofetch': self.cmd_neofetch,
            
            # File commands
            'head': self.cmd_head,
            'tail': self.cmd_tail,
            'wc': self.cmd_wc,
            'sort': self.cmd_sort,
            'uniq': self.cmd_uniq,
        }
        
        if cmd in commands:
            try:
                return commands[cmd](args)
            except Exception as e:
                return f"Error: {str(e)}"
        else:
            return f"Command not found: {cmd}. Type 'help' for available commands."
    
    # ============= BASIC COMMANDS =============

    def _build_path(self, base, name):
        """Helper: join base path and name correctly"""
        if base == "/":
            return f"/{name}"
        return f"{base}/{name}"

    def cmd_ls(self, args):
        """List directory contents"""
        path = args[0] if args else None
        target = path if path else self.filesystem.get_current_path()
        
        # ✅ استخدام list_directory من نظام الملفات الجديد
        files = self.filesystem.list_directory(target)
        if files is None:
            return f"Directory not found: {target}"
        
        if not files:
            return "Directory is empty"
        
        output = ""
        for f in files:
            node = self.filesystem.resolve_path(self._build_path(target, f))
            if node:
                # ✅ استخدام node.type بدلاً من node["type"]
                if node.type == "directory":
                    output += f"📁 {f}\n"
                else:
                    output += f"📄 {f}\n"
            else:
                output += f"  {f}\n"
        return output.rstrip()
    
    def cmd_ls_l(self, args):
        """List directory contents with details"""
        path = args[0] if args else None
        target = path if path else self.filesystem.get_current_path()
        
        # ✅ استخدام list_directory_details
        details = self.filesystem.list_directory_details(target)
        if details is None:
            return f"Directory not found: {target}"
        
        if not details:
            return "Directory is empty"
        
        output = "Permissions   Size  User     Date     Name\n"
        output += "-" * 60 + "\n"
        
        for item in details:
            perms = item.get('permissions', 'rwxr-xr-x')
            size = item['size'] if item['type'] == 'file' else 0
            # تنسيق الحجم
            if size < 1024:
                size_str = f"{size}B"
            elif size < 1024*1024:
                size_str = f"{size/1024:.1f}K"
            else:
                size_str = f"{size/(1024*1024):.1f}M"
            
            # تنسيق التاريخ
            try:
                if isinstance(item['modified'], datetime):
                    modified = item['modified'].strftime("%Y-%m-%d")
                else:
                    modified = str(item['modified']).split("T")[0]
            except:
                modified = "N/A"
            
            icon = "📁" if item['type'] == "directory" else "📄"
            output += f"{perms}  {size_str:>5}  {item.get('owner', 'user'):<8}  {modified}  {icon} {item['name']}\n"
        return output
    
    def cmd_cd(self, args):
        """Change directory"""
        if not args:
            self.filesystem.current_path = "/"
            return ""
            
        if self.filesystem.change_directory(args[0]):
            return ""
        return f"Directory not found: {args[0]}"
    
    def cmd_mkdir(self, args):
        """Create directory"""
        if not args:
            return "Usage: mkdir <directory_name>"
            
        if self.filesystem.create_directory(args[0]):
            return f"✅ Directory '{args[0]}' created"
        return f"❌ Cannot create directory '{args[0]}'"
    
    def cmd_touch(self, args):
        """Create file"""
        if not args:
            return "Usage: touch <filename>"
            
        if self.filesystem.create_file(args[0], ""):
            return f"✅ File '{args[0]}' created"
        return f"❌ Cannot create file '{args[0]}'"
    
    def cmd_rm(self, args):
        """Remove file or directory"""
        if not args:
            return "Usage: rm <name>"
        
        # ✅ التحقق من النوع قبل الحذف
        path = self._build_path(self.filesystem.get_current_path(), args[0])
        node = self.filesystem.resolve_path(path)
        
        if node and node.type == "directory":
            if self.filesystem.delete_recursive(args[0]):
                return f"✅ Directory '{args[0]}' removed"
            return f"❌ Cannot remove directory '{args[0]}'"
        else:
            if self.filesystem.delete_item(args[0]):
                return f"✅ '{args[0]}' removed"
            return f"❌ Cannot remove '{args[0]}'"
    
    def cmd_pwd(self, args):
        """Print working directory"""
        return self.filesystem.get_current_path()
    
    def cmd_clear(self, args):
        """Clear terminal"""
        return "CLEAR_SCREEN"
    
    def cmd_cat(self, args):
        """Display file content"""
        if not args:
            return "Usage: cat <filename>"
        
        file_path = self._build_path(self.filesystem.get_current_path(), args[0])
        content = self.filesystem.read_file(file_path)
        if content is not None:
            return content
        return f"❌ File '{args[0]}' not found"
    
    def cmd_echo(self, args):
        """Echo text to terminal or file"""
        if not args:
            return ""
            
        text = ' '.join(args)
        
        if '>>' in text:
            parts = text.split('>>', 1)
            content = parts[0].strip()
            filename = parts[1].strip()
            file_path = self._build_path(self.filesystem.get_current_path(), filename)
            
            if self.filesystem.append_file(file_path, "\n" + content):
                return f"✅ Appended to {filename}"
            elif self.filesystem.create_file(filename, content):
                return f"✅ Written to {filename}"
            return f"❌ Cannot write to {filename}"
        elif '>' in text:
            parts = text.split('>', 1)
            content = parts[0].strip()
            filename = parts[1].strip()
            file_path = self._build_path(self.filesystem.get_current_path(), filename)
            
            if self.filesystem.write_file(file_path, content):
                return f"✅ Written to {filename}"
            elif self.filesystem.create_file(filename, content):
                return f"✅ Written to {filename}"
            return f"❌ Cannot write to {filename}"
            
        return text
    
    def cmd_mv(self, args):
        """Move or rename file"""
        if len(args) < 2:
            return "Usage: mv <source> <destination>"
        
        source_path = self._build_path(self.filesystem.get_current_path(), args[0])
        source_node = self.filesystem.resolve_path(source_path)
        if not source_node:
            return f"❌ Source '{args[0]}' not found"
        
        source_name = args[0].split('/')[-1] if '/' in args[0] else args[0]
        
        if self.filesystem.rename_item(source_name, args[1]):
            return f"✅ Moved '{args[0]}' to '{args[1]}'"
        return f"❌ Cannot move '{args[0]}'"
    
    def cmd_cp(self, args):
        """Copy file"""
        if len(args) < 2:
            return "Usage: cp <source> <destination>"
        
        source_path = self._build_path(self.filesystem.get_current_path(), args[0])
        source_content = self.filesystem.read_file(source_path)
        if source_content is None:
            return f"❌ Source '{args[0]}' not found"
        
        if self.filesystem.create_file(args[1], source_content):
            return f"✅ Copied '{args[0]}' to '{args[1]}'"
        return f"❌ Cannot copy '{args[0]}'"
    
    def cmd_find(self, args):
        """Find files by name"""
        if not args:
            return "Usage: find <filename>"
        
        query = args[0]
        # ✅ استخدام search_files من نظام الملفات الجديد
        results = self.filesystem.search_files(query)
        
        if results:
            return "Found:\n" + "\n".join(results)
        return f"No files found matching '{query}'"
    
    def cmd_grep(self, args):
        """Search for text in files"""
        if len(args) < 2:
            return "Usage: grep <pattern> <filename>"
        
        pattern = args[0]
        filename = args[1]
        file_path = self._build_path(self.filesystem.get_current_path(), filename)
        
        content = self.filesystem.read_file(file_path)
        if content is None:
            return f"❌ File '{filename}' not found"
        
        lines = content.split('\n')
        matches = []
        for i, line in enumerate(lines, 1):
            if pattern.lower() in line.lower():
                matches.append(f"{i}: {line}")
        
        if matches:
            return f"Matches for '{pattern}' in {filename}:\n" + "\n".join(matches)
        return f"No matches found for '{pattern}'"
    
    def cmd_history(self, args):
        """Show command history"""
        if not self.command_history:
            return "No command history"
        
        output = "Command History:\n"
        for i, cmd in enumerate(self.command_history[-20:], 1):
            output += f"  {i:3}.  {cmd}\n"
        return output
    
    # ============= PERMISSION COMMANDS =============
    
    def get_permissions(self, filename):
        """Get file permissions"""
        path = f"{self.filesystem.get_current_path()}/{filename}" if self.filesystem.get_current_path() != "/" else f"/{filename}"
        if path in self.permissions:
            return self.permissions[path]["perms"]
        return "rw-r--r--"
    
    def cmd_chmod(self, args):
        """Change file permissions"""
        if len(args) < 2:
            return "Usage: chmod <permissions> <filename>"
        
        perms = args[0]
        filename = args[1]
        path = f"{self.filesystem.get_current_path()}/{filename}" if self.filesystem.get_current_path() != "/" else f"/{filename}"
        
        if perms.isdigit() and len(perms) == 3:
            perm_map = {
                '0': '---', '1': '--x', '2': '-w-', '3': '-wx',
                '4': 'r--', '5': 'r-x', '6': 'rw-', '7': 'rwx'
            }
            user_perm = perm_map.get(perms[0], '---')
            group_perm = perm_map.get(perms[1], '---')
            other_perm = perm_map.get(perms[2], '---')
            perm_string = f"{user_perm}{group_perm}{other_perm}"
        else:
            perm_string = perms
        
        if path not in self.permissions:
            self.permissions[path] = {"owner": self.filesystem.username, "perms": "rw-r--r--"}
        
        self.permissions[path]["perms"] = perm_string
        return f"✅ Changed permissions for '{filename}' to {perm_string}"
    
    def cmd_chown(self, args):
        """Change file owner"""
        if len(args) < 2:
            return "Usage: chown <user> <filename>"
        
        owner = args[0]
        filename = args[1]
        path = f"{self.filesystem.get_current_path()}/{filename}" if self.filesystem.get_current_path() != "/" else f"/{filename}"
        
        if path not in self.permissions:
            self.permissions[path] = {"owner": self.filesystem.username, "perms": "rw-r--r--"}
        
        self.permissions[path]["owner"] = owner
        return f"✅ Changed owner of '{filename}' to {owner}"
    
    def cmd_stat(self, args):
        """Display file statistics"""
        if not args:
            return "Usage: stat <filename>"
        
        filename = args[0]
        file_path = self._build_path(self.filesystem.get_current_path(), filename)
        
        # ✅ استخدام get_file_info من نظام الملفات الجديد
        info = self.filesystem.get_file_info(file_path)
        if not info:
            return f"❌ File '{filename}' not found"
        
        perms = self.get_permissions(filename)
        
        output = f"""
File: {filename}
Type: {info['type']}
Size: {info['size']} bytes
Permissions: {perms}
Owner: {info.get('owner', self.filesystem.username)}
Created: {info.get('created', 'N/A')}
Modified: {info.get('modified', 'N/A')}
"""
        return output
    
    # ============= NETWORK COMMANDS =============
    
    def cmd_ipconfig(self, args):
        """Display network configuration"""
        hostname = platform.node()
        random.seed(hash(hostname))
        
        info = f"""
Network Configuration - Vision Z OS
=====================================
Hostname: {hostname}

Ethernet adapter:
   IPv4: 192.168.{random.randint(1,255)}.{random.randint(1,255)}
   Subnet: 255.255.255.0
   Gateway: 192.168.{random.randint(1,255)}.1
   DNS: 8.8.8.8, 8.8.4.4
"""
        return info
    
    def cmd_ping(self, args):
        """Ping a host"""
        if not args:
            return "Usage: ping <hostname or IP>"
        
        host = args[0]
        result = f"Pinging {host} with 32 bytes of data:\n\n"
        
        times = [random.randint(1, 50) for _ in range(4)]
        for i, t in enumerate(times, 1):
            result += f"Reply from {host}: bytes=32 time={t}ms TTL=64\n"
        
        result += f"\nPing statistics: Sent=4, Received=4, Lost=0"
        return result
    
    def cmd_netstat(self, args):
        """Display network statistics"""
        output = "Active Connections\n\nProto  Local Address          State\n"
        output += "-" * 45 + "\n"
        output += "TCP   192.168.1.100:443     ESTABLISHED\n"
        output += "TCP   127.0.0.1:8080        LISTENING\n"
        output += "UDP   0.0.0.0:53            LISTENING\n"
        return output
    
    def cmd_hostname(self, args):
        """Display computer name"""
        return platform.node()
    
    # ============= PROCESS COMMANDS =============
    
    def cmd_ps(self, args):
        """Display running processes"""
        if not self.process_manager:
            return "Process manager not available"
        
        processes = self.process_manager.get_all_processes()
        
        output = "PID   Name                          Type     Status\n"
        output += "-" * 55 + "\n"
        
        for proc in processes:
            status = "Running" if getattr(proc, 'running', True) else "Stopped"
            output += f"{proc.pid:<5} {proc.name:<30} {proc.type:<8} {status}\n"
        
        return output
    
    def cmd_kill(self, args):
        """Terminate a process"""
        if not args:
            return "Usage: kill <PID>"
        
        try:
            pid = int(args[0])
            if self.process_manager and self.process_manager.terminate_process(pid):
                return f"✅ Process {pid} terminated"
            return f"❌ Cannot terminate process {pid}"
        except ValueError:
            return f"❌ Invalid PID: {args[0]}"
    
    def cmd_top(self, args):
        """Display process monitor"""
        if not self.process_manager:
            return "Process manager not available"
        
        stats = self.process_manager.get_system_stats()
        
        output = f"""
Vision Z OS Process Monitor
CPU: {stats.get('cpu_percent', 0)}%  Memory: {stats.get('memory_percent', 0)}%
PID     CPU%    MEM%    Command
-----------------------------------------"""
        
        processes = self.process_manager.get_all_processes()
        for proc in processes[:10]:
            output += f"\n{proc.pid:<7} {getattr(proc, 'cpu_usage', 0):<7} {getattr(proc, 'memory_usage', 0):<7} {proc.name}"
        
        return output
    
    # ============= SYSTEM COMMANDS =============
    
    def cmd_uname(self, args):
        """Display system information"""
        return f"""
Vision Z OS 2.0
Kernel: 6.1.0-visionz
Architecture: x86_64
Hostname: {platform.node()}
"""
    
    def cmd_uptime(self, args):
        """Display system uptime"""
        import time
        uptime_seconds = random.randint(3600, 86400)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        return f"Uptime: {hours} hours, {minutes} minutes"
    
    def cmd_who(self, args):
        """Display logged in users"""
        return f"{self.filesystem.username}  pts/0  {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    def cmd_users(self, args):
        """Display logged in users"""
        return self.filesystem.username
    
    def cmd_neofetch(self, args):
        """Display system info with logo"""
        return f"""
    ╭──────────────────────────────────╮
    │     ██╗   ██╗██╗███████╗██╗      │
    │     ██║   ██║██║██╔════╝██║      │
    │     ██║   ██║██║███████╗██║      │
    │     ╚██╗ ██╔╝██║╚════██║██║      │
    │      ╚████╔╝ ██║███████║██║      │
    │       ╚═══╝  ╚═╝╚══════╝╚═╝      │
    │                                    │
    │  OS: Vision Z OS 2.0               │
    │  Kernel: 6.1.0-visionz             │
    │  User: {self.filesystem.username:<28}│
    │  Terminal: VisionZ Terminal         │
    ╰──────────────────────────────────╯
"""
    
    # ============= FILE CONTENT COMMANDS =============
    
    def cmd_head(self, args):
        """Display first lines of file"""
        if not args:
            return "Usage: head <filename> [lines]"
        
        filename = args[0]
        lines_count = int(args[1]) if len(args) > 1 else 10
        file_path = self._build_path(self.filesystem.get_current_path(), filename)
        
        content = self.filesystem.read_file(file_path)
        if content is None:
            return f"❌ File '{filename}' not found"
        
        lines = content.split('\n')[:lines_count]
        return '\n'.join(lines)
    
    def cmd_tail(self, args):
        """Display last lines of file"""
        if not args:
            return "Usage: tail <filename> [lines]"
        
        filename = args[0]
        lines_count = int(args[1]) if len(args) > 1 else 10
        file_path = self._build_path(self.filesystem.get_current_path(), filename)
        
        content = self.filesystem.read_file(file_path)
        if content is None:
            return f"❌ File '{filename}' not found"
        
        lines = content.split('\n')[-lines_count:]
        return '\n'.join(lines)
    
    def cmd_wc(self, args):
        """Count lines, words, characters"""
        if not args:
            return "Usage: wc <filename>"
        
        filename = args[0]
        file_path = self._build_path(self.filesystem.get_current_path(), filename)
        
        content = self.filesystem.read_file(file_path)
        if content is None:
            return f"❌ File '{filename}' not found"
        
        lines = len(content.split('\n'))
        words = len(content.split())
        chars = len(content)
        
        return f"📊 {filename}: {lines} lines, {words} words, {chars} characters"
    
    def cmd_sort(self, args):
        """Sort lines in file"""
        if not args:
            return "Usage: sort <filename>"
        
        filename = args[0]
        file_path = self._build_path(self.filesystem.get_current_path(), filename)
        
        content = self.filesystem.read_file(file_path)
        if content is None:
            return f"❌ File '{filename}' not found"
        
        lines = sorted(content.split('\n'))
        return '\n'.join(lines)
    
    def cmd_uniq(self, args):
        """Display unique lines"""
        if not args:
            return "Usage: uniq <filename>"
        
        filename = args[0]
        file_path = self._build_path(self.filesystem.get_current_path(), filename)
        
        content = self.filesystem.read_file(file_path)
        if content is None:
            return f"❌ File '{filename}' not found"
        
        seen = set()
        unique_lines = []
        for line in content.split('\n'):
            if line not in seen:
                seen.add(line)
                unique_lines.append(line)
        
        return '\n'.join(unique_lines)
    
    def cmd_tree(self, args):
        """Display directory tree"""
        # ✅ استخدام get_tree من نظام الملفات الجديد
        path = args[0] if args else self.filesystem.get_current_path()
        tree = self.filesystem.get_tree(path)
        return tree if tree else f"Cannot display tree for {path}"
    
    def cmd_help(self, args):
        """Display help information"""
        return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        Vision Z OS Terminal v2.0                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📁 FILE COMMANDS:                                                           ║
║     ls, ls-l     - List directory contents with details                      ║
║     cd <dir>     - Change directory                                          ║
║     pwd          - Print working directory                                   ║
║     mkdir <name> - Create directory                                          ║
║     touch <file> - Create file                                               ║
║     rm <name>    - Remove file/directory                                     ║
║     cat <file>   - Display file content                                      ║
║     echo <text>  - Display text or write to file (> or >>)                   ║
║     mv, cp       - Move or copy files                                        ║
║     find <name>  - Find files by name                                        ║
║     grep <p> <f> - Search for pattern in file                                ║
║     head, tail   - Display first/last lines of file                          ║
║     wc <file>    - Count lines, words, characters                            ║
║     tree         - Display directory tree                                    ║
║                                                                              ║
║  🔒 PERMISSION COMMANDS:                                                     ║
║     chmod <perm> <file> - Change permissions (755, rwxr-xr-x)                ║
║     chown <user> <file> - Change file owner                                  ║
║     stat <file>         - Display file statistics                            ║
║                                                                              ║
║  🌐 NETWORK COMMANDS:                                                        ║
║     ipconfig     - Display network configuration                             ║
║     ping <host>  - Ping a host                                              ║
║     netstat      - Display network statistics                                ║
║     hostname     - Display computer name                                     ║
║                                                                              ║
║  ⚙️ PROCESS COMMANDS:                                                        ║
║     ps           - List running processes                                    ║
║     kill <PID>   - Terminate a process                                       ║
║     top          - Display process monitor                                   ║
║                                                                              ║
║  🖥️ SYSTEM COMMANDS:                                                         ║
║     uname        - Display system information                                ║
║     uptime       - Show system uptime                                        ║
║     whoami       - Show current user                                         ║
║     date         - Show current date/time                                    ║
║     who, users   - Show logged in users                                      ║
║     neofetch     - Display system info with logo                             ║
║     clear        - Clear terminal screen                                     ║
║     history      - Show command history                                      ║
║     help         - Show this help                                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    
    def cmd_whoami(self, args):
        """Show current user"""
        return self.filesystem.username
    
    def cmd_date(self, args):
        """Show current date and time"""
        return datetime.now().strftime("%A, %B %d, %Y - %I:%M:%S %p")