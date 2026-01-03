import subprocess
from pathlib import Path
from modules.voice_input import VoiceInput
from modules.ai_handler import AIHandler
from modules.system_controller import SystemController
from modules.command_processor import CommandProcessor
from modules.conversational_ai import ConversationalAI
from modules.intelligent_web_builder import IntelligentWebBuilder
from modules.file_system_manager import FileSystemManager
from modules.search_system import SearchSystem
from modules.pattern_matcher import PatternMatcher
from modules.lsp_manager import CodeIntelligence
from modules.memory_system import MemorySystem
from modules.context_manager import ContextManager
from modules.learning_system import LearningSystem
from modules.task_scheduler import TaskScheduler
from modules.feature_discovery import FeatureDiscovery
from modules.intent_classifier import IntentClassifier
from modules.workflow_engine import WorkflowEngine
from modules.performance_monitor import PerformanceMonitor
from modules.error_handler import ErrorHandler
from modules.intelligent_workflow_engine import IntelligentWorkflowEngine
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
        self.file_manager = FileSystemManager()  # Enhanced file system manager (Tool 1)
        self.search_system = SearchSystem()  # Advanced search system (Tool 2)
        self.pattern_matcher = PatternMatcher()  # Pattern matching system (Tool 3)
        self.code_intelligence = CodeIntelligence()  # LSP integration foundation (Tool 4)
        
        # Phase 4: Intelligence & Memory System
        self.memory = MemorySystem()  # Long-term memory
        self.context_manager = ContextManager(self.memory)  # Context switching
        self.learning_system = LearningSystem(self.memory)  # Learning from interactions
        self.task_scheduler = TaskScheduler(self)  # Task scheduling
        
        # Start scheduler
        self.task_scheduler.start_scheduler()
        
        # Initialize feature discovery for self-awareness
        self.feature_discovery = FeatureDiscovery(self)
        
        # Initialize intent classifier for smart command/question detection
        self.intent_classifier = IntentClassifier(self.ai)
        
        # Phase 5: Advanced Workflow Automation & Polish
        self.workflow_engine = WorkflowEngine(self)  # Basic workflow automation
        self.intelligent_workflow = IntelligentWorkflowEngine(self)  # Intelligent agentic workflows
        self.performance_monitor = PerformanceMonitor()  # Performance tracking
        self.error_handler = ErrorHandler(self)  # Error handling and recovery
        
        # Update conversational AI with feature awareness and memory
        self.conversation_ai.feature_discovery = self.feature_discovery
        self.conversation_ai.memory_system = self.memory
        
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
                
                # Check if it's a name
                if "my name is" in info.lower():
                    name = info.lower().replace("my name is", "").strip()
                    self.memory.store_knowledge("user_info", "name", name)
                    self.ai.speak(f"I'll remember that your name is {name}")
                else:
                    self.memory.store_knowledge("user_info", "custom", info)
                    self.ai.speak(f"I'll remember that {info}")
                return True
        
        elif "my name is" in user_input.lower():
            # Direct name introduction
            parts = user_input.lower().split("my name is", 1)
            if len(parts) > 1:
                name = parts[1].strip().title()  # Capitalize properly
                self.memory.store_knowledge("user_info", "name", name)
                self.ai.speak(f"Nice to meet you, {name}! I'll remember your name.")
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
        
        elif "workflow" in user_input:
            if "create" in user_input and "development" in user_input:
                # Extract project name
                words = user_input.split()
                project_name = "MyProject"
                for i, word in enumerate(words):
                    if word in ["for", "called", "named"] and i + 1 < len(words):
                        project_name = words[i + 1]
                        break
                
                workflow_id = self.workflow_engine.create_development_workflow(project_name)
                self.ai.speak(f"Created development workflow for {project_name}")
                return True
            
            elif "run" in user_input or "execute" in user_input:
                # Extract workflow name
                if "daily startup" in user_input:
                    # Create and run daily startup workflow
                    workflow_id = self.workflow_engine.create_daily_startup_workflow()
                    success, result = self.workflow_engine.execute_workflow(workflow_id)
                    if success:
                        print(result["message"])
                    return True
                else:
                    self.ai.speak("Please specify which workflow to run")
                    return True
            
            elif "list" in user_input:
                workflows = self.workflow_engine.list_workflows()
                if workflows:
                    self.ai.speak(f"You have {len(workflows)} workflows available")
                    for wf in workflows:
                        print(f"- {wf['name']}: {wf['description']}")
                else:
                    self.ai.speak("No workflows created yet")
                return True
        
        elif "research" in user_input and ("deep" in user_input or "comprehensive" in user_input):
            # Extract research topic
            topic = user_input.replace("deep research", "").replace("comprehensive research", "").replace("research", "").strip()
            if not topic:
                topic = input("What would you like me to research? ").strip()
            
            if topic:
                self.ai.speak(f"Creating intelligent research workflow for {topic}")
                workflow_id = self.intelligent_workflow.generate_research_workflow(topic, "comprehensive")
                
                if workflow_id:
                    self.ai.speak("Research workflow created. Starting automatic execution.")
                    success, result = self.intelligent_workflow.execute_intelligent_workflow(workflow_id)
                    if success:
                        print(f"\n🎯 {result['message']}")
                else:
                    self.ai.speak("Could not create research workflow")
                return True
        
        return False
    
    def handle_special_commands(self, command):
        """Handle special /commands"""
        cmd = command.lower().strip()
        
        if cmd == '/features':
            feature_tree = self.feature_discovery.get_feature_tree()
            print(feature_tree)
            self.ai.speak("Here are all my capabilities. Check the display for the complete list.")
            return None
        
        elif cmd == '/status':
            status = self.feature_discovery.get_feature_status()
            print("\n🔧 JARVIS System Status:")
            print("=" * 30)
            for component, state in status.items():
                print(f"{component}: {state}")
            self.ai.speak("System status displayed. All major components are active.")
            return None
        
        elif cmd == '/capabilities':
            summary = self.feature_discovery.get_capability_summary()
            print(summary)
            self.ai.speak("Here's a summary of my capabilities")
            return None
        
        elif cmd == '/help':
            help_text = """
🤖 JARVIS Special Commands:
/features    - Show all capabilities in tree format
/status      - Show system component status  
/capabilities - Show capability summary
/performance - Show performance metrics
/workflows   - List all workflows
/workflow create [name] - Create interactive workflow
/health      - Show system health status
/help        - Show this help message

🧠 Intelligent Workflow Features:
• "Deep research on [topic]" - Auto-generates research workflow
• "Comprehensive research [topic]" - Creates and runs research workflow
• Ctrl+M during workflow - Modify workflow steps in real-time
• Ctrl+P during workflow - Pause/resume workflow execution

Voice Commands Examples:
• "Create a website for my restaurant"
• "Deep research on artificial intelligence"
• "Remember that I like coffee"
• "Switch context to work"
• "Run workflow daily startup"
• "/workflow create MyWorkflow"
"""
            print(help_text)
            self.ai.speak("Help information displayed. I now have intelligent workflows with real-time modification and tool integration.")
            return None
        
        elif cmd == '/performance':
            summary = self.performance_monitor.get_performance_summary()
            print(summary)
            self.ai.speak("Performance metrics displayed. Check the screen for detailed statistics.")
            return None
        
        elif cmd == '/workflows':
            workflows = self.workflow_engine.list_workflows()
            if workflows:
                print("\n🔄 Available Workflows:")
                print("=" * 30)
                for wf in workflows:
                    status = "✅ Active" if wf["active"] else "❌ Inactive"
                    print(f"{wf['name']} ({wf['id']}) - {status}")
                    print(f"  Steps: {wf['steps']} | Runs: {wf['run_count']}")
                    print(f"  Description: {wf['description']}")
                    print()
                self.ai.speak(f"Found {len(workflows)} workflows. Check the display for details.")
            else:
                print("No workflows created yet.")
                self.ai.speak("No workflows found. You can create workflows for automated task sequences.")
            return None
        
        elif cmd == '/health':
            health = self.error_handler.get_health_status()
            error_stats = self.error_handler.get_error_statistics()
            print(f"\n🏥 JARVIS Health Status: {health}")
            if "error_types" in error_stats:
                print("\nError Summary:")
                for error_type, count in error_stats["error_types"].items():
                    print(f"  {error_type}: {count} occurrences")
        elif cmd.startswith('/workflow create'):
            # Extract workflow name
            parts = cmd.split(' ', 2)
            if len(parts) >= 3:
                workflow_name = parts[2]
                workflow_id = self.intelligent_workflow.create_interactive_workflow(workflow_name)
                if workflow_id:
                    self.ai.speak(f"Interactive workflow {workflow_name} created successfully")
                else:
                    self.ai.speak("Workflow creation cancelled")
            else:
                workflow_name = input("Enter workflow name: ").strip()
                if workflow_name:
                    workflow_id = self.intelligent_workflow.create_interactive_workflow(workflow_name)
                    if workflow_id:
                        self.ai.speak(f"Interactive workflow {workflow_name} created successfully")
            return None
        
        elif cmd == '/stop' or cmd == '/cancel':
            # Stop current running process
            result = self.system.stop_current_process()
            if result["success"]:
                print(f"✅ {result['message']}")
                self.ai.speak("Process stopped successfully")
            else:
                print(f"❌ {result['error']}")
                self.ai.speak("No process to stop or failed to stop process")
            return None
        
        else:
            print(f"Unknown command: {command}")
            print("Available commands: /features, /status, /capabilities, /help, /stop, /cancel")
            return None
    
    def process_input(self, user_input):
        """Main input processing pipeline with intelligent intent classification"""
        print(f"\n🔍 JARVIS Processing: '{user_input}'")
        
        # Start performance monitoring
        operation_data = self.performance_monitor.start_operation("process_input")
        
        try:
            # Handle special commands first
            if user_input.startswith('/'):
                result = self.handle_special_commands(user_input)
                self.performance_monitor.end_operation(operation_data, success=True)
                return result
            
            # Enhanced file system operations (Tool 1)
            elif user_input.startswith('fs_write '):
                # Parse fs_write command: fs_write create /path/to/file "content"
                parts = user_input.split(' ', 2)
                if len(parts) >= 3:
                    command = parts[1]
                    remaining = parts[2]
                    
                    if command == "create":
                        # Parse: create /path/to/file "content"
                        if '"' in remaining:
                            path_part, content_part = remaining.split('"', 1)
                            path = path_part.strip()
                            content = content_part.rstrip('"')
                            result = self.file_manager.fs_write("create", path, file_text=content)
                            if result["success"]:
                                self.ai.speak(f"Created file {Path(path).name}")
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return f"✅ {result['summary']}"
                            else:
                                self.performance_monitor.end_operation(operation_data, success=False)
                                return f"❌ {result['error']}"
                    elif command == "append":
                        # Parse: append /path/to/file "content"
                        if '"' in remaining:
                            path_part, content_part = remaining.split('"', 1)
                            path = path_part.strip()
                            content = content_part.rstrip('"')
                            result = self.file_manager.fs_write("append", path, new_str=content)
                            if result["success"]:
                                self.ai.speak(f"Appended to file {Path(path).name}")
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return f"✅ {result['summary']}"
                            else:
                                self.performance_monitor.end_operation(operation_data, success=False)
                                return f"❌ {result['error']}"
                
                self.performance_monitor.end_operation(operation_data, success=False)
                return "❌ Invalid fs_write command format"
            
            elif user_input.startswith('glob '):
                # Parse glob command: glob "*.py" or glob "**/*.js" --limit=50
                parts = user_input[5:].strip()
                
                if parts.startswith('"'):
                    end_quote = parts.find('"', 1)
                    if end_quote != -1:
                        pattern = parts[1:end_quote]
                        remaining = parts[end_quote+1:].strip()
                        
                        # Parse options
                        kwargs = {}
                        if '--limit=' in remaining:
                            try:
                                limit_start = remaining.find('--limit=') + 8
                                limit_end = remaining.find(' ', limit_start)
                                if limit_end == -1:
                                    limit_end = len(remaining)
                                kwargs['limit'] = int(remaining[limit_start:limit_end])
                            except ValueError:
                                pass
                        
                        if '--max-depth=' in remaining:
                            try:
                                depth_start = remaining.find('--max-depth=') + 12
                                depth_end = remaining.find(' ', depth_start)
                                if depth_end == -1:
                                    depth_end = len(remaining)
                                kwargs['max_depth'] = int(remaining[depth_start:depth_end])
                            except ValueError:
                                pass
                        
                        # Use enhanced pattern matcher
                        result = self.pattern_matcher.glob(pattern, **kwargs)
                        
                        if result["success"]:
                            files = result["filePaths"]
                            if files:
                                file_list = "\n".join(f"• {file}" for file in files[:10])
                                if result["truncated"]:
                                    file_list += f"\n... and {result['totalFiles'] - 10} more files"
                                self.ai.speak(f"Found {result['totalFiles']} files matching pattern")
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return f"📁 Found {result['totalFiles']} files:\n{file_list}"
                            else:
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return f"📁 No files found matching pattern: {pattern}"
                        else:
                            self.performance_monitor.end_operation(operation_data, success=False)
                            return f"❌ {result['error']}"
                    else:
                        self.performance_monitor.end_operation(operation_data, success=False)
                        return "❌ Invalid glob command: missing closing quote"
                else:
                    # Try without quotes for simple patterns
                    pattern = parts.split()[0] if parts else ""
                    if pattern:
                        result = self.pattern_matcher.glob(pattern)
                        if result["success"]:
                            files = result["filePaths"]
                            if files:
                                file_list = "\n".join(f"• {file}" for file in files[:10])
                                if result["truncated"]:
                                    file_list += f"\n... and {result['totalFiles'] - 10} more files"
                                self.ai.speak(f"Found {result['totalFiles']} files matching pattern")
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return f"📁 Found {result['totalFiles']} files:\n{file_list}"
                            else:
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return f"📁 No files found matching pattern: {pattern}"
                        else:
                            self.performance_monitor.end_operation(operation_data, success=False)
                            return f"❌ {result['error']}"
                    else:
                        self.performance_monitor.end_operation(operation_data, success=False)
                        return "❌ Invalid glob command: no pattern specified"
            
            elif user_input.startswith('find_files '):
                # Find files only: find_files "*.py"
                pattern = user_input[11:].strip().strip('"')
                result = self.pattern_matcher.find_files(pattern)
                
                if result["success"]:
                    files = result["filePaths"]
                    if files:
                        file_list = "\n".join(f"• {file}" for file in files[:10])
                        if result["truncated"]:
                            file_list += f"\n... and {result['totalFiles'] - 10} more files"
                        self.ai.speak(f"Found {result['totalFiles']} files")
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return f"📄 Found {result['totalFiles']} files:\n{file_list}"
                    else:
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return f"📄 No files found matching pattern: {pattern}"
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return f"❌ {result['error']}"
            
            elif user_input.startswith('find_dirs '):
                # Find directories only: find_dirs "*test*"
                pattern = user_input[10:].strip().strip('"')
                result = self.pattern_matcher.find_directories(pattern)
                
                if result["success"]:
                    dirs = result["filePaths"]
                    if dirs:
                        dir_list = "\n".join(f"• {dir}" for dir in dirs[:10])
                        if result["truncated"]:
                            dir_list += f"\n... and {result['totalFiles'] - 10} more directories"
                        self.ai.speak(f"Found {result['totalFiles']} directories")
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return f"📁 Found {result['totalFiles']} directories:\n{dir_list}"
                    else:
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return f"📁 No directories found matching pattern: {pattern}"
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return f"❌ {result['error']}"
            
            elif user_input.startswith('code_init'):
                # Initialize code intelligence: code_init or code_init --force
                force = '--force' in user_input
                
                result = self.code_intelligence.initialize_workspace(".", force)
                
                if result["initialized_servers"]:
                    server_names = [info["name"] for info in result["initialized_servers"].values()]
                    self.ai.speak(f"Code intelligence initialized for {len(server_names)} languages")
                    
                    response = f"🧠 Code Intelligence Initialized\n"
                    response += f"📁 Workspace: {Path(result['workspace']).name}\n"
                    response += f"🔍 Languages: {', '.join(result['detected_languages'])}\n"
                    response += f"✅ Servers: {', '.join(server_names)}\n"
                    
                    if result["unavailable_servers"]:
                        unavailable = list(result["unavailable_servers"].keys())
                        response += f"❌ Unavailable: {', '.join(unavailable)}"
                    
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return response
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return "❌ No language servers could be initialized"
            
            elif user_input.startswith('code_status'):
                # Show code intelligence status
                if not self.code_intelligence.is_ready():
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return "🧠 Code intelligence not initialized. Use 'code_init' to initialize."
                
                status = self.code_intelligence.get_status()
                
                response = f"🧠 Code Intelligence Status\n"
                response += f"📁 Workspace: {Path(status['workspace_root']).name}\n"
                response += f"🔧 Active Servers:\n"
                
                for lang, info in status["active_servers"].items():
                    status_icon = "✅" if info["initialized"] else "🔄"
                    response += f"  {status_icon} {info['name']} ({lang})\n"
                
                self.performance_monitor.end_operation(operation_data, success=True)
                return response
            
            elif user_input.startswith('search_symbols '):
                # Search for symbols: search_symbols "UserService"
                symbol_name = user_input[15:].strip().strip('"')
                
                result = self.code_intelligence.search_symbols(symbol_name)
                
                if result.get("success"):
                    symbols = result["symbols"]
                    if symbols:
                        symbol_list = []
                        for symbol in symbols[:5]:
                            file_name = Path(symbol["location"]["file"]).name
                            symbol_list.append(f"• {symbol['name']} at {file_name}:{symbol['location']['line']}")
                        
                        response = f"🔍 Found {len(symbols)} symbols:\n" + "\n".join(symbol_list)
                        if len(symbols) > 5:
                            response += f"\n... and {len(symbols) - 5} more"
                        
                        self.ai.speak(f"Found {len(symbols)} symbols")
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return response
                    else:
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return f"🔍 No symbols found for: {symbol_name}"
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return f"❌ {result['error']}"
            
            elif user_input.startswith('goto_definition '):
                # Go to definition: goto_definition file.py 42 10
                parts = user_input[16:].strip().split()
                if len(parts) >= 3:
                    file_path, line_str, char_str = parts[0], parts[1], parts[2]
                    try:
                        line = int(line_str)
                        character = int(char_str)
                        
                        result = self.code_intelligence.goto_definition(file_path, line, character)
                        
                        if result.get("success"):
                            loc = result["location"]
                            file_name = Path(loc["file"]).name
                            response = f"📍 Definition: {file_name}:{loc['line']}:{loc['character']}"
                            
                            self.ai.speak(f"Found definition in {file_name}")
                            self.performance_monitor.end_operation(operation_data, success=True)
                            return response
                        else:
                            self.performance_monitor.end_operation(operation_data, success=False)
                            return f"❌ {result['error']}"
                    except ValueError:
                        self.performance_monitor.end_operation(operation_data, success=False)
                        return "❌ Invalid line or character number"
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return "❌ Usage: goto_definition <file> <line> <character>"
            
            elif user_input.startswith('find_references '):
                # Find references: find_references file.py 42 10
                parts = user_input[16:].strip().split()
                if len(parts) >= 3:
                    file_path, line_str, char_str = parts[0], parts[1], parts[2]
                    try:
                        line = int(line_str)
                        character = int(char_str)
                        
                        result = self.code_intelligence.find_references(file_path, line, character)
                        
                        if result.get("success"):
                            refs = result["references"]
                            if refs:
                                ref_list = []
                                for ref in refs[:5]:
                                    file_name = Path(ref["file"]).name
                                    ref_list.append(f"• {file_name}:{ref['line']}:{ref['character']}")
                                
                                response = f"🔗 Found {len(refs)} references:\n" + "\n".join(ref_list)
                                if len(refs) > 5:
                                    response += f"\n... and {len(refs) - 5} more"
                                
                                self.ai.speak(f"Found {len(refs)} references")
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return response
                            else:
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return "🔗 No references found"
                        else:
                            self.performance_monitor.end_operation(operation_data, success=False)
                            return f"❌ {result['error']}"
                    except ValueError:
                        self.performance_monitor.end_operation(operation_data, success=False)
                        return "❌ Invalid line or character number"
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return "❌ Usage: find_references <file> <line> <character>"
            
            elif user_input.startswith('document_symbols '):
                # Get document symbols: document_symbols file.py
                file_path = user_input[17:].strip()
                
                result = self.code_intelligence.get_document_symbols(file_path)
                
                if result.get("success"):
                    symbols = result["symbols"]
                    if symbols:
                        symbol_list = []
                        for symbol in symbols[:10]:
                            symbol_list.append(f"• {symbol['name']} (line {symbol['line']})")
                        
                        response = f"📋 Found {len(symbols)} symbols in {Path(file_path).name}:\n" + "\n".join(symbol_list)
                        if len(symbols) > 10:
                            response += f"\n... and {len(symbols) - 10} more"
                        
                        self.ai.speak(f"Found {len(symbols)} symbols in file")
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return response
                    else:
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return f"📋 No symbols found in {Path(file_path).name}"
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return f"❌ {result['error']}"
            
            elif user_input.startswith('get_diagnostics '):
                # Get diagnostics: get_diagnostics file.py
                file_path = user_input[16:].strip()
                
                result = self.code_intelligence.get_diagnostics(file_path)
                
                if result.get("success"):
                    diagnostics = result["diagnostics"]
                    if diagnostics:
                        diag_list = []
                        for diag in diagnostics[:5]:
                            severity_map = {1: "Error", 2: "Warning", 3: "Info", 4: "Hint"}
                            severity = severity_map.get(diag["severity"], "Unknown")
                            diag_list.append(f"• {severity} line {diag['line']}: {diag['message']}")
                        
                        response = f"🔍 Found {len(diagnostics)} diagnostics in {Path(file_path).name}:\n" + "\n".join(diag_list)
                        if len(diagnostics) > 5:
                            response += f"\n... and {len(diagnostics) - 5} more"
                        
                        self.ai.speak(f"Found {len(diagnostics)} diagnostics")
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return response
                    else:
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return f"✅ No diagnostics found in {Path(file_path).name}"
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return f"❌ {result['error']}"
            
            elif user_input.startswith('rename_symbol '):
                # Rename symbol: rename_symbol file.py 42 10 newName --dry-run
                parts = user_input[14:].strip().split()
                if len(parts) >= 4:
                    file_path, line_str, char_str, new_name = parts[0], parts[1], parts[2], parts[3]
                    dry_run = '--dry-run' in user_input
                    
                    try:
                        line = int(line_str)
                        character = int(char_str)
                        
                        result = self.code_intelligence.rename_symbol(file_path, line, character, new_name, dry_run)
                        
                        if result.get("success"):
                            if dry_run:
                                response = f"🔄 Dry run: {result['message']}"
                            else:
                                response = f"✏️ Renamed symbol in {result['changes']} locations"
                                if result.get("files_modified"):
                                    file_names = [Path(f).name for f in result["files_modified"][:3]]
                                    response += f"\nFiles: {', '.join(file_names)}"
                                    if len(result["files_modified"]) > 3:
                                        response += f" and {len(result['files_modified']) - 3} more"
                            
                            self.ai.speak("Symbol rename completed" if not dry_run else "Dry run completed")
                            self.performance_monitor.end_operation(operation_data, success=True)
                            return response
                        else:
                            self.performance_monitor.end_operation(operation_data, success=False)
                            return f"❌ {result['error']}"
                    except ValueError:
                        self.performance_monitor.end_operation(operation_data, success=False)
                        return "❌ Invalid line or character number"
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return "❌ Usage: rename_symbol <file> <line> <character> <new_name> [--dry-run]"
            
            elif user_input.startswith('grep '):
                # Parse grep command: grep "pattern" or grep "pattern" --include="*.py"
                parts = user_input[5:].strip()
                
                # Extract pattern (first quoted string)
                if parts.startswith('"'):
                    end_quote = parts.find('"', 1)
                    if end_quote != -1:
                        pattern = parts[1:end_quote]
                        remaining = parts[end_quote+1:].strip()
                        
                        # Parse additional options
                        kwargs = {}
                        if '--include=' in remaining:
                            include_start = remaining.find('--include=') + 10
                            if remaining[include_start] == '"':
                                include_end = remaining.find('"', include_start + 1)
                                if include_end != -1:
                                    kwargs['include'] = remaining[include_start+1:include_end]
                        
                        if '--case-sensitive' in remaining:
                            kwargs['case_sensitive'] = True
                        
                        # Perform search
                        result = self.search_system.grep(pattern, **kwargs)
                        
                        if result["success"]:
                            if result["numMatches"] > 0:
                                matches_text = f"Found {result['numMatches']} matches in {result['numFiles']} files"
                                if result["truncated"]:
                                    matches_text += " (truncated)"
                                
                                # Show first few matches
                                match_details = []
                                for match in result["results"][:5]:
                                    if "file" in match and "line" in match:
                                        file_name = Path(match["file"]).name
                                        match_details.append(f"• {file_name}:{match['line']} - {match['content'][:60]}...")
                                
                                response = f"🔍 {matches_text}\n" + "\n".join(match_details)
                                if len(result["results"]) > 5:
                                    response += f"\n... and {len(result['results']) - 5} more matches"
                                
                                self.ai.speak(f"Found {result['numMatches']} matches")
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return response
                            else:
                                self.performance_monitor.end_operation(operation_data, success=True)
                                return f"🔍 No matches found for pattern: {pattern}"
                        else:
                            self.performance_monitor.end_operation(operation_data, success=False)
                            return f"❌ Search failed"
                    else:
                        self.performance_monitor.end_operation(operation_data, success=False)
                        return "❌ Invalid grep command: missing closing quote"
                else:
                    self.performance_monitor.end_operation(operation_data, success=False)
                    return "❌ Invalid grep command: pattern must be quoted"
            
            # TIER 0: Classify user intent
            intent = self.intent_classifier.classify_intent(user_input)
            print(f"🎯 Intent detected: {intent}")
            
            # Handle based on intent
            if intent == 'conversation':
                # Pure conversational input
                success, response = self.conversation_ai.handle_conversation(user_input)
                if success:
                    self.ai.speak(response)
                    print(f"💬 {response}")
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return None
            
            elif intent == 'question':
                # User is asking a question - prioritize conversational response
                success, response = self.conversation_ai.handle_conversation(user_input)
                if success:
                    self.ai.speak(response)
                    print(f"❓ {response}")
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return None
                else:
                    # Fallback to AI for complex questions
                    print("🤖 JARVIS thinking about your question...")
                    self.ai.speak("Let me think about that question")
                    advanced_response = self.ai.process_advanced_request(user_input, self.current_dir)
                    if advanced_response:
                        self.ai.speak("Here's what I found")
                        print(f"🎯 {advanced_response}")
                        self.performance_monitor.end_operation(operation_data, success=True)
                        return None
            
            elif intent == 'command':
                # User wants to execute a command - prioritize action
                print("⚙️ Processing as command...")
                
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
                    self.performance_monitor.end_operation(operation_data, success=success)
                    return None
                
                # Handle special JARVIS requests
                if self.handle_memory_commands(user_input):
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return None
                
                if self.handle_web_project_request(user_input):
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return None
                
                if self.handle_vision_commands(user_input):
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return None
                
                if self.handle_application_launch(user_input):
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return None
                    
                if self.handle_system_info_request(user_input):
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return None
                
                # TIER 2: Pattern matching (fast)
                command = self.match_pattern(user_input)
                if command:
                    print(f"⚡ Fast match: {command}")
                    self.ai.speak("Executing command")
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return command
                
                # TIER 3: AI generation (slower)
                print("🤖 JARVIS generating command...")
                self.ai.speak("Let me generate that command")
                
                command = self.ai.generate_command(user_input, self.current_dir)
                if command:
                    print(f"🧠 JARVIS generated: {command}")
                    self.performance_monitor.end_operation(operation_data, success=True)
                    return command
                
                # TIER 4: Assume it's a direct command
                print("📝 Treating as direct command")
                self.performance_monitor.end_operation(operation_data, success=True)
                return user_input
            
            # Fallback for unclassified input
            self.performance_monitor.end_operation(operation_data, success=True)
            return user_input
            
        except Exception as e:
            # Handle errors gracefully
            error_result = self.error_handler.handle_error(e, "process_input", user_input)
            self.ai.speak(error_result["user_message"])
            print(f"❌ {error_result['user_message']}")
            self.performance_monitor.end_operation(operation_data, success=False, error=error_result["error_type"])
            return None
    
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
