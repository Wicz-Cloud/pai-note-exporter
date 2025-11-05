# Installation

This guide will help you install Pai Note Exporter on your system.

## Requirements

- Python 3.11 or higher
- pip (Python package manager)

## Install from PyPI

The easiest way to install Pai Note Exporter is from PyPI:

```bash
pip install pai-note-exporter
```

## Install from Source

If you want to install from source or contribute to development:

### 1. Clone the repository

```bash
git clone https://github.com/Wicz-Cloud/pai-note-exporter.git
cd pai-note-exporter
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install the package

```bash
# Install with dependencies
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"
```

### 4. Install Playwright browsers (required for authentication)

```bash
python -m playwright install chromium
```

## Verify Installation

After installation, verify that Pai Note Exporter is working:

```bash
pai-note-exporter --version
```

You should see output similar to:
```
Pai Note Exporter v0.1.0
```

## Development Setup

If you're planning to contribute to the project:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Generate secrets baseline
detect-secrets scan > .secrets.baseline

# Run tests to ensure everything works
pytest
```

## System Dependencies

### Linux

On Ubuntu/Debian:

```bash
sudo apt-get update
sudo apt-get install -y \
    gconf-service \
    libasound2-dev \
    libatk1.0-dev \
    libcairo2-dev \
    libcups2-dev \
    libfontconfig1-dev \
    libgdk-pixbuf2.0-dev \
    libgtk-3-dev \
    libnspr4-dev \
    libpango-1.0-dev \
    libxss1 \
    fonts-liberation \
    libappindicator1 \
    xdg-utils
```

### macOS

Most dependencies are handled automatically by pip and Playwright.

### Windows

Most dependencies are handled automatically by pip and Playwright.

## Troubleshooting Installation

### Common Issues

**"Python version not supported"**
- Ensure you're using Python 3.11 or higher
- Check your Python version: `python --version`

**"Playwright browsers not found"**
- Run: `python -m playwright install chromium`
- Ensure you have sufficient disk space

**"Permission denied"**
- Try installing in a virtual environment
- On Linux/macOS, you might need `sudo` for system packages

**"Import error after installation"**
- Try reinstalling: `pip uninstall pai-note-exporter && pip install pai-note-exporter`
- Ensure you're using the correct Python interpreter

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Search existing [GitHub Issues](https://github.com/Wicz-Cloud/pai-note-exporter/issues)
3. Create a new issue with your system information and error details