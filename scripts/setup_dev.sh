#!/bin/bash
# Development Environment Setup Script
# This script sets up the development environment for Pai Note Exporter

set -e  # Exit on any error

echo "🚀 Setting up Pai Note Exporter development environment"
echo "======================================================"

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: pyproject.toml not found. Please run this script from the project root."
    exit 1
fi

echo "📁 Project root: $(pwd)"

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "🐍 Python version: $PYTHON_VERSION"

# Check if Python version is 3.11+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    echo "❌ Error: Python 3.11+ is required. Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python version check passed"

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
echo "✅ Virtual environment activated"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo "✅ Pip upgraded"

# Install the package in development mode
echo "📦 Installing package in development mode..."
pip install -e ".[dev]"
echo "✅ Package installed"

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
python -m playwright install chromium
echo "✅ Playwright browsers installed"

# Install pre-commit hooks
echo "🔗 Installing pre-commit hooks..."
pre-commit install
echo "✅ Pre-commit hooks installed"

# Generate secrets baseline
echo "🔒 Generating secrets baseline..."
detect-secrets scan > .secrets.baseline
echo "✅ Secrets baseline generated"

# Create .env.example if it doesn't exist
if [ ! -f ".env.example" ]; then
    echo "📝 Creating .env.example..."
    cat > .env.example << 'EOF'
# Plaud.ai Credentials (Required)
PLAUD_EMAIL=your-email@example.com
PLAUD_PASSWORD=your-password-here

# Logging Configuration (Optional)
LOG_LEVEL=INFO
LOG_FILE=pai_note_exporter.log

# Export Configuration (Optional)
EXPORT_DIR=exports

# API Configuration (Optional)
API_TIMEOUT=30

# Browser Configuration (Optional)
HEADLESS=true
BROWSER_TIMEOUT=30000
EOF
    echo "✅ .env.example created"
else
    echo "✅ .env.example already exists"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "✅ .env created (please edit with your credentials)"
else
    echo "✅ .env already exists"
fi

# Run initial checks
echo "🔍 Running initial checks..."

# Check if code can be imported
echo "Testing import..."
python -c "import pai_note_exporter; print('✅ Import successful')"

# Run basic linting check
echo "Running basic code quality check..."
if command -v ruff &> /dev/null; then
    ruff check src --quiet
    echo "✅ Code quality check passed"
else
    echo "⚠️  Ruff not found, skipping code quality check"
fi

# Create exports directory
mkdir -p exports
echo "📁 Exports directory created"

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Plaud.ai credentials"
echo "2. Run 'pytest' to execute tests"
echo "3. Run 'python -m pai_note_exporter.cli --help' to see available commands"
echo "4. Start developing!"
echo ""
echo "Useful commands:"
echo "  pytest                    # Run tests"
echo "  ruff check src           # Lint code"
echo "  black src                # Format code"
echo "  mypy src                 # Type check"
echo "  pre-commit run --all-files  # Run all checks"