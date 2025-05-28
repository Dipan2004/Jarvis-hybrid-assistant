#!/usr/bin/env python3
"""Configuration Helper for Enhanced JARVIS"""

import os
import json
import requests
from pathlib import Path
from typing import Dict, List

class JarvisConfig:
    """Helper class for JARVIS configuration and setup"""
    
    def __init__(self):
        self.base_dir = Path(".")
        self.audio_dir = self.base_dir / "audio"
        self.models_dir = self.base_dir / "models"
        self.piper_dir = self.base_dir / "piper"
        self.env_file = self.base_dir / ".env"
        self.responses_file = self.base_dir / "responses.json"
    
    def setup_directories(self):
        """Create necessary directories"""
        directories = [self.audio_dir, self.models_dir, self.piper_dir / "models"]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✓ Created directory: {directory}")
    
    def setup_env_file(self):
        """Create .env file with API key placeholders"""
        if self.env_file.exists():
            print("✓ .env file already exists")
            return
        
        env_content = """GEMINI_API_KEY=your_gemini_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        print(f"✓ Created .env file at {self.env_file}")
        print("  Please edit .env and add your actual API keys")
    
    def setup_responses_file(self):
        """Create comprehensive responses.json file"""
        if self.responses_file.exists():
            print("✓ responses.json already exists")
            return
        
        responses = {
            "greeting": [
                "Hello! I'm your Enhanced JARVIS assistant with hybrid online/offline capabilities!",
                "Hi there! I can work both online and offline. How can I help you today?",
                "Greetings! I'm JARVIS - your intelligent assistant ready for any task!",
                "Hello! I'm equipped with file operations, camera control, and much more!"
            ],
            "farewell": [
                "Goodbye! Thank you for using Enhanced JARVIS. Have a wonderful day!",
                "See you later! I'll be here whenever you need assistance.",
                "Until next time! Take care and remember I'm always ready to help!",
                "Farewell! It was a pleasure assisting you today."
            ],
            "file_operation": [
                "I can help with file operations! Try commands like 'open file filename' or 'list files'.",
                "File management is one of my specialties. What files would you like to work with?",
                "I'm ready to handle your file operations. Just tell me what you need!",
                "File access granted! What would you like me to do with your files?"
            ],
            "system": [
                "I can provide detailed system information and perform various system tasks.",
                "System diagnostics and information are available. What would you like to know?",
                "I have access to system information. What details do you need?",
                "System operations are ready. How can I help with your computer?"
            ],
            "camera": [
                "Camera functionality is active! I can open your camera and capture images.",
                "I have camera access ready. Would you like me to take a photo?",
                "Camera systems online! Say 'open camera' to capture an image.",
                "Photography mode available! I can access your camera anytime."
            ],
            "time": [
                "I can tell you the current time and date information.",
                "Time and date services are available. What would you like to know?",
                "Clock functions ready! Ask me about time or date.",
                "I keep track of time for you. What time information do you need?"
            ],
            "weather": [
                "I can provide weather information when connected online.",
                "Weather services are available in online mode. What's your location?",
                "I can check weather conditions when internet is available.",
                "Weather updates ready! I'll need your location for accurate forecasts."
            ],
            "help": [
                "I'm here to help! I can handle file operations, camera control, system info, and answer questions.",
                "I have many capabilities: file management, camera access, system information, and online AI responses.",
                "Need assistance? I can work with files, control hardware, provide information, and learn from our conversations!",
                "I'm your comprehensive assistant! From file operations to AI conversations, I'm ready to help."
            ],
            "question": [
                "That's a great question! Let me think about that and provide you with an answer.",
                "Interesting question! I'll do my best to give you helpful information.",
                "Good question! I'm processing that and will provide the best answer I can.",
                "I love answering questions! Let me help you with that."
            ],
            "command": [
                "Command received! I'm ready to execute various tasks and operations.",
                "I can handle different types of commands. What specific task would you like me to perform?",
                "Task understood! I'm equipped to handle various operations and commands.",
                "Command mode active! What would you like me to do?"
            ],
            "thanks": [
                "You're very welcome! I'm always happy to help.",
                "My pleasure! That's what I'm here for.",
                "Anytime! I enjoy being useful and helping out.",
                "You're welcome! Feel free to ask me anything else you need."
            ],
            "general": [
                "I'm your Enhanced JARVIS with both online AI and offline capabilities!",
                "I combine the best of online AI with practical offline functionality.",
                "Whether online or offline, I'm here to assist with various tasks and questions.",
                "I'm designed to be helpful in any situation - connected or disconnected!",
                "I learn from our conversations and improve over time. How can I help you?"
            ],
            "error": [
                "I apologize, but I encountered an issue. Let me try a different approach.",
                "Something went wrong, but I'm still here to help! Could you try rephrasing that?",
                "I had a small hiccup, but I'm back online! What can I do for you?",
                "Technical difficulties happen, but I'm resilient! How else can I assist you?"
            ],
            "learning": [
                "I'm learning from our conversation to provide better responses!",
                "Every interaction helps me improve. Thank you for teaching me!",
                "I'm getting smarter with each conversation we have.",
                "Machine learning in progress! I'm becoming more helpful over time."
            ]
        }
        
        with open(self.responses_file, 'w') as f:
            json.dump(responses, f, indent=2)
        
        print(f"✓ Created comprehensive responses.json file")
    
    def check_api_connectivity(self):
        """Test API connectivity"""
        print("\n🔍 Testing API Connectivity...")
        
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv()
        
        # Test Gemini API
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key and gemini_key != 'your_gemini_api_key_here':
            try:
                api_url = f"https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent?key={gemini_key}"
                response = requests.post(
                    api_url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{"parts": [{"text": "Hello"}]}],
                        "generationConfig": {"maxOutputTokens": 10}
                    },
                    timeout=5
                )
                if response.status_code == 200:
                    print("✓ Gemini API: Working")
                else:
                    print(f"⚠ Gemini API: Error {response.status_code}")
            except Exception as e:
                print(f"⚠ Gemini API: Connection failed - {str(e)}")
        else:
            print("⚠ Gemini API: Key not configured")
        
        # Test Deepgram API
        deepgram_key = os.getenv('DEEPGRAM_API_KEY')
        if deepgram_key and deepgram_key != 'your_deepgram_api_key_here':
            try:
                response = requests.get(
                    "https://api.deepgram.com/v1/projects",
                    headers={"Authorization": f"Token {deepgram_key}"},
                    timeout=5
                )
                if response.status_code == 200:
                    print("✓ Deepgram API: Working")
                else:
                    print(f"⚠ Deepgram API: Error {response.status_code}")
            except Exception as e:
                print(f"⚠ Deepgram API: Connection failed - {str(e)}")
        else:
            print("⚠ Deepgram API: Key not configured")
        
        # Test HuggingFace API
        hf_key = os.getenv('HUGGINGFACE_API_KEY')
        if hf_key and hf_key != 'your_huggingface_api_key_here':
            try:
                response = requests.post(
                    "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill",
                    headers={"Authorization": f"Bearer {hf_key}"},
                    json={"inputs": "Hello"},
                    timeout=5
                )
                if response.status_code == 200:
                    print("✓ HuggingFace API: Working")
                else:
                    print(f"⚠ HuggingFace API: Error {response.status_code}")
            except Exception as e:
                print(f"⚠ HuggingFace API: Connection failed - {str(e)}")
        else:
            print("⚠ HuggingFace API: Key not configured (optional)")
    
    def download_piper_voices(self):
        """Download common Piper voice models"""
        print("\n🎤 Downloading Piper Voice Models...")
        
        models_to_download = [
            {
                "name": "en_US-lessac-medium",
                "url_base": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/"
            },
            {
                "name": "en_US-libritts-high",
                "url_base": "https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/libritts/high/"
            }
        ]
        
        for model in models_to_download:
            model_dir = self.piper_dir / "models"
            model_file = model_dir / f"{model['name']}.onnx"
            config_file = model_dir / f"{model['name']}.onnx.json"
            
            if model_file.exists():
                print(f"✓ {model['name']} already exists")
                continue
            
            try:
                print(f"Downloading {model['name']}...")
                
                # Download model file
                model_url = model['url_base'] + f"{model['name']}.onnx"
                response = requests.get(model_url, stream=True, timeout=30)
                response.raise_for_status()
                
                with open(model_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Download config file
                config_url = model['url_base'] + f"{model['name']}.onnx.json"
                response = requests.get(config_url, timeout=10)
                response.raise_for_status()
                
                with open(config_file, 'wb') as f:
                    f.write(response.content)
                
                print(f"✓ Downloaded {model['name']}")
                
            except Exception as e:
                print(f"⚠ Failed to download {model['name']}: {str(e)}")
    
    def system_check(self):
        """Perform comprehensive system check"""
        print("🔧 Enhanced JARVIS System Check")
        print("=" * 40)
        
        # Check Python version
        import sys
        print(f"Python Version: {sys.version}")
        
        # Check required modules
        required_modules = [
            'requests', 'pygame', 'numpy', 'sklearn', 
            'cv2', 'dotenv', 'deepgram'
        ]
        
        print("\n📦 Module Check:")
        for module in required_modules:
            try:
                __import__(module)
                print(f"✓ {module}")
            except ImportError:
                print(f"⚠ {module} - Not installed")
        
        # Check optional modules
        optional_modules = ['pyaudio', 'gtts', 'pyttsx3']
        print("\n📦 Optional Modules:")
        for module in optional_modules:
            try:
                __import__(module)
                print(f"✓ {module}")
            except ImportError:
                print(f"⚠ {module} - Not installed (optional)")
        
        # Check directories
        print("\n📁 Directory Check:")
        for directory in [self.audio_dir, self.models_dir, self.piper_dir]:
            if directory.exists():
                print(f"✓ {directory}")
            else:
                print(f"⚠ {directory} - Missing")
        
        # Check files
        print("\n📄 Configuration Files:")
        config_files = [
            (self.env_file, "API Keys"),
            (self.responses_file, "Responses"),
            (Path("main.py"), "Main Application"),
            (Path("display.py"), "Display Interface")
        ]
        
        for file_path, description in config_files:
            if file_path.exists():
                print(f"✓ {description}: {file_path}")
            else:
                print(f"⚠ {description}: {file_path} - Missing")
    
    def full_setup(self):
        """Perform complete setup"""
        print("🚀 Enhanced JARVIS Full Setup")
        print("=" * 40)
        
        self.setup_directories()
        self.setup_env_file()
        self.setup_responses_file()
        self.check_api_connectivity()
        
        # Ask about Piper models
        download_piper = input("\nDownload Piper TTS voice models? (y/N): ").lower()
        if download_piper == 'y':
            self.download_piper_voices()
        
        print("\n🎉 Setup Complete!")
        print("\nNext steps:")
        print("1. Edit .env file with your actual API keys")
        print("2. Install Piper TTS executable if you want high-quality voice")
        print("3. Run: python main.py --mode hybrid")
        print("4. Run display interface: python display.py")

def main():
    """Main configuration interface"""
    config = JarvisConfig()
    
    print("🤖 Enhanced JARVIS Configuration Helper")
    print("=" * 40)
    print("1. Full Setup")
    print("2. System Check")
    print("3. Test API Connectivity")
    print("4. Download Piper Voice Models")
    print("5. Create Config Files Only")
    print("0. Exit")
    
    choice = input("\nSelect option (0-5): ").strip()
    
    if choice == '1':
        config.full_setup()
    elif choice == '2':
        config.system_check()
    elif choice == '3':
        config.check_api_connectivity()
    elif choice == '4':
        config.download_piper_voices()
    elif choice == '5':
        config.setup_directories()
        config.setup_env_file()
        config.setup_responses_file()
        print("✓ Configuration files created!")
    elif choice == '0':
        print("Goodbye!")
    else:
        print("Invalid option!")

if __name__ == "__main__":
    main()