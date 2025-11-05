# API Documentation

This document provides detailed API documentation for the Pai Note Exporter library.

## Overview

Pai Note Exporter provides both a command-line interface and a Python API for exporting recordings and transcriptions from Plaud.ai.

## Python API

### Core Classes

#### `Config`

Configuration management class that handles environment variables and settings.

```python
from pai_note_exporter.config import Config

# Load configuration from .env file
config = Config.from_env()

# Or create manually
config = Config(
    email="user@example.com",
    password="password",
    log_level="INFO",
    export_dir="exports"
)
```

**Methods:**
- `from_env(cls, env_file: str = ".env") -> Config`: Load configuration from environment file
- `validate(self) -> None`: Validate configuration values

**Attributes:**
- `email: str` - Plaud.ai account email
- `password: str` - Plaud.ai account password
- `log_level: str` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_file: Optional[str]` - Path to log file
- `export_dir: str` - Directory for exported files
- `api_timeout: int` - API request timeout in seconds
- `headless: bool` - Whether to run browser in headless mode
- `browser_timeout: int` - Browser operation timeout in milliseconds

#### `PlaudAIExporter`

Main exporter class for interacting with Plaud.ai API.

```python
from pai_note_exporter.export import PlaudAIExporter

# Initialize with access token
exporter = PlaudAIExporter(access_token, config)

# List available recordings
files = await exporter.list_files()

# Download a specific file
await exporter.download_file(file_info, include_audio=True)
```

**Methods:**
- `__init__(self, token: str, config: Config)`: Initialize exporter
- `list_files(self) -> List[Dict]`: Get list of available recordings
- `download_file(self, file_info: Dict, include_audio: bool = False) -> None`: Download a recording
- `download_transcription(self, file_id: str) -> str`: Download transcription text

**Raises:**
- `APIError`: For API request failures
- `ExportError`: For download failures
- `AuthenticationError`: For authentication issues

### Authentication

#### `login`

Authenticate with Plaud.ai and obtain access token.

```python
from pai_note_exporter.login import login

token = await login(config)
```

**Parameters:**
- `config: Config` - Configuration object with credentials

**Returns:**
- `str`: Access token for API calls

**Raises:**
- `AuthenticationError`: For login failures
- `TimeoutError`: For browser timeouts

### Error Handling

The library defines custom exceptions for different error types:

- `ConfigurationError`: Invalid or missing configuration
- `AuthenticationError`: Login failures or invalid credentials
- `APIError`: API request failures or invalid responses
- `ExportError`: File export or download failures

All exceptions inherit from `PlaudAIError`.

### Logging

The library uses Python's logging module with configurable levels and file output.

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pai_note_exporter")
```

## CLI Interface

The command-line interface provides easy access to all functionality:

```bash
# Interactive export
pai-note-exporter export

# Non-interactive export of all files
pai-note-exporter export --all

# Export with audio files
pai-note-exporter export --include-audio

# Skip transcription export
pai-note-exporter export --skip-transcription

# Limit number of files
pai-note-exporter export --limit 5

# Set custom log level
pai-note-exporter export --log-level DEBUG
```

## Examples

### Basic Usage

```python
import asyncio
from pai_note_exporter.config import Config
from pai_note_exporter.login import login
from pai_note_exporter.export import PlaudAIExporter

async def main():
    # Load configuration
    config = Config.from_env()

    # Authenticate
    token = await login(config)
    print("Authentication successful!")

    # Create exporter
    exporter = PlaudAIExporter(token, config)

    # List recordings
    files = await exporter.list_files()
    print(f"Found {len(files)} recordings")

    # Download first recording
    if files:
        await exporter.download_file(files[0], include_audio=True)
        print("Download complete!")

if __name__ == "__main__":
    asyncio.run(main())
```

### Custom Configuration

```python
from pai_note_exporter.config import Config

config = Config(
    email="user@example.com",
    password="secure_password",
    log_level="DEBUG",
    export_dir="./my_exports",
    api_timeout=60
)
```

## Data Structures

### File Info

Recording metadata returned by `list_files()`:

```python
{
    "id": "file_id",
    "name": "recording_name",
    "duration": 3600,  # seconds
    "size": 1048576,   # bytes
    "created_at": "2023-10-01T12:00:00Z",
    "is_trans": True,  # whether transcription is available
    "transcription_status": "completed"
}
```

## Rate Limits

- API requests are subject to Plaud.ai rate limits
- The library includes automatic retry logic for transient failures
- Consider adding delays between bulk operations

## Security Considerations

- Never commit credentials to version control
- Use environment variables for sensitive configuration
- Store credentials securely (keyring, secret managers)
- Regularly rotate credentials
- Monitor account for unauthorized access