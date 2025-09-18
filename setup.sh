#!/bin/bash

echo "RAGnostics Setup for Ubuntu/Debian"
echo "=================================="

# Check Python version
if ! python3 --version | grep -E "3\.(7|8|9|10|11|12)" > /dev/null; then
    echo "Error: Python 3.7+ required"
    exit 1
fi

# Install system dependencies if needed
echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate and install
source venv/bin/activate
pip install --upgrade pip

# Install basic requirements
echo "Installing dependencies..."
cat > requirements.txt << EOF
# No external dependencies for core version
# RAGnostics Core runs with standard library only
EOF

echo "Setup complete!"
echo ""
echo "To use RAGnostics:"
echo "  source venv/bin/activate"
echo "  python3 ragnostics-core.py --docs your_files.pdf"
