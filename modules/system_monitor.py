import psutil
import subprocess
import time
from datetime import datetime

class SystemMonitor:
    def __init__(self):
        self.boot_time = psutil.boot_time()
        
    def get_cpu_info(self):
        """Get CPU information and usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            return {
                'usage_percent': cpu_percent,
                'core_count': cpu_count,
                'frequency': {
                    'current': cpu_freq.current if cpu_freq else 0,
                    'min': cpu_freq.min if cpu_freq else 0,
                    'max': cpu_freq.max if cpu_freq else 0
                },
                'per_cpu': psutil.cpu_percent(percpu=True)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_memory_info(self):
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            return {
                'virtual': {
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used,
                    'percent': memory.percent
                },
                'swap': {
                    'total': swap.total,
                    'used': swap.used,
                    'free': swap.free,
                    'percent': swap.percent
                }
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_disk_info(self):
        """Get disk usage information"""
        try:
            disks = []
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'total': usage.total,
                        'used': usage.used,
                        'free': usage.free,
                        'percent': (usage.used / usage.total) * 100
                    })
                except PermissionError:
                    continue
            return disks
        except Exception as e:
            return {'error': str(e)}
    
    def get_network_info(self):
        """Get network information"""
        try:
            net_io = psutil.net_io_counters()
            interfaces = psutil.net_if_addrs()
            
            return {
                'io_counters': {
                    'bytes_sent': net_io.bytes_sent,
                    'bytes_recv': net_io.bytes_recv,
                    'packets_sent': net_io.packets_sent,
                    'packets_recv': net_io.packets_recv
                },
                'interfaces': {name: [addr.address for addr in addrs] 
                             for name, addrs in interfaces.items()}
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_process_list(self, limit=10, sort_by='cpu'):
        """Get list of running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort by specified criteria
            if sort_by == 'cpu':
                processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            elif sort_by == 'memory':
                processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
            
            return processes[:limit]
        except Exception as e:
            return {'error': str(e)}
    
    def get_system_uptime(self):
        """Get system uptime"""
        try:
            uptime_seconds = time.time() - self.boot_time
            uptime_string = str(datetime.fromtimestamp(uptime_seconds) - datetime.fromtimestamp(0))
            
            return {
                'seconds': uptime_seconds,
                'formatted': uptime_string,
                'boot_time': datetime.fromtimestamp(self.boot_time).strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            return {'error': str(e)}
    
    def get_temperature(self):
        """Get system temperature (if available)"""
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                return temps
            else:
                # Try alternative method for some systems
                try:
                    result = subprocess.run(['sensors'], capture_output=True, text=True)
                    if result.returncode == 0:
                        return {'sensors_output': result.stdout}
                except:
                    pass
                return {'message': 'Temperature sensors not available'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_battery_info(self):
        """Get battery information (for laptops)"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    'percent': battery.percent,
                    'power_plugged': battery.power_plugged,
                    'time_left': battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None
                }
            else:
                return {'message': 'No battery detected'}
        except Exception as e:
            return {'error': str(e)}
    
    def kill_process(self, pid):
        """Kill a process by PID"""
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            return True, f"Process {pid} terminated"
        except psutil.NoSuchProcess:
            return False, f"Process {pid} not found"
        except psutil.AccessDenied:
            return False, f"Access denied to kill process {pid}"
        except Exception as e:
            return False, f"Failed to kill process: {e}"
    
    def get_system_summary(self):
        """Get a comprehensive system summary"""
        try:
            return {
                'cpu': self.get_cpu_info(),
                'memory': self.get_memory_info(),
                'disk': self.get_disk_info(),
                'network': self.get_network_info(),
                'uptime': self.get_system_uptime(),
                'top_processes': self.get_process_list(5),
                'temperature': self.get_temperature(),
                'battery': self.get_battery_info()
            }
        except Exception as e:
            return {'error': str(e)}
