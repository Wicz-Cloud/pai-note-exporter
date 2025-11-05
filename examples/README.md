# Usage Examples

This directory contains example scripts demonstrating how to use the Pai Note Exporter library.

## Examples Overview

### `basic_usage.py`

A simple example showing the fundamental usage of the library:

- Loading configuration from environment
- Authenticating with Plaud.ai
- Listing available recordings
- Exporting a single recording

**Use this example to:**
- Get started quickly
- Understand the basic workflow
- Test your setup

### `advanced_usage.py`

A comprehensive example demonstrating advanced features:

- Custom configuration
- Filtering recordings by criteria
- Batch processing with progress tracking
- Error handling and retries
- Concurrent downloads

**Use this example to:**
- Process large numbers of recordings
- Implement custom filtering logic
- Handle production workloads
- Monitor export progress

## Running the Examples

### Prerequisites

1. Install the package in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

2. Install Playwright browsers:
   ```bash
   python -m playwright install chromium
   ```

3. Set up your `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env with your Plaud.ai credentials
   ```

### Running Basic Example

```bash
cd examples
python basic_usage.py
```

### Running Advanced Example

```bash
cd examples
python advanced_usage.py
```

The advanced example will prompt for confirmation before exporting files.

## Customization

### Modifying Examples

Both examples can be customized by:

1. **Changing configuration**: Modify the `Config` object parameters
2. **Adjusting filters**: In `advanced_usage.py`, modify the criteria in `get_recordings_with_criteria()`
3. **Batch sizes**: Change `batch_size` parameter for concurrent processing
4. **Export options**: Set `include_audio=True` to download audio files

### Creating New Examples

Use these examples as templates for your own scripts:

```python
import asyncio
from pai_note_exporter.config import Config
from pai_note_exporter.login import login
from pai_note_exporter.export import PlaudAIExporter

async def my_custom_export():
    # Your custom logic here
    pass

if __name__ == "__main__":
    asyncio.run(my_custom_export())
```

## Common Patterns

### Authentication Pattern

```python
config = Config.from_env()
token = await login(config)
exporter = PlaudAIExporter(token, config)
```

### File Processing Pattern

```python
files = await exporter.list_files()
for file_info in files:
    await exporter.download_file(file_info, include_audio=False)
```

### Error Handling Pattern

```python
try:
    await exporter.download_file(file_info, include_audio=False)
except PlaudAIError as e:
    print(f"Export failed: {e}")
    # Handle error appropriately
```

### Progress Tracking Pattern

```python
total = len(files)
for i, file_info in enumerate(files, 1):
    print(f"Processing {i}/{total}: {file_info['name']}")
    await exporter.download_file(file_info, include_audio=False)
```

## Best Practices

1. **Start with basic example**: Use `basic_usage.py` to verify your setup
2. **Test with small batches**: Use limits when testing with real data
3. **Handle errors gracefully**: Implement proper error handling for production use
4. **Monitor progress**: Add progress indicators for long-running operations
5. **Respect rate limits**: Add delays between operations when processing many files
6. **Clean up resources**: Ensure proper cleanup of connections and files

## Troubleshooting

### Common Issues

- **Authentication fails**: Check credentials in `.env` file
- **No recordings found**: Verify you have recordings in Plaud.ai
- **Export errors**: Check file permissions and disk space
- **Slow performance**: Reduce batch size or add delays

### Debug Mode

Enable debug logging for troubleshooting:

```bash
export LOG_LEVEL=DEBUG
python examples/basic_usage.py
```

## Contributing

When adding new examples:

1. Follow the existing code style
2. Include comprehensive docstrings
3. Add error handling
4. Update this README
5. Test with both transcribed and non-transcribed recordings