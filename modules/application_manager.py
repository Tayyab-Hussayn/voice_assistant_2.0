import subprocess
import psutil
import os
import time

class ApplicationManager:
    def __init__(self):
        self.app_database = {
            # Browsers
            'chrome': ['google-chrome', 'chromium', 'google-chrome-stable'],
            'firefox': ['firefox'],
            'brave': ['brave', 'brave-browser'],
            
            # Development
            'vscode': ['code', 'code-oss'],
            'vim': ['vim', 'nvim'],
            'emacs': ['emacs'],
            'sublime': ['subl', 'sublime_text'],
            
            # Terminals
            'terminal': ['alacritty', 'kitty', 'gnome-terminal', 'konsole', 'xterm'],
            'alacritty': ['alacritty'],
            'kitty': ['kitty'],
            
            # File managers
            'files': ['nautilus', 'dolphin', 'thunar', 'pcmanfm'],
            'ranger': ['ranger'],
            
            # Media
            'vlc': ['vlc'],
            'mpv': ['mpv'],
            'spotify': ['spotify'],
            
            # Communication
            'discord': ['discord'],
            'telegram': ['telegram-desktop'],
            'slack': ['slack'],
            
            # System
            'calculator': ['gnome-calculator', 'kcalc', 'qalculate-gtk'],
            'settings': ['gnome-control-center', 'systemsettings5'],
            'task manager': ['gnome-system-monitor', 'htop', 'btop']
        }
    
    def find_executable(self, app_name):
        """Find the best executable for an app"""
        app_name = app_name.lower()
        
        if app_name in self.app_database:
            for executable in self.app_database[app_name]:
                if self.is_installed(executable):
                    return executable
        
        # Try direct name if not in database
        if self.is_installed(app_name):
            return app_name
            
        return None
    
    def is_installed(self, executable):
        """Check if an executable is installed"""
        try:
            subprocess.run(['which', executable], 
                         capture_output=True, 
                         check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def launch_app(self, app_name, args=None):
        """Launch an application"""
        executable = self.find_executable(app_name)
        if not executable:
            return False, f"Application '{app_name}' not found"
        
        try:
            cmd = [executable]
            if args:
                cmd.extend(args)
                
            subprocess.Popen(cmd, 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
            return True, f"Launched {app_name}"
        except Exception as e:
            return False, f"Failed to launch {app_name}: {e}"
    
    def kill_app(self, app_name):
        """Kill an application by name"""
        executable = self.find_executable(app_name)
        if not executable:
            return False, f"Application '{app_name}' not found"
        
        try:
            subprocess.run(['pkill', '-f', executable], check=True)
            return True, f"Killed {app_name}"
        except subprocess.CalledProcessError:
            return False, f"Failed to kill {app_name} or not running"
    
    def get_running_apps(self):
        """Get list of running applications"""
        apps = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                apps.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return apps
    
    def is_app_running(self, app_name):
        """Check if an application is running"""
        executable = self.find_executable(app_name)
        if not executable:
            return False
            
        for proc in psutil.process_iter(['name']):
            try:
                if executable in proc.info['name']:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return False
    
    def restart_app(self, app_name):
        """Restart an application"""
        if self.is_app_running(app_name):
            success, msg = self.kill_app(app_name)
            if not success:
                return False, msg
            time.sleep(1)  # Wait for app to close
        
        return self.launch_app(app_name)
    
    def open_file_with_app(self, file_path, app_name=None):
        """Open a file with specific application or default"""
        if not os.path.exists(file_path):
            return False, f"File not found: {file_path}"
        
        try:
            if app_name:
                executable = self.find_executable(app_name)
                if executable:
                    subprocess.Popen([executable, file_path],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
                    return True, f"Opened {file_path} with {app_name}"
                else:
                    return False, f"Application {app_name} not found"
            else:
                # Use default application
                subprocess.Popen(['xdg-open', file_path],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)
                return True, f"Opened {file_path} with default application"
        except Exception as e:
            return False, f"Failed to open file: {e}"
