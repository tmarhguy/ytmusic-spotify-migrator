#!/bin/bash
# Development setup script

set -e

echo "🚀 Setting up YT2Spot development environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python $required_version or higher is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
echo "📚 Installing YT2Spot in development mode..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# Create sample config if it doesn't exist
if [ ! -f ".yt2spot.toml" ]; then
    echo "⚙️  Creating sample configuration..."
    python -c "
from yt2spot.config import ConfigManager
from pathlib import Path
manager = ConfigManager()
manager.create_sample_config(Path('.yt2spot.toml'))
"
fi

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "🔐 Creating .env file from example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your Spotify credentials!"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Spotify API credentials"
echo "2. Edit .yt2spot.toml to customize default settings"
echo "3. Run: source venv/bin/activate"
echo "4. Run: yt2spot --help"
echo ""
echo "For testing:"
echo "- Run tests: pytest"
echo "- Run linting: ruff check ."
echo "- Run type checking: mypy yt2spot"
echo "- Format code: black ."
