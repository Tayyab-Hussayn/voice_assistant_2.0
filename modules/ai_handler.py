import os
import subprocess
from openai import OpenAI
from dotenv import load_dotenv
import pyttsx3
import threading

load_dotenv()

class AIHandler:
    def __init__(self):
        # Setup Minimax M2.1 via OpenAI SDK
        api_key = os.getenv('MINIMAX_API_KEY')
        
        if api_key:
            self.client = OpenAI(
                base_url="https://api.minimax.io/v1",
                api_key=api_key
            )
            self.model = 'MiniMax-M2.1'
            print("✅ Minimax M2.1 connected")
        else:
            self.client = None
            self.model = None
            print("⚠️ AI disabled - Set MINIMAX_API_KEY in .env")
        
        # Setup Text-to-Speech with fallback
        self.tts_engine = None
        self.tts_available = False
        
        try:
            self.tts_engine = pyttsx3.init()
            self.tts_engine.setProperty('rate', 180)
            self.tts_engine.setProperty('volume', 0.9)
            
            # Get available voices and set a good one
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to find a good voice (prefer female for JARVIS feel)
                for voice in voices:
                    if 'female' in voice.name.lower() or 'woman' in voice.name.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        break
            
            self.tts_available = True
            print("✅ Text-to-Speech initialized")
            
        except Exception as e:
            print(f"⚠️ TTS initialization failed: {e}")
            print("🔇 Running in silent mode - JARVIS will not speak")
            self.tts_available = False

    def clean_text_for_speech(self, text):
        """Clean text for speech by removing symbols and formatting"""
        import re
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold** -> bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic* -> italic
        text = re.sub(r'`([^`]+)`', r'\1', text)        # `code` -> code
        
        # Remove quotes and brackets
        text = re.sub(r'["\'\[\]{}()]', '', text)       # Remove quotes and brackets
        
        # Remove special symbols but keep basic punctuation
        text = re.sub(r'[#@$%^&*+=|\\<>~`]', '', text)  # Remove symbols
        
        # Clean up multiple spaces and newlines
        text = re.sub(r'\s+', ' ', text)                # Multiple spaces -> single space
        text = re.sub(r'\n+', '. ', text)               # Newlines -> periods
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text

    def speak(self, text):
        """Convert text to speech with multiple fallback methods"""
        # Clean text before speaking
        clean_text = self.clean_text_for_speech(text)
        
        if not self.tts_available:
            # Fallback to espeak-ng directly
            try:
                subprocess.run(['espeak-ng', clean_text], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL, 
                             timeout=10)
                return
            except:
                pass
            
            # Final fallback - just print
            print(f"🤖 JARVIS: {text}")
            return
            
        def _speak():
            try:
                self.tts_engine.say(clean_text)
                self.tts_engine.runAndWait()
            except Exception as e:
                print(f"🤖 JARVIS: {text}")
                print(f"⚠️ TTS Error: {e}")
        
        # Run TTS in separate thread to avoid blocking
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()

    def get_response(self, prompt):
        """Get AI response for general queries"""
        if not self.client:
            return "AI not available"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are JARVIS, an intelligent AI assistant. Be concise and direct."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"AI Error: {str(e)}"

    def generate_command(self, user_input, current_dir):
        """Use Minimax M2.1 to generate command from natural language"""
        if not self.client:
            return None
    
        prompt = f"""You are JARVIS, an advanced AI assistant. Convert this natural language request into a Linux terminal command.

User request: "{user_input}"
Current directory: {current_dir}

Rules:
- Return ONLY the command, no explanation
- If unclear or dangerous, return "UNSAFE" or "UNCLEAR"  
- Use common Linux tools (ls, cd, find, grep, etc.)
- Prefer safe, non-destructive commands

Command:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are JARVIS, a helpful AI assistant that generates safe Linux commands."},
                    {"role": "user", "content": prompt}
                ],
                extra_body={"reasoning_split": True},
                temperature=0.7
            )
        
            command = response.choices[0].message.content.strip()
            command = command.replace('```bash', '').replace('```', '').replace('`', '').strip()
        
            if command.upper() in ['UNSAFE', 'UNCLEAR']:
                return None
        
            return command
        
        except Exception as e:
            print(f"❌ AI Error: {e}")
            return None

    def process_advanced_request(self, user_input, current_dir):
        """Handle advanced requests that go beyond simple commands"""
        if not self.client:
            return None
            
        system_prompt = """You are JARVIS, an advanced AI assistant capable of complex task execution.
You can:
1. Generate and execute multiple commands in sequence
2. Create files and projects
3. Control system applications
4. Provide intelligent responses

Analyze the user's request and provide a structured response with:
- action_type: "command", "multi_command", "file_creation", "web_project", or "response"
- commands: list of commands to execute (if applicable)
- files: files to create with content (if applicable)
- response: text response to speak to user"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Request: {user_input}\nCurrent directory: {current_dir}"}
                ],
                extra_body={"reasoning_split": True},
                temperature=0.8
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Advanced AI Error: {e}")
            return None
