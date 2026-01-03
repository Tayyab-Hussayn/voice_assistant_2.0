#!/bin/bash
# JARVIS Enhanced CLI Launcher Script

echo "🤖 Starting JARVIS Enhanced CLI..."

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo "📦 Checking dependencies..."
pip install -q rich

# Launch Enhanced CLI Interface
echo "🚀 Launching JARVIS Enhanced Terminal Interface..."
echo "✨ Features: Status indicators, Ctrl+C interrupts, Project analysis"
python jarvis_cli.py
