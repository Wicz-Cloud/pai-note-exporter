# Configuration

Learn how to configure Pai Note Exporter for your needs.

## Configuration Methods

### Environment Variables (.env file)

The recommended way to configure Pai Note Exporter is using environment variables in a `.env` file:

```bash
# Create .env file
cp .env.example .env
# Edit with your values
```

### Environment Variables

```env
# Required Credentials
PLAUD_EMAIL=your-email@example.com
PLAUD_PASSWORD=your-password-here

# Optional Settings
LOG_LEVEL=INFO
LOG_FILE=pai_note_exporter.log
EXPORT_DIR=exports
API_TIMEOUT=30
HEADLESS=true
BROWSER_TIMEOUT=30000
```

## Configuration Options

### Required Settings

| Variable | Description | Example |
|----------|-------------|---------|
| `PLAUD_EMAIL` | Your Plaud.ai email address | `user@example.com` |
| `PLAUD_PASSWORD` | Your Plaud.ai password | `your-secure-password` |

### Optional Settings

#### Logging

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `LOG_LEVEL` | Logging verbosity | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_FILE` | Path to log file | `pai_note_exporter.log` | Any valid file path |

#### Export

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `EXPORT_DIR` | Directory for exported files | `exports` | Any valid directory path |

#### API

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `API_TIMEOUT` | API request timeout (seconds) | `30` | Positive integer |

#### Browser

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `HEADLESS` | Run browser in headless mode | `true` | `true`, `false` |
| `BROWSER_TIMEOUT` | Browser operation timeout (ms) | `30000` | Positive integer |

## Configuration Examples

### Development Configuration

```env
# Development settings with verbose logging
PLAUD_EMAIL=dev@example.com
PLAUD_PASSWORD=dev-password
LOG_LEVEL=DEBUG
LOG_FILE=dev.log
EXPORT_DIR=./dev-exports
HEADLESS=false
```

### Production Configuration

```env
# Production settings with minimal logging
PLAUD_EMAIL=prod@example.com
PLAUD_PASSWORD=prod-password
LOG_LEVEL=WARNING
LOG_FILE=/var/log/pai-note-exporter.log
EXPORT_DIR=/data/exports
API_TIMEOUT=60
BROWSER_TIMEOUT=60000
```

### CI/CD Configuration

```env
# CI/CD settings for automated testing
PLAUD_EMAIL=test@example.com
PLAUD_PASSWORD=test-password
LOG_LEVEL=INFO
LOG_FILE=ci.log
EXPORT_DIR=./test-exports
HEADLESS=true
API_TIMEOUT=45
```

## Programmatic Configuration

You can also configure Pai Note Exporter programmatically in Python:

```python
from pai_note_exporter.config import Config

# Create configuration manually
config = Config(
    email="user@example.com",
    password="secure-password",
    log_level="DEBUG",
    export_dir="./my-exports",
    api_timeout=60,
    headless=True
)

# Or load from environment with defaults
config = Config.from_env()

# Override specific settings
config.export_dir = "/custom/path"
config.log_level = "WARNING"
```

## Configuration Validation

Pai Note Exporter validates your configuration on startup:

```python
from pai_note_exporter.config import Config

config = Config.from_env()
try:
    config.validate()
    print("✅ Configuration is valid")
except Exception as e:
    print(f"❌ Configuration error: {e}")
```

## Security Best Practices

### Credential Management

- **Never commit `.env` files** to version control
- Use strong, unique passwords
- Rotate credentials regularly
- Consider using application-specific passwords
- Store credentials securely (password managers, secret managers)

### File Permissions

```bash
# Set restrictive permissions on .env file
chmod 600 .env

# Create export directory with appropriate permissions
mkdir -p exports
chmod 755 exports
```

### Environment Separation

Use different configurations for different environments:

```bash
# Development
cp .env.example .env.dev

# Production
cp .env.example .env.prod

# Use appropriate file
pai-note-exporter export --env-file .env.prod
```

## Advanced Configuration

### Custom Export Directories

```python
import os
from datetime import datetime

# Dynamic export directory based on date
date_str = datetime.now().strftime("%Y-%m-%d")
export_dir = f"./exports/{date_str}"

config = Config.from_env()
config.export_dir = export_dir

# Ensure directory exists
os.makedirs(export_dir, exist_ok=True)
```

### Conditional Configuration

```python
import os

config = Config.from_env()

# Adjust settings based on environment
if os.getenv("CI") == "true":
    config.headless = True
    config.log_level = "WARNING"
elif os.getenv("DEBUG") == "true":
    config.headless = False
    config.log_level = "DEBUG"
    config.browser_timeout = 60000
```

## Troubleshooting Configuration

### Common Issues

**"Configuration file not found"**
```bash
# Create .env file
touch .env
# Or copy from example
cp .env.example .env
```

**"Invalid configuration"**
- Check for typos in variable names
- Ensure values are in correct format
- Verify file paths exist and are writable

**"Permission denied"**
- Check file permissions on `.env` file
- Ensure export directory is writable
- Verify log file directory permissions

### Debugging Configuration

Enable debug logging to troubleshoot configuration issues:

```bash
# In .env file
LOG_LEVEL=DEBUG

# Or via command line
pai-note-exporter export --log-level DEBUG
```

Check the log file for configuration-related messages:
```
2025-01-01 12:00:00 - pai_note_exporter.config - DEBUG - Loading configuration from .env
2025-01-01 12:00:01 - pai_note_exporter.config - INFO - Configuration validated successfully
```