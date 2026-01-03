import json
from datetime import datetime, timedelta
from collections import defaultdict
import re

class LearningSystem:
    def __init__(self, memory_system):
        self.memory = memory_system
        self.patterns = defaultdict(int)
        self.user_preferences = {}
        self.command_success_rates = defaultdict(lambda: {"attempts": 0, "successes": 0})
        
    def learn_from_interaction(self, user_input, jarvis_response, action_type, success):
        """Learn from each interaction"""
        # Extract patterns from user input
        self.extract_patterns(user_input)
        
        # Update command success rates
        self.update_success_rates(action_type, success)
        
        # Learn user preferences
        self.learn_preferences(user_input, success)
        
        # Store learning insights
        self.store_learning_insights()
    
    def extract_patterns(self, user_input):
        """Extract common patterns from user input"""
        # Common command patterns
        command_patterns = [
            r'(create|make|build)\s+(\w+)',
            r'(open|launch|start)\s+(\w+)',
            r'(show|display|get)\s+(\w+)',
            r'(delete|remove)\s+(\w+)',
            r'(find|search)\s+(\w+)'
        ]
        
        for pattern in command_patterns:
            matches = re.findall(pattern, user_input.lower())
            for match in matches:
                if isinstance(match, tuple):
                    pattern_key = f"{match[0]}_{match[1]}"
                else:
                    pattern_key = match
                self.patterns[pattern_key] += 1
    
    def update_success_rates(self, action_type, success):
        """Update success rates for different action types"""
        self.command_success_rates[action_type]["attempts"] += 1
        if success:
            self.command_success_rates[action_type]["successes"] += 1
    
    def learn_preferences(self, user_input, success):
        """Learn user preferences from successful interactions"""
        if not success:
            return
        
        # Learn preferred applications
        app_keywords = ['chrome', 'firefox', 'vscode', 'terminal', 'files']
        for app in app_keywords:
            if app in user_input.lower():
                pref_key = f"preferred_app_{app}"
                current_count = self.memory.get_preference(pref_key) or "0"
                self.memory.set_preference(pref_key, str(int(current_count) + 1))
        
        # Learn preferred project types
        project_keywords = ['website', 'portfolio', 'dashboard', 'landing']
        for proj_type in project_keywords:
            if proj_type in user_input.lower():
                pref_key = f"preferred_project_{proj_type}"
                current_count = self.memory.get_preference(pref_key) or "0"
                self.memory.set_preference(pref_key, str(int(current_count) + 1))
    
    def get_suggestions(self, user_input):
        """Get suggestions based on learned patterns"""
        suggestions = []
        
        # Suggest based on common patterns
        input_lower = user_input.lower()
        
        if "create" in input_lower or "make" in input_lower:
            # Suggest most common creation patterns
            common_creates = [k for k in self.patterns.keys() if k.startswith('create_') or k.startswith('make_')]
            if common_creates:
                most_common = max(common_creates, key=lambda x: self.patterns[x])
                suggestions.append(f"Based on your history, you often {most_common.replace('_', ' ')}")
        
        if "open" in input_lower or "launch" in input_lower:
            # Suggest preferred applications
            preferred_apps = []
            for pref_key in ['chrome', 'vscode', 'terminal', 'files']:
                count = self.memory.get_preference(f"preferred_app_{pref_key}")
                if count and int(count) > 2:  # Used more than twice
                    preferred_apps.append(pref_key)
            
            if preferred_apps:
                suggestions.append(f"Your frequently used apps: {', '.join(preferred_apps)}")
        
        return suggestions
    
    def get_performance_insights(self):
        """Get insights about JARVIS performance"""
        insights = []
        
        for action_type, stats in self.command_success_rates.items():
            if stats["attempts"] > 0:
                success_rate = (stats["successes"] / stats["attempts"]) * 100
                insights.append({
                    "action": action_type,
                    "success_rate": success_rate,
                    "attempts": stats["attempts"]
                })
        
        # Sort by success rate
        insights.sort(key=lambda x: x["success_rate"], reverse=True)
        return insights
    
    def get_usage_patterns(self):
        """Get user usage patterns"""
        # Get interaction times from memory
        recent_interactions = self.memory.search_interactions("", limit=100)
        
        if not recent_interactions:
            return {}
        
        # Analyze usage by hour
        hour_usage = defaultdict(int)
        action_frequency = defaultdict(int)
        
        for interaction in recent_interactions:
            timestamp_str = interaction[0]
            action_type = interaction[3]
            
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                hour_usage[timestamp.hour] += 1
                action_frequency[action_type] += 1
            except:
                continue
        
        # Find peak usage hours
        peak_hours = sorted(hour_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "peak_hours": [f"{hour}:00" for hour, _ in peak_hours],
            "most_common_actions": dict(sorted(action_frequency.items(), key=lambda x: x[1], reverse=True)[:5]),
            "total_interactions": len(recent_interactions)
        }
    
    def store_learning_insights(self):
        """Store learning insights in memory"""
        # Store top patterns
        top_patterns = dict(sorted(self.patterns.items(), key=lambda x: x[1], reverse=True)[:10])
        self.memory.store_knowledge("learning", "top_patterns", json.dumps(top_patterns))
        
        # Store performance insights
        performance = self.get_performance_insights()
        self.memory.store_knowledge("learning", "performance", json.dumps(performance))
        
        # Store usage patterns
        usage = self.get_usage_patterns()
        self.memory.store_knowledge("learning", "usage_patterns", json.dumps(usage))
    
    def get_learning_summary(self):
        """Get summary of what JARVIS has learned"""
        summary = "JARVIS Learning Summary:\n\n"
        
        # Top patterns
        top_patterns_str = self.memory.recall_knowledge("learning", "top_patterns")
        if top_patterns_str:
            top_patterns = json.loads(top_patterns_str)
            summary += "Most common command patterns:\n"
            for pattern, count in list(top_patterns.items())[:5]:
                summary += f"  - {pattern.replace('_', ' ')}: {count} times\n"
            summary += "\n"
        
        # Performance insights
        performance_str = self.memory.recall_knowledge("learning", "performance")
        if performance_str:
            performance = json.loads(performance_str)
            summary += "Performance by action type:\n"
            for insight in performance[:5]:
                summary += f"  - {insight['action']}: {insight['success_rate']:.1f}% success rate\n"
            summary += "\n"
        
        # Usage patterns
        usage_str = self.memory.recall_knowledge("learning", "usage_patterns")
        if usage_str:
            usage = json.loads(usage_str)
            summary += f"Total interactions: {usage.get('total_interactions', 0)}\n"
            if usage.get('peak_hours'):
                summary += f"Most active hours: {', '.join(usage['peak_hours'])}\n"
        
        return summary
