import os
import re
import glob
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import time

class AdvancedSearchSystem:
    """
    Advanced Search System with Kiro CLI grep capabilities
    Fast text pattern search in files using regex with .gitignore respect
    """
    
    def __init__(self):
        self.default_exclude_patterns = [
            "node_modules", ".git", "dist", "build", "out", ".cache", "target",
            "__pycache__", ".pytest_cache", ".mypy_cache", "venv", ".venv"
        ]
        self.search_history = []
    
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
        path_parts = file_path.parts
        
        for pattern in exclude_patterns:
            # Direct match
            if pattern in path_parts:
                return True
            
            # Glob pattern match
            if '*' in pattern:
                if file_path.match(pattern):
                    return True
            
            # Path contains pattern
            if pattern in path_str:
                return True
        
        return False
    
    def find_files_to_search(self, path: str, include: Optional[str] = None, 
                           exclude_patterns: Optional[List[str]] = None,
                           max_files: int = 1000) -> List[Path]:
        """Find files to search based on include/exclude patterns"""
        base_path = Path(path).expanduser().resolve()
        
        if not base_path.exists():
            return []
        
        # Load .gitignore patterns
        gitignore_patterns = self.load_gitignore_patterns(base_path)
        
        # Combine exclude patterns
        all_exclude_patterns = self.default_exclude_patterns.copy()
        if exclude_patterns:
            all_exclude_patterns.extend(exclude_patterns)
        all_exclude_patterns.extend(gitignore_patterns)
        
        files_to_search = []
        
        if base_path.is_file():
            if not self.should_exclude_path(base_path, all_exclude_patterns):
                files_to_search.append(base_path)
        else:
            # Search directory
            if include:
                # Use glob pattern
                for file_path in base_path.rglob(include):
                    if file_path.is_file() and not self.should_exclude_path(file_path, all_exclude_patterns):
                        files_to_search.append(file_path)
                        if len(files_to_search) >= max_files:
                            break
            else:
                # Search all text files
                for file_path in base_path.rglob("*"):
                    if file_path.is_file() and not self.should_exclude_path(file_path, all_exclude_patterns):
                        # Check if it's likely a text file
                        if self.is_text_file(file_path):
                            files_to_search.append(file_path)
                            if len(files_to_search) >= max_files:
                                break
        
        return files_to_search
    
    def is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file"""
        # Common text file extensions
        text_extensions = {
            '.txt', '.md', '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.htm', 
            '.css', '.scss', '.sass', '.less', '.json', '.xml', '.yaml', '.yml',
            '.toml', '.ini', '.cfg', '.conf', '.log', '.sql', '.sh', '.bash',
            '.zsh', '.fish', '.ps1', '.bat', '.cmd', '.c', '.cpp', '.h', '.hpp',
            '.java', '.kt', '.swift', '.go', '.rs', '.php', '.rb', '.pl', '.r',
            '.scala', '.clj', '.hs', '.elm', '.dart', '.lua', '.vim', '.tex',
            '.rst', '.org', '.adoc', '.csv', '.tsv'
        }
        
        # Check extension
        if file_path.suffix.lower() in text_extensions:
            return True
        
        # Check files without extension (like Dockerfile, Makefile)
        if not file_path.suffix:
            name_lower = file_path.name.lower()
            if any(keyword in name_lower for keyword in ['readme', 'license', 'changelog', 'dockerfile', 'makefile']):
                return True
        
        # Try to read first few bytes to check if it's text
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(1024)
                if b'\x00' in chunk:  # Binary file likely contains null bytes
                    return False
                # Try to decode as UTF-8
                chunk.decode('utf-8')
                return True
        except:
            return False
    
    def search_in_file(self, file_path: Path, pattern: str, case_sensitive: bool = False,
                      context_lines: int = 2, max_matches_per_file: int = 50) -> List[Dict[str, Any]]:
        """Search for pattern in a single file"""
        matches = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            # Compile regex pattern
            flags = 0 if case_sensitive else re.IGNORECASE
            try:
                regex = re.compile(pattern, flags)
            except re.error as e:
                return [{"error": f"Invalid regex pattern: {e}"}]
            
            # Search through lines
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    # Get context lines
                    start_line = max(0, line_num - 1 - context_lines)
                    end_line = min(len(lines), line_num + context_lines)
                    
                    context = []
                    for i in range(start_line, end_line):
                        prefix = ">" if i == line_num - 1 else " "
                        context.append(f"{prefix} {i+1:4d}: {lines[i].rstrip()}")
                    
                    matches.append({
                        "file": str(file_path),
                        "line": line_num,
                        "content": line.rstrip(),
                        "context": context
                    })
                    
                    if len(matches) >= max_matches_per_file:
                        break
        
        except Exception as e:
            return [{"error": f"Error reading {file_path}: {e}"}]
        
        return matches
    
    def grep_search(self, pattern: str, path: str = ".", case_sensitive: bool = False,
                   include: Optional[str] = None, exclude_patterns: Optional[List[str]] = None,
                   context_lines: int = 2, max_files: int = 1000, 
                   max_matches_per_file: int = 50, max_total_lines: int = 1000,
                   output_mode: str = "content") -> Dict[str, Any]:
        """
        Main grep search function matching Kiro CLI grep tool
        
        Args:
            pattern: Regex pattern to search for
            path: Directory to search from
            case_sensitive: Case-sensitive search
            include: File filter glob (e.g., "*.py")
            exclude_patterns: Additional exclude patterns
            context_lines: Number of context lines around matches
            max_files: Max number of files to search
            max_matches_per_file: Max matches per file
            max_total_lines: Max total matched lines
            output_mode: "content", "files_with_matches", or "count"
        """
        start_time = time.time()
        
        # Find files to search
        files_to_search = self.find_files_to_search(
            path, include, exclude_patterns, max_files
        )
        
        if not files_to_search:
            return {
                "success": True,
                "numFiles": 0,
                "numMatches": 0,
                "results": [],
                "truncated": False,
                "search_time": time.time() - start_time
            }
        
        all_matches = []
        files_with_matches = []
        file_match_counts = {}
        total_matches = 0
        
        for file_path in files_to_search:
            file_matches = self.search_in_file(
                file_path, pattern, case_sensitive, context_lines, max_matches_per_file
            )
            
            # Filter out error entries
            valid_matches = [m for m in file_matches if "error" not in m]
            
            if valid_matches:
                files_with_matches.append(str(file_path))
                file_match_counts[str(file_path)] = len(valid_matches)
                all_matches.extend(valid_matches)
                total_matches += len(valid_matches)
                
                # Check if we've hit the total lines limit
                if total_matches >= max_total_lines:
                    all_matches = all_matches[:max_total_lines]
                    break
        
        # Format results based on output mode
        if output_mode == "files_with_matches":
            results = [{"file": f} for f in files_with_matches]
        elif output_mode == "count":
            results = [{"file": f, "count": c} for f, c in file_match_counts.items()]
        else:  # content mode
            results = all_matches
        
        search_result = {
            "success": True,
            "numFiles": len(files_with_matches),
            "numMatches": total_matches,
            "results": results,
            "truncated": total_matches >= max_total_lines,
            "search_time": time.time() - start_time,
            "pattern": pattern,
            "path": path
        }
        
        # Add to search history
        self.search_history.append({
            "pattern": pattern,
            "path": path,
            "timestamp": time.time(),
            "matches": total_matches,
            "files": len(files_with_matches)
        })
        
        return search_result
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history"""
        return self.search_history[-limit:] if limit > 0 else self.search_history
    
    def clear_search_history(self):
        """Clear search history"""
        self.search_history.clear()

# Integration class for JARVIS
class SearchSystem:
    """Search system integration for JARVIS"""
    
    def __init__(self):
        self.advanced_search = AdvancedSearchSystem()
    
    def grep(self, pattern: str, path: str = ".", **kwargs) -> Dict[str, Any]:
        """Main grep interface for JARVIS"""
        return self.advanced_search.grep_search(pattern, path, **kwargs)
    
    def search_files(self, pattern: str, file_pattern: str = "*", search_path: str = ".") -> Dict[str, Any]:
        """Legacy search interface"""
        return self.advanced_search.grep_search(
            pattern, search_path, include=file_pattern, output_mode="content"
        )
