# 🤖 JARVIS Hybrid Assistant

A sophisticated AI assistant that seamlessly operates in both online and offline modes, featuring voice interaction, web interface, and intelligent command processing.

##  Features

### 🌐 Hybrid Intelligence
- **Online Mode**: Powered by Google's Gemini AI for advanced conversations
- **Offline Mode**: Local ML model for basic commands and system operations
- **Seamless Switching**: Automatically switches modes based on connectivity
- **Smart Learning**: ML model improves over time with usage

### 🎤 Voice Interaction
- **Speech Recognition**: Free Google Speech Recognition
- **Text-to-Speech**: Google Cloud TTS (online) + pyttsx3 (offline)
- **Natural Language**: Conversational voice commands
- **Ambient Noise Handling**: Automatic audio adjustment

### 🖥️ Modern Web Interface
- **Real-time Chat**: Live conversation display with Taipy GUI
- **Mode Indicator**: Clear online/offline status
- **Statistics Dashboard**: Usage analytics and ML accuracy
- **Export Features**: Conversation history export
- **Responsive Design**: Works on desktop and mobile

### 🛠️ System Integration
- **Application Control**: Open browsers, cameras, file explorers
- **System Commands**: Shutdown, restart, time/date queries
- **Weather Information**: Real-time weather data (online mode)
- **Smart Commands**: Context-aware command recognition

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection (for initial setup and online features)
- Microphone for voice input

### 1. Clone & Setup
```bash
git clone <repository-url>
cd jarvis-hybrid-assistant
pip install -r requirements.txt
```

### 2. Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys (see Configuration section)
nano .env
```

### 3. Launch JARVIS
```bash
# Interactive launcher
python start.py

# Or direct launch
python start.py start
```

### 4. Access Interfaces
- **Web Interface**: http://localhost:5000
- **Voice Assistant**: Automatically starts with GUI
- **System Tray**: Desktop application interface

## ⚙️ Configuration

### Environment Variables (.env)
```env
# Required for Online Mode
GEMINI_API_KEY=your_gemini_api_key_here

# Optional Enhancements
WEATHER_API_KEY=your_openweathermap_api_key_here
GOOGLE_APPLICATION_CREDENTIALS=path/to/google-credentials.json

# Assistant Settings
ASSISTANT_NAME=JARVIS
VOICE_RATE=150
CONFIDENCE_THRESHOLD=0.6
```

### API Keys Setup

#### Google Gemini API (Required for Online Mode)
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add to `.env` as `GEMINI_API_KEY`

#### OpenWeatherMap API (Optional)
1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get free API key
3. Add to `.env` as `WEATHER_API_KEY`

#### Google Cloud TTS (Optional)
1. Create project in [Google Cloud Console](https://console.cloud.google.com)
2. Enable Text-to-Speech API
3. Create service account and download JSON
4. Set path in `.env` as `GOOGLE_APPLICATION_CREDENTIALS`

## 🎯 Usage

### Voice Commands

#### Mode Control
- *"Toggle mode"* - Switch between online/offline
- *"Switch to offline mode"* - Force offline mode
- *"Go online"* - Switch to online mode

#### System Commands
- *"What time is it?"* - Current time
- *"What's the date?"* - Current date
- *"Open Chrome"* - Launch browser
- *"Open camera"* - Start camera app
- *"Open file explorer"* - Launch file manager

#### Conversation
- *"Hello JARVIS"* - Greeting
- *"How's the weather?"* - Weather information
- *"Tell me a joke"* - Entertainment (online mode)
- *"Explain quantum physics"* - Educational queries (online mode)

#### System Control
- *"Shutdown computer"* - System shutdown (10s delay)
- *"Restart system"* - System restart (10s delay)
- *"Cancel shutdown"* - Abort shutdown/restart

### Web Interface

#### Dashboard Features
- **Mode Toggle**: Switch between online/offline modes
- **Conversation View**: Real-time chat display
- **Statistics Panel**: Usage metrics and ML accuracy
- **Export Tools**: Download conversation history
- **Model Management**: Retrain ML model with new data

#### Controls
- **New Conversation**: Clear chat history
- **Export History**: Save conversations as JSON
- **Retrain Model**: Update offline ML model
- **Status Monitor**: Real-time system status

## 🏗️ Architecture

### Core Components

#### 1. Main Assistant (`main.py`)
- **HybridAssistant**: Core AI processing engine
- **Audio Processing**: Speech recognition and TTS
- **API Integration**: Gemini AI and external services
- **ML Pipeline**: Offline command learning system

#### 2. Web Interface (`display.py`)
- **Taipy GUI**: Modern web framework
- **Real-time Updates**: Live conversation sync
- **Responsive Design**: Mobile-friendly interface
- **Data Visualization**: Usage statistics

#### 3. System Launcher (`start.py`)
- **Process Management**: Multi-component orchestration
- **Health Monitoring**: Automatic restart capabilities
- **Configuration Check**: Environment validation
- **Interactive Setup**: User-friendly installation

### Data Flow
```
Voice Input → Speech Recognition → Intent Processing → Response Generation → TTS Output
     ↓                                      ↓
