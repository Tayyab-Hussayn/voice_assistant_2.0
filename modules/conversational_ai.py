import json
import time
from datetime import datetime
from pathlib import Path

class ConversationalAI:
    def __init__(self, ai_handler, feature_discovery=None):
        self.ai_handler = ai_handler
        self.feature_discovery = feature_discovery
        self.memory_system = None  # Will be set by JARVIS
        self.conversation_history = []
        self.context_memory = {}
        self.personality_traits = {
            'name': 'JARVIS',
            'role': 'Advanced AI Assistant',
            'personality': 'Professional, helpful, slightly witty',
            'capabilities': [
                'System control and automation',
                'File and application management', 
                'Computer vision and gesture control',
                'Web development assistance',
                'General conversation and information'
            ]
        }
        
        # Conversation patterns
        self.conversation_patterns = {
            'greetings': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'
            ],
            'questions_about_self': [
                'who are you', 'what are you', 'tell me about yourself', 'what can you do', 'your capabilities', 'your features'
            ],
            'status_inquiries': [
                'how are you', 'status', 'are you okay', 'how do you feel'
            ],
            'compliments': [
                'good job', 'well done', 'excellent', 'perfect', 'amazing'
            ],
            'thanks': [
                'thank you', 'thanks', 'appreciate it', 'grateful'
            ]
        }
        
        # Load conversation history if exists
        self.load_conversation_history()
    
    def save_conversation_history(self):
        """Save conversation history to file"""
        try:
            history_file = Path('conversation_history.json')
            with open(history_file, 'w') as f:
                json.dump({
                    'history': self.conversation_history[-50:],  # Keep last 50 exchanges
                    'context': self.context_memory,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)
        except Exception as e:
            print(f"Failed to save conversation history: {e}")
    
    def load_conversation_history(self):
        """Load conversation history from file"""
        try:
            history_file = Path('conversation_history.json')
            if history_file.exists():
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    self.conversation_history = data.get('history', [])
                    self.context_memory = data.get('context', {})
        except Exception as e:
            print(f"Failed to load conversation history: {e}")
    
    def add_to_conversation(self, user_input, jarvis_response):
        """Add exchange to conversation history"""
        self.conversation_history.append({
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'jarvis': jarvis_response
        })
        self.save_conversation_history()
    
    def detect_conversation_type(self, user_input):
        """Detect what type of conversation this is"""
        user_input_lower = user_input.lower()
        
        for pattern_type, patterns in self.conversation_patterns.items():
            for pattern in patterns:
                if pattern in user_input_lower:
                    return pattern_type
        
        # Check for questions
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which']
        if any(word in user_input_lower for word in question_words):
            return 'question'
        
        # Check for commands vs conversation
        command_indicators = ['create', 'open', 'launch', 'kill', 'move', 'delete', 'find']
        if any(word in user_input_lower for word in command_indicators):
            return 'command'
        
        return 'general_conversation'
    
    def generate_personality_response(self, conversation_type, user_input):
        """Generate personality-driven responses"""
        responses = {
            'greetings': [
                "Hello! JARVIS at your service. How may I assist you today?",
                "Good to see you! I'm ready to help with whatever you need.",
                "Greetings! All systems are online and ready for your commands."
            ],
            'questions_about_self': [
                "I'm JARVIS, your advanced AI assistant. I can control your system, manage files, recognize gestures, create web projects, and have conversations like this one. Think of me as your digital companion for productivity and automation.",
                "I'm an AI assistant inspired by Tony Stark's JARVIS. I specialize in system control, automation, and making your computing experience more intuitive through voice commands and gesture recognition.",
                self.get_capabilities_response()
            ],
            'status_inquiries': [
                "I'm operating at full capacity! All systems are green and ready for action.",
                "Functioning perfectly, thank you for asking. How can I make your day more productive?",
                "All systems nominal. I'm here and ready to assist with whatever you need."
            ],
            'compliments': [
                "Thank you! I do my best to be helpful. Is there anything else I can assist you with?",
                "I appreciate that! It's my pleasure to serve. What shall we tackle next?",
                "Much appreciated! I'm always striving to improve my assistance."
            ],
            'thanks': [
                "You're very welcome! Happy to help anytime.",
                "My pleasure! That's what I'm here for.",
                "Glad I could assist! Feel free to ask if you need anything else."
            ]
        }
        
        if conversation_type in responses:
            import random
            return random.choice(responses[conversation_type])
        
        return None
    
    def handle_conversation(self, user_input):
        """Main conversation handler"""
        conversation_type = self.detect_conversation_type(user_input)
        
        # Check memory first for personal questions
        if self.memory_system and ("remember" in user_input.lower() or "my name" in user_input.lower() or "do you know" in user_input.lower()):
            memory_response = self.check_memory_for_response(user_input)
            if memory_response:
                self.add_to_conversation(user_input, memory_response)
                return True, memory_response
        
        # Try personality response first
        personality_response = self.generate_personality_response(conversation_type, user_input)
        if personality_response:
            self.add_to_conversation(user_input, personality_response)
            return True, personality_response
        
        # For questions and general conversation, use AI
        if conversation_type in ['question', 'general_conversation']:
            return self.generate_ai_response(user_input)
        
        return False, "I'm not sure how to respond to that."
    
    def generate_ai_response(self, user_input):
        """Generate AI response for complex conversations"""
        if not self.ai_handler.client:
            return False, "AI conversation not available - no API key configured"
        
        # Build context from recent conversation and memory
        context = ""
        if self.conversation_history:
            recent_history = self.conversation_history[-3:]  # Last 3 exchanges
            for exchange in recent_history:
                context += f"User: {exchange['user']}\nJARVIS: {exchange['jarvis']}\n"
        
        # Add memory context if available
        if self.memory_system:
            user_info = self.memory_system.recall_knowledge("user_info")
            if user_info:
                context += "\nWhat I know about the user:\n"
                for key, value in user_info.items():
                    context += f"- {key}: {value}\n"
        
        system_prompt = f"""You are JARVIS, an advanced AI assistant inspired by Tony Stark's AI from Marvel. 

Your personality:
- Professional but friendly
- Slightly witty and sophisticated
- Knowledgeable about technology and systems
- Helpful and proactive
- Confident but not arrogant

Your capabilities include:
- System control and automation
- File and application management
- Computer vision and gesture recognition
- Web development assistance
- General knowledge and conversation
- Long-term memory and learning

You have access to persistent memory and can remember information about users between conversations.

Keep responses concise but informative. Use a tone that's professional yet personable.

Recent conversation context:
{context}

Respond as JARVIS would - helpful, intelligent, and with subtle personality."""

        try:
            response = self.ai_handler.client.chat.completions.create(
                model=self.ai_handler.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                extra_body={"reasoning_split": True},
                temperature=0.8,
                max_tokens=200
            )
            
            ai_response = response.choices[0].message.content.strip()
            self.add_to_conversation(user_input, ai_response)
            return True, ai_response
            
        except Exception as e:
            return False, f"AI conversation error: {e}"
    
    def get_conversation_summary(self):
        """Get summary of recent conversation"""
        if not self.conversation_history:
            return "No conversation history available."
        
        recent_count = min(5, len(self.conversation_history))
        return f"Recent conversation: {recent_count} exchanges in history. Last interaction was about: {self.conversation_history[-1]['user'][:50]}..."
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        self.context_memory = {}
        self.save_conversation_history()
        return "Conversation history cleared."
    
    def is_conversational_input(self, user_input):
        """Check if input is conversational rather than a command"""
        # Don't handle name introductions - let memory system handle them
        if "my name is" in user_input.lower():
            return False
            
        conversation_indicators = [
            'tell me', 'what is', 'how are', 'who are', 'explain', 'describe',
            'hello', 'hi', 'hey', 'thanks', 'thank you', 'good job',
            'what can you', 'do you know', 'can you help', 'i need help',
            'do you remember', 'what do you know about me'
        ]
        
        user_input_lower = user_input.lower()
        return any(indicator in user_input_lower for indicator in conversation_indicators)
    
    def get_capabilities_response(self):
        """Get dynamic capabilities response"""
        if self.feature_discovery:
            summary = self.feature_discovery.get_capability_summary()
            return f"I'm JARVIS with comprehensive capabilities: {summary}"
        else:
            return "I'm JARVIS, your advanced AI assistant with system control, web development, memory, and automation capabilities."
    
    def check_memory_for_response(self, user_input):
        """Check memory system for relevant information"""
        if not self.memory_system:
            return None
            
        user_input_lower = user_input.lower()
        
        # Check for name-related queries
        if "my name" in user_input_lower or "do you remember my name" in user_input_lower:
            name = self.memory_system.recall_knowledge("user_info", "name")
            if name:
                return f"Yes, I remember your name is {name}."
            else:
                return "I don't have your name stored in my memory yet. You can tell me your name and I'll remember it."
        
        # Check for general memory queries
        if "do you remember" in user_input_lower:
            # Extract what they're asking about
            parts = user_input_lower.split("do you remember")
            if len(parts) > 1:
                query = parts[1].strip()
                # Search interactions for relevant information
                results = self.memory_system.search_interactions(query, limit=3)
                if results:
                    return f"Yes, I remember we discussed {query}. I found {len(results)} related interactions in my memory."
                else:
                    return f"I don't have any specific memories about {query} in my records."
        
        # Check for stored knowledge
        if "what do you know about me" in user_input_lower:
            user_info = self.memory_system.recall_knowledge("user_info")
            if user_info:
                info_list = [f"{key}: {value}" for key, value in user_info.items()]
                return f"Here's what I know about you: {', '.join(info_list)}"
            else:
                return "I don't have any personal information stored about you yet. Feel free to share details you'd like me to remember."
        
        return None
