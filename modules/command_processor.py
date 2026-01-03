import json
import re
from modules.window_manager import WindowManager
from modules.application_manager import ApplicationManager
from modules.file_system_manager import FileSystemManager
from modules.system_monitor import SystemMonitor

class CommandProcessor:
    def __init__(self):
        self.window_manager = WindowManager()
        self.app_manager = ApplicationManager()
        self.file_manager = FileSystemManager()
        self.system_monitor = SystemMonitor()
        
        # Advanced command patterns
        self.command_patterns = {
            'window_management': {
                r'close (window|this)': self.close_window,
                r'focus (\w+)': self.focus_application,
                r'switch to (\w+)': self.focus_application,
                r'fullscreen': self.toggle_fullscreen,
                r'move window (left|right|up|down)': self.move_window,
                r'resize window (bigger|smaller)': self.resize_window,
                r'workspace (\d+)': self.switch_workspace,
                r'move to workspace (\d+)': self.move_to_workspace,
            },
            'application_control': {
                r'launch (\w+)': self.launch_app,
                r'open (\w+)': self.launch_app,
                r'start (\w+)': self.launch_app,
                r'kill (\w+)': self.kill_app,
                r'restart (\w+)': self.restart_app,
                r'is (\w+) running': self.check_app_running,
            },
            'file_operations': {
                r'create folder (.+)': self.create_folder,
                r'create file (.+)': self.create_file,
                r'delete (.+)': self.delete_item,
                r'copy (.+) to (.+)': self.copy_item,
                r'move (.+) to (.+)': self.move_item,
                r'find (.+)': self.find_files,
                r'search for (.+)': self.search_in_files,
                r'go to (.+)': self.change_directory,
                r'list files': self.list_files,
            },
            'system_info': {
                r'cpu usage': self.get_cpu_info,
                r'memory usage': self.get_memory_info,
                r'disk usage': self.get_disk_info,
                r'system status': self.get_system_summary,
                r'running processes': self.get_processes,
                r'uptime': self.get_uptime,
                r'temperature': self.get_temperature,
            }
        }
    
    def process_command(self, user_input):
        """Process natural language commands"""
        user_input = user_input.lower().strip()
        
        for category, patterns in self.command_patterns.items():
            for pattern, handler in patterns.items():
                match = re.search(pattern, user_input)
                if match:
                    try:
                        if match.groups():
                            return handler(*match.groups())
                        else:
                            return handler()
                    except Exception as e:
                        return False, f"Error executing command: {e}"
        
        return None  # No pattern matched
    
    # Window Management Commands
    def close_window(self):
        success = self.window_manager.close_window()
        return success, "Window closed" if success else "Failed to close window"
    
    def focus_application(self, app_name):
        success = self.window_manager.focus_window(app_name)
        return success, f"Focused {app_name}" if success else f"Could not focus {app_name}"
    
    def toggle_fullscreen(self):
        success = self.window_manager.toggle_fullscreen()
        return success, "Toggled fullscreen" if success else "Failed to toggle fullscreen"
    
    def move_window(self, direction):
        success = self.window_manager.move_window(direction)
        return success, f"Moved window {direction}" if success else f"Failed to move window"
    
    def resize_window(self, size):
        amount = 50 if size == "bigger" else -50
        success = self.window_manager.resize_window("right", amount)
        return success, f"Resized window {size}" if success else "Failed to resize window"
    
    def switch_workspace(self, workspace):
        success = self.window_manager.switch_workspace(workspace)
        return success, f"Switched to workspace {workspace}" if success else f"Failed to switch workspace"
    
    def move_to_workspace(self, workspace):
        success = self.window_manager.move_to_workspace(workspace)
        return success, f"Moved to workspace {workspace}" if success else f"Failed to move to workspace"
    
    # Application Management Commands
    def launch_app(self, app_name):
        success, message = self.app_manager.launch_app(app_name)
        return success, message
    
    def kill_app(self, app_name):
        success, message = self.app_manager.kill_app(app_name)
        return success, message
    
    def restart_app(self, app_name):
        success, message = self.app_manager.restart_app(app_name)
        return success, message
    
    def check_app_running(self, app_name):
        running = self.app_manager.is_app_running(app_name)
        return True, f"{app_name} is {'running' if running else 'not running'}"
    
    # File System Commands
    def create_folder(self, folder_name):
        success, message = self.file_manager.create_directory(folder_name)
        return success, message
    
    def create_file(self, file_name):
        success, message = self.file_manager.create_file(file_name)
        return success, message
    
    def delete_item(self, item_name):
        success, message = self.file_manager.delete_file(item_name)
        return success, message
    
    def copy_item(self, source, destination):
        success, message = self.file_manager.copy_file(source, destination)
        return success, message
    
    def move_item(self, source, destination):
        success, message = self.file_manager.move_file(source, destination)
        return success, message
    
    def find_files(self, pattern):
        success, results = self.file_manager.find_files(pattern)
        if success:
            if results:
                return True, f"Found {len(results)} files: {', '.join(results[:5])}"
            else:
                return True, "No files found matching pattern"
        return success, results
    
    def search_in_files(self, pattern):
        success, results = self.file_manager.search_in_files(pattern)
        if success:
            if results:
                return True, f"Found {len(results)} matches in files"
            else:
                return True, "No matches found"
        return success, results
    
    def change_directory(self, path):
        success, message = self.file_manager.change_directory(path)
        return success, message
    
    def list_files(self):
        success, items = self.file_manager.list_directory()
        if success:
            file_count = len([i for i in items if i['type'] == 'file'])
            dir_count = len([i for i in items if i['type'] == 'dir'])
            return True, f"Found {file_count} files and {dir_count} directories"
        return success, items
    
    # System Information Commands
    def get_cpu_info(self):
        info = self.system_monitor.get_cpu_info()
        if 'error' not in info:
            return True, f"CPU usage: {info['usage_percent']:.1f}% ({info['core_count']} cores)"
        return False, info['error']
    
    def get_memory_info(self):
        info = self.system_monitor.get_memory_info()
        if 'error' not in info:
            mem = info['virtual']
            return True, f"Memory: {mem['percent']:.1f}% used ({mem['used']//1024//1024//1024}GB/{mem['total']//1024//1024//1024}GB)"
        return False, info['error']
    
    def get_disk_info(self):
        info = self.system_monitor.get_disk_info()
        if isinstance(info, list) and info:
            main_disk = info[0]
            return True, f"Disk: {main_disk['percent']:.1f}% used ({main_disk['used']//1024//1024//1024}GB/{main_disk['total']//1024//1024//1024}GB)"
        return False, "Could not get disk information"
    
    def get_system_summary(self):
        summary = self.system_monitor.get_system_summary()
        if 'error' not in summary:
            cpu = summary['cpu']['usage_percent']
            mem = summary['memory']['virtual']['percent']
            return True, f"System Status - CPU: {cpu:.1f}%, Memory: {mem:.1f}%"
        return False, summary['error']
    
    def get_processes(self):
        processes = self.system_monitor.get_process_list(5)
        if isinstance(processes, list):
            return True, f"Top 5 processes by CPU usage: {', '.join([p['name'] for p in processes[:5]])}"
        return False, "Could not get process list"
    
    def get_uptime(self):
        uptime = self.system_monitor.get_system_uptime()
        if 'error' not in uptime:
            return True, f"System uptime: {uptime['formatted']}"
        return False, uptime['error']
    
    def get_temperature(self):
        temp = self.system_monitor.get_temperature()
        if 'error' not in temp:
            if 'message' in temp:
                return True, temp['message']
            else:
                return True, "Temperature information available"
        return False, temp['error']
