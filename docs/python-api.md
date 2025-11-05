# Python API Reference

Complete API reference for using Pai Note Exporter as a Python library.

## Installation

```bash
pip install pai-note-exporter
```

Or for development:

```bash
git clone https://github.com/Wicz-Cloud/pai-note-exporter.git
cd pai-note-exporter
pip install -e .
```

## Quick Start

```python
from pai_note_exporter import PlaudClient, Exporter

# Initialize client
client = PlaudClient(
    email="your-email@example.com",
    password="your-password"
)

# Login
await client.login()

# Export recordings
exporter = Exporter(client)
recordings = await exporter.get_recordings()

for recording in recordings:
    transcription = await exporter.export_transcription(recording)
    print(f"Exported: {recording.name}")
```

## Core Classes

### PlaudClient

Main client for interacting with Plaud.ai API.

#### Constructor

```python
PlaudClient(
    email: str,
    password: str,
    timeout: float = 30.0,
    session: Optional[aiohttp.ClientSession] = None
)
```

**Parameters:**
- `email`: Plaud.ai account email
- `password`: Plaud.ai account password
- `timeout`: Request timeout in seconds (default: 30.0)
- `session`: Optional aiohttp session for custom configuration

#### Methods

##### async login() -> bool

Authenticate with Plaud.ai API.

**Returns:** `True` if login successful, `False` otherwise

**Raises:**
- `AuthenticationError`: Invalid credentials
- `NetworkError`: Connection issues

**Example:**
```python
client = PlaudClient("user@example.com", "password")
success = await client.login()
if success:
    print("Login successful")
```

##### async get_recordings(limit: Optional[int] = None) -> List[Recording]

Fetch available recordings from account.

**Parameters:**
- `limit`: Maximum number of recordings to fetch (optional)

**Returns:** List of `Recording` objects

**Raises:**
- `AuthenticationError`: Not logged in
- `NetworkError`: API request failed

**Example:**
```python
recordings = await client.get_recordings(limit=10)
for recording in recordings:
    print(f"{recording.name}: {recording.duration}s")
```

##### async get_recording_details(recording_id: str) -> Recording

Get detailed information about a specific recording.

**Parameters:**
- `recording_id`: Unique recording identifier

**Returns:** `Recording` object with full details

**Raises:**
- `AuthenticationError`: Not logged in
- `NotFoundError`: Recording not found
- `NetworkError`: API request failed

##### async download_audio(recording_id: str, output_path: str) -> bool

Download audio file for a recording.

**Parameters:**
- `recording_id`: Recording identifier
- `output_path`: Local file path to save audio

**Returns:** `True` if download successful

**Raises:**
- `AuthenticationError`: Not logged in
- `NotFoundError`: Recording not found
- `NetworkError`: Download failed

**Example:**
```python
success = await client.download_audio(
    "rec_123",
    "/path/to/recording.mp3"
)
```

##### async close()

Close the client session and cleanup resources.

**Example:**
```python
await client.close()
```

### Exporter

High-level export functionality.

#### Constructor

```python
Exporter(
    client: PlaudClient,
    output_dir: str = "exports",
    include_audio: bool = False
)
```

**Parameters:**
- `client`: Authenticated `PlaudClient` instance
- `output_dir`: Directory to save exported files (default: "exports")
- `include_audio`: Whether to download audio files (default: False)

#### Methods

##### async export_all() -> ExportResult

Export all available recordings.

**Returns:** `ExportResult` with summary statistics

**Raises:**
- `AuthenticationError`: Client not authenticated
- `ExportError`: Export process failed

**Example:**
```python
result = await exporter.export_all()
print(f"Exported {result.successful} recordings")
```

##### async export_recording(recording: Recording) -> bool

Export a single recording.

**Parameters:**
- `recording`: `Recording` object to export

**Returns:** `True` if export successful

**Raises:**
- `ExportError`: Export failed

**Example:**
```python
recording = recordings[0]
success = await exporter.export_recording(recording)
```

