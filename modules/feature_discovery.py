import inspect
from pathlib import Path

class FeatureDiscovery:
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.features = {}
        self.discover_features()
    
    def discover_features(self):
        """Automatically discover all JARVIS capabilities"""
        self.features = {
            "core": {
                "name": "Core System",
                "description": "Essential JARVIS functionality",
                "capabilities": []
            },
            "intelligence": {
                "name": "Intelligence & Memory",
                "description": "Learning, memory, and context management",
                "capabilities": []
            },
            "automation": {
                "name": "Automation & Control",
                "description": "System control and task automation",
                "capabilities": []
            },
            "development": {
                "name": "Development Tools",
                "description": "Web development and coding assistance",
                "capabilities": []
            },
            "interaction": {
                "name": "User Interaction",
                "description": "Voice, vision, and communication",
                "capabilities": []
            }
        }
        
        # Discover core capabilities
        if hasattr(self.jarvis, 'ai') and self.jarvis.ai:
            self.features["core"]["capabilities"].extend([
                "Natural Language Processing (Minimax M2.1)",
                "Text-to-Speech Communication",
                "Command Generation and Execution"
            ])
        
        # Discover intelligence capabilities
        if hasattr(self.jarvis, 'memory') and self.jarvis.memory:
            self.features["intelligence"]["capabilities"].extend([
                "Long-term Memory Storage",
                "Interaction History Tracking",
                "Knowledge Base Management",
                "User Preference Learning"
            ])
        
        if hasattr(self.jarvis, 'context_manager') and self.jarvis.context_manager:
            self.features["intelligence"]["capabilities"].extend([
                "Context Switching",
                "Context Variable Management",
                "Multi-project Context Support"
            ])
        
        if hasattr(self.jarvis, 'learning_system') and self.jarvis.learning_system:
            self.features["intelligence"]["capabilities"].extend([
                "Pattern Recognition",
                "Success Rate Tracking",
                "Usage Analytics",
                "Adaptive Learning"
            ])
        
        # Discover automation capabilities
        if hasattr(self.jarvis, 'system') and self.jarvis.system:
            self.features["automation"]["capabilities"].extend([
                "System Command Execution",
                "Application Management",
                "File System Operations"
            ])
        
        if hasattr(self.jarvis, 'command_processor') and self.jarvis.command_processor:
            self.features["automation"]["capabilities"].extend([
                "Window Management (Hyprland)",
                "Process Control",
                "System Monitoring"
            ])
        
        if hasattr(self.jarvis, 'task_scheduler') and self.jarvis.task_scheduler:
            self.features["automation"]["capabilities"].extend([
                "Task Scheduling",
                "Automated Reminders",
                "Background Task Execution"
            ])
        
        # Discover development capabilities
        if hasattr(self.jarvis, 'web_developer') and self.jarvis.web_developer:
            self.features["development"]["capabilities"].extend([
                "Intelligent Web Page Generation",
                "Custom HTML/CSS/JS Creation",
                "Multi-template Support",
                "Automatic Browser Integration"
            ])
        
        # Discover interaction capabilities
        if hasattr(self.jarvis, 'voice') and self.jarvis.voice:
            self.features["interaction"]["capabilities"].extend([
                "Speech Recognition",
                "Wake Word Detection",
                "Voice Command Processing"
            ])
        
        if hasattr(self.jarvis, 'conversation_ai') and self.jarvis.conversation_ai:
            self.features["interaction"]["capabilities"].extend([
                "Natural Conversation",
                "Personality Responses",
                "Context-aware Dialogue"
            ])
        
        if hasattr(self.jarvis, 'computer_vision') and self.jarvis.computer_vision:
            self.features["interaction"]["capabilities"].extend([
                "Computer Vision",
                "Hand Gesture Recognition",
                "Screen Analysis",
                "Screenshot Capture"
            ])
        
        # Check for web search capability
        try:
            from modules import web_search
            self.features["intelligence"]["capabilities"].append("Web Search Integration")
        except ImportError:
            pass
    
    def get_feature_tree(self):
        """Generate a tree structure of all features"""
        tree = "🤖 JARVIS Capabilities Overview\n"
        tree += "=" * 50 + "\n\n"
        
        for category_id, category in self.features.items():
            if not category["capabilities"]:
                continue
                
            tree += f"📁 {category['name']}\n"
            tree += f"   {category['description']}\n"
            tree += "   " + "─" * 40 + "\n"
            
            for i, capability in enumerate(category["capabilities"]):
                prefix = "├──" if i < len(category["capabilities"]) - 1 else "└──"
                tree += f"   {prefix} {capability}\n"
            
            tree += "\n"
        
        return tree
    
    def get_capability_summary(self):
        """Get a summary of capabilities for AI context"""
        summary = "JARVIS Capabilities Summary:\n"
        
        all_capabilities = []
        for category in self.features.values():
            all_capabilities.extend(category["capabilities"])
        
        summary += f"Total Capabilities: {len(all_capabilities)}\n\n"
        
        for category_id, category in self.features.items():
            if category["capabilities"]:
                summary += f"{category['name']}: {', '.join(category['capabilities'][:3])}"
                if len(category["capabilities"]) > 3:
                    summary += f" and {len(category['capabilities']) - 3} more"
                summary += "\n"
        
        return summary
    
    def can_perform(self, task_description):
        """Check if JARVIS can perform a specific task"""
        task_lower = task_description.lower()
        
        # Web development tasks
        if any(word in task_lower for word in ["website", "webpage", "html", "css", "web"]):
            return hasattr(self.jarvis, 'web_developer') and self.jarvis.web_developer
        
        # Memory tasks
        if any(word in task_lower for word in ["remember", "recall", "memory", "learn"]):
            return hasattr(self.jarvis, 'memory') and self.jarvis.memory
        
        # System tasks
        if any(word in task_lower for word in ["open", "launch", "system", "file", "process"]):
            return hasattr(self.jarvis, 'system') and self.jarvis.system
        
        # Vision tasks
        if any(word in task_lower for word in ["screenshot", "vision", "gesture", "camera"]):
            return hasattr(self.jarvis, 'computer_vision') and self.jarvis.computer_vision
        
        # Scheduling tasks
        if any(word in task_lower for word in ["schedule", "remind", "task", "automate"]):
            return hasattr(self.jarvis, 'task_scheduler') and self.jarvis.task_scheduler
        
        # Context tasks
        if any(word in task_lower for word in ["context", "switch", "project"]):
            return hasattr(self.jarvis, 'context_manager') and self.jarvis.context_manager
        
        return True  # Default to yes for general tasks
    
    def suggest_capability(self, user_input):
        """Suggest which capability to use for a given input"""
        suggestions = []
        
        input_lower = user_input.lower()
        
        # Web development suggestions
        if any(word in input_lower for word in ["create", "build", "make"]) and any(word in input_lower for word in ["website", "page", "web"]):
            if hasattr(self.jarvis, 'web_developer'):
                suggestions.append("Use Web Development capability to create custom websites")
        
        # Memory suggestions
        if any(word in input_lower for word in ["remember", "save", "store"]):
            if hasattr(self.jarvis, 'memory'):
                suggestions.append("Use Memory System to store and recall information")
        
        # Search suggestions
        if any(word in input_lower for word in ["search", "find", "look up", "what is"]):
            suggestions.append("Use Web Search to find current information")
        
        # System suggestions
        if any(word in input_lower for word in ["open", "launch", "start", "run"]):
            if hasattr(self.jarvis, 'system'):
                suggestions.append("Use System Control to manage applications and files")
        
        return suggestions
    
    def get_feature_status(self):
        """Get status of all features"""
        status = {}
        
        # Check each major component
        components = [
            ('ai', 'AI Engine'),
            ('memory', 'Memory System'),
            ('context_manager', 'Context Manager'),
            ('learning_system', 'Learning System'),
            ('task_scheduler', 'Task Scheduler'),
            ('web_developer', 'Web Developer'),
            ('voice', 'Voice Input'),
            ('conversation_ai', 'Conversation AI'),
            ('computer_vision', 'Computer Vision'),
            ('system', 'System Controller'),
            ('command_processor', 'Command Processor')
        ]
        
        for attr, name in components:
            if hasattr(self.jarvis, attr) and getattr(self.jarvis, attr):
                status[name] = "✅ Active"
            else:
                status[name] = "❌ Inactive"
        
        return status
