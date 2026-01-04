#!/bin/bash

# 🤖 JARVIS - Unified Start Script
# Single script to launch JARVIS with the best interface

echo "🤖 JARVIS - Advanced AI Assistant"
echo "=================================="

# Navigate to project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "🔧 Please run: ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate
echo "✅ Virtual environment activated"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "🔧 Please create .env with your MINIMAX_API_KEY"
    echo "   Example: echo 'MINIMAX_API_KEY=your_key_here' > .env"
    exit 1
fi

# Check dependencies
echo "📦 Checking dependencies..."
pip install -q rich > /dev/null 2>&1

echo ""
echo "🚀 Starting JARVIS Unified Terminal..."
echo "💡 Features: AI Chat + Native Shell in one prompt"
echo "📖 Usage: Type commands, 'ai: question', '$ shell_cmd', or 'help'"
echo ""

# Launch JARVIS Unified Terminal (best interface)
python jarvis_unified_cli.py

echo ""
echo "👋 JARVIS session ended. Goodbye!"
