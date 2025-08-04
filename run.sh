#!/bin/bash
# PDF to Markdown Converter - Run Helper
# This script ensures virtual environment is active and uses correct Python

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run: python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source .venv/bin/activate

# Verify PyMuPDF is available
if ! python3 -c "import fitz" 2>/dev/null; then
    echo "❌ PyMuPDF not found. Installing..."
    python3 -m pip install PyMuPDF
fi

echo "✅ Running PDF to Markdown converter..."
python3 main.py "$@"