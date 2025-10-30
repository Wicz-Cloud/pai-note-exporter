# Pai Note Exporter

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python 3.11+ program that authenticates with Plaud.ai API and exports recordings and transcriptions. This tool provides automated authentication and data export from Plaud.ai with comprehensive error handling, logging, and security features.

## ⚠️ Security Disclaimer

**IMPORTANT:** This tool handles sensitive authentication credentials. Please be aware of the following:

- **Never commit your `.env` file** containing actual credentials to version control
- Store credentials securely and use environment variables in production
- This tool is provided as-is without any guarantees of security or functionality
- Use at your own risk - automated login tools may violate Plaud.ai's Terms of Service
- The maintainers are not responsible for any account issues, data loss, or security breaches
- Regularly rotate your credentials and use strong, unique passwords
- Consider using application-specific passwords or API tokens if available
- Monitor your account for unauthorized access

## Features

- 🔐 Secure authentication with Plaud.ai API using Bearer tokens
- 📥 Export recordings and transcriptions from Plaud.ai
- 📝 Automatic transcription text processing and formatting
- 🎵 Audio file download with temporary URL generation
- 📚 Clean, readable transcription output (removes JSON wrappers, handles unicode)
- 📝 Comprehensive logging with configurable levels
- 🛡️ Robust error handling with custom exceptions
- ⚙️ Configuration via environment variables (.env file)
- 🧪 Full test coverage with pytest
- 🎨 Code quality tools (Black, isort, Ruff, mypy)
- 🔒 Pre-commit hooks with detect-secrets
- 📚 Clear documentation and docstrings
- 🚀 Easy CLI interface with interactive and non-interactive modes

## Requirements

- Python 3.11 or higher
- pip (Python package manager)

## Installation

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

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and add your Plaud.ai credentials
```

## Configuration

Create a `.env` file in the project root with your credentials:

```env
# Required
PLAUD_EMAIL=your-email@example.com
PLAUD_PASSWORD=your-password-here

# Optional
LOG_LEVEL=INFO
LOG_FILE=pai_note_exporter.log
HEADLESS=true
BROWSER_TIMEOUT=30000
```

### Configuration Options

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `PLAUD_EMAIL` | Your Plaud.ai email address | - | Yes |
| `PLAUD_PASSWORD` | Your Plaud.ai password | - | Yes |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | INFO | No |
| `LOG_FILE` | Path to log file | pai_note_exporter.log | No |
| `EXPORT_DIR` | Directory to save exported files | exports | No |
| `API_TIMEOUT` | API request timeout in seconds | 30 | No |

## Usage

### Command Line Interface

```bash
# Export recordings interactively (prompts for selection)
pai-note-exporter export

# Export all recordings without prompts (non-interactive)
pai-note-exporter export --all

# Export with audio files included
pai-note-exporter export --include-audio

# Skip transcription export (audio only)
pai-note-exporter export --skip-transcription

# Limit number of files to export
pai-note-exporter export --limit 5

# Export with specific .env file
pai-note-exporter export --env-file /path/to/.env

# Set log level
pai-note-exporter export --log-level DEBUG

# Show help
pai-note-exporter --help
```

### Python API

```python
import asyncio
from pai_note_exporter.config import Config
from pai_note_exporter.login import login
from pai_note_exporter.export import PlaudAIExporter

async def main():
    # Load configuration from .env
    config = Config.from_env()

    # Login and get access token
    token = await login(config)
    print("Successfully authenticated!")

    # Create exporter and list files
    exporter = PlaudAIExporter(token, config)
    files = await exporter.list_files()
    print(f"Found {len(files)} recordings")

    # Export specific file
    if files:
        await exporter.download_file(files[0], include_audio=True)
        print("File exported successfully!")

if __name__ == "__main__":
    asyncio.run(main())
```

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Generate secrets baseline
detect-secrets scan > .secrets.baseline
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/pai_note_exporter --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code with Black
black src tests

# Sort imports with isort
isort src tests

# Lint with Ruff
ruff check src tests

# Type check with mypy
mypy src

# Run all pre-commit hooks
pre-commit run --all-files
```

### Project Structure

```
pai-note-exporter/
├── src/
│   └── pai_note_exporter/
│       ├── __init__.py          # Package initialization
│       ├── cli.py               # Command-line interface
│       ├── config.py            # Configuration management
│       ├── exceptions.py        # Custom exceptions
│       ├── export.py            # Plaud.ai export functionality
│       ├── logger.py            # Logging setup
│       ├── login.py             # Plaud.ai API authentication
│       ├── text_processor.py    # Transcription text processing and formatting
│       └── audio_processor.py   # Audio file processing and summary generation
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_exceptions.py
│   ├── test_logger.py
│   ├── test_login.py
│   └── test_export.py
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore rules
├── .pre-commit-config.yaml      # Pre-commit hooks configuration
├── CHANGELOG.md                 # Version history
├── CONTRIBUTING.md              # Contribution guidelines
├── LICENSE                      # MIT License
├── README.md                    # This file
└── pyproject.toml              # Project configuration

```

## Error Handling

The application includes comprehensive error handling:

- **ConfigurationError**: Invalid or missing configuration
- **AuthenticationError**: Login failures or invalid credentials
- **APIError**: API request failures or invalid responses
- **ExportError**: File export or download failures
- **TimeoutError**: Operations that exceed timeout limits

All errors are logged with appropriate detail levels and include helpful error messages.

## Logging

Logs are written to both console and file (if configured). Log levels:

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages
- **ERROR**: Error messages
- **CRITICAL**: Critical errors

Example log output:
```
2025-10-29 12:00:00 - pai_note_exporter.login - INFO - Attempting API login...
2025-10-29 12:00:01 - pai_note_exporter.login - INFO - Login successful, received access token
2025-10-29 12:00:02 - pai_note_exporter.export - INFO - Listing available recordings...
2025-10-29 12:00:03 - pai_note_exporter.export - INFO - Found 5 recordings, downloading selected files...
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [httpx](https://www.python-httpx.org/) for async HTTP API calls
- Uses [python-dotenv](https://github.com/theskumar/python-dotenv) for environment variable management

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Remember:** Always handle credentials securely and never commit sensitive information to version control!
