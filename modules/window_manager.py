import subprocess
import json
import re
from typing import Dict, List, Any, Optional

class WindowManager:
    """
    Window management system for Hyprland/X11 environments
    """
    
    def __init__(self):
        self.wm_type = self._detect_window_manager()
        
    def _detect_window_manager(self) -> str:
        """Detect the current window manager"""
        try:
            # Check for Hyprland
            result = subprocess.run(['hyprctl', 'version'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return 'hyprland'
        except:
            pass
            
        try:
            # Check for X11
            result = subprocess.run(['xwininfo', '-root'], 
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                return 'x11'
        except:
            pass
            
        return 'unknown'
    
    def list_windows(self) -> Dict[str, Any]:
        """List all open windows"""
        if self.wm_type == 'hyprland':
            return self._hyprland_list_windows()
        elif self.wm_type == 'x11':
            return self._x11_list_windows()
        else:
            return {"success": False, "error": "Window manager not supported"}
    
    def focus_window(self, window_id: str) -> Dict[str, Any]:
        """Focus a specific window"""
        if self.wm_type == 'hyprland':
            return self._hyprland_focus_window(window_id)
        elif self.wm_type == 'x11':
            return self._x11_focus_window(window_id)
        else:
            return {"success": False, "error": "Window manager not supported"}
    
    def close_window(self, window_id: str) -> Dict[str, Any]:
        """Close a specific window"""
        if self.wm_type == 'hyprland':
            return self._hyprland_close_window(window_id)
        elif self.wm_type == 'x11':
            return self._x11_close_window(window_id)
        else:
            return {"success": False, "error": "Window manager not supported"}
    
    def move_window(self, window_id: str, x: int, y: int) -> Dict[str, Any]:
        """Move window to specific coordinates"""
        if self.wm_type == 'hyprland':
            return self._hyprland_move_window(window_id, x, y)
        elif self.wm_type == 'x11':
            return self._x11_move_window(window_id, x, y)
        else:
            return {"success": False, "error": "Window manager not supported"}
    
    def resize_window(self, window_id: str, width: int, height: int) -> Dict[str, Any]:
        """Resize window to specific dimensions"""
        if self.wm_type == 'hyprland':
            return self._hyprland_resize_window(window_id, width, height)
        elif self.wm_type == 'x11':
            return self._x11_resize_window(window_id, width, height)
        else:
            return {"success": False, "error": "Window manager not supported"}
    
    # Hyprland implementations
    def _hyprland_list_windows(self) -> Dict[str, Any]:
        """List windows in Hyprland"""
        try:
            result = subprocess.run(['hyprctl', 'clients', '-j'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                windows = json.loads(result.stdout)
                return {
                    "success": True,
                    "windows": [
                        {
                            "id": str(w.get("address", "")),
                            "title": w.get("title", ""),
                            "class": w.get("class", ""),
                            "workspace": w.get("workspace", {}).get("name", ""),
                            "position": [w.get("at", [0, 0])[0], w.get("at", [0, 0])[1]],
                            "size": [w.get("size", [0, 0])[0], w.get("size", [0, 0])[1]]
                        }
                        for w in windows
                    ]
                }
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _hyprland_focus_window(self, window_id: str) -> Dict[str, Any]:
        """Focus window in Hyprland"""
        try:
            result = subprocess.run(['hyprctl', 'dispatch', 'focuswindow', f'address:{window_id}'], 
                                  capture_output=True, text=True, timeout=5)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _hyprland_close_window(self, window_id: str) -> Dict[str, Any]:
        """Close window in Hyprland"""
        try:
            result = subprocess.run(['hyprctl', 'dispatch', 'closewindow', f'address:{window_id}'], 
                                  capture_output=True, text=True, timeout=5)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _hyprland_move_window(self, window_id: str, x: int, y: int) -> Dict[str, Any]:
        """Move window in Hyprland"""
        try:
            result = subprocess.run(['hyprctl', 'dispatch', 'movewindowpixel', f'{x} {y}', f'address:{window_id}'], 
                                  capture_output=True, text=True, timeout=5)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _hyprland_resize_window(self, window_id: str, width: int, height: int) -> Dict[str, Any]:
        """Resize window in Hyprland"""
        try:
            result = subprocess.run(['hyprctl', 'dispatch', 'resizewindowpixel', f'{width} {height}', f'address:{window_id}'], 
                                  capture_output=True, text=True, timeout=5)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # X11 implementations
    def _x11_list_windows(self) -> Dict[str, Any]:
        """List windows in X11"""
        try:
            result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                windows = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            windows.append({
                                "id": parts[0],
                                "workspace": parts[1],
                                "host": parts[2],
                                "title": parts[3]
                            })
                return {"success": True, "windows": windows}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _x11_focus_window(self, window_id: str) -> Dict[str, Any]:
        """Focus window in X11"""
        try:
            result = subprocess.run(['wmctrl', '-i', '-a', window_id], 
                                  capture_output=True, text=True, timeout=5)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _x11_close_window(self, window_id: str) -> Dict[str, Any]:
        """Close window in X11"""
        try:
            result = subprocess.run(['wmctrl', '-i', '-c', window_id], 
                                  capture_output=True, text=True, timeout=5)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _x11_move_window(self, window_id: str, x: int, y: int) -> Dict[str, Any]:
        """Move window in X11"""
        try:
            result = subprocess.run(['wmctrl', '-i', '-r', window_id, '-e', f'0,{x},{y},-1,-1'], 
                                  capture_output=True, text=True, timeout=5)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _x11_resize_window(self, window_id: str, width: int, height: int) -> Dict[str, Any]:
        """Resize window in X11"""
        try:
            result = subprocess.run(['wmctrl', '-i', '-r', window_id, '-e', f'0,-1,-1,{width},{height}'], 
                                  capture_output=True, text=True, timeout=5)
            return {"success": result.returncode == 0, "output": result.stdout}
        except Exception as e:
            return {"success": False, "error": str(e)}
