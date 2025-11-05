# CLI Usage

Comprehensive guide to using Pai Note Exporter from the command line.

## Command Overview

```bash
pai-note-exporter [OPTIONS] COMMAND [ARGS]...
```

## Global Options

| Option | Description | Default |
|--------|-------------|---------|
| `--help` | Show help message and exit | - |
| `--version` | Show version information and exit | - |
| `--log-level LEVEL` | Set logging level | INFO |
| `--env-file PATH` | Path to .env file | .env |

## Commands

### export

Export recordings and transcriptions from Plaud.ai.

```bash
pai-note-exporter export [OPTIONS]
```

#### Export Options

| Option | Description | Default |
|--------|-------------|---------|
| `--all` | Export all recordings without prompting | - |
| `--include-audio` | Include audio files in export | `false` |
| `--skip-transcription` | Skip transcription export (audio only) | `false` |
| `--limit N` | Limit number of recordings to export | - |
| `--help` | Show export command help | - |

#### Export Examples

**Interactive export (recommended for first use):**
```bash
pai-note-exporter export
```

**Export all recordings:**
```bash
pai-note-exporter export --all
```

**Export with audio files:**
```bash
pai-note-exporter export --include-audio
```

**Export first 5 recordings:**
```bash
pai-note-exporter export --limit 5
```

**Audio-only export:**
```bash
pai-note-exporter export --skip-transcription --include-audio
```

**Debug mode:**
```bash
pai-note-exporter export --log-level DEBUG
```

**Custom configuration:**
```bash
pai-note-exporter export --env-file /path/to/custom.env
```

## Output and Files

### Export Directory Structure

```
exports/
├── recording_2025-01-01_12-00-00.txt      # Transcription
├── recording_2025-01-01_12-00-00.mp3      # Audio (if included)
├── recording_2025-01-01_12-05-30.txt      # Another transcription
└── pai_note_exporter.log                  # Log file
```

### File Naming Convention

Files are named using the recording timestamp:
```
recording_YYYY-MM-DD_HH-MM-SS.txt/mp3
```

Example: `recording_2025-01-01_14-30-15.txt`

### Log File

All operations are logged to `pai_note_exporter.log`:

```
2025-01-01 14:30:15 - pai_note_exporter.login - INFO - Attempting API login...
2025-01-01 14:30:16 - pai_note_exporter.login - INFO - Login successful
2025-01-01 14:30:17 - pai_note_exporter.export - INFO - Found 5 recordings
2025-01-01 14:30:18 - pai_note_exporter.export - INFO - Exporting recording_2025-01-01_14-30-15
2025-01-01 14:30:19 - pai_note_exporter.export - INFO - Export completed successfully
```

## Interactive Mode

When running without `--all`, Pai Note Exporter enters interactive mode:

```
Pai Note Exporter v0.1.0
========================

📁 Found 5 recordings

Recordings available for export:
┌────┬─────────────────────────────────────┬────────────┬─────────────┐
│ #  │ Name                                │ Duration   │ Status      │
├────┼─────────────────────────────────────┼────────────┼─────────────┤
│ 1  │ recording_2025-01-01_12-00-00       │ 45m 30s    │ transcribed │
│ 2  │ recording_2025-01-01_12-45-15       │ 32m 12s    │ transcribed │
│ 3  │ recording_2025-01-01_13-30-22       │ 18m 45s    │ processing  │
│ 4  │ recording_2025-01-01_14-15-08       │ 67m 23s    │ transcribed │
│ 5  │ recording_2025-01-01_15-00-01       │ 12m 34s    │ transcribed │
└────┴─────────────────────────────────────┴────────────┴─────────────┘

Enter recording numbers to export (comma-separated, 'all' for all, 'quit' to exit):
```

### Interactive Commands

- **Number**: Export specific recording (e.g., `1`)
- **Range**: Export range of recordings (e.g., `1-3`)
- **Multiple**: Export multiple recordings (e.g., `1,3,5`)
- **All**: Export all recordings (e.g., `all`)
- **Quit**: Exit without exporting (e.g., `quit`)

## Progress Indicators

Pai Note Exporter shows progress during long operations:

### Authentication
```
🔐 Authenticating with Plaud.ai...
✅ Authentication successful
```

### File Listing
```
📁 Listing recordings...
📁 Found 5 recordings
```

### Export Progress
```
📥 Exporting recordings...
├── 1/5: recording_2025-01-01_12-00-00 [████████████] 100%
├── 2/5: recording_2025-01-01_12-45-15 [████████████] 100%
├── 3/5: recording_2025-01-01_13-30-22 [████░░░░░░░░] 40% (waiting for transcription)
├── 4/5: recording_2025-01-01_14-15-08 [████████████] 100%
└── 5/5: recording_2025-01-01_15-00-01 [████████████] 100%

✅ Export completed: 5/5 files exported
```

## Error Handling

### Common Errors

**Authentication Failed:**
```
❌ Authentication failed: Invalid credentials
Please check your PLAUD_EMAIL and PLAUD_PASSWORD in .env
```

**No Recordings Found:**
```
❌ No recordings found
Please check your Plaud.ai account has recordings
```

**Export Failed:**
```
❌ Export failed for recording_2025-01-01_12-00-00: Network timeout
The file may be retried individually
```

### Recovery Options

**Retry Failed Exports:**
```bash
# Export only failed recordings
pai-note-exporter export --limit 1  # Select the failed one
```

**Skip Problematic Files:**
```bash
# Use --limit to export in batches
pai-note-exporter export --limit 3
```

## Advanced Usage

### Batch Processing

```bash
# Export in batches to avoid timeouts
for i in {1..10}; do
    pai-note-exporter export --limit 5 --log-level WARNING
    sleep 30  # Wait between batches
done
```

### Custom Logging

```bash
# Log to custom file
pai-note-exporter export --log-level DEBUG 2>&1 | tee export.log

# Filter specific log levels
pai-note-exporter export --log-level DEBUG 2>&1 | grep ERROR
```

### Integration with Scripts

```bash
#!/bin/bash
# Daily export script

DATE=$(date +%Y-%m-%d)
EXPORT_DIR="./exports/$DATE"

# Create date-based directory
mkdir -p "$EXPORT_DIR"

# Export with custom settings
pai-note-exporter export \
    --all \
    --include-audio \
    --env-file .env \
    --log-level INFO

# Move exports to dated directory
mv exports/*.txt exports/*.mp3 "$EXPORT_DIR/" 2>/dev/null || true

echo "✅ Daily export completed to $EXPORT_DIR"
```

## Performance Tips

### Large Exports
- Use `--limit` to process in batches
- Add delays between operations
- Monitor system resources

### Network Issues
- Increase `API_TIMEOUT` in configuration
- Use `--log-level DEBUG` for diagnostics
- Check network connectivity

### Storage Considerations
- Ensure sufficient disk space (audio files are large)
- Clean up old exports regularly
- Use compression for long-term storage

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Authentication error |
| 4 | Network error |
| 5 | Export error |

## Getting Help

```bash
# Show general help
pai-note-exporter --help

# Show export command help
pai-note-exporter export --help

# Enable verbose logging
pai-note-exporter export --log-level DEBUG
```