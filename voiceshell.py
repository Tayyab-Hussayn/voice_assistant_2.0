import subprocess
from modules.voice_input import VoiceInput
from modules.ai_handler import AIHandler
import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class VoiceShell:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.command_patterns = self.load_patterns()
        self.ai = AIHandler() 
        self.voice = VoiceInput() 

    def load_patterns(self):
        """Load command patterns from JSON"""
        try:
            with open('command_patterns.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("⚠️  command_patterns.json not found - pattern matching disabled")
            return {}
    
    def match_pattern(self, user_input):
        """Try to match user input to a known command pattern"""
        user_input = user_input.lower().strip()
        
        for category in self.command_patterns.values():
            for pattern, command in category.items():
                if user_input == pattern.lower():
                    return command
                
                if user_input.startswith(pattern.lower()):
                    arg = user_input[len(pattern):].strip()
                    if arg:
                        return f"{command} {arg}"
                    return command
        
        return None
    
    def execute_command(self, command):
        """Execute a shell command safely"""
        try:
            os.chdir(self.current_dir)
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            self.current_dir = Path.cwd()
            
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def is_dangerous_command(self, command):
        """Check if command is potentially dangerous"""
        dangerous_patterns = [
            'rm -rf /',
            'rm -rf /*',
            'sudo rm',
            'mkfs',
            '> /dev/',
            'dd if=',
            'chmod -R 777 /',
            ':(){:|:&};:',
            'sudo',
            'su ',
        ]
        
        cmd_lower = command.lower()
        return any(pattern in cmd_lower for pattern in dangerous_patterns)
    
    def process_input(self, user_input):
        """Main input processing pipeline"""
        print(f"\n🔍 Processing: '{user_input}'")
        
        # TIER 1: Pattern matching (fast)
        command = self.match_pattern(user_input)
        if command:
            print(f"⚡ Fast match: {command}")
            return command
        
        # TIER 2: AI generation (slower)
        print("🤖 Asking AI...")
        command = self.ai.generate_command(user_input, self.current_dir)
        if command:
            print(f"🧠 AI generated: {command}")
            return command
        
        # TIER 3: Assume it's a direct command
        print("📝 Treating as direct command")
        return user_input
    
    def run(self):
        print("\n" + "="*60)
        print("🚀 VoiceShell v0.4 - Modular")
        print("="*60)
        print(f"📁 Current directory: {self.current_dir}")
        print("\nPress Enter to speak, or type 'exit' to quit\n")
    
        while True:
            mode = input("Press ENTER for voice (or type command): ").strip()
            
            if mode.lower() == 'exit':
                print("👋 Goodbye!")
                break
            
            # Get input
            if mode == "":
                user_input = self.voice.listen() 
                if not user_input:
                    continue
            else:
                user_input = mode
        
            # Process
            command = self.process_input(user_input)
            
            if not command:
                print("❌ Could not understand request")
                continue
            
            # Safety check
            if self.is_dangerous_command(command):
                print(f"⚠️  DANGEROUS: {command}")
                confirm = input("Continue? (yes): ")
                if confirm.lower() != 'yes':
                    print("❌ Cancelled")
                    continue
            
            # Execute
            print(f"⚙️  Executing: {command}")
            result = self.execute_command(command)
        
            print("\n" + "-"*60)
            if result['success']:
                if result['output']:
                    print(result['output'])
                print("✅ Done")
            else:
                print(f"❌ Error: {result['error']}")
            print("-"*60 + "\n")

if __name__ == "__main__":
    agent = VoiceShell()
    agent.run()
