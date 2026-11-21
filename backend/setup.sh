#!/bin/bash
# ============================================================
# Healthcare PII Anonymizer - Backend Setup Script (Unix/macOS)
# ============================================================

set -e

echo "============================================"
echo "  Healthcare PII Anonymizer - Backend Setup"
echo "============================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1)
echo "✅ Found $PYTHON_VERSION"

# Navigate to backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "📁 Working directory: $(pwd)"
echo ""

# Create virtual environment
echo "🐍 Creating virtual environment..."
if [ -d "venv" ]; then
    echo "   Virtual environment already exists. Skipping creation."
else
    python3 -m venv venv
    echo "   Virtual environment created successfully."
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt --quiet
echo "   Requirements installed successfully."

# Download spaCy model
echo "🧠 Downloading spaCy language model (en_core_web_sm)..."
python3 -m spacy download en_core_web_sm --quiet
echo "   spaCy model downloaded successfully."

# Create .env from .env.example if it doesn't exist
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
        echo "   .env file created. Please update it with your API keys."
    else
        echo "⚠️  No .env.example found. Skipping .env creation."
    fi
else
    echo "📝 .env file already exists. Skipping."
fi

# Create sample_data directory if needed
if [ ! -d "sample_data" ]; then
    mkdir -p sample_data
fi

echo ""
echo "============================================"
echo "  ✅ Setup complete!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Update backend/.env with your API keys"
echo "  2. Run the server: uvicorn main:app --reload"
echo ""
