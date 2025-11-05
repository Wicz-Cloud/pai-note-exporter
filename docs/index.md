# Pai Note Exporter

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/pai-note-exporter.svg)](https://pypi.org/project/pai-note-exporter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://wicz-cloud.github.io/pai-note-exporter/)

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

## ✨ Features

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

## 🚀 Quick Start

### Installation

```bash
pip install pai-note-exporter
```

### Basic Usage

```bash
# Interactive export
pai-note-exporter export

# Export all recordings
pai-note-exporter export --all

# Export with audio files
pai-note-exporter export --include-audio
```

### Python API

```python
import asyncio
from pai_note_exporter.config import Config
from pai_note_exporter.login import login
from pai_note_exporter.export import PlaudAIExporter

async def main():
    config = Config.from_env()
    token = await login(config)
    exporter = PlaudAIExporter(token, config)

    files = await exporter.list_files()
    if files:
        await exporter.download_file(files[0], include_audio=True)

asyncio.run(main())
```

## 📖 Documentation

- [📚 Full Documentation](https://wicz-cloud.github.io/pai-note-exporter/)
- [🚀 Getting Started](installation.md)
- [⚙️ Configuration](configuration.md)
- [🛠️ CLI Usage](cli-usage.md)
- [🐍 Python API](python-api.md)
- [🔧 Troubleshooting](troubleshooting.md)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/Wicz-Cloud/pai-note-exporter/blob/master/LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [httpx](https://www.python-httpx.org/) for async HTTP API calls
- Uses [python-dotenv](https://github.com/theskumar/python-dotenv) for environment variable management
- Powered by [Playwright](https://playwright.dev/) for browser automation