#!/bin/bash

echo "🤖 Setting up JARVIS AI Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install system dependencies for audio (Arch Linux)
echo "🔊 Installing system audio dependencies..."
sudo pacman -S --noconfirm portaudio python-pyaudio espeak espeak-data

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Get your Minimax API key from https://platform.minimax.io/"
echo "2. Add it to .env file: MINIMAX_API_KEY=your_key_here"
echo "3. Run: python jarvis.py"
echo ""
echo "🤖 JARVIS will be ready to serve!"
