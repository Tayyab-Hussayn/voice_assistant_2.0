import json
from pathlib import Path
from datetime import datetime

class ContextManager:
    def __init__(self, memory_system):
        self.memory = memory_system
        self.contexts = {}
        self.active_context = "general"
        self.context_dir = Path.cwd() / "Contexts"
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing contexts
        self.load_contexts()
        
    def load_contexts(self):
        """Load saved contexts from disk"""
        context_file = self.context_dir / "contexts.json"
        if context_file.exists():
            try:
                with open(context_file, 'r') as f:
                    self.contexts = json.load(f)
            except:
                self.contexts = {}
        
        # Ensure general context exists
        if "general" not in self.contexts:
            self.contexts["general"] = {
                "name": "General",
                "description": "Default context for general tasks",
                "created": datetime.now().isoformat(),
                "variables": {},
                "history": []
            }
    
    def save_contexts(self):
        """Save contexts to disk"""
        context_file = self.context_dir / "contexts.json"
        with open(context_file, 'w') as f:
            json.dump(self.contexts, f, indent=2)
    
    def create_context(self, name, description=""):
        """Create a new context"""
        context_id = name.lower().replace(' ', '_')
        
        self.contexts[context_id] = {
            "name": name,
            "description": description,
            "created": datetime.now().isoformat(),
            "variables": {},
            "history": []
        }
        
        self.save_contexts()
        self.memory.store_knowledge("contexts", context_id, name)
        return context_id
    
    def switch_context(self, context_id):
        """Switch to a different context"""
        if context_id in self.contexts:
            # Save current context state
            if self.active_context in self.contexts:
                self.contexts[self.active_context]["last_accessed"] = datetime.now().isoformat()
            
            self.active_context = context_id
            self.contexts[context_id]["last_accessed"] = datetime.now().isoformat()
            self.save_contexts()
            return True
        return False
    
    def get_current_context(self):
        """Get current context information"""
        if self.active_context in self.contexts:
            return self.contexts[self.active_context]
        return None
    
    def set_context_variable(self, key, value):
        """Set a variable in current context"""
        if self.active_context in self.contexts:
            self.contexts[self.active_context]["variables"][key] = {
                "value": value,
                "timestamp": datetime.now().isoformat()
            }
            self.save_contexts()
    
    def get_context_variable(self, key):
        """Get a variable from current context"""
        if self.active_context in self.contexts:
            var_data = self.contexts[self.active_context]["variables"].get(key)
            return var_data["value"] if var_data else None
        return None
    
    def add_to_context_history(self, action, details):
        """Add action to context history"""
        if self.active_context in self.contexts:
            self.contexts[self.active_context]["history"].append({
                "action": action,
                "details": details,
                "timestamp": datetime.now().isoformat()
            })
            
            # Keep only last 50 history items
            if len(self.contexts[self.active_context]["history"]) > 50:
                self.contexts[self.active_context]["history"] = \
                    self.contexts[self.active_context]["history"][-50:]
            
            self.save_contexts()
    
    def get_context_summary(self):
        """Get summary of current context"""
        context = self.get_current_context()
        if not context:
            return "No active context"
        
        summary = f"Context: {context['name']}\n"
        summary += f"Description: {context.get('description', 'No description')}\n"
        
        if context['variables']:
            summary += f"Variables: {len(context['variables'])} stored\n"
        
        if context['history']:
            summary += f"Recent actions: {len(context['history'])}\n"
            # Show last 3 actions
            for action in context['history'][-3:]:
                summary += f"  - {action['action']}: {action['details']}\n"
        
        return summary
    
    def list_contexts(self):
        """List all available contexts"""
        return [(cid, ctx['name'], ctx.get('description', '')) 
                for cid, ctx in self.contexts.items()]
    
    def delete_context(self, context_id):
        """Delete a context"""
        if context_id == "general":
            return False, "Cannot delete general context"
        
        if context_id in self.contexts:
            del self.contexts[context_id]
            self.save_contexts()
            
            # Switch to general if deleting active context
            if self.active_context == context_id:
                self.active_context = "general"
            
            return True, f"Context '{context_id}' deleted"
        
        return False, "Context not found"
    
    def get_contextual_prompt(self):
        """Generate contextual prompt for AI"""
        context = self.get_current_context()
        if not context:
            return ""
        
        prompt = f"Current context: {context['name']}\n"
        
        if context.get('description'):
            prompt += f"Context description: {context['description']}\n"
        
        # Add relevant variables
        if context['variables']:
            prompt += "Context variables:\n"
            for key, var_data in context['variables'].items():
                prompt += f"  {key}: {var_data['value']}\n"
        
        # Add recent history
        if context['history']:
            prompt += "Recent actions in this context:\n"
            for action in context['history'][-3:]:
                prompt += f"  - {action['action']}: {action['details']}\n"
        
        return prompt
