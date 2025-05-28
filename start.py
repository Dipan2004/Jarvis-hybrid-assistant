#!/usr/bin/env python3
"""
JARVIS Hybrid Assistant Launcher
Provides an easy way to start and manage the assistant
"""

import os
import sys
import time
import subprocess
import threading
from pathlib import Path
import signal

class JARVISLauncher:
    def __init__(self):
        self.processes = []
        self.running = False
        
    def check_requirements(self):
        """Check if all requirements are met"""
        print("🔍 Checking requirements...")
        
        # Check Python version
        if sys.version_info < (3, 8):
            print("❌ Python 3.8 or higher required")
            return False
            
        # Check if required files exist
        required_files = ['main.py', 'display.py', 'requirements.txt']
        missing_files = []
        
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)
                
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
            return False
            
        # Check if .env file exists
        if not Path('.env').exists():
            print("⚠️  .env file not found. Creating template...")
            self.create_env_template()
            
        # Create necessary directories
        directories = ['data', 'audio', 'exports']
        for directory in directories:
            Path(directory).mkdir(exist_ok=True)
            
        print("✅ Requirements check passed")
        return True
        
    def create_env_template(self):
        """Create a template .env file"""
        env_template = """# Hybrid JARVIS Assistant Configuration
# Required for online mode
GEMINI_API_KEY=your_gemini_api_key_here

# Optional APIs (for enhanced features)
WEATHER_API_KEY=your_openweathermap_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=path/to/google-credentials.json

# Assistant Configuration
ASSISTANT_NAME=JARVIS
VOICE_RATE=150
CONFIDENCE_THRESHOLD=0.6
"""
        with open('.env', 'w') as f:
            f.write(env_template)
        print("📝 Created .env template. Please add your API keys.")
        
    def install_requirements(self):
        """Install required packages"""
        print("📦 Installing requirements...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ Requirements installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install requirements: {e}")
            return False
            
    def start_display(self):
        """Start the web display interface"""
        print("🌐 Starting web interface...")
        try:
            process = subprocess.Popen([sys.executable, 'display.py'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            self.processes.append(('Display', process))
            time.sleep(2)  # Give it time to start
            print("✅ Web interface started at http://localhost:5000")
            return True
        except Exception as e:
            print(f"❌ Failed to start web interface: {e}")
            return False
            
    def start_assistant(self):
        """Start the main assistant"""
        print("🤖 Starting JARVIS assistant...")
        try:
            process = subprocess.Popen([sys.executable, 'main.py'], 
                                     stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE)
            self.processes.append(('Assistant', process))
            print("✅ JARVIS assistant started")
            return True
        except Exception as e:
            print(f"❌ Failed to start assistant: {e}")
            return False
            
    def monitor_processes(self):
        """Monitor running processes"""
        while self.running:
            for name, process in self.processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} process stopped unexpectedly")
                    # Attempt to restart
                    if name == 'Display':
                        self.start_display()
                    elif name == 'Assistant':
                        self.start_assistant()
                        
            time.sleep(5)
            
    def stop_all(self):
        """Stop all processes"""
        print("\n🛑 Stopping all processes...")
        self.running = False
        
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Stopped {name}")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔥 Force killed {name}")
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
                
        self.processes.clear()
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n📡 Received signal {signum}")
        self.stop_all()
        sys.exit(0)
        
    def show_status(self):
        """Show current status"""
        print("\n📊 JARVIS Status:")
        print("=" * 50)
        
        for name, process in self.processes:
            status = "🟢 Running" if process.poll() is None else "🔴 Stopped"
            print(f"{name:15} : {status}")
            
        # Check files
        print(f"\nConfiguration:")
        env_exists = "✅" if Path('.env').exists() else "❌"
        print(f"Environment file : {env_exists}")
        
        # Check directories
        for directory in ['data', 'audio', 'exports']:
            exists = "✅" if Path(directory).exists() else "❌"
            print(f"{directory:15} : {exists}")
            
    def interactive_menu(self):
        """Show interactive menu"""
        while True:
            print("\n" + "="*50)
            print("🤖 JARVIS Hybrid Assistant Launcher")
            print("="*50)
            print("1. 🚀 Start JARVIS (Full System)")
            print("2. 🌐 Start Web Interface Only")
            print("3. 🎤 Start Assistant Only") 
            print("4. 📊 Show Status")
            print("5. 🛑 Stop All")
            print("6. 📦 Install Requirements")
            print("7. 🔧 Check Configuration")
            print("8. ❌ Exit")
            print("="*50)
            
            try:
                choice = input("Enter your choice (1-8): ").strip()
                
                if choice == '1':
                    if self.check_requirements():
                        self.start_full_system()
                elif choice == '2':
                    if self.check_requirements():
                        self.start_display()
                elif choice == '3':
                    if self.check_requirements():
                        self.start_assistant()
                elif choice == '4':
                    self.show_status()
                elif choice == '5':
                    self.stop_all()
                elif choice == '6':
                    self.install_requirements()
                elif choice == '7':
                    self.check_requirements()
                elif choice == '8':
                    self.stop_all()
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                self.stop_all()
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                
    def start_full_system(self):
        """Start the complete JARVIS system"""
        print("🚀 Starting complete JARVIS system...")
        
        if not self.check_requirements():
            return False
            
        # Start display first
        if not self.start_display():
            return False
            
        # Start assistant
        if not self.start_assistant():
            return False
            
        self.running = True
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self.monitor_processes)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("\n🎉 JARVIS system started successfully!")
        print("🌐 Web Interface: http://localhost:5000")
        print("🎤 Voice Assistant: Active")
        print("💡 Say 'toggle mode' to switch between online/offline")
        print("🛑 Press Ctrl+C to stop")
        
        try:
            # Keep main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop_all()
            
        return True

def main():
    """Main launcher function"""
    launcher = JARVISLauncher()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, launcher.signal_handler)
    signal.signal(signal.SIGTERM, launcher.signal_handler)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == 'start':
            launcher.start_full_system()
        elif arg == 'display':
            launcher.check_requirements()
            launcher.start_display()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                launcher.stop_all()
        elif arg == 'assistant':
            launcher.check_requirements()
            launcher.start_assistant()
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                launcher.stop_all()
        elif arg == 'install':
            launcher.install_requirements()
        elif arg == 'status':
            launcher.show_status()
        else:
            print("Usage: python launcher.py [start|display|assistant|install|status]")
    else:
        # Interactive mode
        launcher.interactive_menu()

if __name__ == "__main__":
    main()