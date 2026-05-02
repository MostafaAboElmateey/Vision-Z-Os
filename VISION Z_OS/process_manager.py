"""
Process Manager - Handles running processes and task management
"""

import random
from datetime import datetime

class Process:
    """Represents a running process"""
    
    def __init__(self, name, pid, process_type="app"):
        self.name = name
        self.pid = pid
        self.type = process_type
        self.start_time = datetime.now()
        self.cpu_usage = 0
        self.memory_usage = 0
        
class ProcessManager:
    """Manages all running processes"""
    
    def __init__(self):
        self.processes = {}
        self.next_pid = 1000
        
    def create_process(self, name, process_type="app"):
        """Create a new process"""
        pid = self.next_pid
        self.next_pid += 1
        
        process = Process(name, pid, process_type)
        self.processes[pid] = process
        
        # Simulate resource usage
        self.update_process_resources(process)
        
        print(f"[ProcessManager] Created process: {name} (PID: {pid}, Type: {process_type})")
        return pid
        
    def update_process_resources(self, process):
        """Simulate CPU and memory usage updates"""
        process.cpu_usage = random.randint(1, 30)
        process.memory_usage = random.randint(10, 200)
        
    def terminate_process(self, pid):
        """Terminate a running process"""
        if pid in self.processes:
            process_name = self.processes[pid].name
            del self.processes[pid]
            print(f"[ProcessManager] Terminated process: {process_name} (PID: {pid})")
            return True
        print(f"[ProcessManager] Process not found: PID {pid}")
        return False
        
    def get_all_processes(self):
        """Get list of all running processes"""
        # Update resource usage for all processes
        for process in self.processes.values():
            self.update_process_resources(process)
        return list(self.processes.values())
        
    def get_system_stats(self):
        """Get simulated system statistics"""
        return {
            'cpu_percent': random.randint(10, 80),
            'memory_percent': random.randint(20, 70),
            'memory_used': random.randint(1024, 4096),
            'memory_total': 8192
        }