##### async export_transcription(recording: Recording) -> str

Export only the transcription text.

**Parameters:**
- `recording`: Recording to export

**Returns:** Transcription text content

**Raises:**
- `ExportError`: Export failed

##### async export_audio(recording: Recording) -> bool

Export only the audio file.

**Parameters:**
- `recording`: Recording to export

**Returns:** `True` if successful

**Raises:**
- `ExportError`: Export failed

##### get_export_path(recording: Recording, extension: str) -> str

Generate file path for exported recording.

**Parameters:**
- `recording`: Recording object
- `extension`: File extension (e.g., "txt", "mp3")

**Returns:** Full file path string

**Example:**
```python
path = exporter.get_export_path(recording, "txt")
# Returns: "exports/recording_2025-01-01_12-00-00.txt"
```

## Data Models

### Recording

Represents a Plaud.ai recording.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `id` | `str` | Unique recording identifier |
| `name` | `str` | Recording name/timestamp |
| `duration` | `int` | Duration in seconds |
| `size` | `int` | File size in bytes |
| `created_at` | `datetime` | Creation timestamp |
| `status` | `str` | Processing status ("transcribed", "processing", etc.) |
| `has_audio` | `bool` | Whether audio file is available |
| `has_transcription` | `bool` | Whether transcription is available |

#### Methods

##### is_transcribed() -> bool

Check if recording has completed transcription.

**Returns:** `True` if transcription is available

##### get_filename(extension: str = "txt") -> str

Get standardized filename for the recording.

**Parameters:**
- `extension`: File extension (default: "txt")

**Returns:** Filename string

**Example:**
```python
filename = recording.get_filename("mp3")
# Returns: "recording_2025-01-01_12-00-00.mp3"
```

### ExportResult

Summary of an export operation.

#### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `total` | `int` | Total recordings processed |
| `successful` | `int` | Number of successful exports |
| `failed` | `int` | Number of failed exports |
| `skipped` | `int` | Number of skipped recordings |
| `errors` | `List[str]` | List of error messages |
| `duration` | `float` | Total export time in seconds |

#### Methods

##### success_rate() -> float

Calculate success rate as percentage.

**Returns:** Success rate (0.0 to 100.0)

**Example:**
```python
rate = result.success_rate()
print(f"Success rate: {rate:.1f}%")
```

## Exceptions

### AuthenticationError

Raised when authentication fails.

```python
class AuthenticationError(Exception):
    """Authentication failed"""
    pass
```

### NetworkError

Raised for network-related issues.

```python
class NetworkError(Exception):
    """Network request failed"""
    pass
```

### ExportError

Raised when export operations fail.

```python
class ExportError(Exception):
    """Export operation failed"""
    pass
```

### NotFoundError

Raised when requested resource doesn't exist.

```python
class NotFoundError(Exception):
    """Resource not found"""
    pass
```

## Advanced Usage

### Custom Session Configuration

```python
import aiohttp

# Custom session with proxy
connector = aiohttp.TCPConnector(limit=10)
session = aiohttp.ClientSession(connector=connector)

client = PlaudClient(
    email="user@example.com",
    password="password",
    session=session
)

# Use client...
await client.close()
```

### Async Context Manager

```python
from pai_note_exporter import PlaudClient, Exporter

async with PlaudClient("email", "password") as client:
    await client.login()

    exporter = Exporter(client)
    result = await exporter.export_all()

    print(f"Exported {result.successful} recordings")
```

### Progress Callbacks

```python
from typing import Callable

async def progress_callback(recording: Recording, current: int, total: int):
    print(f"Processing {current}/{total}: {recording.name}")

exporter = Exporter(client)
# Note: Progress callbacks not yet implemented in base version
# This is a planned feature for future releases
```

### Batch Processing

