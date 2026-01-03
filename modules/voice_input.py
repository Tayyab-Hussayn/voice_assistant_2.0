import speech_recognition as sr
import pyaudio
import numpy as np
import threading
import time

class VoiceInput:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        # Wake word detection
        self.wake_words = ["hey jarvis", "jarvis", "hey assistant"]
        self.listening_for_wake_word = False
        self.wake_word_detected = False
        
    def detect_wake_word(self, text):
        """Check if wake word is in the text"""
        text_lower = text.lower()
        for wake_word in self.wake_words:
            if wake_word in text_lower:
                return True
        return False
    
    def listen_for_wake_word(self):
        """Continuously listen for wake word"""
        print("🔊 Wake word detection active (say 'Hey JARVIS')")
        
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
        while self.listening_for_wake_word:
            try:
                with sr.Microphone() as source:
                    # Listen for short phrases
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=3)
                    
                try:
                    text = self.recognizer.recognize_google(audio, language='en-US')
                    if self.detect_wake_word(text):
                        print("🎯 Wake word detected!")
                        self.wake_word_detected = True
                        return
                except sr.UnknownValueError:
                    pass  # Ignore unrecognized audio
                    
            except sr.WaitTimeoutError:
                pass  # Continue listening
            except Exception as e:
                print(f"Wake word detection error: {e}")
                time.sleep(0.1)
    
    def listen(self, wake_word_mode=False):
        """Listen for voice input and convert to text"""
        if wake_word_mode:
            self.listening_for_wake_word = True
            self.wake_word_detected = False
            
            # Start wake word detection in background
            wake_thread = threading.Thread(target=self.listen_for_wake_word)
            wake_thread.daemon = True
            wake_thread.start()
            
            # Wait for wake word
            while not self.wake_word_detected:
                time.sleep(0.1)
            
            self.listening_for_wake_word = False
            print("🎤 Wake word detected! Listening for command...")
        
        with sr.Microphone() as source:
            if not wake_word_mode:
                print("🎤 Listening... (speak clearly)")
            
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            try:
                audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=15)
                print("🔄 Processing...")
                
                text = self.recognizer.recognize_google(audio, language='en-US', show_all=False)
                print(f"📝 Heard: '{text}'")
                
                # Remove wake word from command if present
                text_lower = text.lower()
                for wake_word in self.wake_words:
                    if text_lower.startswith(wake_word):
                        text = text[len(wake_word):].strip()
                        break
                
                return text.lower()
                
            except sr.WaitTimeoutError:
                print("⏱️ Timeout")
                return None
            except sr.UnknownValueError:
                print("❌ Could not understand")
                return None
            except Exception as e:
                print(f"❌ Error: {e}")
                return None
    
    def stop_wake_word_detection(self):
        """Stop wake word detection"""
        self.listening_for_wake_word = False
