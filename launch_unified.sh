#!/bin/bash

# JARVIS Unified Terminal Launcher
# Warp Terminal-inspired AI + Shell interface

echo "🚀 Launching JARVIS Unified Terminal..."

# Navigate to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found. Run ./setup.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it with your MINIMAX_API_KEY"
    exit 1
fi

# Launch unified terminal
echo "🤖 Starting JARVIS Unified Terminal..."
echo ""
python jarvis_unified_cli.py

echo ""
echo "👋 JARVIS Unified Terminal closed"