```python
import asyncio
from pai_note_exporter import PlaudClient, Exporter

async def batch_export(batch_size: int = 5):
    async with PlaudClient("email", "password") as client:
        await client.login()

        exporter = Exporter(client)
        recordings = await client.get_recordings()

        for i in range(0, len(recordings), batch_size):
            batch = recordings[i:i + batch_size]

            tasks = [
                exporter.export_recording(recording)
                for recording in batch
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results...
            successful = sum(1 for r in results if r is True)
            print(f"Batch {i//batch_size + 1}: {successful}/{len(batch)} successful")

            # Optional delay between batches
            await asyncio.sleep(1)

asyncio.run(batch_export())
```

### Error Handling

```python
from pai_note_exporter import (
    PlaudClient, Exporter,
    AuthenticationError, NetworkError, ExportError
)

async def robust_export():
    try:
        async with PlaudClient("email", "password") as client:
            await client.login()

            exporter = Exporter(client)
            result = await exporter.export_all()

    except AuthenticationError as e:
        print(f"Authentication failed: {e}")
        return False

    except NetworkError as e:
        print(f"Network error: {e}")
        # Could retry with backoff here
        return False

    except ExportError as e:
        print(f"Export failed: {e}")
        return False

    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

    return True
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PLAUD_EMAIL` | Account email | - |
| `PLAUD_PASSWORD` | Account password | - |
| `PLAUD_TIMEOUT` | API timeout (seconds) | 30.0 |
| `PLAUD_EXPORT_DIR` | Export directory | exports |
| `PLAUD_INCLUDE_AUDIO` | Include audio files | false |

### Programmatic Configuration

```python
import os
from pai_note_exporter import PlaudClient, Exporter

# Load from environment
client = PlaudClient(
    email=os.getenv("PLAUD_EMAIL"),
    password=os.getenv("PLAUD_PASSWORD"),
    timeout=float(os.getenv("PLAUD_TIMEOUT", "30.0"))
)

exporter = Exporter(
    client=client,
    output_dir=os.getenv("PLAUD_EXPORT_DIR", "exports"),
    include_audio=os.getenv("PLAUD_INCLUDE_AUDIO", "false").lower() == "true"
)
```

## Performance Considerations

### Connection Pooling

```python
import aiohttp

# Configure connection pooling
connector = aiohttp.TCPConnector(
    limit=20,          # Max concurrent connections
    limit_per_host=5,  # Max per host
    ttl_dns_cache=300  # DNS cache TTL
)

session = aiohttp.ClientSession(connector=connector)
client = PlaudClient("email", "password", session=session)
```

### Memory Management

```python
# For large exports, process in chunks
recordings = await client.get_recordings()
chunk_size = 10

for i in range(0, len(recordings), chunk_size):
    chunk = recordings[i:i + chunk_size]

    # Process chunk
    tasks = [exporter.export_recording(r) for r in chunk]
    await asyncio.gather(*tasks)

    # Force garbage collection if needed
    import gc
    gc.collect()
```

### Rate Limiting

```python
import asyncio

# Add delays between requests
async def export_with_delay(recordings, delay: float = 1.0):
    for recording in recordings:
        await exporter.export_recording(recording)
        await asyncio.sleep(delay)
```

## Testing

### Mock Client for Testing

```python
from unittest.mock import AsyncMock, MagicMock
from pai_note_exporter import PlaudClient

# Create mock client
mock_client = MagicMock(spec=PlaudClient)
mock_client.login = AsyncMock(return_value=True)
mock_client.get_recordings = AsyncMock(return_value=[
    Recording(id="1", name="test", duration=60, ...)
])

# Use in tests
exporter = Exporter(mock_client)
result = await exporter.export_all()
```

## Migration Guide

### From v0.1.x to v0.2.x

```python
# Old way (v0.1.x)
from pai_note_exporter import PlaudAPI

api = PlaudAPI()
api.login("email", "password")
recordings = api.get_all_recordings()

# New way (v0.2.x)
from pai_note_exporter import PlaudClient

client = PlaudClient("email", "password")
await client.login()
recordings = await client.get_recordings()
```

Key changes:
- All methods are now async
- `PlaudAPI` renamed to `PlaudClient`
- Context manager support added
- Improved error handling
- Better type hints
