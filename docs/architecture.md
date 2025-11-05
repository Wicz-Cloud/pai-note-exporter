# Architecture

Detailed architecture overview of Pai Note Exporter.

## System Overview

Pai Note Exporter is a Python-based tool for exporting recordings and transcriptions from Plaud.ai. It provides both a command-line interface and a Python API for automation and integration.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Interface │    │  Python API     │    │  Integrations   │
│                 │    │                 │    │                 │
│ • Interactive   │    │ • PlaudClient   │    │ • Webhooks      │
│ • Batch export  │    │ • Exporter      │    │ • Databases     │
│ • Progress      │    │ • Async/Await   │    │ • Cloud storage │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   Core Components   │
                    │                     │
                    │ • Authentication    │
                    │ • API Client        │
                    │ • Export Engine     │
                    │ • File Management   │
                    └─────────────────────┘
                                 │
                    ┌─────────────────────┐
                    │   External APIs     │
                    │                     │
                    │ • Plaud.ai API      │
                    │ • HTTP Client       │
                    │ • File System       │
                    └─────────────────────┘
```

## Core Components

### PlaudClient

**Purpose**: Handles authentication and communication with Plaud.ai API

**Key Features**:
- OAuth2 authentication flow
- Session management with automatic token refresh
- Rate limiting and retry logic
- Connection pooling for performance

**Architecture**:
```python
class PlaudClient:
    def __init__(self, email: str, password: str, session: ClientSession = None):
        self.email = email
        self.password = password
        self.session = session or ClientSession()
        self.auth_token = None

    async def login(self) -> bool:
        # 1. Navigate to login page
        # 2. Submit credentials
        # 3. Extract authentication token
        # 4. Validate token
        pass

    async def get_recordings(self, limit: int = None) -> List[Recording]:
        # 1. Make authenticated API request
        # 2. Parse JSON response
        # 3. Create Recording objects
        # 4. Return sorted list
        pass
```

**Error Handling**:
- `AuthenticationError`: Invalid credentials or token expired
- `NetworkError`: Connection issues or API unavailability
- `RateLimitError`: Too many requests

### Exporter

**Purpose**: Orchestrates the export process and file management

**Key Features**:
- Batch processing with progress tracking
- Selective export (transcription-only, audio-only, or both)
- File organization and naming conventions
- Export statistics and reporting

**Architecture**:
```python
class Exporter:
    def __init__(self, client: PlaudClient, output_dir: str = "exports"):
        self.client = client
        self.output_dir = Path(output_dir)
        self.include_audio = False

    async def export_all(self) -> ExportResult:
        recordings = await self.client.get_recordings()

        results = []
        for recording in recordings:
            try:
                success = await self.export_recording(recording)
                results.append(success)
            except Exception as e:
                results.append(False)
                logger.error(f"Failed to export {recording.name}: {e}")

        return ExportResult(
            total=len(recordings),
            successful=sum(results),
            failed=len(recordings) - sum(results)
        )
```

### Recording Model

**Purpose**: Data structure representing a Plaud.ai recording

**Attributes**:
```python
@dataclass
class Recording:
    id: str
    name: str
    duration: int  # seconds
    size: int      # bytes
    created_at: datetime
    status: str    # "transcribed", "processing", "failed"
    has_audio: bool
    has_transcription: bool

    def is_transcribed(self) -> bool:
        return self.status == "transcribed"

    def get_filename(self, extension: str) -> str:
        timestamp = self.created_at.strftime("%Y-%m-%d_%H-%M-%S")
        return f"recording_{timestamp}.{extension}"
```

## Data Flow

### Authentication Flow

```
1. User provides credentials
2. PlaudClient navigates to login page
3. Browser automation submits credentials
4. Extract authentication cookies/tokens
5. Validate token with API call
6. Store token for subsequent requests
```

### Export Flow

```
1. User initiates export
2. PlaudClient fetches recording list
3. Filter recordings (if specified)
4. For each recording:
   a. Check if transcription is ready
   b. Download transcription text
   c. Optionally download audio file
   d. Save to local filesystem
   e. Update progress
5. Generate export summary
6. Clean up connections
```

### Error Recovery Flow

```
1. Operation fails
2. Check error type:
   - NetworkError: Retry with backoff
   - AuthenticationError: Re-authenticate
   - NotFoundError: Skip recording
   - Other: Log and continue
3. Update error statistics
4. Continue with next item
```

## File Organization

### Directory Structure

```
pai-note-exporter/
├── src/
│   ├── __init__.py
│   ├── client.py          # PlaudClient implementation
│   ├── exporter.py        # Exporter implementation
│   ├── models.py          # Data models
│   ├── cli.py            # Command-line interface
│   └── utils.py          # Utility functions
├── tests/
│   ├── test_client.py
│   ├── test_exporter.py
│   └── test_cli.py
├── docs/                 # Documentation
├── exports/              # Default export directory
├── pyproject.toml        # Project configuration
├── requirements.txt      # Dependencies
└── README.md
```

### Export File Structure

```
exports/
├── recording_2025-01-01_12-00-00.txt    # Transcription
├── recording_2025-01-01_12-00-00.mp3    # Audio (optional)
├── recording_2025-01-01_12-45-15.txt    # Another transcription
├── pai_note_exporter.log                # Application logs
└── export_summary.json                  # Export metadata
```

## Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `httpx` | ^0.25.0 | HTTP client for API requests |
| `playwright` | ^1.40.0 | Browser automation for login |
| `pydantic` | ^2.5.0 | Data validation and models |
| `rich` | ^13.7.0 | Beautiful CLI output |
| `loguru` | ^0.7.0 | Structured logging |
| `aiofiles` | ^23.2.1 | Async file operations |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pytest` | ^7.4.0 | Testing framework |
| `pytest-asyncio` | ^0.21.0 | Async test support |
| `black` | ^23.11.0 | Code formatting |
| `ruff` | ^0.1.0 | Linting |
| `mypy` | ^1.7.0 | Type checking |

