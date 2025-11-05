# Quick Start

Get up and running with Pai Note Exporter in minutes.

## Prerequisites

- Python 3.11+
- Plaud.ai account with recordings

## 1. Installation

```bash
pip install pai-note-exporter
```

## 2. Configuration

Create a `.env` file in your project directory:

```bash
# Create .env file
touch .env
```

Edit `.env` with your Plaud.ai credentials:

```env
# Required
PLAUD_EMAIL=your-email@example.com
PLAUD_PASSWORD=your-password-here

# Optional
LOG_LEVEL=INFO
EXPORT_DIR=./exports
```

## 3. First Export

### Interactive Mode (Recommended for first use)

```bash
pai-note-exporter export
```

This will:
1. Prompt you to select recordings to export
2. Show progress during export
3. Save files to the `exports` directory

### Non-Interactive Mode

```bash
# Export all recordings
pai-note-exporter export --all

# Export with audio files
pai-note-exporter export --include-audio

# Export specific number of recordings
pai-note-exporter export --limit 5
```

## 4. Check Your Results

After export, check the `exports` directory:

```bash
ls -la exports/
```

You should see files like:
```
recording_2025-01-01_12-00-00.txt
recording_2025-01-01_12-00-00.mp3  # if --include-audio was used
```

## 5. Advanced Usage

### Export with Custom Settings

```bash
# Set custom log level
pai-note-exporter export --log-level DEBUG

# Use custom .env file
pai-note-exporter export --env-file /path/to/custom.env

# Skip transcription export
pai-note-exporter export --skip-transcription
```

### Python API Usage

```python
import asyncio
from pai_note_exporter.config import Config
from pai_note_exporter.login import login
from pai_note_exporter.export import PlaudAIExporter

async def quick_export():
    # Load configuration
    config = Config.from_env()

    # Authenticate
    token = await login(config)
    print("✅ Authentication successful")

    # Create exporter
    exporter = PlaudAIExporter(token, config)

    # List recordings
    files = await exporter.list_files()
    print(f"📁 Found {len(files)} recordings")

    # Export first recording
    if files:
        await exporter.download_file(files[0], include_audio=True)
        print("✅ Export completed")

# Run the export
asyncio.run(quick_export())
```

## Next Steps

- [Configure advanced options](configuration.md)
- [Learn CLI commands](cli-usage.md)
- [Explore Python API](api.md)
- [Check troubleshooting](troubleshooting.md) if you encounter issues

## Common Issues

**"Login failed"**
- Verify your Plaud.ai credentials in `.env`
- Check your internet connection

**"No recordings found"**
- Ensure you have recordings in your Plaud.ai account
- Check that you're logged into the correct account

**"Permission denied"**
- Ensure the export directory is writable
- Check file system permissions

For more help, see the [Troubleshooting Guide](troubleshooting.md).