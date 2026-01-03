import subprocess
from modules.voice_input import VoiceInput
from modules.ai_handler import AIHandler
from modules.system_controller import SystemController
from modules.command_processor import CommandProcessor
from modules.conversational_ai import ConversationalAI
from modules.intelligent_web_builder import IntelligentWebBuilder
from modules.memory_system import MemorySystem
from modules.context_manager import ContextManager
from modules.learning_system import LearningSystem
from modules.task_scheduler import TaskScheduler
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Try to import computer vision module (optional)
try:
    from modules.computer_vision import ComputerVision
    VISION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Computer vision not available: {e}")
    VISION_AVAILABLE = False

load_dotenv()

class JARVIS:
    def __init__(self):
        self.current_dir = Path.cwd()
        self.command_patterns = self.load_patterns()
        self.ai = AIHandler() 
        self.voice = VoiceInput()
        self.system = SystemController()
        self.command_processor = CommandProcessor()
        self.conversation_ai = ConversationalAI(self.ai)  # Conversational AI
        self.computer_vision = ComputerVision() if VISION_AVAILABLE else None  # Optional computer vision
        self.web_developer = IntelligentWebBuilder(self.ai)  # Intelligent web builder
        
        # Phase 4: Intelligence & Memory System
        self.memory = MemorySystem()  # Long-term memory
        self.context_manager = ContextManager(self.memory)  # Context switching
        self.learning_system = LearningSystem(self.memory)  # Learning from interactions
        self.task_scheduler = TaskScheduler(self)  # Task scheduling
        
        # Start scheduler
        self.task_scheduler.start_scheduler()
        
        self.wake_word_mode = False
        self.vision_active = False
        
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
        """Handle intelligent web page creation requests"""
        web_keywords = ["web", "website", "webpage", "page", "site"]
        create_keywords = ["create", "build", "make", "generate", "design"]
        
        # Check if this is a web creation request
        has_web_keyword = any(keyword in user_input.lower() for keyword in web_keywords)
        has_create_keyword = any(keyword in user_input.lower() for keyword in create_keywords)
        
        if has_web_keyword and has_create_keyword:
            # Extract project name if specified
            words = user_input.split()
            project_name = None
            
            for i, word in enumerate(words):
                if word in ["called", "named"] and i + 1 < len(words):
                    project_name = words[i + 1]
                    break
            
            self.ai.speak("Analyzing your web page requirements and building a custom solution")
            success, message = self.web_developer.build_intelligent_webpage(user_input, project_name)
            
            if success:
                self.ai.speak("Custom web page created in Web Projects folder and opened in browser!")
            else:
                self.ai.speak(f"Error creating web page: {message}")
            
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
    
    def handle_vision_commands(self, user_input):
        """Handle computer vision and gesture control commands"""
        if not VISION_AVAILABLE or not self.computer_vision:
            self.ai.speak("Computer vision is not available in this environment")
            return True
            
        if "start vision" in user_input or "enable vision" in user_input or "gesture control" in user_input:
            self.ai.speak("Starting computer vision and gesture control")
            success, message = self.computer_vision.start_gesture_control()
            if success:
                self.vision_active = True
                self.ai.speak("Vision system active. Use gestures to control your computer.")
            else:
                self.ai.speak(f"Vision error: {message}")
            return True
        
        elif "stop vision" in user_input or "disable vision" in user_input:
            self.ai.speak("Stopping computer vision")
            success, message = self.computer_vision.stop_camera()
            self.vision_active = False
            self.ai.speak("Vision system stopped")
            return True
        
        elif "take screenshot" in user_input or "screenshot" in user_input:
            self.ai.speak("Taking screenshot")
            success, message = self.computer_vision.take_screenshot()
            self.ai.speak(message)
            return True
        
        elif "analyze screen" in user_input:
            self.ai.speak("Analyzing screen content")
            success, result = self.computer_vision.analyze_screen()
            if success:
                self.ai.speak(f"Screen analysis complete. Found {result['ui_elements']} UI elements.")
            else:
                self.ai.speak(f"Screen analysis failed: {result}")
            return True
        
        return False
    
    def handle_memory_commands(self, user_input):
        """Handle memory and context commands"""
        if "remember" in user_input and "that" in user_input:
            # Extract what to remember
            parts = user_input.split("that", 1)
            if len(parts) > 1:
                info = parts[1].strip()
                self.memory.store_knowledge("user_info", "custom", info)
                self.ai.speak(f"I'll remember that {info}")
                return True
        
        elif "what do you remember" in user_input or "what have you learned" in user_input:
            summary = self.learning_system.get_learning_summary()
            self.ai.speak("Here's what I've learned from our interactions")
            print(summary)
            return True
        
        elif "switch context" in user_input or "change context" in user_input:
            words = user_input.split()
            if "to" in words:
                context_name = " ".join(words[words.index("to") + 1:])
                context_id = context_name.lower().replace(' ', '_')
                if self.context_manager.switch_context(context_id):
                    self.ai.speak(f"Switched to {context_name} context")
                else:
                    self.ai.speak(f"Context {context_name} not found. Creating new context.")
                    self.context_manager.create_context(context_name)
                    self.context_manager.switch_context(context_id)
                    self.ai.speak(f"Created and switched to {context_name} context")
                return True
        
        elif "create context" in user_input:
            words = user_input.split()
            if "called" in words:
                context_name = " ".join(words[words.index("called") + 1:])
                context_id = self.context_manager.create_context(context_name)
                self.ai.speak(f"Created context {context_name}")
                return True
        
        elif "current context" in user_input or "context status" in user_input:
            summary = self.context_manager.get_context_summary()
            self.ai.speak("Here's your current context information")
            print(summary)
            return True
        
        elif "schedule" in user_input and ("task" in user_input or "reminder" in user_input):
            self.ai.speak("Task scheduling is available. You can schedule daily, weekly, or one-time tasks.")
            return True
        
        return False
    
    def process_input(self, user_input):
        """Main input processing pipeline with JARVIS intelligence"""
        print(f"\n🔍 JARVIS Processing: '{user_input}'")
        
        # TIER 0: Check for conversational input first
        if self.conversation_ai.is_conversational_input(user_input):
            success, response = self.conversation_ai.handle_conversation(user_input)
            if success:
                self.ai.speak(response)
                print(f"💬 {response}")
                return None
        
        # TIER 1: Enhanced command processing (modular system)
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
        
        if self.handle_vision_commands(user_input):
            return None
        
        if self.handle_memory_commands(user_input):
            return None
        
        if self.handle_application_launch(user_input):
            return None
            
        if self.handle_system_info_request(user_input):
            return None
        
        # TIER 2: Pattern matching (fast)
        command = self.match_pattern(user_input)
        if command:
            print(f"⚡ Fast match: {command}")
            self.ai.speak("Executing command")
            return command
        
        # TIER 3: AI generation (slower)
        print("🤖 JARVIS thinking...")
        self.ai.speak("Let me think about that")
        
        command = self.ai.generate_command(user_input, self.current_dir)
        if command:
            print(f"🧠 JARVIS generated: {command}")
            return command
        
        # TIER 4: Advanced AI processing
        advanced_response = self.ai.process_advanced_request(user_input, self.current_dir)
        if advanced_response:
            self.ai.speak("I understand. Let me handle that for you.")
            print(f"🎯 Advanced processing: {advanced_response}")
            return None
        
        # TIER 5: Assume it's a direct command
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
                    
                    # End session and cleanup
                    session_summary = self.memory.end_session()
                    self.task_scheduler.stop_scheduler()
                    
                    if session_summary:
                        print(f"📊 Session Summary: {session_summary['total_interactions']} interactions, {session_summary['success_rate']:.1f}% success rate")
                    
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
            # Process input and learn from interaction
            command = self.process_input(user_input)
            
            if not command:
                # Still learn from non-command interactions
                self.memory.remember_interaction(user_input, "Handled by specialized system", "system", True)
                self.learning_system.learn_from_interaction(user_input, "System handled", "system", True)
                continue
            
            # Safety check
            if self.is_dangerous_command(command):
                print(f"⚠️  DANGEROUS: {command}")
                self.ai.speak("This command could be dangerous. Please confirm.")
                confirm = input("Continue? (yes): ")
                if confirm.lower() != 'yes':
                    self.ai.speak("Command cancelled for safety.")
                    print("❌ Cancelled")
                    self.memory.remember_interaction(user_input, "Command cancelled for safety", "safety", False)
                    continue
            
            # Execute
            print(f"⚙️  Executing: {command}")
            result = self.system.execute_command(command)
            
            # Remember the interaction
            response = "Command executed successfully" if result['success'] else f"Command failed: {result.get('error', 'Unknown error')}"
            self.memory.remember_interaction(user_input, response, "command", result['success'])
            self.learning_system.learn_from_interaction(user_input, response, "command", result['success'])
        
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
