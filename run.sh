#!/bin/bash
# PDF to Markdown Converter - Run Helper
# This script ensures virtual environment is active and uses correct Python

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Please install it first: https://python-poetry.org/docs/#installation"
    echo "   Or run: curl -sSL https://install.python-poetry.org | python3 -"
    exit 1
fi

echo "📦 Installing/Updating dependencies with Poetry..."
# This handles the python version check automatically based on pyproject.toml
if ! poetry install; then
    echo "❌ Poetry install failed. Please check the errors above."
    echo "💡 Note: You need Python 3.10, 3.11, or 3.12 installed on your system."
    exit 1
fi

echo "✅ Running PDF to Markdown converter..."
# Run the script within the poetry environment
poetry run python main.py "$@"