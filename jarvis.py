import subprocess
from modules.voice_input import VoiceInput
from modules.ai_handler import AIHandler
from modules.system_controller import SystemController
from modules.command_processor import CommandProcessor
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class JARVIS:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.command_patterns = self.load_patterns()
        self.ai = AIHandler() 
        self.voice = VoiceInput()
        self.system = SystemController()
        self.command_processor = CommandProcessor()  # New enhanced processor
        self.wake_word_mode = False
        
        # JARVIS personality responses
        self.responses = {
            "greeting": ["Hello! JARVIS at your service.", "Good to see you again!", "JARVIS online and ready."],
            "confirmation": ["Certainly!", "Right away!", "Consider it done!", "On it!"],
            "error": ["I apologize, but I encountered an issue.", "Something went wrong.", "I'm having trouble with that."],
            "success": ["Task completed successfully!", "Done!", "Mission accomplished!"]
        }

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
    
    def handle_web_project_request(self, user_input):
        """Handle web project creation requests"""
        if "web" in user_input and ("create" in user_input or "build" in user_input or "make" in user_input):
            # Extract project name
            words = user_input.split()
            project_name = "web_project"
            
            # Try to find project name
            for i, word in enumerate(words):
                if word in ["called", "named"] and i + 1 < len(words):
                    project_name = words[i + 1]
                    break
                elif word in ["create", "build", "make"] and i + 1 < len(words) and words[i + 1] not in ["a", "an", "the"]:
                    project_name = words[i + 1]
                    break
            
            self.ai.speak("Creating web project now!")
            project_path = self.system.create_web_project(project_name)
            
            # Open in browser
            index_file = project_path / "index.html"
            if self.system.open_in_browser(index_file):
                self.ai.speak(f"Web project {project_name} created and opened in browser!")
                return True
            else:
                self.ai.speak(f"Web project {project_name} created successfully!")
                return True
        
        return False
    
    def handle_application_launch(self, user_input):
        """Handle application launch requests"""
        launch_keywords = ["open", "launch", "start", "run"]
        
        for keyword in launch_keywords:
            if keyword in user_input:
                # Extract app name
                words = user_input.split()
                try:
                    keyword_index = words.index(keyword)
                    if keyword_index + 1 < len(words):
                        app_name = " ".join(words[keyword_index + 1:])
                        
                        self.ai.speak(f"Opening {app_name}")
                        if self.system.launch_application(app_name):
                            self.ai.speak(f"{app_name} launched successfully!")
                            return True
                        else:
                            self.ai.speak(f"Sorry, I couldn't launch {app_name}")
                            return True
                except ValueError:
                    continue
        
        return False
    
    def handle_system_info_request(self, user_input):
        """Handle system information requests"""
        info_keywords = ["system info", "disk space", "memory", "status"]
        
        if any(keyword in user_input for keyword in info_keywords):
            self.ai.speak("Getting system information")
            info = self.system.get_system_info()
            
            response = "Here's your system status: "
            if 'current_dir' in info:
                response += f"Current directory is {info['current_dir']}. "
            if 'disk_usage' in info:
                response += f"Disk usage: {info['disk_usage']}. "
            if 'memory' in info:
                response += f"Memory: {info['memory']}."
            
            self.ai.speak(response)
            return True
        
        return False
    
    def process_input(self, user_input):
        """Main input processing pipeline with JARVIS intelligence"""
        print(f"\n🔍 JARVIS Processing: '{user_input}'")
        
        # TIER 0: Enhanced command processing (new modular system)
        result = self.command_processor.process_command(user_input)
        if result is not None:
            success, message = result
            if success:
                self.ai.speak(message)
                print(f"✅ {message}")
            else:
                self.ai.speak(f"Error: {message}")
                print(f"❌ {message}")
            return None
        
        # Handle special JARVIS requests
        if self.handle_web_project_request(user_input):
            return None
        
        if self.handle_application_launch(user_input):
            return None
            
        if self.handle_system_info_request(user_input):
            return None
        
        # TIER 1: Pattern matching (fast)
        command = self.match_pattern(user_input)
        if command:
            print(f"⚡ Fast match: {command}")
            self.ai.speak("Executing command")
            return command
        
        # TIER 2: AI generation (slower)
        print("🤖 JARVIS thinking...")
        self.ai.speak("Let me think about that")
        
        command = self.ai.generate_command(user_input, self.current_dir)
        if command:
            print(f"🧠 JARVIS generated: {command}")
            return command
        
        # TIER 3: Advanced AI processing
        advanced_response = self.ai.process_advanced_request(user_input, self.current_dir)
        if advanced_response:
            self.ai.speak("I understand. Let me handle that for you.")
            print(f"🎯 Advanced processing: {advanced_response}")
            return None
        
        # TIER 4: Assume it's a direct command
        print("📝 Treating as direct command")
        return user_input
    
    def run(self):
        print("\n" + "="*60)
        print("🤖 JARVIS v1.0 - Advanced AI Assistant")
        print("="*60)
        print(f"📁 Current directory: {self.current_dir}")
        print("\nModes:")
        print("1. Press ENTER for voice input")
        print("2. Type 'wake' for wake word mode")
        print("3. Type command directly")
        print("4. Type 'exit' to quit\n")
        
        self.ai.speak("JARVIS online and ready to assist you!")
    
        while True:
            if self.wake_word_mode:
                print("🔊 Wake word mode active - say 'Hey JARVIS' then your command")
                user_input = self.voice.listen(wake_word_mode=True)
            else:
                mode = input("JARVIS> ").strip()
                
                if mode.lower() == 'exit':
                    self.ai.speak("Goodbye! JARVIS signing off.")
                    print("👋 JARVIS offline")
                    break
                
                if mode.lower() == 'wake':
                    self.wake_word_mode = True
                    continue
                
                # Get input
                if mode == "":
                    user_input = self.voice.listen() 
                    if not user_input:
                        continue
                else:
                    user_input = mode
        
            if not user_input:
                continue
                
            # Process
            command = self.process_input(user_input)
            
            if not command:
                continue
            
            # Safety check
            if self.is_dangerous_command(command):
                print(f"⚠️  DANGEROUS: {command}")
                self.ai.speak("This command could be dangerous. Please confirm.")
                confirm = input("Continue? (yes): ")
                if confirm.lower() != 'yes':
                    self.ai.speak("Command cancelled for safety.")
                    print("❌ Cancelled")
                    continue
            
            # Execute
            print(f"⚙️  Executing: {command}")
            result = self.system.execute_command(command)
        
            print("\n" + "-"*60)
            if result['success']:
                if result['output']:
                    print(result['output'])
                self.ai.speak("Task completed successfully!")
                print("✅ Done")
            else:
                print(f"❌ Error: {result['error']}")
                self.ai.speak("I encountered an error while executing that command.")
            print("-"*60 + "\n")

if __name__ == "__main__":
    jarvis = JARVIS()
    jarvis.run()
