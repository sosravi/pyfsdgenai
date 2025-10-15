#!/bin/bash
# PyFSD GenAI - Development Environment Setup Script

set -e  # Exit on any error

echo "🚀 Setting up PyFSD GenAI Development Environment..."

# Check if Python 3.9+ is available
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9+ is required. Found: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install core dependencies first
echo "📦 Installing core dependencies..."
pip install fastapi uvicorn pydantic pytest docker python-dotenv

# Install additional dependencies
echo "📦 Installing additional dependencies..."
pip install pytest-cov pytest-asyncio pytest-xdist pytest-mock hypothesis

# Install remaining dependencies from requirements.txt
echo "📦 Installing remaining dependencies..."
pip install -r requirements.txt

# Verify installation
echo "🔍 Verifying installation..."
python -c "import fastapi, pydantic, pytest, docker; print('✅ Core packages imported successfully')"

# Run basic tests
echo "🧪 Running basic environment tests..."
python -m pytest tests/unit/test_development_environment.py::TestDevelopmentEnvironment::test_required_packages_available -v

echo "🎉 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Run tests: python -m pytest tests/unit/test_development_environment.py -v"
echo "3. Start development server: python src/main.py"
echo ""
echo "🔗 Useful commands:"
echo "- Run all tests: pytest"
echo "- Run with coverage: pytest --cov=src"
echo "- Format code: black src/ tests/"
echo "- Lint code: flake8 src/ tests/"