## Security Architecture

### Authentication Security

- **No credential storage**: Credentials are used only for login and not persisted
- **Token management**: Authentication tokens are kept in memory only
- **Session isolation**: Each client instance has its own session
- **Timeout handling**: Automatic session cleanup and token refresh

### Data Protection

- **HTTPS only**: All API communications use HTTPS
- **No data retention**: Exported files are not stored in application memory
- **Secure file handling**: Atomic file writes to prevent corruption
- **Permission checks**: Validates file system permissions before writing

### Network Security

- **Certificate validation**: Validates SSL certificates
- **Timeout protection**: Prevents hanging connections
- **Rate limiting**: Respects API rate limits
- **Error masking**: Doesn't expose sensitive information in error messages

## Performance Characteristics

### Memory Usage

- **Base memory**: ~50MB for core application
- **Per recording**: ~1MB for metadata + transcription size
- **Peak usage**: Scales linearly with concurrent exports
- **Cleanup**: Automatic garbage collection of large objects

### Network Performance

- **Concurrent connections**: Up to 10 simultaneous downloads
- **Connection pooling**: Reuses connections for efficiency
- **Retry logic**: Exponential backoff for failed requests
- **Timeout handling**: 30-second default timeout with configurability

### Disk I/O

- **Atomic writes**: Prevents file corruption
- **Buffering**: 64KB buffer for file operations
- **Progress tracking**: Real-time progress updates
- **Error recovery**: Resumes interrupted downloads

## Scalability Considerations

### Large Recording Sets

- **Pagination**: API responses are paginated
- **Batch processing**: Exports can be processed in chunks
- **Memory limits**: Automatic cleanup prevents memory exhaustion
- **Progress persistence**: Can resume interrupted exports

### High-Frequency Exports

- **Caching**: Recording metadata can be cached
- **Incremental exports**: Only export new/changed recordings
- **Parallel processing**: Multiple recordings can be exported concurrently
- **Resource limits**: Configurable concurrency limits

### Long-Running Operations

- **Background processing**: Exports can run in background
- **Progress monitoring**: Real-time status updates
- **Graceful shutdown**: Can be interrupted and resumed
- **Logging**: Comprehensive operation logging

## Error Handling Strategy

### Exception Hierarchy

```
PaiNoteExporterError
├── AuthenticationError
├── NetworkError
├── ExportError
├── ValidationError
└── ConfigurationError
```

### Recovery Strategies

- **Retry logic**: Automatic retry for transient failures
- **Fallback options**: Alternative export methods
- **Partial success**: Continue processing after individual failures
- **Detailed logging**: Comprehensive error information for debugging

### Monitoring and Alerting

- **Health checks**: Periodic validation of API connectivity
- **Metrics collection**: Export statistics and performance metrics
- **Error aggregation**: Summary of common failure patterns
- **Alert thresholds**: Configurable alerting for critical errors

## Testing Strategy

### Unit Testing

- **Mock API responses**: Test without real API calls
- **Error simulation**: Test error handling paths
- **Data validation**: Test model parsing and validation
- **Edge cases**: Test boundary conditions

### Integration Testing

- **Real API calls**: Test with actual Plaud.ai API (rate limited)
- **File system operations**: Test actual file creation and management
- **Network conditions**: Test with various network scenarios
- **Authentication flow**: Test complete login and export flow

### Performance Testing

- **Load testing**: Test with large numbers of recordings
- **Memory profiling**: Monitor memory usage patterns
- **Network profiling**: Analyze network usage and bottlenecks
- **Benchmarking**: Compare performance across versions

## Deployment Options

### Python Package

```bash
pip install pai-note-exporter
pai-note-exporter export
```

### Docker Container

```dockerfile
FROM python:3.11-slim
COPY . /app
RUN pip install -e /app
CMD ["pai-note-exporter", "export"]
```

### System Service

```systemd
[Unit]
Description=Pai Note Exporter
After=network.target

[Service]
Type=simple
User=exporter
ExecStart=/usr/local/bin/pai-note-exporter export
Restart=always

[Install]
WantedBy=multi-user.target
```

### Cloud Functions

```python
# AWS Lambda
def lambda_handler(event, context):
    # Process webhook trigger
    # Run export
    # Upload results to S3
    pass
```

## Future Architecture Considerations

### Microservices Evolution

- **API service**: Separate authentication and export services
- **Queue system**: Asynchronous processing with message queues
- **Storage abstraction**: Support for multiple storage backends
- **Plugin system**: Extensible architecture for custom integrations

### Advanced Features

- **Real-time sync**: Continuous synchronization of recordings
- **AI processing**: Integration with transcription improvement services
- **Analytics**: Recording analytics and usage patterns
- **Multi-user**: Support for multiple Plaud.ai accounts

### Performance Optimizations

- **CDN integration**: Faster downloads with content delivery networks
- **Compression**: Automatic compression of exported files
- **Caching layers**: Redis caching for metadata and tokens
- **Load balancing**: Distributed processing across multiple instances

This architecture provides a solid foundation for reliable, scalable, and maintainable recording exports while allowing for future enhancements and integrations.
