#!/usr/bin/env python3
"""
JARVIS Unified Terminal Interface
Warp Terminal-inspired unified prompt for AI chat and shell commands
"""

import os
import sys
import signal
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.prompt import Prompt
from rich.status import Status
from rich.table import Table
from rich import box

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from jarvis import JARVIS
from modules.unified_terminal import UnifiedTerminal

class JARVISUnifiedCLI:
    """
    Unified CLI interface that combines AI chat and terminal functionality
    """
    
    def __init__(self):
        self.console = Console()
        self.jarvis = None
        self.unified_terminal = None
        self.running = True
        self.terminal_mode = True  # Always in unified mode
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle interrupt signals gracefully"""
        self.console.print("\n👋 JARVIS shutting down gracefully...")
        self.running = False
        sys.exit(0)
    
    def initialize_jarvis(self):
        """Initialize JARVIS and unified terminal"""
        try:
            with Status("🤖 Initializing JARVIS...", console=self.console):
                self.jarvis = JARVIS()
                self.unified_terminal = UnifiedTerminal(self.jarvis)
                
                # Set terminal context for better intent classification
                if hasattr(self.jarvis.intent_classifier, 'set_terminal_context'):
                    self.jarvis.intent_classifier.set_terminal_context(True)
            
            self.console.print("✅ JARVIS Unified Terminal ready!", style="bold green")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Failed to initialize JARVIS: {str(e)}", style="bold red")
            return False
    
    def create_header_panel(self):
        """Create header panel with status information"""
        # Get current directory and mode info
        cwd = self.unified_terminal.get_current_directory() if self.unified_terminal else os.getcwd()
        mode_info = self.unified_terminal.get_mode_info() if self.unified_terminal else {"current_mode": "auto"}
        
        # Create header content
        header_text = Text()
        header_text.append("🤖 JARVIS Unified Terminal", style="bold cyan")
        header_text.append(" | ", style="dim")
        header_text.append(f"📁 {Path(cwd).name}", style="yellow")
        header_text.append(" | ", style="dim")
        header_text.append(f"Mode: {mode_info['current_mode']}", style="green")
        
        return Panel(
            header_text,
            box=box.ROUNDED,
            style="cyan",
            height=3
        )
    
    def create_help_panel(self):
        """Create help panel with usage instructions"""
        help_table = Table(show_header=False, box=None, padding=(0, 1))
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="dim")
        
        help_table.add_row("$ command", "Force shell mode")
        help_table.add_row("ai: message", "Force AI chat mode")
        help_table.add_row("jarvis: task", "Force JARVIS processing")
        help_table.add_row("help", "Show this help")
        help_table.add_row("exit", "Quit JARVIS")
        
        return Panel(
            help_table,
            title="💡 Quick Help",
            box=box.ROUNDED,
            style="blue"
        )
    
    def format_output(self, result: dict) -> str:
        """Format command output based on mode and result"""
        if not result:
            return ""
        
        mode = result.get('mode', 'unknown')
        success = result.get('success', True)
        output = result.get('output', '')
        
        # Mode indicators
        mode_icons = {
            'shell': '🖥️',
            'ai': '🤖',
            'intelligent': '🧠',
            'auto': '⚡'
        }
        
        mode_icon = mode_icons.get(mode, '❓')
        
        # Success/failure styling
        if success:
            status_style = "green"
            status_icon = "✅"
        else:
            status_style = "red"
            status_icon = "❌"
        
        # Format output
        if output:
            formatted = f"{mode_icon} {output}"
        else:
            formatted = f"{status_icon} Command completed"
        
        return formatted
    
    def process_special_commands(self, user_input: str) -> bool:
        """Handle special CLI commands"""
        user_input_lower = user_input.lower().strip()
        
        if user_input_lower in ['exit', 'quit', 'q']:
            self.running = False
            return True
        
        elif user_input_lower in ['help', '?']:
            self.console.print(self.create_help_panel())
            return True
        
        elif user_input_lower == 'clear':
            self.console.clear()
            return True
        
        elif user_input_lower == 'history':
            history = self.unified_terminal.get_command_history() if self.unified_terminal else []
            if history:
                self.console.print("📜 Command History:")
                for i, cmd in enumerate(history[-10:], 1):
                    self.console.print(f"  {i}. {cmd}")
            else:
                self.console.print("📜 No command history")
            return True
        
        elif user_input_lower.startswith('mode '):
            mode = user_input_lower[5:].strip()
            if self.unified_terminal:
                try:
                    self.unified_terminal.set_mode(mode)
                    self.console.print(f"✅ Mode set to: {mode}", style="green")
                except ValueError as e:
                    self.console.print(f"❌ {str(e)}", style="red")
            return True
        
        return False
    
    def run(self):
        """Main CLI loop"""
        # Initialize JARVIS
        if not self.initialize_jarvis():
            return
        
        # Show header
        self.console.print(self.create_header_panel())
        self.console.print()
        
        # Welcome message
        welcome_text = Text()
        welcome_text.append("Welcome to JARVIS Unified Terminal! ", style="bold")
        welcome_text.append("Chat with AI or run shell commands in the same prompt.", style="dim")
        self.console.print(Panel(welcome_text, style="green"))
        self.console.print()
        
        # Show quick help
        self.console.print(self.create_help_panel())
        self.console.print()
        
        # Main interaction loop
        while self.running:
            try:
                # Get current directory for prompt
                cwd = self.unified_terminal.get_current_directory() if self.unified_terminal else os.getcwd()
                cwd_name = Path(cwd).name
                
                # Create dynamic prompt
                prompt_text = f"[cyan]JARVIS[/cyan] [yellow]{cwd_name}[/yellow] [dim]❯[/dim] "
                
                # Get user input
                user_input = Prompt.ask(prompt_text, console=self.console)
                
                if not user_input.strip():
                    continue
                
                # Handle special commands
                if self.process_special_commands(user_input):
                    continue
                
                # Process through unified terminal
                with Status("Processing...", console=self.console) as status:
                    result = self.unified_terminal.process_input(user_input)
                
                # Display result
                if result:
                    formatted_output = self.format_output(result)
                    if formatted_output:
                        self.console.print(formatted_output)
                
                self.console.print()  # Add spacing
                
            except KeyboardInterrupt:
                self.console.print("\n👋 JARVIS shutting down...")
                break
            except EOFError:
                self.console.print("\n👋 JARVIS shutting down...")
                break
            except Exception as e:
                self.console.print(f"❌ Unexpected error: {str(e)}", style="red")
                continue
        
        # Cleanup
        self.console.print("👋 JARVIS offline. Goodbye!", style="bold blue")

def main():
    """Main entry point"""
    try:
        cli = JARVISUnifiedCLI()
        cli.run()
    except Exception as e:
        console = Console()
        console.print(f"❌ Fatal error: {str(e)}", style="bold red")
        sys.exit(1)

if __name__ == "__main__":
    main()
