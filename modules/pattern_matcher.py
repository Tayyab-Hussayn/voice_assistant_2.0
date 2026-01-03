import os
import glob
import fnmatch
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import time
import re

class PatternMatchingSystem:
    """
    Advanced Pattern Matching System with Kiro CLI glob capabilities
    Find files and directories whose paths match glob patterns with .gitignore respect
    """
    
    def __init__(self):
        self.default_exclude_patterns = [
            "node_modules", ".git", "dist", "build", "out", ".cache", "target",
            "__pycache__", ".pytest_cache", ".mypy_cache", "venv", ".venv",
            "*.pyc", "*.pyo", "*.pyd", ".DS_Store", "Thumbs.db"
        ]
        self.match_history = []
    
    def load_gitignore_patterns(self, path: str) -> List[str]:
        """Load patterns from .gitignore file"""
        gitignore_path = Path(path) / ".gitignore"
        patterns = []
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception:
                pass
        
        return patterns
    
    def should_exclude_path(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if path should be excluded based on patterns"""
        path_str = str(file_path)
        relative_path = file_path.name
        
        for pattern in exclude_patterns:
            # Handle different pattern types
            if pattern.startswith('/'):
                # Absolute pattern from root
                pattern = pattern[1:]
                if fnmatch.fnmatch(path_str, f"*/{pattern}") or fnmatch.fnmatch(path_str, f"*/{pattern}/*"):
                    return True
            elif pattern.endswith('/'):
                # Directory pattern
                pattern = pattern[:-1]
                if pattern in file_path.parts:
                    return True
            elif '/' in pattern:
                # Path pattern
                if fnmatch.fnmatch(path_str, f"*/{pattern}") or fnmatch.fnmatch(path_str, f"*/{pattern}/*"):
                    return True
            else:
                # Simple pattern - check filename and path parts
                if fnmatch.fnmatch(relative_path, pattern):
                    return True
                if pattern in file_path.parts:
                    return True
                if fnmatch.fnmatch(path_str, f"*/{pattern}/*"):
                    return True
        
        return False
    
    def glob_find(self, pattern: str, path: str = ".", limit: int = 1000, 
                  max_depth: int = None) -> Dict[str, Any]:
        """
        Find files and directories matching glob pattern (Kiro CLI glob functionality)
        
        Args:
            pattern: Glob pattern to match
            path: Root directory to search from
            limit: Maximum files to return
            max_depth: Maximum directory depth to traverse
        """
        start_time = time.time()
        base_path = Path(path).expanduser().resolve()
        
        if not base_path.exists():
            return {
                "success": False,
                "error": f"Path does not exist: {path}",
                "totalFiles": 0,
                "truncated": False,
                "filePaths": []
            }
        
        # Load .gitignore patterns
        gitignore_patterns = self.load_gitignore_patterns(base_path)
        all_exclude_patterns = self.default_exclude_patterns + gitignore_patterns
        
        matched_paths = []
        
        try:
            if pattern.startswith('/'):
                # Absolute pattern
                search_pattern = str(base_path) + pattern
            else:
                # Relative pattern
                search_pattern = str(base_path / pattern)
            
            # Use glob with recursive support
            if '**' in pattern:
                matches = glob.glob(search_pattern, recursive=True)
            else:
                matches = glob.glob(search_pattern)
            
            # Process matches
            for match in matches:
                match_path = Path(match)
                
                # Check depth limit
                if max_depth is not None:
                    try:
                        relative_to_base = match_path.relative_to(base_path)
                        if len(relative_to_base.parts) > max_depth:
                            continue
                    except ValueError:
                        continue
                
                # Check exclusion patterns
                if not self.should_exclude_path(match_path, all_exclude_patterns):
                    matched_paths.append(str(match_path))
                    
                    if len(matched_paths) >= limit:
                        break
            
            # Sort results
            matched_paths.sort()
            
            result = {
                "success": True,
                "totalFiles": len(matched_paths),
                "truncated": len(matched_paths) >= limit,
                "filePaths": matched_paths,
                "pattern": pattern,
                "search_path": str(base_path),
                "search_time": time.time() - start_time
            }
            
            # Add to history
            self.match_history.append({
                "pattern": pattern,
                "path": path,
                "matches": len(matched_paths),
                "timestamp": time.time()
            })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "totalFiles": 0,
                "truncated": False,
                "filePaths": [],
                "pattern": pattern,
                "search_path": str(base_path)
            }
    
    def find_by_name(self, name: str, path: str = ".", case_sensitive: bool = False,
                     limit: int = 1000) -> Dict[str, Any]:
        """Find files/directories by exact name"""
        if case_sensitive:
            pattern = name
        else:
            # Create case-insensitive pattern
            pattern = ''.join(f'[{c.upper()}{c.lower()}]' if c.isalpha() else c for c in name)
        
        return self.glob_find(f"**/{pattern}", path, limit)
    
    def find_by_extension(self, extension: str, path: str = ".", limit: int = 1000) -> Dict[str, Any]:
        """Find files by extension"""
        if not extension.startswith('.'):
            extension = '.' + extension
        
        pattern = f"**/*{extension}"
        return self.glob_find(pattern, path, limit)
    
    def find_directories(self, pattern: str = "*", path: str = ".", limit: int = 1000) -> Dict[str, Any]:
        """Find directories matching pattern"""
        result = self.glob_find(pattern, path, limit * 2)  # Get more to filter
        
        if result["success"]:
            # Filter to directories only
            directories = []
            for file_path in result["filePaths"]:
                if Path(file_path).is_dir():
                    directories.append(file_path)
                    if len(directories) >= limit:
                        break
            
            result["filePaths"] = directories
            result["totalFiles"] = len(directories)
            result["truncated"] = len(directories) >= limit
        
        return result
    
    def find_files_only(self, pattern: str = "*", path: str = ".", limit: int = 1000) -> Dict[str, Any]:
        """Find files only (no directories) matching pattern"""
        result = self.glob_find(pattern, path, limit * 2)  # Get more to filter
        
        if result["success"]:
            # Filter to files only
            files = []
            for file_path in result["filePaths"]:
                if Path(file_path).is_file():
                    files.append(file_path)
                    if len(files) >= limit:
                        break
            
            result["filePaths"] = files
            result["totalFiles"] = len(files)
            result["truncated"] = len(files) >= limit
        
        return result
    
    def validate_pattern(self, pattern: str) -> Dict[str, Any]:
        """Validate glob pattern syntax"""
        try:
            # Test the pattern with glob
            test_path = Path.cwd()
            glob.glob(str(test_path / pattern))
            
            return {
                "valid": True,
                "pattern": pattern,
                "message": "Pattern is valid"
            }
        except Exception as e:
            return {
                "valid": False,
                "pattern": pattern,
                "error": str(e),
                "message": f"Invalid pattern: {e}"
            }
    
    def get_pattern_info(self, pattern: str) -> Dict[str, Any]:
        """Get information about a glob pattern"""
        info = {
            "pattern": pattern,
            "is_recursive": "**" in pattern,
            "has_wildcards": "*" in pattern or "?" in pattern,
            "is_absolute": pattern.startswith("/"),
            "targets_directories": pattern.endswith("/"),
            "estimated_complexity": "low"
        }
        
        # Estimate complexity
        if info["is_recursive"] and info["has_wildcards"]:
            info["estimated_complexity"] = "high"
        elif info["is_recursive"] or info["has_wildcards"]:
            info["estimated_complexity"] = "medium"
        
        return info
    
    def get_match_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent pattern matching history"""
        return self.match_history[-limit:] if limit > 0 else self.match_history
    
    def clear_match_history(self):
        """Clear pattern matching history"""
        self.match_history.clear()

# Integration class for JARVIS
class PatternMatcher:
    """Pattern matching integration for JARVIS"""
    
    def __init__(self):
        self.pattern_system = PatternMatchingSystem()
    
    def glob(self, pattern: str, path: str = ".", **kwargs) -> Dict[str, Any]:
        """Main glob interface for JARVIS"""
        return self.pattern_system.glob_find(pattern, path, **kwargs)
    
    def find_files(self, pattern: str, path: str = ".", limit: int = 1000) -> Dict[str, Any]:
        """Find files matching pattern"""
        return self.pattern_system.find_files_only(pattern, path, limit)
    
    def find_directories(self, pattern: str = "*", path: str = ".", limit: int = 1000) -> Dict[str, Any]:
        """Find directories matching pattern"""
        return self.pattern_system.find_directories(pattern, path, limit)
    
    def validate_pattern(self, pattern: str) -> Dict[str, Any]:
        """Validate glob pattern"""
        return self.pattern_system.validate_pattern(pattern)
