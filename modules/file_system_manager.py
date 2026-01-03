import os
import shutil
import subprocess
from pathlib import Path
import mimetypes
from modules.workspace_manager import WorkspaceManager

class FileSystemManager:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.workspace_manager = WorkspaceManager()
        
    def create_directory(self, dir_name, path=None):
        """Create a directory"""
        try:
            if path:
                full_path = Path(path) / dir_name
            else:
                full_path = self.current_dir / dir_name
                
            full_path.mkdir(parents=True, exist_ok=True)
            return True, f"Created directory: {full_path}"
        except Exception as e:
            return False, f"Failed to create directory: {e}"
    
    def create_file(self, file_name, content="", path=None):
        """Create a file with optional content"""
        try:
            if path:
                full_path = Path(path) / file_name
            else:
                full_path = self.current_dir / file_name
                
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
            return True, f"Created file: {full_path}"
        except Exception as e:
            return False, f"Failed to create file: {e}"
    
    def copy_file(self, source, destination):
        """Copy a file or directory"""
        try:
            source_path = Path(source)
            dest_path = Path(destination)
            
            if source_path.is_file():
                shutil.copy2(source_path, dest_path)
            elif source_path.is_dir():
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
            else:
                return False, f"Source not found: {source}"
                
            return True, f"Copied {source} to {destination}"
        except Exception as e:
            return False, f"Failed to copy: {e}"
    
    def move_file(self, source, destination):
        """Move/rename a file or directory"""
        try:
            shutil.move(source, destination)
            return True, f"Moved {source} to {destination}"
        except Exception as e:
            return False, f"Failed to move: {e}"
    
    def delete_file(self, file_path, force=False):
        """Delete a file or directory"""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False, f"Path not found: {file_path}"
            
            if path.is_file():
                path.unlink()
                return True, f"Deleted file: {file_path}"
            elif path.is_dir():
                if force:
                    shutil.rmtree(path)
                    return True, f"Deleted directory: {file_path}"
                else:
                    path.rmdir()  # Only works if empty
                    return True, f"Deleted empty directory: {file_path}"
        except Exception as e:
            return False, f"Failed to delete: {e}"
    
    def find_files(self, pattern, search_path=None, max_results=50):
        """Find files matching a pattern"""
        try:
            if search_path:
                base_path = Path(search_path)
            else:
                base_path = self.current_dir
                
            results = []
            for file_path in base_path.rglob(pattern):
                results.append(str(file_path))
                if len(results) >= max_results:
                    break
                    
            return True, results
        except Exception as e:
            return False, f"Search failed: {e}"
    
    def get_file_info(self, file_path):
        """Get detailed file information"""
        try:
            path = Path(file_path)
            if not path.exists():
                return False, f"File not found: {file_path}"
            
            stat = path.stat()
            info = {
                'name': path.name,
                'path': str(path.absolute()),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'permissions': oct(stat.st_mode)[-3:],
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'mime_type': mimetypes.guess_type(str(path))[0] if path.is_file() else None
            }
            return True, info
        except Exception as e:
            return False, f"Failed to get file info: {e}"
    
    def list_directory(self, dir_path=None, show_hidden=False):
        """List directory contents"""
        try:
            if dir_path:
                path = Path(dir_path)
            else:
                path = self.current_dir
                
            if not path.is_dir():
                return False, f"Not a directory: {path}"
            
            items = []
            for item in path.iterdir():
                if not show_hidden and item.name.startswith('.'):
                    continue
                    
                stat = item.stat()
                items.append({
                    'name': item.name,
                    'type': 'dir' if item.is_dir() else 'file',
                    'size': stat.st_size if item.is_file() else 0,
                    'permissions': oct(stat.st_mode)[-3:]
                })
            
            return True, sorted(items, key=lambda x: (x['type'], x['name']))
        except Exception as e:
            return False, f"Failed to list directory: {e}"
    
    def change_directory(self, dir_path):
        """Change current directory"""
        try:
            new_path = Path(dir_path).resolve()
            if not new_path.is_dir():
                return False, f"Not a directory: {dir_path}"
                
            os.chdir(new_path)
            self.current_dir = new_path
            return True, f"Changed to: {new_path}"
        except Exception as e:
            return False, f"Failed to change directory: {e}"
    
    def get_disk_usage(self, path=None):
        """Get disk usage information"""
        try:
            if path:
                check_path = Path(path)
            else:
                check_path = self.current_dir
                
            usage = shutil.disk_usage(check_path)
            return True, {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'path': str(check_path)
            }
        except Exception as e:
            return False, f"Failed to get disk usage: {e}"
    
    def search_in_files(self, pattern, file_pattern="*", search_path=None):
        """Search for text pattern in files"""
        try:
            if search_path:
                base_path = Path(search_path)
            else:
                base_path = self.current_dir
            
            results = []
            for file_path in base_path.rglob(file_pattern):
                if file_path.is_file():
                    try:
                        content = file_path.read_text(encoding='utf-8', errors='ignore')
                        lines = content.split('\n')
                        for i, line in enumerate(lines, 1):
                            if pattern.lower() in line.lower():
                                results.append({
                                    'file': str(file_path),
                                    'line': i,
                                    'content': line.strip()
                                })
                    except:
                        continue  # Skip binary files or permission errors
                        
            return True, results[:100]  # Limit results
        except Exception as e:
            return False, f"Search failed: {e}"