Web Interface ← Real-time Updates ← Conversation Logger
```

### File Structure
```
jarvis-hybrid-assistant/
├── main.py                 # Core assistant logic
├── display.py              # Web interface
├── start.py                # System launcher
├── requirements.txt        # Python dependencies
├── .env                    # Configuration file
├── data/                   # Data storage
│   ├── conversation_history.json
│   ├── offline_commands.json
│   └── offline_model.pkl
├── audio/                  # Audio files
├── exports/                # Exported conversations
└── models/                 # ML models
```

## 🔧 Advanced Configuration

### Offline Commands Customization
Edit `data/offline_commands.json` to add custom commands:

```json
{
  "custom_command": {
    "patterns": ["pattern1", "pattern2"],
    "action": "custom_action",
    "responses": ["Response 1", "Response 2"]
  }
}
```

### ML Model Training
The system automatically retrains the ML model every 10 conversations. Manual retraining:

```python
assistant.train_ml_model()
```

### Voice Settings
Customize TTS parameters in the code:

```python
self.tts_engine.setProperty('rate', 150)    # Speech rate
self.tts_engine.setProperty('volume', 0.9)  # Volume level
```

## 🐛 Troubleshooting

### Common Issues

#### "No module named 'X'" Error
```bash
pip install -r requirements.txt
# or specific module
pip install module_name
```

#### Speech Recognition Not Working
- Check microphone permissions
- Verify internet connection
- Try different microphone
- Adjust ambient noise settings

#### API Errors
- Verify API keys in `.env`
- Check API quotas and limits
- Test connectivity to API endpoints

#### Web Interface Not Loading
- Check if port 5000 is available
- Verify Taipy installation
- Check firewall settings

### Debug Mode
Enable detailed logging:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Performance Optimization
- Reduce conversation history size for faster processing
- Adjust ML model confidence threshold
- Optimize audio buffer settings

## 🤝 Contributing

### Development Setup
```bash
# Clone repository
git clone <repository-url>
cd jarvis-hybrid-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where possible
- Add docstrings for all functions
- Include error handling

### Testing
```bash
# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_assistant.py
```

## 📋 Requirements

### System Requirements
- **OS**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 1GB for installation, 2GB for data
- **Network**: Internet connection for online features

### Python Dependencies
```
speechrecognition>=3.10.0
pyttsx3>=2.90
requests>=2.28.0
scikit-learn>=1.1.0
joblib>=1.2.0
numpy>=1.21.0
google-generativeai>=0.3.0
google-cloud-texttospeech>=2.14.0
python-dotenv>=0.19.0
pygame>=2.1.0
taipy-gui>=2.0.0
pathlib>=1.0.1
```

## 📚 API Documentation

### HybridAssistant Class

#### Methods
- `__init__(gui=None)`: Initialize assistant
- `listen()`: Capture voice input
- `speak(text)`: Convert text to speech
- `process_online_request(input)`: Handle online AI processing
- `process_offline_request(input)`: Handle offline command processing
- `toggle_mode()`: Switch between online/offline modes

#### Properties
- `is_online`: Current mode status
- `conversation_history`: Chat history
- `ml_model`: Offline ML model
- `gemini_model`: Online AI model

## 🔒 Privacy & Security

### Data Handling
- **Local Storage**: Conversations stored locally in JSON format
- **API Calls**: Only sent to configured services (Gemini, Weather)
- **Audio Processing**: Voice data processed in real-time, not stored
- **No Telemetry**: No usage data sent to external servers

### Security Features
- **API Key Protection**: Environment variable storage
- **Local Processing**: Offline mode for sensitive operations
- **Data Encryption**: Consider encrypting conversation history
- **Access Control**: Local network access only for web interface

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google**: Gemini AI and Speech Recognition APIs
- **Taipy**: Modern GUI framework
- **OpenWeatherMap**: Weather data API
- **scikit-learn**: Machine learning capabilities
- **pyttsx3**: Text-to-speech functionality

## 📞 Support

### Getting Help
1. **Documentation**: Check this README first
2. **Issues**: Create GitHub issue with detailed description
3. **Discussions**: Use GitHub Discussions for questions
4. **Wiki**: Check project wiki for additional guides

### Reporting Bugs
Include the following information:
- Operating system and version
- Python version
- Error messages and stack traces
- Steps to reproduce
- Configuration (without sensitive data)

### Feature Requests
- Describe the feature clearly
- Explain the use case
- Provide implementation ideas if possible

---

**Happy Chatting with JARVIS! 🤖✨**


