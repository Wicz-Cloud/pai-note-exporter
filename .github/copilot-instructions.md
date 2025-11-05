# AI Coding Assistant Instructions for Pai Note Exporter

## Project Overview
Python 3.11+ CLI tool that authenticates with Plaud.ai API and exports recordings/transcriptions using direct REST API calls (no browser automation).

## Architecture
- **CLI Entry Point** (`cli.py`): Two commands - `login` (get Bearer token) and `export` (download files)
- **API Integration**: Direct httpx calls to Plaud.ai REST endpoints with Bearer token auth
- **Async Context Managers**: All API clients use `async with` pattern for proper resource cleanup
- **Modular Design**: Separate modules for config, login, export, text processing, and audio processing

## Key Workflows

### Setup & Development
```bash
pip install -e ".[dev]"                    # Install with dev dependencies
pre-commit install                         # Setup pre-commit hooks
pre-commit run --all-files                 # Run all quality checks
pytest --cov=src --cov-report=html         # Run tests with coverage
```

### CLI Usage Patterns
```bash
pai-note-exporter login                     # Authenticate and get token
pai-note-exporter export --all              # Export all recordings non-interactively
pai-note-exporter export --limit 5          # Export 5 most recent recordings
```

## Code Patterns & Conventions

### Configuration Management
- Environment variables via `.env` file (never commit real credentials)
- `Config.from_env()` loads and validates settings
- Required: `PLAUD_EMAIL`, `PLAUD_PASSWORD`
- Optional: `LOG_LEVEL`, `HEADLESS`, `BROWSER_TIMEOUT`

### API Integration
- Bearer token authentication: `Authorization: Bearer {token}`
- Device ID generation: `str(uuid.uuid4()).replace('-', '')[:18]`
- Headers: `edit-from: web`, `app-platform: web`, `x-device-id`, `x-pld-tag`
- Async httpx client with 30s timeout

### Error Handling
- Custom exceptions: `AuthenticationError`, `APIError`, `ConfigurationError`, `TimeoutError`
- All exceptions logged with appropriate levels
- Graceful failure with user-friendly error messages

### Async Patterns
```python
async with PlaudAILogin(config) as login:
    success, token = await login.login()

async with PlaudAIExporter(config, token) as exporter:
    files = await exporter.list_files()
```

### Logging
- Centralized setup via `setup_logger(name, level, file)`
- Structured logging with context
- File + console output with configurable levels

### Text Processing
- Clean JSON wrappers from transcriptions
- Unicode handling for international content
- Multiple export formats: txt, docx, pdf, srt

## Development Guidelines

### Code Quality
- **Black formatting** (100 char lines) + **isort** imports
- **Ruff linting** with comprehensive rules
- **mypy strict typing** with `disallow_untyped_defs`
- **Google-style docstrings** for all public functions

### Testing
- Async tests with `pytest.mark.asyncio`
- Mock external API calls (httpx)
- Test coverage target: >90%
- Fixtures for common setup

### File Organization
```
src/pai_note_exporter/
├── cli.py              # Command-line interface
├── config.py           # Environment configuration
├── login.py            # API authentication
├── export.py           # File listing/download
├── text_processor.py   # Transcription cleaning
├── audio_processor.py  # Audio file handling
├── exceptions.py       # Custom error hierarchy
└── logger.py           # Logging setup
```

## Integration Points
- **Plaud.ai API**: REST endpoints for auth, file listing, and downloads
- **httpx**: Async HTTP client for API calls
- **python-dotenv**: Environment variable management
- **Playwright**: Legacy browser automation (being phased out)

## Common Patterns
- Device ID generation for API consistency
- Bearer token reuse across API calls
- Pagination with skip/limit parameters
- Temporary URL generation for file downloads
- Unicode-safe text processing