#!/usr/bin/env python3
"""
JARVIS CLI - Terminal Interface with Advanced Features
Enhanced with status indicators, interrupt handling, and project analysis
"""

import sys
import os
import threading
import time
import signal
import glob
from datetime import datetime
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.columns import Columns
from rich.align import Align
from rich.prompt import Prompt
from rich.live import Live
from rich.layout import Layout
from rich.spinner import Spinner
from rich.status import Status

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from jarvis import JARVIS
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False

class JARVISTerminalCLI:
    """JARVIS CLI with Kiro-like features"""
    
    def __init__(self):
        self.console = Console()
        self.jarvis = None
        self.is_running = False
        self.message_count = 0
        self.current_task = None
        self.task_interrupted = False
        self.processing = False
        
        # Setup interrupt handler
        signal.signal(signal.SIGINT, self.handle_interrupt)
        
    def handle_interrupt(self, signum, frame):
        """Handle Ctrl+C interrupt"""
        if self.processing:
            self.task_interrupted = True
            self.console.print("\n[yellow]⏸️ Task interrupted. Type your next instruction...[/]")
            if self.jarvis and hasattr(self.jarvis, 'system'):
                self.jarvis.system.stop_current_process()
        else:
            self.console.print("\n[yellow]Use '/exit' to quit JARVIS[/]")
    
    def print_header(self):
        """Print elegant header"""
        header = Panel(
            Align.center(
                Text("🤖 JARVIS", style="bold bright_blue") + 
                Text(" • ", style="dim") +
                Text("Advanced AI Assistant", style="bright_white")
            ),
            style="bright_blue",
            padding=(0, 2)
        )
        self.console.print(header)
        self.console.print()
    
    def get_status_message(self, command):
        """Get appropriate status message based on command"""
        command_lower = command.lower()
        
        # Project analysis
        if any(word in command_lower for word in ['analyze', 'understand', 'explain', 'what is']):
            return "Analyzing"
        
        # File operations
        if any(word in command_lower for word in ['read', 'file', 'directory', 'folder']):
            return "Reading files"
        
        # Web operations
        if any(word in command_lower for word in ['search', 'web', 'internet', 'online']):
            return "Web search"
        
        # System operations
        if any(word in command_lower for word in ['install', 'run', 'execute', 'command']):
            return "System task"
        
        # Code operations
        if any(word in command_lower for word in ['code', 'program', 'script', 'build']):
            return "Code analysis"
        
        # Learning/Understanding
        if any(word in command_lower for word in ['learn', 'study', 'understand', 'how']):
            return "Learning"
        
        # Default
        return "Thinking"
    
    def analyze_project_directory(self, directory_path):
        """Analyze a project directory like Kiro CLI"""
        try:
            path = Path(directory_path).expanduser().resolve()
            if not path.exists():
                return f"Directory {directory_path} does not exist"
            
            if not path.is_dir():
                return f"{directory_path} is not a directory"
            
            analysis = {
                'path': str(path),
                'name': path.name,
                'files': [],
                'languages': set(),
                'frameworks': set(),
                'config_files': [],
                'readme_content': '',
                'package_files': []
            }
            
            # Analyze files
            for file_path in path.rglob('*'):
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts[len(path.parts):]):
                    relative_path = file_path.relative_to(path)
                    analysis['files'].append(str(relative_path))
                    
                    # Detect languages and frameworks
                    suffix = file_path.suffix.lower()
                    name = file_path.name.lower()
                    
                    # Languages
                    if suffix in ['.py']:
                        analysis['languages'].add('Python')
                    elif suffix in ['.js', '.jsx']:
                        analysis['languages'].add('JavaScript')
                    elif suffix in ['.ts', '.tsx']:
                        analysis['languages'].add('TypeScript')
                    elif suffix in ['.java']:
                        analysis['languages'].add('Java')
                    elif suffix in ['.cpp', '.c', '.h']:
                        analysis['languages'].add('C/C++')
                    elif suffix in ['.rs']:
                        analysis['languages'].add('Rust')
                    elif suffix in ['.go']:
                        analysis['languages'].add('Go')
                    elif suffix in ['.php']:
                        analysis['languages'].add('PHP')
                    elif suffix in ['.rb']:
                        analysis['languages'].add('Ruby')
                    elif suffix in ['.html', '.css']:
                        analysis['languages'].add('Web')
                    
                    # Frameworks and tools
                    if name in ['package.json']:
                        analysis['frameworks'].add('Node.js')
                        analysis['package_files'].append(str(relative_path))
                    elif name in ['requirements.txt', 'pyproject.toml', 'setup.py']:
                        analysis['frameworks'].add('Python Project')
                        analysis['package_files'].append(str(relative_path))
                    elif name in ['cargo.toml']:
                        analysis['frameworks'].add('Rust Project')
                        analysis['package_files'].append(str(relative_path))
                    elif name in ['pom.xml', 'build.gradle']:
                        analysis['frameworks'].add('Java Project')
                        analysis['package_files'].append(str(relative_path))
                    elif name in ['dockerfile', 'docker-compose.yml']:
                        analysis['frameworks'].add('Docker')
                        analysis['config_files'].append(str(relative_path))
                    elif name in ['.gitignore', '.env', 'config.json', 'settings.json']:
                        analysis['config_files'].append(str(relative_path))
                    elif 'readme' in name:
                        try:
                            content = file_path.read_text(encoding='utf-8', errors='ignore')
                            analysis['readme_content'] = content[:500] + '...' if len(content) > 500 else content
                        except:
                            pass
            
            return self.format_project_analysis(analysis)
            
        except Exception as e:
            return f"Error analyzing directory: {e}"
    
    def format_project_analysis(self, analysis):
        """Format project analysis results"""
        result = f"""[bold cyan]📁 Project Analysis: {analysis['name']}[/]

[bright_white]📍 Location:[/] {analysis['path']}
[bright_white]📊 Total Files:[/] {len(analysis['files'])}

[bright_white]💻 Languages Detected:[/]
{', '.join(analysis['languages']) if analysis['languages'] else 'None detected'}

[bright_white]🛠️ Frameworks/Tools:[/]
{', '.join(analysis['frameworks']) if analysis['frameworks'] else 'None detected'}

[bright_white]📦 Package Files:[/]
{', '.join(analysis['package_files']) if analysis['package_files'] else 'None found'}

[bright_white]⚙️ Config Files:[/]
{', '.join(analysis['config_files']) if analysis['config_files'] else 'None found'}"""

        if analysis['readme_content']:
            result += f"""

[bright_white]📖 README Content:[/]
[dim]{analysis['readme_content']}[/]"""

        # Key files preview
        key_files = [f for f in analysis['files'][:10] if not f.startswith('.')]
        if key_files:
            result += f"""

[bright_white]🔍 Key Files:[/]
{chr(10).join(f'• {f}' for f in key_files)}"""
            if len(analysis['files']) > 10:
                result += f"\n[dim]... and {len(analysis['files']) - 10} more files[/]"

        return result
    
    def initialize_jarvis(self):
        """Initialize JARVIS with loading animation"""
        if not JARVIS_AVAILABLE:
            self.console.print("[red]⚠️ JARVIS module not available[/]")
            return False
            
        with self.console.status("[yellow]Initializing JARVIS...", spinner="dots"):
            try:
                self.jarvis = JARVIS()
                self.is_running = True
                time.sleep(1)
                self.console.print("[green]✅ JARVIS initialized successfully![/]")
                return True
            except Exception as e:
                self.console.print(f"[red]❌ Failed to initialize: {e}[/]")
                return False
    
    def print_welcome(self):
        """Print welcome message"""
        welcome_text = """
[dim]Welcome to JARVIS CLI - Your Advanced AI Assistant[/]

[bright_white]Available Commands:[/]
• Type naturally - JARVIS understands conversation
• [cyan]analyze /path/to/project[/] - Analyze project directory
• [cyan]/help[/] - Show detailed help
• [cyan]/status[/] - System information  
• [cyan]/clear[/] - Clear screen
• [cyan]/exit[/] - Exit JARVIS

[dim]Ready for your commands... (Ctrl+C to interrupt tasks)[/]
        """
        
        welcome_panel = Panel(
            welcome_text.strip(),
            title="[bright_blue]Getting Started[/]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(welcome_panel)
        self.console.print()
    
    def format_user_message(self, message):
        """Format user input message"""
        timestamp = datetime.now().strftime("%H:%M")
        
        user_panel = Panel(
            message,
            title=f"[dim]{timestamp}[/]",
            title_align="right",
            border_style="bright_blue",
            padding=(0, 1)
        )
        
        self.console.print(user_panel)
    
    def format_jarvis_response(self, response):
        """Format JARVIS response"""
        timestamp = datetime.now().strftime("%H:%M")
        
        jarvis_panel = Panel(
            response,
            title=f"[bright_blue]🤖 JARVIS[/] [dim]{timestamp}[/]",
            border_style="green",
            padding=(0, 1)
        )
        
        self.console.print(jarvis_panel)
        self.console.print()
    
    def show_help(self):
        """Show detailed help"""
        help_text = """
[bold bright_blue]🤖 JARVIS CLI Help[/]

[bright_white]Natural Language:[/]
• "Analyze the project in ~/code/myapp"
• "What files are in this directory?"
• "Create a web project called portfolio"
• "Show me system information"
• "Open Chrome browser"

[bright_white]Project Analysis:[/]
• [cyan]analyze /path/to/project[/] - Deep project analysis
• [cyan]understand this directory[/] - Analyze current directory
• [cyan]what is this project[/] - Project overview

[bright_white]Commands:[/]
• [cyan]/help[/] - Show this help
• [cyan]/status[/] - System status
• [cyan]/clear[/] - Clear screen
• [cyan]/features[/] - List capabilities
• [cyan]/stop[/] - Stop running process
• [cyan]/exit[/] - Exit application

[bright_white]Interruption:[/]
• [cyan]Ctrl+C[/] - Interrupt current task
• Continue with new instructions after interruption

[dim]JARVIS understands natural language - just type what you want![/]
        """
        
        help_panel = Panel(
            help_text.strip(),
            title="[bright_blue]JARVIS Help[/]",
            border_style="blue",
            padding=(1, 2)
        )
        
        self.console.print(help_panel)
        self.console.print()
    
    def process_command(self, command):
        """Process user command with status indicators"""
        if not self.is_running or not JARVIS_AVAILABLE:
            self.console.print("[red]❌ JARVIS is not available[/]")
            return
        
        self.processing = True
        self.task_interrupted = False
        
        # Check for project analysis
        if command.lower().startswith('analyze '):
            directory = command[8:].strip()
            status_msg = "Analyzing project"
        elif any(word in command.lower() for word in ['analyze', 'understand', 'what is']) and any(word in command.lower() for word in ['directory', 'project', 'folder']):
            # Analyze current directory
            directory = '.'
            status_msg = "Analyzing project"
        else:
            directory = None
            status_msg = self.get_status_message(command)
        
        # Show status with spinner
        try:
            with self.console.status(f"[yellow]{status_msg}...", spinner="dots") as status:
                if directory:
                    # Project analysis
                    result = self.analyze_project_directory(directory)
                    if not self.task_interrupted:
                        self.format_jarvis_response(result)
                else:
                    # Regular JARVIS processing
                    import io
                    from contextlib import redirect_stdout, redirect_stderr
                    
                    output_buffer = io.StringIO()
                    with redirect_stdout(output_buffer), redirect_stderr(output_buffer):
                        if not self.task_interrupted:
                            result = self.jarvis.process_input(command)
                    
                    if not self.task_interrupted:
                        captured = output_buffer.getvalue()
                        response = captured if captured else (result if result else "Task completed successfully")
                        
                        # Clean response
                        if response:
                            import re
                            clean_response = re.sub(r'\x1b\[[0-9;]*m', '', response)
                            clean_response = clean_response.strip()
                            
                            if clean_response:
                                self.format_jarvis_response(clean_response)
                            else:
                                self.format_jarvis_response("✅ Command executed successfully")
                
        except Exception as e:
            if not self.task_interrupted:
                self.format_jarvis_response(f"[red]❌ Error: {e}[/]")
        
        finally:
            self.processing = False
    
    def run(self):
        """Main CLI loop"""
        # Clear screen and show header
        self.console.clear()
        self.print_header()
        
        # Initialize JARVIS
        if not self.initialize_jarvis():
            self.console.print("[dim]Running in demo mode...[/]")
            self.console.print()
        
        # Show welcome
        self.print_welcome()
        
        try:
            while True:
                try:
                    # Only accept input when not processing
                    if not self.processing:
                        user_input = Prompt.ask(
                            "[bright_blue]❯[/]",
                            console=self.console
                        ).strip()
                        
                        if not user_input:
                            continue
                        
                        # Display user message
                        self.format_user_message(user_input)
                        self.message_count += 1
                        
                        # Handle special commands
                        if user_input.lower() in ['/exit', 'exit', 'quit']:
                            self.format_jarvis_response("[yellow]Goodbye! JARVIS signing off. 👋[/]")
                            break
                            
                        elif user_input.lower() in ['/clear', 'clear']:
                            self.console.clear()
                            self.print_header()
                            self.format_jarvis_response("[green]Screen cleared[/]")
                            
                        elif user_input.lower() in ['/help', 'help']:
                            self.show_help()
                            
                        else:
                            # Process through JARVIS
                            self.process_command(user_input)
                    else:
                        time.sleep(0.1)  # Brief pause when processing
                
                except KeyboardInterrupt:
                    continue  # Handled by signal handler
                    
                except EOFError:
                    break
                    
        except Exception as e:
            self.console.print(f"[red]❌ Unexpected error: {e}[/]")
        
        finally:
            self.console.print("[dim]JARVIS CLI session ended.[/]")

def main():
    """Launch JARVIS CLI"""
    cli = JARVISTerminalCLI()
    cli.run()

if __name__ == "__main__":
    main()
