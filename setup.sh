#!/bin/bash
# /home/dijital/Documents/ragnostics-tool/setup.sh
# Setup script for RAGnostics Tool

set -e

echo "🔭 RAGnostics Tool Setup"
echo "======================="

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment for Pro version
echo "📦 Setting up Pro version environment..."
python3 -m venv venv-pro
source venv-pro/bin/activate

# Install Pro dependencies
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Pro version setup complete"
deactivate

# Make scripts executable
chmod +x ragnostics-core.py
chmod +x ragnostics-pro.py
chmod +x license-generator.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Usage:"
echo "  Free version:  python3 ragnostics-core.py --help"
echo "  Pro version:   source venv-pro/bin/activate && python ragnostics-pro.py --help"
echo "  License gen:   source venv-pro/bin/activate && python license-generator.py --help"
echo ""
echo "Example usage:"
echo "  python3 ragnostics-core.py --docs *.pdf --queries 'How do I reset password?'"
echo ""
