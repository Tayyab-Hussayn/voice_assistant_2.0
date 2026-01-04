import subprocess
import re
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
from modules.web_search import WebSearch
from modules.research_system import ResearchAnalysis
from modules.knowledge_base import KnowledgeManager
from modules.subagent_system import SubagentManager
from modules.task_management import TaskManagement
from modules.workflow_engine import WorkflowAutomation
from modules.aws_integration import AWSIntegration
from modules.infrastructure_management import InfrastructureIntegration
from modules.security_compliance import SecurityCompliance
from modules.memory_system import MemorySystem
from modules.context_manager import ContextManager
from modules.learning_system import LearningSystem
from modules.task_scheduler import TaskScheduler
from modules.feature_discovery import FeatureDiscovery
from modules.intent_classifier import IntentClassifier
from modules.workflow_engine import WorkflowEngine
from modules.window_manager import WindowManager
from modules.process_manager import ProcessManager
from modules.performance_monitor import PerformanceMonitor
from modules.process_manager import ProcessManager
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
        self.web_search = WebSearch()  # Web search integration (Tool 7)
        self.research = ResearchAnalysis(self.web_search, self.ai)  # Research system (Tool 9)
        self.knowledge = KnowledgeManager()  # Knowledge base (Tool 10)
        self.subagents = SubagentManager(self)  # Subagent system (Tool 13)
        self.tasks = TaskManagement()  # Task management (Tool 14)
        self.workflows = WorkflowAutomation(self)  # Workflow automation (Tool 15)
        self.aws = AWSIntegration()  # AWS CLI integration (Tool 16)
        self.infra = InfrastructureIntegration(self.aws.aws_manager)  # Infrastructure management (Tool 17)
        self.security = SecurityCompliance(self.aws.aws_manager)  # Security & compliance (Tool 18)
        
        # Phase 2: System Control & Automation (Complete)
        self.window_manager = WindowManager()  # Window management
        self.process_manager = ProcessManager()  # Process management
        
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
        
        # Mode management
        self.voice_mode = False  # Default: text chat mode
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
    
    def _is_task_request(self, user_input):
        """Detect if input is a natural language task request"""
        task_indicators = [
            'rename', 'move', 'copy', 'delete', 'remove', 'create', 'make',
            'go to', 'navigate', 'find', 'search for', 'list', 'show',
            'task:', 'execute:', 'i need you to', 'i want you to',
            'please', 'can you', 'directory', 'folder', 'file'
        ]
        
        user_lower = user_input.lower()
        return any(indicator in user_lower for indicator in task_indicators)
    
    def _process_intelligent_task(self, user_input):
        """Process natural language task with AI reasoning"""
        print("🧠 JARVIS analyzing task...")
        
        # Check if this is a workflow/tool task vs a file system task
        if self._is_workflow_task(user_input):
            return self._process_workflow_task(user_input)
        else:
            return self._process_command_task(user_input)
    
    def _is_workflow_task(self, user_input):
        """Detect if task requires workflow/tool operations vs file system commands"""
        workflow_indicators = [
            'research', 'analyze', 'knowledge base', 'store knowledge', 'create task',
            'workflow', 'agent', 'search web', 'compliance', 'security scan',
            'subagent', 'parallel', 'automation'
        ]
        
        user_lower = user_input.lower()
        return any(indicator in user_lower for indicator in workflow_indicators)
    
    def _process_workflow_task(self, user_input):
        """Process complex workflow task using JARVIS tools with REAL INTELLIGENCE"""
        print("🔄 JARVIS planning intelligent execution...")
        
        # CRITICAL FIX: Actually execute tasks instead of just creating workflows
        workflow_context = {}
        
        try:
            # CODE ANALYSIS INTELLIGENCE
            if any(word in user_input.lower() for word in ['analyze', 'codebase', 'code', 'functions', 'refactor', 'documentation']):
                return self._execute_code_analysis_task(user_input, workflow_context)
            
            # RESEARCH INTELLIGENCE  
            elif any(word in user_input.lower() for word in ['research', 'analyze', 'trends', 'developments', 'study', 'investigate']):
                return self._execute_research_task(user_input, workflow_context)
            
            # SECURITY INTELLIGENCE
            elif any(word in user_input.lower() for word in ['security', 'vulnerability', 'compliance', 'scan', 'audit']):
                return self._execute_security_task(user_input, workflow_context)
            
            # WEB DEVELOPMENT INTELLIGENCE
            elif any(word in user_input.lower() for word in ['create', 'build', 'develop', 'website', 'app', 'application']):
                return self._execute_development_task(user_input, workflow_context)
            
            # SYSTEM INTELLIGENCE
            elif any(word in user_input.lower() for word in ['system', 'process', 'monitor', 'optimize', 'performance']):
                return self._execute_system_task(user_input, workflow_context)
            
            # GENERAL INTELLIGENCE - Use AI reasoning for complex tasks
            else:
                return self._execute_intelligent_reasoning_task(user_input, workflow_context)
                
        except Exception as e:
            print(f"❌ Error in intelligent processing: {str(e)}")
            return f"❌ Error processing task: {str(e)}"
    
    def _execute_security_workflow(self, user_input, workflow_context):
        """Execute security-focused workflow"""
        print("🔒 JARVIS executing security workflow...")
        
        # Step 1: Security scan if requested
        if 'vulnerabilit' in user_input.lower() or 'scan' in user_input.lower():
            print("🔧 JARVIS scanning for security vulnerabilities...")
            # Scan both code and AWS security
            code_scan = self.security.scan_code(".")
            aws_scan = self.security.scan_aws()
            scan_result = f"Code scan completed. AWS scan completed."
            workflow_context['security_scan'] = scan_result
            workflow_context['code_scan_details'] = code_scan
            workflow_context['aws_scan_details'] = aws_scan
            print(f"✅ Security scan completed: {scan_result}")
        
        # Step 2: Compliance check if requested
        if 'compliance' in user_input.lower():
            print("🔧 JARVIS running compliance checks...")
            compliance_result = self.security.check_compliance("SOC2")
            workflow_context['compliance_check'] = compliance_result
            print(f"✅ Compliance check completed: {str(compliance_result)[:100]}...")
        
        # Step 3: Create tasks for issues found
        if 'task' in user_input.lower() or 'issues' in user_input.lower():
            issues_found = 0
            if 'security_scan' in workflow_context and 'vulnerabilities found' in workflow_context['security_scan'].lower():
                issues_found += 1
                task_result = self.tasks.add(
                    "Fix Security Vulnerabilities",
                    "Address security vulnerabilities found in codebase scan",
                    "high",
                    "security"
                )
                workflow_context['security_task'] = task_result
                print(f"✅ Security task created: {task_result}")
            
            if 'compliance_check' in workflow_context and 'non-compliant' in workflow_context['compliance_check'].lower():
                issues_found += 1
                task_result = self.tasks.add(
                    "Fix Compliance Issues",
                    "Address compliance violations found in security audit",
                    "high",
                    "compliance"
                )
                workflow_context['compliance_task'] = task_result
                print(f"✅ Compliance task created: {task_result}")
        
        # Step 4: Create security monitoring workflow
        if 'workflow' in user_input.lower() and 'monitor' in user_input.lower():
            print("🔧 JARVIS creating security monitoring workflow...")
            workflow_result = self.workflows.create(
                "Security Monitoring Workflow",
                "Automated security scanning and compliance monitoring",
                "security_monitoring"
            )
            workflow_context['monitoring_workflow'] = workflow_result
            print(f"✅ Security workflow created: {workflow_result}")
        
        # Step 5: Coordinate security agents
        if 'agent' in user_input.lower():
            print("🔧 JARVIS coordinating security agents...")
            agent_result = self.subagents.create_task(
                "security",
                scan_type="vulnerability",
                priority="high"
            )
            workflow_context['security_agent'] = agent_result
            print(f"✅ Security agent coordinated: {agent_result}")
        
        return self._summarize_workflow(workflow_context, "security")
    
    def _execute_research_workflow(self, user_input, workflow_context):
        """Execute research-focused workflow"""
        print("🔬 JARVIS executing research workflow...")
        
        # Step 1: Research if requested
        topic = self._extract_research_topic(user_input)
        if topic:
            print(f"🔧 JARVIS researching: {topic}")
            research_result = self.research.research(topic, "medium")
            workflow_context['research_content'] = research_result
            print(f"✅ Research completed: {len(research_result)} characters")
        
        # Step 2: Analyze if requested
        if 'analyze' in user_input.lower() and 'research_content' in workflow_context:
            print("🔧 JARVIS analyzing research findings...")
            analysis_result = self.research.analyze(workflow_context['research_content'], "summary")
            workflow_context['analysis'] = analysis_result
            print(f"✅ Analysis completed: {len(analysis_result)} characters")
        
        # Step 3: Store in knowledge base if requested
        if 'knowledge base' in user_input.lower() or 'store knowledge' in user_input.lower():
            content = workflow_context.get('analysis') or workflow_context.get('research_content', "Research results")
            topic = topic or "Research Task"
            print(f"🔧 JARVIS storing knowledge: {topic}")
            kb_result = self.knowledge.add(f"{topic} Research", content[:1000], "JARVIS Research", "research")
            workflow_context['kb_id'] = kb_result
            print(f"✅ Knowledge stored: {kb_result}")
        
        # Step 4: Create task if requested
        if 'create task' in user_input.lower() or 'task' in user_input.lower():
            topic = topic or "Research Documentation"
            print(f"🔧 JARVIS creating task: Document {topic}")
            task_result = self.tasks.add(
                f"Document {topic} Research",
                f"Create comprehensive documentation for {topic} research findings",
                "medium",
                "documentation"
            )
            workflow_context['task_id'] = task_result
            print(f"✅ Task created: {task_result}")
        
        # Step 5: Create workflow if requested
        if 'workflow' in user_input.lower() and 'automate' in user_input.lower():
            print("🔧 JARVIS creating automation workflow...")
            workflow_result = self.workflows.create(
                "Research Automation Workflow",
                "Automated workflow for research, analysis, and documentation tasks",
                "research_analysis"
            )
            workflow_context['workflow_id'] = workflow_result
            print(f"✅ Workflow created: {workflow_result}")
        
        # Step 6: Use subagents for parallel tasks if needed
        if 'agent' in user_input.lower():
            print("🔧 JARVIS coordinating research agents...")
            agent_result = self.subagents.create_task(
                "research",
                topic=topic or "General Research",
                priority="medium"
            )
            workflow_context['agent_task'] = agent_result
            print(f"✅ Research agent coordinated: {agent_result}")
        
        return self._summarize_workflow(workflow_context, "research")
    
    def _execute_general_workflow(self, user_input, workflow_context):
        """Execute general workflow tasks"""
        print("⚙️ JARVIS executing general workflow...")
        
        # Basic workflow steps based on keywords
        if 'task' in user_input.lower():
            task_result = self.tasks.add(
                "General Task",
                f"Task created from workflow: {user_input[:100]}",
                "medium",
                "general"
            )
            workflow_context['task_id'] = task_result
            print(f"✅ Task created: {task_result}")
        
        if 'workflow' in user_input.lower():
            workflow_result = self.workflows.create(
                "General Workflow",
                f"Workflow created from request: {user_input[:100]}",
                "general"
            )
            workflow_context['workflow_id'] = workflow_result
            print(f"✅ Workflow created: {workflow_result}")
        
        return self._summarize_workflow(workflow_context, "general")
    
    def _summarize_workflow(self, workflow_context, workflow_type):
        """Summarize workflow execution results"""
        completed_steps = len(workflow_context)
        if completed_steps > 0:
            self.ai.speak(f"{workflow_type.title()} workflow completed with {completed_steps} steps")
            summary = f"🎉 Intelligent {workflow_type} workflow completed! Executed {completed_steps} coordinated steps:"
            for key, value in workflow_context.items():
                summary += f"\n• {key}: {str(value)[:50]}..."
            print(summary)
            return "✅ Complex workflow execution completed successfully"
        else:
            return f"❌ No {workflow_type} workflow steps could be identified from the task."
    
    def _handle_mode_commands(self, user_input):
        """Handle voice/text mode switching commands"""
        user_lower = user_input.lower().strip()
        
        # Voice mode activation
        if any(phrase in user_lower for phrase in [
            'start voice mode', 'enable voice', 'switch to voice', 'voice mode on',
            'activate voice', 'turn on voice', 'voice chat'
        ]):
            self.voice_mode = True
            self.ai.speak("Voice mode activated. I'm now listening and speaking.")
            return "🎤 Voice mode activated - JARVIS will now listen and speak"
        
        # Voice mode deactivation  
        elif any(phrase in user_lower for phrase in [
            'stop voice mode', 'disable voice', 'switch to text', 'voice mode off',
            'deactivate voice', 'turn off voice', 'text chat', 'text mode'
        ]):
            self.voice_mode = False
            return "💬 Text chat mode activated - Type your messages"
        
        # Wake word mode (within voice mode)
        elif user_lower in ['wake', 'wake word', 'wake mode']:
            if self.voice_mode:
                self.wake_word_mode = True
                self.ai.speak("Wake word mode enabled. Say 'Hey JARVIS' to activate.")
                return "👂 Wake word mode enabled - Say 'Hey JARVIS'"
            else:
                return "❌ Wake word mode only available in voice mode"
        
        return None
    
    def _get_user_input(self):
        """Get user input based on current mode"""
        if self.voice_mode:
            if self.wake_word_mode:
                # Wait for wake word
                print("👂 Listening for 'Hey JARVIS'...")
                wake_detected = self.voice.wait_for_wake_word()
                if wake_detected:
                    self.ai.speak("Yes, I'm listening")
                    print("🎤 JARVIS activated - Listening...")
                    return self.voice.listen()
                return None
            else:
                # Direct voice input
                print("🎤 Voice mode - Speak your command...")
                return self.voice.listen()
        else:
            # Text chat mode
            return input("💬 JARVIS> ").strip()
    
    def _display_mode_status(self):
        """Display current mode status"""
        if self.voice_mode:
            mode_icon = "🎤"
            mode_text = "Voice Mode"
            if self.wake_word_mode:
                mode_text += " (Wake Word)"
        else:
            mode_icon = "💬"
            mode_text = "Text Chat Mode"
        
        print(f"\n{mode_icon} Current Mode: {mode_text}")
        return mode_text

    def _determine_action_type(self, user_input):
        """Determine the type of action from user input"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['research', 'analyze', 'study']):
            return "research"
        elif any(word in user_lower for word in ['security', 'vulnerability', 'compliance']):
            return "security"
        elif any(word in user_lower for word in ['workflow', 'automate', 'agent']):
            return "workflow"
        elif any(word in user_lower for word in ['task', 'todo', 'schedule']):
            return "task_management"
        elif any(word in user_lower for word in ['knowledge', 'store', 'remember']):
            return "knowledge"
        elif any(word in user_input for word in ['mv', 'cp', 'rm', 'mkdir', 'ls', 'cd']):
            return "file_system"
        elif user_input.startswith('/') or user_input.startswith('./'):
            return "command"
        else:
            return "general"
        """Determine the type of action from user input"""
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ['research', 'analyze', 'study']):
            return "research"
        elif any(word in user_lower for word in ['security', 'vulnerability', 'compliance']):
            return "security"
        elif any(word in user_lower for word in ['workflow', 'automate', 'agent']):
            return "workflow"
        elif any(word in user_lower for word in ['task', 'todo', 'schedule']):
            return "task_management"
        elif any(word in user_lower for word in ['knowledge', 'store', 'remember']):
            return "knowledge"
        elif any(word in user_input for word in ['mv', 'cp', 'rm', 'mkdir', 'ls', 'cd']):
            return "file_system"
        elif user_input.startswith('/') or user_input.startswith('./'):
            return "command"
        else:
            return "general"

    def _extract_research_topic(self, text):
        """Extract research topic from user input"""
        import re
        
        # Look for quoted topics first
        quoted_match = re.search(r'"([^"]+)"', text)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for "research X" patterns
        research_match = re.search(r'research\s+([^,\.]+)', text, re.IGNORECASE)
        if research_match:
            return research_match.group(1).strip()
        
        return None
    
    def _execute_tool_command(self, command):
        """Execute a tool command and return result"""
        try:
            # Temporarily disable performance monitoring for internal calls
            if command.startswith('research '):
                topic = command[9:].strip().strip('"')
                return self.research.research(topic, "medium")
            elif command.startswith('quick_research '):
                topic = command[15:].strip().strip('"')
                return self.research.quick_research(topic)
            elif command.startswith('kb_add '):
                parts = command[7:].strip().split('"')
                if len(parts) >= 4:
                    title, content = parts[1], parts[3]
                    source = parts[5] if len(parts) > 5 else ""
                    category = parts[7] if len(parts) > 7 else "general"
                    return self.knowledge.add(title, content, source, category)
            elif command.startswith('kb_search '):
                query = command[10:].strip().strip('"')
                return self.knowledge.search(query)
            elif command.startswith('task_add '):
                parts = command[9:].strip().split('"')
                if len(parts) >= 4:
                    title, description = parts[1], parts[3]
                    remaining = parts[4].strip().split() if len(parts) > 4 else []
                    priority = remaining[0] if remaining else "medium"
                    category = remaining[1] if len(remaining) > 1 else "general"
                    return self.tasks.add(title, description, priority, category)
            elif command.startswith('agent_task '):
                parts = command[11:].strip().split()
                if len(parts) >= 2:
                    task_type = parts[0]
                    kwargs = {}
                    for part in parts[1:]:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            kwargs[key] = value.strip('"')
                    return self.subagents.create_task(task_type, **kwargs)
            elif command.startswith('workflow_create '):
                parts = command[16:].strip().split('"')
                if len(parts) >= 2:
                    name = parts[1]
                    description = parts[3] if len(parts) > 3 else ""
                    template = parts[4].strip() if len(parts) > 4 else None
                    return self.workflows.create(name, description, template)
            elif command.startswith('web_search '):
                query = command[11:].strip().strip('"')
                result = self.web_search.search(query)
                return f"🌐 Found {result.get('num_results', 0)} results" if result.get('success') else f"❌ Search failed"
            elif command.startswith('analyze '):
                parts = command[8:].strip().split('"')
                if len(parts) >= 2:
                    content = parts[1]
                    analysis_type = parts[2].strip() if len(parts) > 2 else "summary"
                    return self.research.analyze(content, analysis_type)
            
            return f"❌ Unknown tool command: {command}"
            
        except Exception as e:
            return f"❌ Tool execution error: {str(e)}"
    
    def _process_command_task(self, user_input):
        """Process file system command task"""

    def process_input(self, user_input):
        """Main input processing pipeline with intelligent intent classification"""
        print(f"\n🔍 JARVIS Processing: '{user_input}'")
        
        # Start performance monitoring
        operation_data = self.performance_monitor.start_operation("process_input")
        
        try:
            # Phase 2: System Control & Automation Commands (High Priority)
            if (user_input.startswith('list windows') or user_input.startswith('show windows') or
                user_input.startswith('list processes') or user_input.startswith('show processes') or
                user_input.startswith('system stats') or user_input.startswith('system status') or
                user_input.startswith('close window ') or user_input.startswith('focus window ') or
                user_input.startswith('kill process ') or user_input.startswith('launch ') or 
                user_input.startswith('start ')):
                
                if user_input.startswith('list windows') or user_input.startswith('show windows'):
                    result = self.window_manager.list_windows()
                    if result['success']:
                        windows = result['windows']
                        if windows:
                            response = f"🪟 Found {len(windows)} open windows:\n"
                            for w in windows[:10]:  # Show first 10
                                response += f"• {w.get('title', 'Untitled')} ({w.get('class', 'Unknown')})\n"
                        else:
                            response = "🪟 No windows found"
                    else:
                        response = f"❌ Window listing failed: {result['error']}"
                    
                    self.performance_monitor.end_operation(operation_data, success=result['success'])
                    return response
                
                elif user_input.startswith('list processes') or user_input.startswith('show processes'):
                    filter_name = None
                    if ' ' in user_input and len(user_input.split()) > 2:
                        filter_name = user_input.split(None, 2)[2]
                    
                    result = self.process_manager.list_processes(filter_name)
                    if result['success']:
                        processes = result['processes'][:10]  # Show top 10
                        response = f"🔄 Top {len(processes)} processes"
                        if filter_name:
                            response += f" matching '{filter_name}'"
                        response += ":\n"
                        for p in processes:
                            response += f"• {p['name']} (PID: {p['pid']}) - CPU: {p['cpu_percent']:.1f}%\n"
                    else:
                        response = f"❌ Process listing failed: {result['error']}"
                    
                    self.performance_monitor.end_operation(operation_data, success=result['success'])
                    return response
                
                elif user_input.startswith('system stats') or user_input.startswith('system status'):
                    result = self.process_manager.get_system_stats()
                    if result['success']:
                        stats = result['stats']
                        response = f"📊 System Statistics:\n"
                        response += f"• CPU: {stats['cpu_percent']:.1f}%\n"
                        response += f"• Memory: {stats['memory']['percent']:.1f}% ({stats['memory']['used']//1024//1024//1024}GB used)\n"
                        response += f"• Disk: {stats['disk']['percent']:.1f}% ({stats['disk']['used']//1024//1024//1024}GB used)\n"
                        response += f"• Processes: {stats['process_count']}"
                    else:
                        response = f"❌ System stats failed: {result['error']}"
                    
                    self.performance_monitor.end_operation(operation_data, success=result['success'])
                    return response
            
            # Handle special commands first
            if user_input.startswith('/'):
                result = self.handle_special_commands(user_input)
                self.performance_monitor.end_operation(operation_data, success=True)
                return result
            
            # Enhanced intelligent task processing
            if self._is_task_request(user_input):
                result = self._process_intelligent_task(user_input)
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
            
            # Phase 2: System Control & Automation Commands
            elif user_input.startswith('list windows') or user_input.startswith('show windows'):
                result = self.window_manager.list_windows()
                if result['success']:
                    windows = result['windows']
                    if windows:
                        response = f"🪟 Found {len(windows)} open windows:\n"
                        for w in windows[:10]:  # Show first 10
                            response += f"• {w.get('title', 'Untitled')} ({w.get('class', 'Unknown')})\n"
                    else:
                        response = "🪟 No windows found"
                else:
                    response = f"❌ Window listing failed: {result['error']}"
                
                self.performance_monitor.end_operation(operation_data, success=result['success'])
                return response
            
            elif user_input.startswith('close window '):
                window_id = user_input[13:].strip()
                result = self.window_manager.close_window(window_id)
                response = f"✅ Window closed" if result['success'] else f"❌ {result['error']}"
                self.performance_monitor.end_operation(operation_data, success=result['success'])
                return response
            
            elif user_input.startswith('focus window '):
                window_id = user_input[13:].strip()
                result = self.window_manager.focus_window(window_id)
                response = f"✅ Window focused" if result['success'] else f"❌ {result['error']}"
                self.performance_monitor.end_operation(operation_data, success=result['success'])
                return response
            
            elif user_input.startswith('list processes') or user_input.startswith('show processes'):
                filter_name = None
                if ' ' in user_input and len(user_input.split()) > 2:
                    filter_name = user_input.split(None, 2)[2]
                
                result = self.process_manager.list_processes(filter_name)
                if result['success']:
                    processes = result['processes'][:10]  # Show top 10
                    response = f"🔄 Top {len(processes)} processes:\n"
                    for p in processes:
                        response += f"• {p['name']} (PID: {p['pid']}) - CPU: {p['cpu_percent']:.1f}%\n"
                else:
                    response = f"❌ Process listing failed: {result['error']}"
                
                self.performance_monitor.end_operation(operation_data, success=result['success'])
                return response
            
            elif user_input.startswith('kill process '):
                target = user_input[13:].strip()
                force = 'force' in user_input.lower()
                
                try:
                    pid = int(target)
                    result = self.process_manager.kill_process(pid, force)
                except ValueError:
                    result = self.process_manager.kill_process_by_name(target, force)
                
                response = f"✅ {result.get('message', 'Process killed')}" if result['success'] else f"❌ {result['error']}"
                self.performance_monitor.end_operation(operation_data, success=result['success'])
                return response
            
            elif user_input.startswith('launch ') or user_input.startswith('start '):
                app_name = user_input.split(None, 1)[1] if len(user_input.split()) > 1 else ""
                if app_name:
                    result = self.process_manager.launch_application(app_name)
                    response = f"✅ {result.get('message', 'Application launched')}" if result['success'] else f"❌ {result['error']}"
                else:
                    response = "❌ Please specify an application name"
                    result = {'success': False}
                
                self.performance_monitor.end_operation(operation_data, success=result['success'])
                return response
            
            elif user_input.startswith('system stats') or user_input.startswith('system status'):
                result = self.process_manager.get_system_stats()
                if result['success']:
                    stats = result['stats']
                    response = f"📊 System Statistics:\n"
                    response += f"• CPU: {stats['cpu_percent']:.1f}%\n"
                    response += f"• Memory: {stats['memory']['percent']:.1f}% ({stats['memory']['used']//1024//1024//1024}GB used)\n"
                    response += f"• Disk: {stats['disk']['percent']:.1f}% ({stats['disk']['used']//1024//1024//1024}GB used)\n"
                    response += f"• Processes: {stats['process_count']}"
                else:
                    response = f"❌ System stats failed: {result['error']}"
                
                self.performance_monitor.end_operation(operation_data, success=result['success'])
                return response
            
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
            
            elif user_input.startswith('web_search '):
                # Web search: web_search "Python tutorials"
                query = user_input[11:].strip().strip('"')
                
                result = self.web_search.search(query)
                
                if result["success"]:
                    if result["results"]:
                        response = f"🌐 Found {result['num_results']} results for '{query}':\n\n"
                        
                        for i, res in enumerate(result["results"], 1):
                            response += f"{i}. {res['title']}\n"
                            response += f"   {res['snippet'][:100]}...\n"
                            response += f"   🔗 {res['domain']}\n\n"
                        
                        response += f"Search completed in {result['search_time']:.2f}s"
                        
                        self.ai.speak(f"Found {result['num_results']} search results")
                        return response
                    else:
                        self.ai.speak("No search results found")
                        return "🔍 No results found for your search query"
                else:
                    self.ai.speak("Search failed")
                    return f"❌ Search failed: {result['error']}"
            
            elif user_input.startswith('web_fetch '):
                # Web content fetcher: web_fetch <url> [mode] [search_terms]
                parts = user_input[10:].strip().split()
                if not parts:
                    return "❌ Usage: web_fetch <url> [selective|truncated|full] [search_terms]"
                
                url = parts[0]
                mode = parts[1] if len(parts) > 1 else "selective"
                search_terms = " ".join(parts[2:]) if len(parts) > 2 else None
                
                result = self.web_search.search_system.fetch_content(url, mode, search_terms)
                
                if result["success"]:
                    response = f"📄 Content from {result['title']}\n"
                    response += f"🔗 {result['url']}\n"
                    response += f"📝 Mode: {result['mode']}\n\n"
                    response += result['content']
                    
                    if result.get('truncated'):
                        response += "\n\n⚠️ Content was truncated"
                    
                    self.ai.speak("Content fetched successfully")
                    return response
                else:
                    self.ai.speak("Failed to fetch content")
                    return f"❌ {result['error']}"
            
            elif user_input.startswith('quick_search '):
                # Quick search with formatted response: quick_search "AI news"
                query = user_input[13:].strip().strip('"')
                
                response = self.web_search.quick_search(query)
                self.ai.speak("Search completed")
                self.performance_monitor.end_operation(operation_data, success=True)
                return response
            
            elif user_input.startswith('research '):
                # Research command: research "AI development" [quick|medium|deep]
                parts = user_input[9:].strip().split()
                if not parts:
                    return "❌ Usage: research <topic> [quick|medium|deep]"
                
                topic = parts[0].strip('"')
                depth = parts[1] if len(parts) > 1 else "medium"
                
                response = self.research.research(topic, depth)
                self.ai.speak("Research completed")
                return response
            
            elif user_input.startswith('quick_research '):
                # Quick research: quick_research "Python tutorials"
                topic = user_input[15:].strip().strip('"')
                
                response = self.research.quick_research(topic)
                self.ai.speak("Quick research completed")
                return response
            
            elif user_input.startswith('analyze '):
                # Content analysis: analyze "content" [summary|keywords|sentiment|structure]
                parts = user_input[8:].strip().split('"')
                if len(parts) < 2:
                    return "❌ Usage: analyze \"content\" [summary|keywords|sentiment|structure]"
                
                content = parts[1]
                analysis_type = parts[2].strip() if len(parts) > 2 else "summary"
                
                response = self.research.analyze(content, analysis_type)
                self.ai.speak("Analysis completed")
                return response
            
            elif user_input.startswith('kb_add '):
                # Add knowledge: kb_add "title" "content" [source] [category]
                parts = user_input[7:].strip().split('"')
                if len(parts) < 4:
                    return "❌ Usage: kb_add \"title\" \"content\" [source] [category]"
                
                title = parts[1]
                content = parts[3]
                source = parts[5] if len(parts) > 5 else ""
                category = parts[7] if len(parts) > 7 else "general"
                
                response = self.knowledge.add(title, content, source, category)
                self.ai.speak("Knowledge added")
                return response
            
            elif user_input.startswith('kb_search '):
                # Search knowledge: kb_search "query"
                query = user_input[10:].strip().strip('"')
                
                response = self.knowledge.search(query)
                self.ai.speak("Knowledge search completed")
                return response
            
            elif user_input.startswith('kb_get '):
                # Get knowledge entry: kb_get 123
                try:
                    entry_id = int(user_input[7:].strip())
                    response = self.knowledge.get(entry_id)
                    self.ai.speak("Knowledge retrieved")
                    return response
                except ValueError:
                    return "❌ Usage: kb_get <entry_id>"
            
            elif user_input == 'kb_stats':
                # Knowledge base statistics
                response = self.knowledge.stats()
                self.ai.speak("Knowledge statistics ready")
                return response
            
            elif user_input.startswith('kb_update '):
                # Update knowledge: kb_update 123 title="New Title" content="New Content"
                parts = user_input[10:].strip().split()
                if not parts:
                    return "❌ Usage: kb_update <id> [title=\"...\"] [content=\"...\"] [source=\"...\"] [category=\"...\"]"
                
                try:
                    entry_id = int(parts[0])
                    kwargs = {}
                    
                    # Parse key=value pairs
                    for part in parts[1:]:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            kwargs[key] = value.strip('"')
                    
                    response = self.knowledge.update(entry_id, **kwargs)
                    self.ai.speak("Knowledge updated")
                    return response
                except ValueError:
                    return "❌ Invalid entry ID"
            
            elif user_input.startswith('kb_delete '):
                # Delete knowledge: kb_delete 123
                try:
                    entry_id = int(user_input[10:].strip())
                    response = self.knowledge.delete(entry_id)
                    self.ai.speak("Knowledge deleted")
                    return response
                except ValueError:
                    return "❌ Usage: kb_delete <entry_id>"
            
            elif user_input.startswith('kb_list'):
                # List knowledge: kb_list [category]
                parts = user_input[7:].strip().split()
                category = parts[0] if parts else None
                
                response = self.knowledge.list_entries(category)
                self.ai.speak("Knowledge list ready")
                return response
            
            elif user_input == 'kb_categories':
                # List categories
                response = self.knowledge.categories()
                self.ai.speak("Categories ready")
                return response
            
            elif user_input.startswith('kb_export'):
                # Export knowledge: kb_export [category]
                parts = user_input[9:].strip().split()
                category = parts[0] if parts else None
                
                response = self.knowledge.export_knowledge(category)
                self.ai.speak("Knowledge exported")
                return response
            
            elif user_input.startswith('kb_import '):
                # Import knowledge: kb_import filename.json
                filename = user_input[10:].strip()
                
                response = self.knowledge.import_knowledge(filename)
                self.ai.speak("Knowledge imported")
                return response
            
            elif user_input == 'kb_backup':
                # Create backup
                response = self.knowledge.backup()
                self.ai.speak("Backup created")
                return response
            
            elif user_input.startswith('kb_semantic '):
                # Semantic search: kb_semantic "query" [threshold]
                parts = user_input[12:].strip().split()
                if not parts:
                    return "❌ Usage: kb_semantic \"query\" [threshold]"
                
                query = parts[0].strip('"')
                threshold = float(parts[1]) if len(parts) > 1 else 0.1
                
                response = self.knowledge.semantic_search(query, threshold)
                self.ai.speak("Semantic search completed")
                return response
            
            elif user_input == 'kb_analyze':
                # Knowledge graph analysis
                response = self.knowledge.analyze_knowledge_graph()
                self.ai.speak("Knowledge analysis ready")
                return response
            
            elif user_input.startswith('kb_related '):
                # Find related entries: kb_related 123
                try:
                    entry_id = int(user_input[11:].strip())
                    response = self.knowledge.find_related(entry_id)
                    self.ai.speak("Related entries found")
                    return response
                except ValueError:
                    return "❌ Usage: kb_related <entry_id>"
            
            elif user_input == 'kb_insights':
                # Knowledge insights
                response = self.knowledge.knowledge_insights()
                self.ai.speak("Knowledge insights ready")
                return response
            
            elif user_input.startswith('agent_task '):
                # Create subagent task: agent_task search query="Python programming"
                parts = user_input[11:].strip().split()
                if len(parts) < 2:
                    return "❌ Usage: agent_task <type> <param>=<value> ..."
                
                task_type = parts[0]
                kwargs = {}
                
                for part in parts[1:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        kwargs[key] = value.strip('"')
                
                response = self.subagents.create_task(task_type, **kwargs)
                self.ai.speak("Subagent task created")
                return response
            
            elif user_input.startswith('agent_status '):
                # Get task status: agent_status abc123
                task_id = user_input[13:].strip()
                
                response = self.subagents.task_status(task_id)
                self.ai.speak("Task status ready")
                return response
            
            elif user_input.startswith('agent_result '):
                # Get task result: agent_result abc123
                task_id = user_input[13:].strip()
                
                response = self.subagents.task_result(task_id)
                self.ai.speak("Task result ready")
                return response
            
            elif user_input.startswith('agent_workflow '):
                # Create parallel workflow: agent_workflow "search:query=AI" "research:topic=ML"
                tasks = user_input[15:].strip().split('" "')
                tasks = [task.strip('"') for task in tasks]
                
                response = self.subagents.parallel_workflow(*tasks)
                self.ai.speak("Parallel workflow created")
                return response
            
            elif user_input.startswith('workflow_status '):
                # Get workflow status: workflow_status def456
                workflow_id = user_input[16:].strip()
                
                response = self.subagents.workflow_status(workflow_id)
                self.ai.speak("Workflow status ready")
                return response
            
            elif user_input == 'agent_system':
                # Get system status
                response = self.subagents.system_status()
                self.ai.speak("System status ready")
                return response
            
            elif user_input.startswith('task_add '):
                # Add task: task_add "title" "description" priority category due_date
                parts = user_input[9:].strip().split('"')
                if len(parts) < 2:
                    return "❌ Usage: task_add \"title\" [\"description\"] [priority] [category] [due_date]"
                
                title = parts[1]
                description = parts[3] if len(parts) > 3 else ""
                remaining = parts[4].strip().split() if len(parts) > 4 else []
                
                priority = remaining[0] if remaining else "medium"
                category = remaining[1] if len(remaining) > 1 else "general"
                due_date = remaining[2] if len(remaining) > 2 else None
                
                response = self.tasks.add(title, description, priority, category, due_date)
                self.ai.speak("Task added")
                return response
            
            elif user_input.startswith('task_list'):
                # List tasks: task_list [status] [category]
                parts = user_input[9:].strip().split()
                status = parts[0] if parts else None
                category = parts[1] if len(parts) > 1 else None
                
                response = self.tasks.list_tasks(status, category)
                self.ai.speak("Task list ready")
                return response
            
            elif user_input.startswith('task_complete '):
                # Complete task: task_complete 123
                try:
                    task_id = int(user_input[14:].strip())
                    response = self.tasks.complete(task_id)
                    self.ai.speak("Task completed")
                    return response
                except ValueError:
                    return "❌ Usage: task_complete <task_id>"
            
            elif user_input.startswith('task_update '):
                # Update task: task_update 123 status=in_progress priority=high
                parts = user_input[12:].strip().split()
                if not parts:
                    return "❌ Usage: task_update <task_id> <field>=<value> ..."
                
                try:
                    task_id = int(parts[0])
                    kwargs = {}
                    
                    for part in parts[1:]:
                        if '=' in part:
                            key, value = part.split('=', 1)
                            kwargs[key] = value
                    
                    response = self.tasks.update(task_id, **kwargs)
                    self.ai.speak("Task updated")
                    return response
                except ValueError:
                    return "❌ Invalid task ID"
            
            elif user_input.startswith('task_delete '):
                # Delete task: task_delete 123
                try:
                    task_id = int(user_input[12:].strip())
                    response = self.tasks.delete(task_id)
                    self.ai.speak("Task deleted")
                    return response
                except ValueError:
                    return "❌ Usage: task_delete <task_id>"
            
            elif user_input == 'task_dashboard':
                # Task dashboard
                response = self.tasks.dashboard()
                self.ai.speak("Task dashboard ready")
                return response
            
            elif user_input.startswith('task_due'):
                # Tasks due soon: task_due [days]
                parts = user_input[8:].strip().split()
                days = int(parts[0]) if parts else 7
                
                response = self.tasks.due_soon(days)
                self.ai.speak("Due tasks ready")
                return response
            
            elif user_input.startswith('workflow_create '):
                # Create workflow: workflow_create "name" "description" [template]
                parts = user_input[16:].strip().split('"')
                if len(parts) < 2:
                    return "❌ Usage: workflow_create \"name\" [\"description\"] [template]"
                
                name = parts[1]
                description = parts[3] if len(parts) > 3 else ""
                template = parts[4].strip() if len(parts) > 4 else None
                
                response = self.workflows.create(name, description, template)
                self.ai.speak("Workflow created")
                return response
            
            elif user_input.startswith('workflow_add_step '):
                # Add workflow step: workflow_add_step wf_123 search query="AI"
                parts = user_input[18:].strip().split()
                if len(parts) < 2:
                    return "❌ Usage: workflow_add_step <workflow_id> <step_type> <param>=<value> ..."
                
                workflow_id = parts[0]
                step_type = parts[1]
                kwargs = {}
                
                for part in parts[2:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        kwargs[key] = value.strip('"')
                
                response = self.workflows.add_step(workflow_id, step_type, **kwargs)
                self.ai.speak("Workflow step added")
                return response
            
            elif user_input.startswith('workflow_execute '):
                # Execute workflow: workflow_execute wf_123 topic="AI development"
                parts = user_input[17:].strip().split()
                if not parts:
                    return "❌ Usage: workflow_execute <workflow_id> [var=value] ..."
                
                workflow_id = parts[0]
                kwargs = {}
                
                for part in parts[1:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        kwargs[key] = value.strip('"')
                
                response = self.workflows.execute(workflow_id, **kwargs)
                self.ai.speak("Workflow started")
                return response
            
            elif user_input.startswith('workflow_status '):
                # Get workflow status: workflow_status wf_123
                workflow_id = user_input[16:].strip()
                
                response = self.workflows.status(workflow_id)
                self.ai.speak("Workflow status ready")
                return response
            
            elif user_input == 'workflow_list':
                # List workflows
                response = self.workflows.list_workflows()
                self.ai.speak("Workflow list ready")
                return response
            
            elif user_input == 'workflow_templates':
                # List workflow templates
                response = self.workflows.templates()
                self.ai.speak("Workflow templates ready")
                return response
            
            elif user_input == 'aws_status':
                # AWS CLI status
                response = self.aws.status()
                self.ai.speak("AWS status ready")
                return response
            
            elif user_input == 'aws_s3':
                # List S3 buckets
                response = self.aws.s3_buckets()
                self.ai.speak("S3 buckets ready")
                return response
            
            elif user_input.startswith('aws_ec2'):
                # List EC2 instances: aws_ec2 [region]
                parts = user_input[7:].strip().split()
                region = parts[0] if parts else None
                
                response = self.aws.ec2_instances(region)
                self.ai.speak("EC2 instances ready")
                return response
            
            elif user_input.startswith('aws_lambda'):
                # List Lambda functions: aws_lambda [region]
                parts = user_input[10:].strip().split()
                region = parts[0] if parts else None
                
                response = self.aws.lambda_functions(region)
                self.ai.speak("Lambda functions ready")
                return response
            
            elif user_input == 'aws_iam':
                # List IAM users
                response = self.aws.iam_users()
                self.ai.speak("IAM users ready")
                return response
            
            elif user_input.startswith('aws_vpc'):
                # List VPCs: aws_vpc [region]
                parts = user_input[7:].strip().split()
                region = parts[0] if parts else None
                
                response = self.aws.vpcs(region)
                self.ai.speak("VPCs ready")
                return response
            
            elif user_input.startswith('aws_cf'):
                # List CloudFormation stacks: aws_cf [region]
                parts = user_input[6:].strip().split()
                region = parts[0] if parts else None
                
                response = self.aws.cloudformation_stacks(region)
                self.ai.speak("CloudFormation stacks ready")
                return response
            
            elif user_input.startswith('aws_rds'):
                # List RDS instances: aws_rds [region]
                parts = user_input[7:].strip().split()
                region = parts[0] if parts else None
                
                response = self.aws.rds_instances(region)
                self.ai.speak("RDS instances ready")
                return response
            
            elif user_input.startswith('aws_cmd '):
                # Custom AWS command: aws_cmd service operation param=value
                parts = user_input[8:].strip().split()
                if len(parts) < 2:
                    return "❌ Usage: aws_cmd <service> <operation> [param=value] ..."
                
                service = parts[0]
                operation = parts[1]
                kwargs = {}
                
                for part in parts[2:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        kwargs[key] = value
                
                response = self.aws.execute_custom(service, operation, **kwargs)
                self.ai.speak("AWS command completed")
                return response
            
            elif user_input == 'infra_templates':
                # List infrastructure templates
                response = self.infra.list_templates()
                self.ai.speak("Infrastructure templates ready")
                return response
            
            elif user_input.startswith('infra_template '):
                # Get template details: infra_template simple_s3
                template_id = user_input[15:].strip()
                
                response = self.infra.get_template(template_id)
                self.ai.speak("Template details ready")
                return response
            
            elif user_input.startswith('infra_deploy '):
                # Deploy template: infra_deploy simple_s3 my-stack BucketName=my-bucket
                parts = user_input[13:].strip().split()
                if len(parts) < 2:
                    return "❌ Usage: infra_deploy <template_id> <stack_name> [param=value] ..."
                
                template_id = parts[0]
                stack_name = parts[1]
                kwargs = {}
                
                for part in parts[2:]:
                    if '=' in part:
                        key, value = part.split('=', 1)
                        kwargs[key] = value
                
                response = self.infra.deploy(template_id, stack_name, **kwargs)
                self.ai.speak("Infrastructure deployment initiated")
                return response
            
            elif user_input.startswith('infra_status '):
                # Get stack status: infra_status my-stack
                stack_name = user_input[13:].strip()
                
                response = self.infra.stack_status(stack_name)
                self.ai.speak("Stack status ready")
                return response
            
            elif user_input.startswith('infra_delete '):
                # Delete stack: infra_delete my-stack
                stack_name = user_input[13:].strip()
                
                response = self.infra.delete_stack(stack_name)
                self.ai.speak("Stack deletion initiated")
                return response
            
            elif user_input == 'infra_deployments':
                # List deployments
                response = self.infra.list_deployments()
                self.ai.speak("Deployments ready")
                return response
            
            elif user_input.startswith('infra_terraform '):
                # Generate Terraform: infra_terraform simple_s3
                template_id = user_input[16:].strip()
                
                response = self.infra.generate_terraform(template_id)
                self.ai.speak("Terraform configuration ready")
                return response
            
            elif user_input.startswith('security_scan_aws'):
                # Scan AWS security: security_scan_aws [region]
                parts = user_input[18:].strip().split()
                region = parts[0] if parts else None
                
                response = self.security.scan_aws(region)
                self.ai.speak("AWS security scan completed")
                return response
            
            elif user_input.startswith('security_scan_code '):
                # Scan code security: security_scan_code file.py
                file_path = user_input[19:].strip()
                
                response = self.security.scan_code(file_path)
                self.ai.speak("Code security scan completed")
                return response
            
            elif user_input.startswith('security_compliance'):
                # Check compliance: security_compliance [framework]
                parts = user_input[19:].strip().split()
                framework = parts[0] if parts else "cis_aws"
                
                response = self.security.check_compliance(framework)
                self.ai.speak("Compliance check completed")
                return response
            
            elif user_input.startswith('security_report'):
                # Generate security report: security_report [scan_id]
                parts = user_input[15:].strip().split()
                scan_id = parts[0] if parts else None
                
                response = self.security.security_report(scan_id)
                self.ai.speak("Security report ready")
                return response
            
            elif user_input == 'security_history':
                # Security scan history
                response = self.security.scan_history()
                self.ai.speak("Security history ready")
                return response
            
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
        
        # Display initial mode
        self._display_mode_status()
        
        print("\n💡 Mode Commands:")
        print("• 'start voice mode' - Switch to voice interaction")
        print("• 'text mode' - Switch to text chat")
        print("• 'wake' - Enable wake word (voice mode only)")
        print("• 'exit' - Quit JARVIS\n")
        
        self.ai.speak("JARVIS online and ready to assist you!")
        
        try:
            while True:
                try:
                    # Get input based on current mode
                    user_input = self._get_user_input()
                    
                    if not user_input:
                        continue
                    
                    # Handle exit command
                    if user_input.lower() == 'exit':
                        if self.voice_mode:
                            self.ai.speak("Goodbye! JARVIS signing off.")
                        print("👋 JARVIS offline")
                        
                        # End session and cleanup
                        session_summary = self.memory.end_session()
                        self.task_scheduler.stop_scheduler()
                        
                        if session_summary:
                            print(f"📊 Session Summary: {session_summary['total_interactions']} interactions, {session_summary['success_rate']:.1f}% success rate")
                        break
                    
                    # Check for mode switching commands first
                    mode_result = self._handle_mode_commands(user_input)
                    if mode_result:
                        print(mode_result)
                        continue
                    
                    # Process the input
                    result = self.process_input(user_input)
                    
                    if result:
                        # Determine if the operation was successful
                        success = not (result.startswith('❌') or 'Error:' in result or 'failed' in result.lower() or result.startswith('⚠️'))
                        action_type = self._determine_action_type(user_input)
                        
                        # Record interaction in memory system
                        self.memory.remember_interaction(user_input, result, action_type, success)
                        self.learning_system.learn_from_interaction(user_input, result, action_type, success)
                        
                        # Output result based on mode
                        if self.voice_mode and success:
                            # Speak successful results in voice mode
                            self.ai.speak("Task completed successfully")
                        
                        print(result)
                        continue
                    
                    # Fallback to treating as direct command
                    command = user_input
                    
                    if not command:
                        # Still learn from non-command interactions
                        self.memory.remember_interaction(user_input, "Handled by specialized system", "system", True)
                        self.learning_system.learn_from_interaction(user_input, "System handled", "system", True)
                        continue
                    
                    # Safety check
                    if self.is_dangerous_command(command):
                        warning_msg = f"⚠️  DANGEROUS: {command}"
                        print(warning_msg)
                        
                        if self.voice_mode:
                            self.ai.speak("This command could be dangerous. Please confirm.")
                            # In voice mode, get voice confirmation
                            print("🎤 Say 'yes' to confirm or anything else to cancel...")
                            confirm = self.voice.listen()
                        else:
                            confirm = input("Continue? (yes): ")
                        
                        if not confirm or confirm.lower() != 'yes':
                            cancel_msg = "❌ Cancelled for safety"
                            if self.voice_mode:
                                self.ai.speak("Command cancelled for safety.")
                            print(cancel_msg)
                            self.memory.remember_interaction(user_input, "Command cancelled for safety", "safety", False)
                            continue
                    
                    # Execute
                    print(f"⚙️  Executing: {command}")
                    result = self.system.execute_command(command)
                    
                    # Remember the interaction
                    response = "Command executed successfully" if result['success'] else f"Command failed: {result.get('error', 'Unknown error')}"
                    self.memory.remember_interaction(user_input, response, "command", result['success'])
                    self.learning_system.learn_from_interaction(user_input, response, "command", result['success'])
                    
                    # Voice feedback for command execution
                    if self.voice_mode:
                        if result['success']:
                            self.ai.speak("Command executed successfully")
                        else:
                            self.ai.speak("Command failed")
                
                    print("\n" + "-"*60)
                    
                    if result['success']:
                        if result['output']:
                            print(result['output'])
                    else:
                        print(f"❌ Error: {result['error']}")
                        if self.voice_mode:
                            self.ai.speak(f"I encountered an error while executing that command.")
                        print(f"\n🤖 JARVIS: I encountered an error while executing that command.")
                        
                except KeyboardInterrupt:
                    if self.voice_mode:
                        self.ai.speak("Interrupted. Switching to text mode.")
                    print("\n⚠️ Interrupted - Switching to text mode")
                    self.voice_mode = False
                    self.wake_word_mode = False
                    continue
                    
        except Exception as e:
            error_msg = f"❌ Critical error: {str(e)}"
            print(error_msg)
            if self.voice_mode:
                self.ai.speak("Critical error occurred. Shutting down.")
            
        finally:
            # Cleanup
            if hasattr(self, 'task_scheduler'):
                self.task_scheduler.stop_scheduler()

if __name__ == "__main__":
    jarvis = JARVIS()
    jarvis.run()
