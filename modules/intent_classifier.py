import re

class IntentClassifier:
    def __init__(self, ai_handler):
        self.ai_handler = ai_handler
        
        # Command indicators - words that suggest action/execution
        self.command_indicators = {
            'action_verbs': [
                'create', 'make', 'build', 'generate', 'open', 'launch', 'start', 'run',
                'close', 'kill', 'stop', 'delete', 'remove', 'move', 'copy', 'rename',
                'install', 'download', 'upload', 'save', 'execute', 'play', 'pause',
                'restart', 'shutdown', 'reboot', 'switch', 'change', 'set', 'configure'
            ],
            'system_objects': [
                'file', 'folder', 'directory', 'application', 'app', 'program', 'process',
                'window', 'browser', 'terminal', 'website', 'webpage', 'project', 'script'
            ],
            'command_patterns': [
                r'^(open|launch|start|run)\s+\w+',
                r'^(create|make|build)\s+\w+',
                r'^(delete|remove|kill)\s+\w+',
                r'^(show|list|display)\s+\w+',
                r'^(go to|navigate to|cd)\s+\w+'
            ]
        }
        
        # Question indicators - words that suggest inquiry
        self.question_indicators = {
            'question_words': [
                'what', 'how', 'why', 'when', 'where', 'who', 'which', 'whose',
                'can you', 'do you', 'are you', 'will you', 'would you', 'could you',
                'is', 'are', 'was', 'were', 'does', 'did', 'has', 'have'
            ],
            'inquiry_phrases': [
                'tell me', 'explain', 'describe', 'help me understand', 'i want to know',
                'i need to know', 'can you help', 'what is', 'how does', 'why does'
            ],
            'question_patterns': [
                r'^\w+\s+(is|are|was|were|does|did|has|have)\s+',
                r'^(what|how|why|when|where|who|which)\s+',
                r'^(can|do|are|will|would|could)\s+you\s+',
                r'\?$'  # Ends with question mark
            ]
        }
        
        # Conversational indicators
        self.conversational_indicators = [
            'hello', 'hi', 'hey', 'thanks', 'thank you', 'good morning',
            'good afternoon', 'good evening', 'goodbye', 'bye', 'see you'
        ]
    
    def classify_intent(self, user_input):
        """Classify user input as 'command', 'question', or 'conversation'"""
        user_input_lower = user_input.lower().strip()
        
        # Check for conversational input first
        if any(indicator in user_input_lower for indicator in self.conversational_indicators):
            return 'conversation'
        
        # Check for explicit question patterns
        question_score = self._calculate_question_score(user_input_lower)
        command_score = self._calculate_command_score(user_input_lower)
        
        # If it's clearly a question
        if question_score > command_score and question_score > 2:
            return 'question'
        
        # If it's clearly a command
        if command_score > question_score and command_score > 1:
            return 'command'
        
        # Use AI for ambiguous cases
        if self.ai_handler and self.ai_handler.client:
            ai_classification = self._ai_classify_intent(user_input)
            if ai_classification:
                return ai_classification
        
        # Default fallback based on scores
        if question_score > command_score:
            return 'question'
        elif command_score > 0:
            return 'command'
        else:
            return 'conversation'
    
    def _calculate_question_score(self, user_input):
        """Calculate how likely the input is a question"""
        score = 0
        
        # Check question words
        for word in self.question_indicators['question_words']:
            if user_input.startswith(word + ' ') or f' {word} ' in user_input:
                score += 2
        
        # Check inquiry phrases
        for phrase in self.question_indicators['inquiry_phrases']:
            if phrase in user_input:
                score += 3
        
        # Check question patterns
        for pattern in self.question_indicators['question_patterns']:
            if re.search(pattern, user_input):
                score += 2
        
        return score
    
    def _calculate_command_score(self, user_input):
        """Calculate how likely the input is a command"""
        score = 0
        
        # Check action verbs
        for verb in self.command_indicators['action_verbs']:
            if user_input.startswith(verb + ' '):
                score += 3
            elif f' {verb} ' in user_input:
                score += 1
        
        # Check system objects
        for obj in self.command_indicators['system_objects']:
            if obj in user_input:
                score += 1
        
        # Check command patterns
        for pattern in self.command_indicators['command_patterns']:
            if re.search(pattern, user_input):
                score += 3
        
        return score
    
    def _ai_classify_intent(self, user_input):
        """Use AI to classify ambiguous inputs"""
        try:
            prompt = f"""Classify this user input as either "command", "question", or "conversation":

Input: "{user_input}"

Rules:
- "command" = User wants to execute an action (create, open, run, delete, etc.)
- "question" = User wants information or explanation (what, how, why, etc.)
- "conversation" = User wants to chat (greetings, thanks, casual talk)

Respond with only one word: command, question, or conversation"""

            response = self.ai_handler.client.chat.completions.create(
                model=self.ai_handler.model,
                messages=[
                    {"role": "system", "content": "You are an intent classifier. Respond with only one word."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=10
            )
            
            result = response.choices[0].message.content.strip().lower()
            if result in ['command', 'question', 'conversation']:
                return result
                
        except Exception as e:
            print(f"AI classification error: {e}")
        
        return None
    
    def get_intent_explanation(self, user_input, intent):
        """Get explanation of why input was classified as specific intent"""
        explanations = []
        user_input_lower = user_input.lower()
        
        if intent == 'command':
            for verb in self.command_indicators['action_verbs']:
                if verb in user_input_lower:
                    explanations.append(f"Contains action verb: '{verb}'")
            
            for obj in self.command_indicators['system_objects']:
                if obj in user_input_lower:
                    explanations.append(f"References system object: '{obj}'")
        
        elif intent == 'question':
            for word in self.question_indicators['question_words']:
                if word in user_input_lower:
                    explanations.append(f"Contains question word: '{word}'")
            
            if user_input.endswith('?'):
                explanations.append("Ends with question mark")
        
        elif intent == 'conversation':
            for indicator in self.conversational_indicators:
                if indicator in user_input_lower:
                    explanations.append(f"Contains conversational indicator: '{indicator}'")
        
        return explanations if explanations else ["Classified by AI or default logic"]
