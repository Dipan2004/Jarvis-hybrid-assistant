#!/usr/bin/env python3

import os
import json
import asyncio
import threading
import time
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import tkinter as tk
from tkinter import scrolledtext, ttk

import speech_recognition as sr
import pyttsx3
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
import numpy as np

import google.generativeai as genai
from google.cloud import texttospeech

from dotenv import load_dotenv
import pygame
from pygame import mixer

load_dotenv()

class HybridAssistantGUI:
    def __init__(self, root):
        """Initialize the hybrid assistant with GUI"""
        self.root = root
        self.setup_gui()
        self.assistant = HybridAssistant(self)
        self.stop_conversation = False
        self.conversation_active = False
        
    def setup_gui(self):
        """Setup the graphical user interface"""
        self.root.title("JARVIS Hybrid Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg='#1e1e2d')
        
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1e1e2d')
        style.configure('TLabel', background='#1e1e2d', foreground='white')
        style.configure('TButton', background='#3a3a4a', foreground='white', 
                       font=('Arial', 10, 'bold'), borderwidth=1)
        style.map('TButton', 
                 background=[('active', '#4a4a5a'), ('pressed', '#2a2a3a')])
        
        
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        
        self.conversation_area = scrolledtext.ScrolledText(
            main_frame, wrap=tk.WORD, width=80, height=25,
            font=('Arial', 10), bg='#2a2a3a', fg='white',
            insertbackground='white'
        )
        self.conversation_area.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        
        self.start_button = ttk.Button(
            button_frame, text="Start Conversation", 
            command=self.start_conversation
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        
        self.end_button = ttk.Button(
            button_frame, text="End Conversation", 
            command=self.end_conversation, state=tk.DISABLED
        )
        self.end_button.pack(side=tk.LEFT, padx=5)
        
        
        self.mode_button = ttk.Button(
            button_frame, text="Toggle Mode (Checking...)", 
            command=self.toggle_mode
        )
        self.mode_button.pack(side=tk.LEFT, padx=5)
        
        
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var,
            relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
    
        self.conversation_area.tag_config('user', foreground='#ff6b6b')
        self.conversation_area.tag_config('jarvis', foreground='#4ecdc4')
        self.conversation_area.tag_config('system', foreground='#ffd700')
        
        
        self.root.after(1000, self.check_initial_connectivity)
        
    def check_initial_connectivity(self):
        """Check initial connectivity and update mode button"""
        def check():
            connectivity = self.assistant.check_online_connectivity()
            mode = "Online" if connectivity else "Offline"
            self.mode_button.config(text=f"Toggle Mode ({mode})")
            if not connectivity:
                self.add_message("System: Starting in Offline mode - No internet or API issues detected", 'system')
            else:
                self.add_message("System: Online mode available - Gemini API connected", 'system')
        
        threading.Thread(target=check, daemon=True).start()
        
    def start_conversation(self):
        """Start the conversation thread"""
        if not self.conversation_active:
            self.conversation_active = True
            self.stop_conversation = False
            self.start_button.config(state=tk.DISABLED)
            self.end_button.config(state=tk.NORMAL)
            
            # Initialize message
            mode = "Online" if self.assistant.is_online else "Offline"
            self.add_message(f"System: JARVIS Hybrid Assistant initialized in {mode} mode. Say 'toggle mode' to switch modes.", 'system')
            self.assistant.speak(f"JARVIS Hybrid Assistant initialized in {mode} mode.")
            
        
            threading.Thread(
                target=self.run_conversation_loop,
                daemon=True
            ).start()
    
    def end_conversation(self):
        """End the current conversation"""
        self.conversation_active = False
        self.stop_conversation = True
        self.start_button.config(state=tk.NORMAL)
        self.end_button.config(state=tk.DISABLED)
        self.add_message("System: Conversation ended", 'system')
        self.assistant.speak("Conversation ended")
    
    def toggle_mode(self):
        """Toggle between online and offline modes"""
        
        if not self.assistant.is_online:
            
            if self.assistant.check_online_connectivity():
                self.assistant.is_online = True
                self.mode_button.config(text="Toggle Mode (Online)")
                self.add_message("System: Switched to Online mode - Gemini AI connected", 'system')
                self.assistant.speak("Switched to Online mode")
            else:
                self.add_message("System: Cannot switch to Online mode - Check internet connection and API keys", 'system')
                self.assistant.speak("Cannot switch to online mode. Please check your connection.")
        else:
            
            self.assistant.is_online = False
            self.mode_button.config(text="Toggle Mode (Offline)")
            self.add_message("System: Switched to Offline mode", 'system')
            self.assistant.speak("Switched to Offline mode")
    
    def run_conversation_loop(self):
        """Main conversation loop"""
        while not self.stop_conversation and self.conversation_active:
            try:
                
                self.update_status("Listening...")
                user_input = self.assistant.listen()
                
                if user_input is None:
                    continue
                
                
                self.add_message(f"You: {user_input}", 'user')
                
                
                if "toggle mode" in user_input.lower():
                    self.toggle_mode()
                    continue
                
                
                if any(phrase in user_input.lower() for phrase in ['exit', 'quit', 'goodbye']):
                    self.add_message("JARVIS: Goodbye! Have a great day!", 'jarvis')
                    self.assistant.speak("Goodbye! Have a great day!")
                    self.end_conversation()
                    break
                
                
                self.update_status("Processing...")
                
                if self.assistant.is_online:
                    response = asyncio.run(self.assistant.process_online_request(user_input))
                else:
                    response = self.assistant.process_offline_request(user_input)
                
                
                self.add_message(f"JARVIS: {response}", 'jarvis')
                self.assistant.speak(response)
                
                
                self.update_status("Ready")
                
            except Exception as e:
                self.add_message(f"System Error: {str(e)}", 'system')
                self.update_status("Error")
                time.sleep(1)
                self.update_status("Ready")
    
    def add_message(self, message, tag=None):
        """Add a message to the conversation area"""
        self.conversation_area.config(state=tk.NORMAL)
        self.conversation_area.insert(tk.END, message + "\n\n", tag)
        self.conversation_area.config(state=tk.DISABLED)
        self.conversation_area.see(tk.END)
    
    def update_status(self, text):
        """Update the status bar"""
        self.status_var.set(text)
        self.root.update_idletasks()

class HybridAssistant:
    def __init__(self, gui=None):
        """Initialize the hybrid assistant with both online and offline capabilities"""
        self.gui = gui
        self.setup_logging()
        self.is_online = False  # Start as offline, will be checked during setup
        self.conversation_history = []
        self.offline_commands = {}
        self.ml_model = None
        self.gemini_model = None
        self.tts_client = None
        
        self.load_configuration()
        self.setup_apis()
        self.setup_offline_capabilities()
        self.setup_audio()
        
        # Check initial connectivity
        self.is_online = self.check_online_connectivity()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('assistant.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_configuration(self):
        """Load configuration settings"""
        self.config = {
            'gemini_api_key': os.getenv('GEMINI_API_KEY'),
            'weather_api_key': os.getenv('WEATHER_API_KEY'),
            'conversation_file': 'data/conversation_history.json',
            'model_file': 'data/offline_model.pkl',
            'commands_file': 'data/offline_commands.json',
            'audio_dir': 'audio/',
            'data_dir': 'data/'
        }
        
        
        for directory in [self.config['audio_dir'], self.config['data_dir']]:
            Path(directory).mkdir(exist_ok=True)
            
    def setup_apis(self):
        """Setup online API connections"""
        try:
            
            if self.config['gemini_api_key']:
                genai.configure(api_key=self.config['gemini_api_key'])
                self.gemini_model = genai.GenerativeModel('models/gemini-1.5-flash')
                self.logger.info("Gemini AI configured")
            else:
                self.logger.warning("Gemini API key not found in environment variables")
                
            
            try:
                self.tts_client = texttospeech.TextToSpeechClient()
                self.logger.info("Google TTS configured")
            except Exception as e:
                self.logger.warning(f"Google TTS not available: {e}")
                self.tts_client = None
                
        except Exception as e:
            self.logger.error(f"Error setting up APIs: {e}")
            
    def check_online_connectivity(self) -> bool:
        """Check if online services are available"""
        if not self.config['gemini_api_key']:
            self.logger.info("No Gemini API key found")
            return False
            
        if not self.gemini_model:
            self.logger.info("Gemini model not initialized")
            return False
            
        try:
            
            response = requests.get('https://www.google.com', timeout=5)
            if response.status_code != 200:
                self.logger.info("No internet connection")
                return False
                
            
            test_response = self.gemini_model.generate_content("Hello")
            if test_response and test_response.text:
                self.logger.info("Gemini API is working")
                return True
            else:
                self.logger.info("Gemini API test failed")
                return False
                
        except requests.exceptions.RequestException:
            self.logger.info("Internet connection test failed")
            return False
        except Exception as e:
            self.logger.error(f"Connectivity check failed: {e}")
            return False
            
    def setup_offline_capabilities(self):
        """Setup offline command handling and ML model"""
        self.load_offline_commands()
        self.load_ml_model()
        self.load_conversation_history()
        
    def load_offline_commands(self):
        """Load predefined offline commands"""
        default_commands = {
            "weather": {
                "patterns": ["weather", "temperature", "forecast", "climate"],
                "action": "get_weather",
                "responses": ["Getting weather information...", "Checking the weather for you..."]
            },
            "open_browser": {
                "patterns": ["open chrome", "open browser", "launch chrome", "start browser"],
                "action": "open_chrome",
                "responses": ["Opening Chrome browser...", "Launching your browser..."]
            },
            "open_camera": {
                "patterns": ["open camera", "start camera", "launch camera", "take photo"],
                "action": "open_camera",
                "responses": ["Opening camera application...", "Starting camera..."]
            },
            "open_file": {
                "patterns": ["open file", "browse files", "file explorer", "open folder"],
                "action": "open_file_explorer",
                "responses": ["Opening file explorer...", "Launching file browser..."]
            },
            "time": {
                "patterns": ["time", "current time", "what time is it", "clock"],
                "action": "get_time",
                "responses": ["The current time is", "It's currently"]
            },
            "date": {
                "patterns": ["date", "today's date", "what's the date", "calendar"],
                "action": "get_date",
                "responses": ["Today's date is", "The date is"]
            },
            "shutdown": {
                "patterns": ["shutdown", "turn off", "power off", "shut down computer"],
                "action": "shutdown_system",
                "responses": ["Shutting down the system...", "Powering off..."]
            },
            "restart": {
                "patterns": ["restart", "reboot", "restart computer", "reboot system"],
                "action": "restart_system",
                "responses": ["Restarting the system...", "Rebooting..."]
            }
        }
        
        try:
            with open(self.config['commands_file'], 'r') as f:
                self.offline_commands = json.load(f)
        except FileNotFoundError:
            self.offline_commands = default_commands
            self.save_offline_commands()
            
    def save_offline_commands(self):
        """Save offline commands to file"""
        with open(self.config['commands_file'], 'w') as f:
            json.dump(self.offline_commands, f, indent=2)
            
    def load_ml_model(self):
        """Load or create ML model for offline command recognition"""
        try:
            self.ml_model = joblib.load(self.config['model_file'])
            self.logger.info("ML model loaded successfully")
        except FileNotFoundError:
            self.train_ml_model()
            
    def train_ml_model(self):
        """Train ML model on offline commands and conversation history"""
        training_data = []
        labels = []
        
        
        for command, data in self.offline_commands.items():
            for pattern in data['patterns']:
                training_data.append(pattern)
                labels.append(command)
                
        
        for conv in self.conversation_history:
            if conv.get('offline_command'):
                training_data.append(conv['user_input'])
                labels.append(conv['offline_command'])
                
        if len(training_data) > 0:
            
            self.ml_model = Pipeline([
                ('tfidf', TfidfVectorizer(stop_words='english', ngram_range=(1, 2))),
                ('classifier', MultinomialNB())
            ])
            
            self.ml_model.fit(training_data, labels)
            joblib.dump(self.ml_model, self.config['model_file'])
            self.logger.info("ML model trained and saved")
        else:
            self.logger.warning("No training data available for ML model")
            
    def setup_audio(self):
        """Setup audio input/output"""
        
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        
        self.tts_engine = pyttsx3.init()
        voices = self.tts_engine.getProperty('voices')
        if voices:
            self.tts_engine.setProperty('voice', voices[0].id)
        self.tts_engine.setProperty('rate', 150)
        
        
        mixer.init()
        
        self.logger.info("Audio systems initialized")
        
    def load_conversation_history(self):
        """Load conversation history from file"""
        try:
            with open(self.config['conversation_file'], 'r') as f:
                self.conversation_history = json.load(f)
        except FileNotFoundError:
            self.conversation_history = []
            
    def save_conversation_history(self):
        """Save conversation history to file"""
        with open(self.config['conversation_file'], 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
            
    def listen(self) -> Optional[str]:
        """Listen for voice input using free speech recognition"""
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.logger.info("Listening...")
                if self.gui:
                    self.gui.update_status("Listening...")
                
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            self.logger.info("Processing speech...")
            if self.gui:
                self.gui.update_status("Processing speech...")
            
            
            text = self.recognizer.recognize_google(audio)
            self.logger.info(f"Recognized: {text}")
            return text.lower()
            
        except sr.UnknownValueError:
            self.logger.warning("Could not understand audio")
            if self.gui:
                self.gui.add_message("JARVIS: Sorry, I didn't catch that. Please repeat.", 'jarvis')
            self.speak("Sorry, I didn't catch that. Please repeat.")
            return None
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition error: {e}")
            # Auto-switch to offline if speech recognition fails due to network
            if self.is_online:
                self.speak("Speech recognition service unavailable, switching to offline mode")
                self.is_online = False
                if self.gui:
                    self.gui.mode_button.config(text="Toggle Mode (Offline)")
            return None
        except Exception as e:
            self.logger.error(f"Listening error: {e}")
            return None
            
    def speak(self, text: str):
        """Convert text to speech using available TTS services"""
        self.logger.info(f"Speaking: {text}")
        
        if self.is_online and self.tts_client:
            try:
                
                synthesis_input = texttospeech.SynthesisInput(text=text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3
                )
                
                response = self.tts_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )
                
            
                audio_file = f"{self.config['audio_dir']}response.mp3"
                with open(audio_file, "wb") as out:
                    out.write(response.audio_content)
                    
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"Google TTS error: {e}")
                # Fallback to offline TTS
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
        else:
            # Use offline TTS
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
            
    async def process_online_request(self, user_input: str) -> str:
        """Process request using online services (Gemini)"""
        try:
            if not self.check_online_connectivity():
                self.is_online = False
                if self.gui:
                    self.gui.mode_button.config(text="Toggle Mode (Offline)")
                    self.gui.add_message("System: Switched to Offline mode - Connection lost", 'system')
                return self.process_offline_request(user_input)
            
        
            context = "You are JARVIS, an advanced AI assistant. Keep responses concise and helpful.\n\n"
            
            
            recent_history = self.conversation_history[-5:] if len(self.conversation_history) > 5 else self.conversation_history
            for conv in recent_history:
                context += f"Human: {conv['user_input']}\nAssistant: {conv['response']}\n\n"
                
            context += f"Human: {user_input}\nAssistant:"
            
            response = self.gemini_model.generate_content(context)
            
            
            self.add_to_conversation_history(user_input, response.text)
            
            return response.text
            
        except Exception as e:
            self.logger.error(f"Online processing error: {e}")
            
            self.is_online = False
            if self.gui:
                self.gui.mode_button.config(text="Toggle Mode (Offline)")
                self.gui.add_message("System: Switched to Offline mode - API error", 'system')
            return self.process_offline_request(user_input)
            
    def process_offline_request(self, user_input: str) -> str:
        """Process request using offline capabilities"""
        
        if self.ml_model:
            try:
                prediction = self.ml_model.predict([user_input])[0]
                confidence = max(self.ml_model.predict_proba([user_input])[0])
                
                if confidence > 0.6:  
                    response = self.execute_offline_command(prediction, user_input)
                    self.add_to_conversation_history(user_input, response, prediction)
                    return response
            except Exception as e:
                self.logger.error(f"ML prediction error: {e}")
                
        
        for command, data in self.offline_commands.items():
            for pattern in data['patterns']:
                if pattern in user_input:
                    response = self.execute_offline_command(command, user_input)
                    self.add_to_conversation_history(user_input, response, command)
                    return response
                    

        response = self.generate_offline_response(user_input)
        self.add_to_conversation_history(user_input, response)
        return response
        
    def execute_offline_command(self, command: str, user_input: str) -> str:
        """Execute offline commands"""
        try:
            command_data = self.offline_commands.get(command, {})
            action = command_data.get('action')
            responses = command_data.get('responses', ["Processing your request..."])
            
            if action == 'get_weather':
                return self.get_weather_offline()
            elif action == 'open_chrome':
                self.open_chrome()
                return np.random.choice(responses)
            elif action == 'open_camera':
                self.open_camera()
                return np.random.choice(responses)
            elif action == 'open_file_explorer':
                self.open_file_explorer()
                return np.random.choice(responses)
            elif action == 'get_time':
                current_time = datetime.now().strftime("%H:%M")
                return f"{np.random.choice(responses)} {current_time}"
            elif action == 'get_date':
                current_date = datetime.now().strftime("%B %d, %Y")
                return f"{np.random.choice(responses)} {current_date}"
            elif action == 'shutdown_system':
                return self.shutdown_system()
            elif action == 'restart_system':
                return self.restart_system()
            else:
                return "I understand your request but I'm not sure how to help with that offline."
                
        except Exception as e:
            self.logger.error(f"Command execution error: {e}")
            return "I encountered an error while processing your request."
            
    def get_weather_offline(self) -> str:
        """Get weather information (offline fallback)"""
        if self.config['weather_api_key'] and self.is_online:
            try:
                
                url = f"http://api.openweathermap.org/data/2.5/weather?q=London&appid={self.config['weather_api_key']}&units=metric"
                response = requests.get(url, timeout=5)
                data = response.json()
                
                temp = data['main']['temp']
                description = data['weather'][0]['description']
                return f"The current temperature is {temp}°C with {description}."
                
            except Exception as e:
                self.logger.error(f"Weather API error: {e}")
                
        return "I can't get current weather information in offline mode. You might want to check your weather app or enable online mode."
        
    def open_chrome(self):
        """Open Chrome browser"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['start', 'chrome'], shell=True)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.Popen(['google-chrome'])
        except Exception as e:
            webbrowser.open('http://www.google.com')
            
    def open_camera(self):
        """Open camera application"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['start', 'microsoft.windows.camera:'], shell=True)
            elif os.name == 'posix':  # macOS/Linux
                subprocess.Popen(['cheese'])  # Linux
        except Exception as e:
            self.logger.error(f"Cannot open camera: {e}")
            
    def open_file_explorer(self):
        """Open file explorer"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['explorer'])
            elif os.name == 'posix':  # macOS/Linux
                subprocess.Popen(['nautilus'])  # Linux
        except Exception as e:
            self.logger.error(f"Cannot open file explorer: {e}")
            
    def shutdown_system(self) -> str:
        """Shutdown the system"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['shutdown', '/s', '/t', '10'])
            else:  # macOS/Linux
                subprocess.Popen(['sudo', 'shutdown', '-h', '+1'])
            return "System will shutdown in 10 seconds. Say 'cancel shutdown' to abort."
        except Exception as e:
            return f"Cannot shutdown system: {e}"
            
    def restart_system(self) -> str:
        """Restart the system"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.Popen(['shutdown', '/r', '/t', '10'])
            else:  # macOS/Linux
                subprocess.Popen(['sudo', 'reboot'])
            return "System will restart in 10 seconds. Say 'cancel restart' to abort."
        except Exception as e:
            return f"Cannot restart system: {e}"
            
    def generate_offline_response(self, user_input: str) -> str:
        """Generate response based on conversation history and patterns"""
        
        responses = {
            'greeting': ["Hello! How can I help you today?", "Hi there!", "Good to see you!"],
            'thanks': ["You're welcome!", "Happy to help!", "No problem!"],
            'goodbye': ["Goodbye!", "See you later!", "Take care!"],
            'default': ["I'm not sure I understand. Could you rephrase that?", 
                       "I'm in offline mode with limited capabilities.", 
                       "Try asking me about the time, date, or opening applications."]
        }
        
        input_lower = user_input.lower()
        
        if any(word in input_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return np.random.choice(responses['greeting'])
        elif any(word in input_lower for word in ['thank', 'thanks', 'thank you']):
            return np.random.choice(responses['thanks'])
        elif any(word in input_lower for word in ['bye', 'goodbye', 'see you', 'exit']):
            return np.random.choice(responses['goodbye'])
        else:
            return np.random.choice(responses['default'])
            
    def add_to_conversation_history(self, user_input: str, response: str, offline_command: str = None):
        """Add conversation to history and retrain model if needed"""
        conversation = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'response': response,
            'mode': 'offline' if not self.is_online else 'online',
            'offline_command': offline_command
        }
        
        self.conversation_history.append(conversation)
        self.save_conversation_history()
        
        
        if len(self.conversation_history) % 10 == 0:
            self.train_ml_model()

def main():
    """Main function to run the assistant with GUI"""
    root = tk.Tk()
    app = HybridAssistantGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()