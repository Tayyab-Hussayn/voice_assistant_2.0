# 🤖 JARVIS - Advanced AI Assistant

A JARVIS-like AI assistant that can control your entire Linux system through voice commands, built with Minimax M2.1 and advanced capabilities.

## ✨ Features

### Core Capabilities
- **Voice Control**: Natural language voice commands with wake word detection
- **Text-to-Speech**: JARVIS speaks back to you with confirmations and responses
- **System Control**: Full Linux system management and automation
- **Web Development**: Create and launch web projects instantly
- **Application Launcher**: Open any application with voice commands
- **Smart Command Processing**: 3-tier processing (Pattern → AI → Direct)

### Advanced Features
- **Wake Word Detection**: Say "Hey JARVIS" to activate
- **Minimax M2.1 Integration**: Advanced reasoning and thinking capabilities
- **Safety Features**: Dangerous command detection and confirmation
- **Project Management**: Create, organize, and manage development projects
- **System Monitoring**: Real-time system information and diagnostics

## 🚀 Quick Start

### 1. Setup
```bash
# Clone and navigate to project
cd voice_shell_mini

# Run setup script (installs dependencies)
./setup.sh
```

### 2. Configure API Key
1. Get your Minimax API key from [https://platform.minimax.io/](https://platform.minimax.io/)
2. Add it to `.env` file:
```bash
MINIMAX_API_KEY=your_minimax_api_key_here
```

### 3. Run JARVIS

```bash
# Simple one-command startup
./start.sh
```

**Alternative Options:**
```bash
# Direct unified terminal
python jarvis_unified_cli.py

# Classic CLI interface  
python jarvis_cli.py

# Original JARVIS
python jarvis.py
```

## 🎯 Usage Examples

### Unified Terminal (Warp-style) 🆕
- **Mixed Usage**: `ls -la` → `ai: explain this directory` → `$ cd modules` → `jarvis: analyze this code`
- **Shell Commands**: `git status`, `npm install`, `python script.py`
- **AI Chat**: `ai: how do I deploy to AWS?`, `ai: create a React component`
- **JARVIS Tasks**: `jarvis: research machine learning`, `jarvis: create a web project`
- **Mode Switching**: `$ command` (force shell), `ai: message` (force AI), `jarvis: task` (force JARVIS)

### Voice Commands
- **"Hey JARVIS, create a web project called portfolio"**
- **"Open Chrome browser"**
- **"Show me system information"**
- **"List all files in this directory"**
- **"Create a folder called projects"**
- **"What's my current location?"**

### Text Commands
- Type commands directly: `ls -la`
- Use wake word mode: `wake` then speak
- Get help: `jarvis help`

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Voice Input   │───▶│  Minimax M2.1    │───▶│  System Ctrl    │
│  (Speech-to-    │    │  (Main Brain)    │    │  (Linux/Apps)   │
│   Text)         │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         ▲                       │                       │
         │                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Voice Output   │◀───│  Response Gen    │    │  Web Projects   │
│  (Text-to-      │    │  (TTS)           │    │  (HTML/CSS/JS)  │
│   Speech)       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
voice_shell_mini/
├── jarvis.py              # Main JARVIS application
├── jarvis_cli.py          # Terminal CLI interface (Gemini CLI style)
├── launch_tui.sh          # CLI launcher script
├── tui_options.sh         # Interface comparison guide
├── voiceshell.py          # Legacy voice shell (backup)
├── modules/
│   ├── ai_handler.py      # Minimax M2.1 integration + TTS
│   ├── voice_input.py     # Speech recognition + wake word
│   ├── system_controller.py # System operations + web projects
│   ├── intent_classifier.py # Intelligent command classification
│   ├── memory_system.py   # Persistent memory and learning
│   ├── workflow_engine.py # Automated task sequences
│   └── __init__.py
├── command_patterns.json  # Fast command patterns
├── requirements.txt       # Python dependencies
├── setup.sh              # Installation script
├── .env                  # API keys (add your own)
├── roadmap.txt           # Development roadmap
└── README.md             # This file
```

## 🛠️ Development Roadmap

The project follows a 6-phase development plan:

1. **Phase 1**: Foundation & Minimax Integration ✅
2. **Phase 2**: System Control & Automation (In Progress)
3. **Phase 3**: Advanced Capabilities (Computer Vision)
4. **Phase 4**: Intelligence & Memory System
5. **Phase 5**: Smart Home Integration
6. **Phase 6**: Polish & Optimization

See `roadmap.txt` for detailed development plan.

## 🔧 Dependencies

### Python Packages
- `openai` - Minimax M2.1 integration
- `SpeechRecognition` - Voice input processing
- `pyttsx3` - Text-to-speech output
- `python-dotenv` - Environment variable management
- `pyaudio` - Audio input/output
- `numpy` - Audio processing

### System Dependencies (Arch Linux)
- `portaudio` - Audio interface
- `python-pyaudio` - Python audio bindings
- `espeak` - Text-to-speech engine

## 🔒 Security Features

- **Command Validation**: Prevents dangerous system operations
- **User Confirmation**: Requires approval for risky commands
- **API Key Protection**: Secure environment variable storage
- **Safe Execution**: Sandboxed command execution with timeouts

## 🎨 Customization

### Adding New Commands
Edit `command_patterns.json` to add fast-response patterns:
```json
{
  "custom_category": {
    "your command": "linux_command_here"
  }
}
```

### Modifying Voice Settings
In `modules/ai_handler.py`, adjust TTS settings:
```python
self.tts_engine.setProperty('rate', 180)    # Speech speed
self.tts_engine.setProperty('volume', 0.9)  # Volume level
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use, modify, and distribute.

## 🆘 Troubleshooting

### Common Issues

**Audio not working:**
```bash
# Install audio dependencies
sudo pacman -S portaudio python-pyaudio espeak
```

**API key errors:**
- Ensure your Minimax API key is correctly set in `.env`
- Check your API quota and billing status

**Voice recognition issues:**
- Check microphone permissions
- Adjust `energy_threshold` in `voice_input.py`
- Ensure quiet environment for better recognition

---

**🤖 "JARVIS at your service!"**
