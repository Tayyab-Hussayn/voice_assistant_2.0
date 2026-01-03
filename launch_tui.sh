#!/bin/bash
# JARVIS CLI Launcher Script

echo "🤖 Starting JARVIS CLI..."

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo "📦 Checking dependencies..."
pip install -q rich

# Launch CLI Interface
echo "🚀 Launching JARVIS Terminal Interface..."
python jarvis_cli.py
