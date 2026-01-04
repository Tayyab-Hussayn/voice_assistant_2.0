import subprocess
import psutil
import signal
import os
from typing import Dict, List, Any, Optional

class ProcessManager:
    """
    Process management system for monitoring and controlling system processes
    """
    
    def __init__(self):
        pass
    
    def list_processes(self, filter_name: str = None) -> Dict[str, Any]:
        """List running processes, optionally filtered by name"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    if filter_name is None or filter_name.lower() in proc_info['name'].lower():
                        processes.append({
                            'pid': proc_info['pid'],
                            'name': proc_info['name'],
                            'cpu_percent': proc_info['cpu_percent'],
                            'memory_percent': proc_info['memory_percent'],
                            'status': proc_info['status']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return {
                "success": True,
                "processes": sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def kill_process(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """Kill a process by PID"""
        try:
            if not psutil.pid_exists(pid):
                return {"success": False, "error": f"Process {pid} does not exist"}
            
            proc = psutil.Process(pid)
            proc_name = proc.name()
            
            if force:
                proc.kill()  # SIGKILL
                action = "force killed"
            else:
                proc.terminate()  # SIGTERM
                action = "terminated"
            
            return {
                "success": True,
                "message": f"Process {proc_name} (PID: {pid}) {action}"
            }
        except psutil.NoSuchProcess:
            return {"success": False, "error": f"Process {pid} no longer exists"}
        except psutil.AccessDenied:
            return {"success": False, "error": f"Access denied to kill process {pid}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def kill_process_by_name(self, name: str, force: bool = False) -> Dict[str, Any]:
        """Kill all processes matching a name"""
        try:
            killed_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if name.lower() in proc.info['name'].lower():
                        result = self.kill_process(proc.info['pid'], force)
                        if result['success']:
                            killed_processes.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if killed_processes:
                action = "force killed" if force else "terminated"
                return {
                    "success": True,
                    "message": f"{action.title()} {len(killed_processes)} processes matching '{name}': {killed_processes}"
                }
            else:
                return {"success": False, "error": f"No processes found matching '{name}'"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def launch_application(self, app_name: str, args: List[str] = None) -> Dict[str, Any]:
        """Launch an application"""
        try:
            cmd = [app_name]
            if args:
                cmd.extend(args)
            
            # Launch process in background
            proc = subprocess.Popen(cmd, 
                                  stdout=subprocess.DEVNULL, 
                                  stderr=subprocess.DEVNULL,
                                  start_new_session=True)
            
            return {
                "success": True,
                "message": f"Launched {app_name} with PID {proc.pid}",
                "pid": proc.pid
            }
        except FileNotFoundError:
            return {"success": False, "error": f"Application '{app_name}' not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get overall system statistics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "success": True,
                "stats": {
                    "cpu_percent": cpu_percent,
                    "memory": {
                        "total": memory.total,
                        "available": memory.available,
                        "percent": memory.percent,
                        "used": memory.used
                    },
                    "disk": {
                        "total": disk.total,
                        "used": disk.used,
                        "free": disk.free,
                        "percent": (disk.used / disk.total) * 100
                    },
                    "process_count": len(psutil.pids())
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
