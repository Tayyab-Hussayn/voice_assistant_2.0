import os
import shutil
import subprocess
from pathlib import Path
import mimetypes
import glob
import re
import time
from typing import List, Dict, Any, Optional, Union
from modules.workspace_manager import WorkspaceManager

class EnhancedFileSystemManager:
    """
    Enhanced File System Manager with Kiro CLI capabilities
    Supports: create, str_replace, insert, append, batch operations, pattern matching
    """
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.workspace_manager = WorkspaceManager()
        self.operation_history = []
        
    def fs_write_create(self, path: str, file_text: str, summary: str = "") -> Dict[str, Any]:
        """Create a new file with content (Kiro CLI fs_write create)"""
        try:
            file_path = Path(path).expanduser().resolve()
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_text)
            
            result = {
                "success": True,
                "operation": "create",
                "path": str(file_path),
                "summary": summary or f"Created file {file_path.name}",
                "size": len(file_text),
                "timestamp": time.time()
            }
            
            self.operation_history.append(result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "operation": "create",
                "path": path,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def fs_write_str_replace(self, path: str, old_str: str, new_str: str, summary: str = "") -> Dict[str, Any]:
        """Replace string in file (Kiro CLI fs_write str_replace)"""
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return {
                    "success": False,
                    "operation": "str_replace",
                    "path": str(file_path),
                    "error": "File does not exist",
                    "timestamp": time.time()
                }
            
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if old_str exists
            if old_str not in content:
                return {
                    "success": False,
                    "operation": "str_replace", 
                    "path": str(file_path),
                    "error": f"String not found in file",
                    "timestamp": time.time()
                }
            
            # Count occurrences
            occurrences = content.count(old_str)
            if occurrences > 1:
                return {
                    "success": False,
                    "operation": "str_replace",
                    "path": str(file_path),
                    "error": f"String appears {occurrences} times. Must be unique for replacement.",
                    "timestamp": time.time()
                }
            
            # Perform replacement
            new_content = content.replace(old_str, new_str)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            result = {
                "success": True,
                "operation": "str_replace",
                "path": str(file_path),
                "summary": summary or f"Replaced text in {file_path.name}",
                "old_length": len(old_str),
                "new_length": len(new_str),
                "timestamp": time.time()
            }
            
            self.operation_history.append(result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "operation": "str_replace",
                "path": path,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def fs_write_insert(self, path: str, insert_line: int, new_str: str, summary: str = "") -> Dict[str, Any]:
        """Insert content after specified line number (Kiro CLI fs_write insert)"""
        try:
            file_path = Path(path).expanduser().resolve()
            
            if not file_path.exists():
                return {
                    "success": False,
                    "operation": "insert",
                    "path": str(file_path),
                    "error": "File does not exist",
                    "timestamp": time.time()
                }
            
            # Read current lines
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Validate line number
            if insert_line < 0 or insert_line > len(lines):
                return {
                    "success": False,
                    "operation": "insert",
                    "path": str(file_path),
                    "error": f"Invalid line number: {insert_line}. File has {len(lines)} lines.",
                    "timestamp": time.time()
                }
            
            # Insert content after the specified line
            if not new_str.endswith('\n'):
                new_str += '\n'
            lines.insert(insert_line, new_str)
            
            # Write back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            result = {
                "success": True,
                "operation": "insert",
                "path": str(file_path),
                "summary": summary or f"Inserted content after line {insert_line} in {file_path.name}",
                "line_number": insert_line,
                "content_length": len(new_str),
                "timestamp": time.time()
            }
            
            self.operation_history.append(result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "operation": "insert",
                "path": path,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def fs_write_append(self, path: str, new_str: str, summary: str = "") -> Dict[str, Any]:
        """Append content to end of file (Kiro CLI fs_write append)"""
        try:
            file_path = Path(path).expanduser().resolve()
            
            # Create file if it doesn't exist
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("")
            
            # Check if file ends with newline
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # Add newline if file doesn't end with one and has content
            if existing_content and not existing_content.endswith('\n'):
                new_str = '\n' + new_str
            
            # Append content
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(new_str)
            
            result = {
                "success": True,
                "operation": "append",
                "path": str(file_path),
                "summary": summary or f"Appended content to {file_path.name}",
                "content_length": len(new_str),
                "timestamp": time.time()
            }
            
            self.operation_history.append(result)
            return result
            
        except Exception as e:
            return {
                "success": False,
                "operation": "append",
                "path": path,
                "error": str(e),
                "timestamp": time.time()
            }
    
    def batch_file_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute multiple file operations in batch"""
        results = []
        successful_ops = 0
        failed_ops = 0
        
        for i, op in enumerate(operations):
            try:
                command = op.get("command")
                
                if command == "create":
                    result = self.fs_write_create(op["path"], op["file_text"], op.get("summary", ""))
                elif command == "str_replace":
                    result = self.fs_write_str_replace(op["path"], op["old_str"], op["new_str"], op.get("summary", ""))
                elif command == "insert":
                    result = self.fs_write_insert(op["path"], op["insert_line"], op["new_str"], op.get("summary", ""))
                elif command == "append":
                    result = self.fs_write_append(op["path"], op["new_str"], op.get("summary", ""))
                else:
                    result = {
                        "success": False,
                        "operation": "batch",
                        "index": i,
                        "error": f"Unknown command: {command}",
                        "timestamp": time.time()
                    }
                
                results.append(result)
                
                if result["success"]:
                    successful_ops += 1
                else:
                    failed_ops += 1
                    
            except Exception as e:
                result = {
                    "success": False,
                    "operation": "batch",
                    "index": i,
                    "error": str(e),
                    "timestamp": time.time()
                }
                results.append(result)
                failed_ops += 1
        
        batch_result = {
            "success": failed_ops == 0,
            "operation": "batch",
            "total_operations": len(operations),
            "successful": successful_ops,
            "failed": failed_ops,
            "results": results,
            "timestamp": time.time()
        }
        
        self.operation_history.append(batch_result)
        return batch_result
    
    def find_files_by_pattern(self, pattern: str, base_path: str = ".", max_files: int = 1000) -> List[str]:
        """Find files matching glob pattern (Kiro CLI glob functionality)"""
        try:
            base_path = Path(base_path).expanduser().resolve()
            
            # Use glob to find matching files
            if pattern.startswith("/"):
                # Absolute pattern
                matches = glob.glob(pattern, recursive=True)
            else:
                # Relative pattern
                matches = glob.glob(str(base_path / pattern), recursive=True)
            
            # Convert to Path objects and filter files only
            file_paths = []
            for match in matches:
                path = Path(match)
                if path.is_file():
                    file_paths.append(str(path))
                    if len(file_paths) >= max_files:
                        break
            
            return sorted(file_paths)
            
        except Exception as e:
            print(f"Error finding files: {e}")
            return []
    
    def get_operation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent operation history"""
        return self.operation_history[-limit:] if limit > 0 else self.operation_history
    
    def clear_history(self):
        """Clear operation history"""
        self.operation_history.clear()

class FileSystemManager:
    """Enhanced File System Manager with both legacy and new capabilities"""
    
    def __init__(self):
        self.current_dir = Path.cwd()
        self.workspace_manager = WorkspaceManager()
        self.enhanced_fs = EnhancedFileSystemManager()
        
    # Kiro CLI fs_write operations
    def fs_write(self, command: str, path: str, **kwargs) -> Dict[str, Any]:
        """Main fs_write interface matching Kiro CLI"""
        if command == "create":
            return self.enhanced_fs.fs_write_create(path, kwargs.get("file_text", ""), kwargs.get("summary", ""))
        elif command == "str_replace":
            return self.enhanced_fs.fs_write_str_replace(path, kwargs.get("old_str", ""), kwargs.get("new_str", ""), kwargs.get("summary", ""))
        elif command == "insert":
            return self.enhanced_fs.fs_write_insert(path, kwargs.get("insert_line", 0), kwargs.get("new_str", ""), kwargs.get("summary", ""))
        elif command == "append":
            return self.enhanced_fs.fs_write_append(path, kwargs.get("new_str", ""), kwargs.get("summary", ""))
        else:
            return {
                "success": False,
                "error": f"Unknown fs_write command: {command}",
                "timestamp": time.time()
            }
    
    # Kiro CLI glob operations
    def glob_files(self, pattern: str, path: str = ".", limit: int = 1000) -> Dict[str, Any]:
        """Find files matching glob pattern"""
        try:
            files = self.enhanced_fs.find_files_by_pattern(pattern, path, limit)
            return {
                "success": True,
                "totalFiles": len(files),
                "truncated": len(files) >= limit,
                "filePaths": files
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # Legacy methods (maintained for compatibility)
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
        """Create a file with optional content (legacy)"""
        try:
            if path:
                full_path = Path(path) / file_name
            else:
                full_path = self.current_dir / file_name
                
            result = self.enhanced_fs.fs_write_create(str(full_path), content)
            return result["success"], result.get("summary", result.get("error", ""))
        except Exception as e:
            return False, f"Failed to create file: {e}"
        
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
