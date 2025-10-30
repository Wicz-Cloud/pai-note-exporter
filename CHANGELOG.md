# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- API-based authentication with Plaud.ai (replaced browser automation)
- Export functionality for recordings and transcriptions
- CLI export command with interactive and non-interactive modes
- Audio file download capability
- **Text processor module for cleaning and formatting transcriptions**
- **Automatic transcription text processing (removes JSON wrappers, handles unicode)**
- Bearer token authentication for API calls
- Export directory configuration
- --all flag for non-interactive export of all files
- --include-audio flag for downloading audio files
- --skip-transcription flag to bypass transcription export
- --limit flag to restrict number of files exported
- Async HTTP client using httpx for API operations
- Comprehensive export error handling

### Changed
- Replaced Playwright browser automation with direct REST API calls
- Updated authentication flow to use api.plaud.ai/auth/login endpoint
- Modified CLI to focus on export operations instead of just login
- Updated configuration options (removed browser-specific settings)
- Updated project structure with export.py module

### Removed
- Playwright dependency and browser automation code
- Browser-specific configuration options (HEADLESS, BROWSER_TIMEOUT)
- Screenshot functionality (no longer applicable with API approach)

### Fixed
- Resolved authentication issues with proper Bearer token format
- Fixed file listing API response parsing
- Added non-interactive mode to prevent hanging on user input
- Improved error handling for API failures and timeouts

## [0.1.0] - 2025-10-29

### Added
- Initial release
- Core functionality for logging into Plaud.ai
- Browser automation with Playwright
- Environment-based configuration
- Logging with configurable levels
- Error handling with custom exceptions
- CLI with login command
- Python 3.11+ support
- Test coverage for core modules
- Development tools and pre-commit hooks
- Documentation and contribution guidelines

### Security
- Credentials stored in .env file (not in code)
- .gitignore configured to prevent credential leaks
- detect-secrets integration for secret scanning
- Security disclaimer in README

[Unreleased]: https://github.com/Wicz-Cloud/pai-note-exporter/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Wicz-Cloud/pai-note-exporter/releases/tag/v0.1.0
