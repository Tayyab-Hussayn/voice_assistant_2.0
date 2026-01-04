import re
import subprocess
import os
from typing import Dict, Any, Optional, List
from pathlib import Path

class UnifiedTerminal:
    """
    Unified terminal interface that seamlessly handles both AI chat and shell commands
    Similar to Warp Terminal's unified prompt experience
    """
    
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.current_mode = 'auto'  # auto, shell, ai
        self.command_history = []
        self.shell_context = {
            'cwd': os.getcwd(),
            'env': os.environ.copy()
        }
        
        # Shell command patterns for detection
        self.shell_patterns = [
            # Common shell commands
            r'^(ls|cd|pwd|mkdir|rm|cp|mv|grep|find|cat|echo|chmod|chown|touch|head|tail|sort|uniq|wc)\s',
            # Commands with flags
            r'^\w+\s+(-\w+|--\w+)',
            # Commands with pipes
            r'^\w+.*\|\s*\w+',
            # File operations
            r'^\w+\s+\w+\.\w+',
            # Directory navigation
            r'^cd\s+[~/\.]',
            # Git commands
            r'^git\s+\w+',
            # Package managers
            r'^(npm|pip|apt|yum|brew)\s+\w+',
            # System commands
            r'^(ps|top|htop|df|du|free|uname|whoami|which|whereis)\s*',
        ]
        
        # AI chat patterns for detection
        self.ai_patterns = [
            # Development requests
            r'^(create|build|make|develop|design|generate)\s+(app|website|project|component|function)',
            # Questions
            r'^(how|what|why|when|where|can you|could you|please|help me)',
            # Requests ending with question marks
            r'.*\?$',
            # Conversational starters
            r'^(i need|i want|i would like|let me|show me)',
            # JARVIS-specific commands
            r'^(jarvis|research|analyze|workflow|task|knowledge)',
        ]
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Main input processing that routes between AI chat and shell commands
        """
        if not user_input.strip():
            return {"success": False, "output": "", "mode": "none"}
        
        # Add to history
        self.command_history.append(user_input)
        
        # Detect explicit mode indicators
        if user_input.startswith('$'):
            return self.handle_shell_mode(user_input[1:].strip())
        elif user_input.startswith('ai:'):
            return self.handle_ai_mode(user_input[3:].strip())
        elif user_input.startswith('jarvis:'):
            return self.handle_ai_mode(user_input[7:].strip())
        
        # Auto-detect mode based on input patterns
        detected_mode = self.detect_mode(user_input)
        
        if detected_mode == 'shell':
            return self.handle_shell_mode(user_input)
        elif detected_mode == 'ai':
            return self.handle_ai_mode(user_input)
        else:
            # Fallback to JARVIS's intelligent processing
            return self.handle_intelligent_mode(user_input)
    
    def detect_mode(self, user_input: str) -> str:
        """
        Intelligent mode detection based on input patterns
        """
        user_input_lower = user_input.lower().strip()
        
        # Score shell command likelihood
        shell_score = 0
        for pattern in self.shell_patterns:
            if re.match(pattern, user_input_lower):
                shell_score += 2
            elif re.search(pattern, user_input_lower):
                shell_score += 1
        
        # Score AI chat likelihood  
        ai_score = 0
        for pattern in self.ai_patterns:
            if re.match(pattern, user_input_lower):
                ai_score += 2
            elif re.search(pattern, user_input_lower):
                ai_score += 1
        
        # Additional context-based scoring
        if self.is_likely_shell_command(user_input):
            shell_score += 1
        
        if self.is_likely_ai_chat(user_input):
            ai_score += 1
        
        # Decision logic
        if shell_score > ai_score and shell_score > 1:
            return 'shell'
        elif ai_score > shell_score and ai_score > 1:
            return 'ai'
        else:
            return 'intelligent'  # Let JARVIS decide
    
    def is_likely_shell_command(self, user_input: str) -> bool:
        """
        Additional heuristics for shell command detection
        """
        # Check for common shell command characteristics
        indicators = [
            user_input.startswith('./'),
            user_input.startswith('/'),
            ' | ' in user_input,  # Pipes
            ' && ' in user_input or ' || ' in user_input,  # Logical operators
            user_input.endswith(' &'),  # Background process
            re.search(r'\s-[a-zA-Z]', user_input),  # Short flags
            re.search(r'\s--[a-zA-Z]', user_input),  # Long flags
        ]
        return any(indicators)
    
    def is_likely_ai_chat(self, user_input: str) -> bool:
        """
        Additional heuristics for AI chat detection
        """
        indicators = [
            len(user_input.split()) > 8,  # Long sentences
            user_input.endswith('?'),
            'please' in user_input.lower(),
            'help' in user_input.lower(),
            'create' in user_input.lower() and ('app' in user_input.lower() or 'website' in user_input.lower()),
        ]
        return any(indicators)
    
    def handle_shell_mode(self, command: str) -> Dict[str, Any]:
        """
        Handle shell command execution with native terminal behavior
        """
        if not command.strip():
            return {"success": True, "output": "", "mode": "shell"}
        
        try:
            # Handle cd command specially to maintain context
            if command.startswith('cd '):
                return self.handle_cd_command(command)
            
            # Execute command in current shell context
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.shell_context['cwd'],
                env=self.shell_context['env'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n{result.stderr}"
            
            return {
                "success": result.returncode == 0,
                "output": output.strip(),
                "mode": "shell",
                "command": command,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "❌ Command timed out after 30 seconds",
                "mode": "shell",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "output": f"❌ Shell error: {str(e)}",
                "mode": "shell",
                "command": command
            }
    
    def handle_cd_command(self, command: str) -> Dict[str, Any]:
        """
        Handle cd command to maintain shell context
        """
        try:
            # Parse cd command
            parts = command.split(None, 1)
            if len(parts) == 1:
                # cd with no arguments goes to home
                target_dir = os.path.expanduser('~')
            else:
                target_dir = os.path.expanduser(parts[1])
            
            # Resolve relative paths
            if not os.path.isabs(target_dir):
                target_dir = os.path.join(self.shell_context['cwd'], target_dir)
            
            # Normalize path
            target_dir = os.path.normpath(target_dir)
            
            # Check if directory exists
            if not os.path.isdir(target_dir):
                return {
                    "success": False,
                    "output": f"cd: {target_dir}: No such file or directory",
                    "mode": "shell",
                    "command": command
                }
            
            # Update shell context
            self.shell_context['cwd'] = target_dir
            
            return {
                "success": True,
                "output": f"📁 Changed directory to: {target_dir}",
                "mode": "shell",
                "command": command,
                "cwd": target_dir
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": f"❌ cd error: {str(e)}",
                "mode": "shell",
                "command": command
            }
    
    def handle_ai_mode(self, user_input: str) -> Dict[str, Any]:
        """
        Handle AI chat mode using JARVIS's conversational capabilities
        """
        try:
            # Use JARVIS's existing AI processing
            response = self.jarvis.process_input(user_input)
            
            return {
                "success": True,
                "output": response if response else "🤖 JARVIS processed your request",
                "mode": "ai",
                "input": user_input
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": f"❌ AI processing error: {str(e)}",
                "mode": "ai",
                "input": user_input
            }
    
    def handle_intelligent_mode(self, user_input: str) -> Dict[str, Any]:
        """
        Handle intelligent mode using JARVIS's full processing pipeline
        """
        try:
            # Let JARVIS handle with its full intelligence
            response = self.jarvis.process_input(user_input)
            
            return {
                "success": True,
                "output": response if response else "✅ JARVIS completed the task",
                "mode": "intelligent",
                "input": user_input
            }
            
        except Exception as e:
            return {
                "success": False,
                "output": f"❌ Processing error: {str(e)}",
                "mode": "intelligent",
                "input": user_input
            }
    
    def get_current_directory(self) -> str:
        """Get current working directory for shell context"""
        return self.shell_context['cwd']
    
    def get_command_history(self, limit: int = 10) -> List[str]:
        """Get recent command history"""
        return self.command_history[-limit:] if self.command_history else []
    
    def clear_history(self):
        """Clear command history"""
        self.command_history.clear()
    
    def set_mode(self, mode: str):
        """Explicitly set the processing mode"""
        if mode in ['auto', 'shell', 'ai']:
            self.current_mode = mode
        else:
            raise ValueError(f"Invalid mode: {mode}. Use 'auto', 'shell', or 'ai'")
    
    def get_mode_info(self) -> Dict[str, Any]:
        """Get current mode and context information"""
        return {
            "current_mode": self.current_mode,
            "cwd": self.shell_context['cwd'],
            "history_count": len(self.command_history),
            "available_modes": ["auto", "shell", "ai"]
        }
