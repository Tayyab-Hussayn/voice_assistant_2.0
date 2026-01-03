import json
import subprocess
import threading
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import uuid

class LSPServer:
    """Individual LSP Server instance"""
    
    def __init__(self, name: str, command: str, args: List[str], file_extensions: List[str]):
        self.name = name
        self.command = command
        self.args = args
        self.file_extensions = file_extensions
        self.process = None
        self.initialized = False
        self.capabilities = {}
        self.request_id = 0
        self.pending_requests = {}
        
    def start(self, root_path: str) -> bool:
        """Start the LSP server process"""
        try:
            self.process = subprocess.Popen(
                [self.command] + self.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=root_path
            )
            
            # Initialize the server
            return self._initialize(root_path)
            
        except Exception as e:
            print(f"Failed to start {self.name}: {e}")
            return False
    
    def _initialize(self, root_path: str) -> bool:
        """Send initialize request to LSP server"""
        try:
            init_params = {
                "processId": os.getpid(),
                "rootPath": root_path,
                "rootUri": f"file://{root_path}",
                "capabilities": {
                    "textDocument": {
                        "hover": {"contentFormat": ["markdown", "plaintext"]},
                        "definition": {"linkSupport": True},
                        "references": {"context": True},
                        "documentSymbol": {"hierarchicalDocumentSymbolSupport": True},
                        "completion": {"completionItem": {"snippetSupport": True}}
                    },
                    "workspace": {
                        "symbol": {"symbolKind": {"valueSet": list(range(1, 27))}}
                    }
                }
            }
            
            response = self._send_request("initialize", init_params)
            if response and "result" in response:
                self.capabilities = response["result"].get("capabilities", {})
                
                # Send initialized notification
                self._send_notification("initialized", {})
                self.initialized = True
                return True
                
        except Exception as e:
            print(f"Failed to initialize {self.name}: {e}")
            
        return False
    
    def _send_request(self, method: str, params: Any) -> Optional[Dict]:
        """Send LSP request and wait for response"""
        if not self.process:
            return None
            
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params
        }
        
        try:
            message = json.dumps(request)
            content = f"Content-Length: {len(message)}\r\n\r\n{message}"
            
            self.process.stdin.write(content)
            self.process.stdin.flush()
            
            # Read response (simplified - real implementation needs proper parsing)
            return self._read_response()
            
        except Exception as e:
            print(f"Request failed for {self.name}: {e}")
            return None
    
    def _send_notification(self, method: str, params: Any):
        """Send LSP notification (no response expected)"""
        if not self.process:
            return
            
        notification = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params
        }
        
        try:
            message = json.dumps(notification)
            content = f"Content-Length: {len(message)}\r\n\r\n{message}"
            
            self.process.stdin.write(content)
            self.process.stdin.flush()
            
        except Exception as e:
            print(f"Notification failed for {self.name}: {e}")
    
    def _read_response(self) -> Optional[Dict]:
        """Read LSP response (simplified implementation)"""
        try:
            # Read Content-Length header
            header_line = self.process.stdout.readline()
            if not header_line.startswith("Content-Length:"):
                return None
                
            content_length = int(header_line.split(":")[1].strip())
            
            # Read empty line
            self.process.stdout.readline()
            
            # Read JSON content
            content = self.process.stdout.read(content_length)
            return json.loads(content)
            
        except Exception as e:
            print(f"Failed to read response from {self.name}: {e}")
            return None
    
    def search_symbols(self, symbol_name: str, file_path: Optional[str] = None, 
                      symbol_type: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Search for symbols by name across workspace"""
        if not self.process or not self.initialized:
            return {"error": "Server not initialized"}
        
        params = {
            "query": symbol_name,
            "limit": limit
        }
        
        if file_path:
            params["location"] = {"uri": f"file://{file_path}"}
        
        response = self._send_request("workspace/symbol", params)
        
        if response and "result" in response:
            symbols = []
            for symbol in response["result"]:
                symbols.append({
                    "name": symbol.get("name", ""),
                    "kind": symbol.get("kind", 0),
                    "location": {
                        "file": symbol.get("location", {}).get("uri", "").replace("file://", ""),
                        "line": symbol.get("location", {}).get("range", {}).get("start", {}).get("line", 0) + 1,
                        "character": symbol.get("location", {}).get("range", {}).get("start", {}).get("character", 0)
                    },
                    "containerName": symbol.get("containerName", "")
                })
            
            return {"success": True, "symbols": symbols}
        
        return {"error": "No symbols found"}
    
    def goto_definition(self, file_path: str, line: int, character: int) -> Dict[str, Any]:
        """Go to definition of symbol at position"""
        if not self.process or not self.initialized:
            return {"error": "Server not initialized"}
        
        params = {
            "textDocument": {"uri": f"file://{file_path}"},
            "position": {"line": line - 1, "character": character}
        }
        
        response = self._send_request("textDocument/definition", params)
        
        if response and "result" in response:
            result = response["result"]
            if isinstance(result, list) and result:
                location = result[0]
                return {
                    "success": True,
                    "location": {
                        "file": location.get("uri", "").replace("file://", ""),
                        "line": location.get("range", {}).get("start", {}).get("line", 0) + 1,
                        "character": location.get("range", {}).get("start", {}).get("character", 0)
                    }
                }
        
        return {"error": "Definition not found"}
    
    def find_references(self, file_path: str, line: int, character: int) -> Dict[str, Any]:
        """Find all references to symbol at position"""
        if not self.process or not self.initialized:
            return {"error": "Server not initialized"}
        
        params = {
            "textDocument": {"uri": f"file://{file_path}"},
            "position": {"line": line - 1, "character": character},
            "context": {"includeDeclaration": True}
        }
        
        response = self._send_request("textDocument/references", params)
        
        if response and "result" in response:
            references = []
            for ref in response["result"]:
                references.append({
                    "file": ref.get("uri", "").replace("file://", ""),
                    "line": ref.get("range", {}).get("start", {}).get("line", 0) + 1,
                    "character": ref.get("range", {}).get("start", {}).get("character", 0)
                })
            
            return {"success": True, "references": references}
        
        return {"error": "No references found"}
    
    def get_document_symbols(self, file_path: str) -> Dict[str, Any]:
        """Get all symbols in a document"""
        if not self.process or not self.initialized:
            return {"error": "Server not initialized"}
        
        params = {
            "textDocument": {"uri": f"file://{file_path}"}
        }
        
        response = self._send_request("textDocument/documentSymbol", params)
        
        if response and "result" in response:
            symbols = []
            for symbol in response["result"]:
                symbols.append({
                    "name": symbol.get("name", ""),
                    "kind": symbol.get("kind", 0),
                    "line": symbol.get("range", {}).get("start", {}).get("line", 0) + 1,
                    "character": symbol.get("range", {}).get("start", {}).get("character", 0),
                    "detail": symbol.get("detail", "")
                })
            
            return {"success": True, "symbols": symbols}
        
        return {"error": "No symbols found"}

class LSPManager:
    """
    LSP Integration Foundation - Language Server Protocol client
    Manages multiple language servers for code intelligence
    """
    
    def __init__(self):
        self.servers = {}
        self.workspace_root = None
        self.server_configs = self._get_default_configs()
        self.initialization_status = {}
        
    def _get_default_configs(self) -> Dict[str, Dict]:
        """Get default LSP server configurations"""
        return {
            "python": {
                "name": "pyright",
                "command": "pyright-langserver",
                "args": ["--stdio"],
                "file_extensions": [".py"],
                "project_patterns": ["pyproject.toml", "setup.py", "requirements.txt"]
            },
            "typescript": {
                "name": "typescript-language-server",
                "command": "typescript-language-server",
                "args": ["--stdio"],
                "file_extensions": [".ts", ".tsx", ".js", ".jsx"],
                "project_patterns": ["package.json", "tsconfig.json"]
            },
            "rust": {
                "name": "rust-analyzer",
                "command": "rust-analyzer",
                "args": [],
                "file_extensions": [".rs"],
                "project_patterns": ["Cargo.toml"]
            },
            "go": {
                "name": "gopls",
                "command": "gopls",
                "args": [],
                "file_extensions": [".go"],
                "project_patterns": ["go.mod", "go.sum"]
            },
            "java": {
                "name": "jdtls",
                "command": "jdtls",
                "args": [],
                "file_extensions": [".java"],
                "project_patterns": ["pom.xml", "build.gradle"]
            },
            "cpp": {
                "name": "clangd",
                "command": "clangd",
                "args": ["--background-index"],
                "file_extensions": [".cpp", ".c", ".h", ".hpp"],
                "project_patterns": ["CMakeLists.txt", "compile_commands.json"]
            }
        }
    
    def detect_languages(self, workspace_path: str) -> List[str]:
        """Detect programming languages in workspace"""
        workspace = Path(workspace_path)
        detected_languages = set()
        
        # Check for project markers
        for lang, config in self.server_configs.items():
            for pattern in config.get("project_patterns", []):
                if list(workspace.glob(pattern)):
                    detected_languages.add(lang)
        
        # Check file extensions
        for file_path in workspace.rglob("*"):
            if file_path.is_file():
                suffix = file_path.suffix
                for lang, config in self.server_configs.items():
                    if suffix in config["file_extensions"]:
                        detected_languages.add(lang)
        
        return list(detected_languages)
    
    def check_server_availability(self, language: str) -> Dict[str, Any]:
        """Check if LSP server is available for language"""
        if language not in self.server_configs:
            return {"available": False, "reason": "Language not supported"}
        
        config = self.server_configs[language]
        command = config["command"]
        
        try:
            # Try to run the command with --version or --help
            result = subprocess.run(
                [command, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return {"available": True, "version": result.stdout.strip()}
            else:
                # Try --help as fallback
                result = subprocess.run(
                    [command, "--help"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    return {"available": True, "version": "unknown"}
                    
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return {"available": False, "reason": f"Command '{command}' not found"}
    
    def initialize_workspace(self, workspace_path: str, force_restart: bool = False) -> Dict[str, Any]:
        """Initialize LSP servers for workspace"""
        workspace_path = str(Path(workspace_path).resolve())
        self.workspace_root = workspace_path
        
        # Stop existing servers if force restart
        if force_restart:
            self.shutdown_all_servers()
        
        # Detect languages
        detected_languages = self.detect_languages(workspace_path)
        
        # Check server availability
        available_servers = {}
        unavailable_servers = {}
        
        for lang in detected_languages:
            availability = self.check_server_availability(lang)
            if availability["available"]:
                available_servers[lang] = availability
            else:
                unavailable_servers[lang] = availability
        
        # Initialize available servers
        initialized_servers = {}
        failed_servers = {}
        
        for lang in available_servers:
            self.initialization_status[lang] = "initializing"
            
            try:
                config = self.server_configs[lang]
                server = LSPServer(
                    config["name"],
                    config["command"],
                    config["args"],
                    config["file_extensions"]
                )
                
                if server.start(workspace_path):
                    self.servers[lang] = server
                    initialized_servers[lang] = {
                        "name": config["name"],
                        "status": "initialized",
                        "capabilities": server.capabilities
                    }
                    self.initialization_status[lang] = "initialized"
                else:
                    failed_servers[lang] = "Failed to initialize"
                    self.initialization_status[lang] = "failed"
                    
            except Exception as e:
                failed_servers[lang] = str(e)
                self.initialization_status[lang] = "failed"
        
        return {
            "workspace": workspace_path,
            "detected_languages": detected_languages,
            "available_servers": available_servers,
            "unavailable_servers": unavailable_servers,
            "initialized_servers": initialized_servers,
            "failed_servers": failed_servers
        }
    
    def get_server_for_file(self, file_path: str) -> Optional[LSPServer]:
        """Get appropriate LSP server for file"""
        file_ext = Path(file_path).suffix
        
        for lang, server in self.servers.items():
            if file_ext in server.file_extensions:
                return server
        
        return None
    
    def shutdown_server(self, language: str) -> bool:
        """Shutdown specific LSP server"""
        if language in self.servers:
            self.servers[language].stop()
            del self.servers[language]
            self.initialization_status[language] = "stopped"
            return True
        return False
    
    def shutdown_all_servers(self):
        """Shutdown all LSP servers"""
        for language in list(self.servers.keys()):
            self.shutdown_server(language)
    
    def get_workspace_status(self) -> Dict[str, Any]:
        """Get current workspace and server status"""
        return {
            "workspace_root": self.workspace_root,
            "active_servers": {
                lang: {
                    "name": server.name,
                    "initialized": server.initialized,
                    "capabilities": list(server.capabilities.keys())
                }
                for lang, server in self.servers.items()
            },
            "initialization_status": self.initialization_status.copy()
        }

# Integration class for JARVIS
class CodeIntelligence:
    """Code Intelligence integration for JARVIS"""
    
    def __init__(self):
        self.lsp_manager = LSPManager()
        self.workspace_initialized = False
    
    def initialize_workspace(self, path: str = ".", force: bool = False) -> Dict[str, Any]:
        """Initialize code intelligence for workspace"""
        result = self.lsp_manager.initialize_workspace(path, force)
        self.workspace_initialized = len(result["initialized_servers"]) > 0
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get code intelligence status"""
        return self.lsp_manager.get_workspace_status()
    
    def is_ready(self) -> bool:
        """Check if code intelligence is ready"""
        return self.workspace_initialized and len(self.lsp_manager.servers) > 0
    
    def search_symbols(self, symbol_name: str, file_path: Optional[str] = None, 
                      symbol_type: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Search for symbols by name across workspace"""
        if not self.is_ready():
            return {"error": "Code intelligence not initialized"}
        
        # Try each available server
        for lang, server in self.lsp_manager.servers.items():
            if file_path:
                # Check if server handles this file type
                file_ext = Path(file_path).suffix
                if file_ext not in server.file_extensions:
                    continue
            
            result = server.search_symbols(symbol_name, file_path, symbol_type, limit)
            if result.get("success"):
                return result
        
        return {"error": "No symbols found"}
    
    def goto_definition(self, file_path: str, line: int, character: int) -> Dict[str, Any]:
        """Go to definition of symbol at position"""
        if not self.is_ready():
            return {"error": "Code intelligence not initialized"}
        
        server = self.lsp_manager.get_server_for_file(file_path)
        if not server:
            return {"error": f"No language server available for {Path(file_path).suffix}"}
        
        return server.goto_definition(file_path, line, character)
    
    def find_references(self, file_path: str, line: int, character: int) -> Dict[str, Any]:
        """Find all references to symbol at position"""
        if not self.is_ready():
            return {"error": "Code intelligence not initialized"}
        
        server = self.lsp_manager.get_server_for_file(file_path)
        if not server:
            return {"error": f"No language server available for {Path(file_path).suffix}"}
        
        return server.find_references(file_path, line, character)
    
    def get_document_symbols(self, file_path: str) -> Dict[str, Any]:
        """Get all symbols in a document"""
        if not self.is_ready():
            return {"error": "Code intelligence not initialized"}
        
        server = self.lsp_manager.get_server_for_file(file_path)
        if not server:
            return {"error": f"No language server available for {Path(file_path).suffix}"}
        
        return server.get_document_symbols(file_path)
    
    def lookup_symbols(self, symbols: List[str], file_path: Optional[str] = None) -> Dict[str, Any]:
        """Look up specific symbols by exact name"""
        if not self.is_ready():
            return {"error": "Code intelligence not initialized"}
        
        results = {}
        for symbol_name in symbols:
            result = self.search_symbols(symbol_name, file_path, limit=10)
            if result.get("success"):
                # Filter for exact matches
                exact_matches = [s for s in result["symbols"] if s["name"] == symbol_name]
                if exact_matches:
                    results[symbol_name] = exact_matches
        
        return {"success": True, "symbols": results} if results else {"error": "No symbols found"}
    
    def get_diagnostics(self, file_path: str) -> Dict[str, Any]:
        """Get diagnostics (errors, warnings) for a file"""
        if not self.is_ready():
            return {"error": "Code intelligence not initialized"}
        
        server = self.lsp_manager.get_server_for_file(file_path)
        if not server:
            return {"error": f"No language server available for {Path(file_path).suffix}"}
        
        return server.get_diagnostics(file_path)
    
    def rename_symbol(self, file_path: str, line: int, character: int, new_name: str, dry_run: bool = False) -> Dict[str, Any]:
        """Rename symbol across codebase"""
        if not self.is_ready():
            return {"error": "Code intelligence not initialized"}
        
        server = self.lsp_manager.get_server_for_file(file_path)
        if not server:
            return {"error": f"No language server available for {Path(file_path).suffix}"}
        
        return server.rename_symbol(file_path, line, character, new_name, dry_run)
