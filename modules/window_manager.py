import subprocess
import json
import re

class WindowManager:
    def __init__(self):
        self.wm_type = self.detect_window_manager()
        
    def detect_window_manager(self):
        """Detect the current window manager"""
        try:
            # Check for Hyprland
            result = subprocess.run(['pgrep', 'Hyprland'], capture_output=True)
            if result.returncode == 0:
                return 'hyprland'
            
            # Check for other WMs
            wms = ['i3', 'sway', 'bspwm', 'dwm', 'awesome']
            for wm in wms:
                result = subprocess.run(['pgrep', wm], capture_output=True)
                if result.returncode == 0:
                    return wm
                    
            return 'unknown'
        except:
            return 'unknown'
    
    def hyprctl_command(self, cmd):
        """Execute hyprctl command"""
        try:
            result = subprocess.run(['hyprctl', cmd], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except:
            return None
    
    def get_active_window(self):
        """Get information about the active window"""
        if self.wm_type == 'hyprland':
            output = self.hyprctl_command('activewindow')
            if output:
                return self.parse_hyprland_window(output)
        return None
    
    def get_all_windows(self):
        """Get list of all windows"""
        if self.wm_type == 'hyprland':
            output = self.hyprctl_command('clients -j')
            if output:
                try:
                    return json.loads(output)
                except:
                    return []
        return []
    
    def focus_window(self, window_class):
        """Focus a window by class name"""
        if self.wm_type == 'hyprland':
            cmd = f'dispatch focuswindow class:{window_class}'
            return self.hyprctl_command(cmd) is not None
        return False
    
    def close_window(self):
        """Close the active window"""
        if self.wm_type == 'hyprland':
            return self.hyprctl_command('dispatch killactive') is not None
        return False
    
    def move_window(self, direction):
        """Move window in direction (left, right, up, down)"""
        if self.wm_type == 'hyprland':
            cmd = f'dispatch movewindow {direction}'
            return self.hyprctl_command(cmd) is not None
        return False
    
    def resize_window(self, direction, amount=50):
        """Resize window"""
        if self.wm_type == 'hyprland':
            cmd = f'dispatch resizeactive {direction} {amount}'
            return self.hyprctl_command(cmd) is not None
        return False
    
    def toggle_fullscreen(self):
        """Toggle fullscreen for active window"""
        if self.wm_type == 'hyprland':
            return self.hyprctl_command('dispatch fullscreen') is not None
        return False
    
    def switch_workspace(self, workspace):
        """Switch to workspace"""
        if self.wm_type == 'hyprland':
            cmd = f'dispatch workspace {workspace}'
            return self.hyprctl_command(cmd) is not None
        return False
    
    def move_to_workspace(self, workspace):
        """Move active window to workspace"""
        if self.wm_type == 'hyprland':
            cmd = f'dispatch movetoworkspace {workspace}'
            return self.hyprctl_command(cmd) is not None
        return False
    
    def parse_hyprland_window(self, output):
        """Parse hyprland window info"""
        info = {}
        for line in output.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        return info
    
    def get_workspaces(self):
        """Get list of workspaces"""
        if self.wm_type == 'hyprland':
            output = self.hyprctl_command('workspaces -j')
            if output:
                try:
                    return json.loads(output)
                except:
                    return []
        return []
