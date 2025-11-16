#!/bin/bash
# Setup script for TDDRAGON Python environment

set -e

echo "🐉 Setting up TDDRAGON Python environment..."

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install development dependencies
echo "Installing development dependencies..."
pip install -r requirements-dev.txt

# Verify installation
echo ""
echo "Verifying installation..."
echo "pytest version: $(pytest --version)"
echo "black version: $(black --version)"
echo "mypy version: $(mypy --version)"
echo "ruff version: $(ruff --version)"

# Run initial tests
echo ""
echo "Running initial tests..."
pytest tests/ -v

echo ""
echo "✅ Setup complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To format code:"
echo "  black src tests"
echo "  isort src tests"
echo ""
echo "To lint code:"
echo "  ruff check src tests"
echo "  mypy src"

