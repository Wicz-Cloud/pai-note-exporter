# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure
- Plaud.ai login functionality using Playwright
- Configuration management via environment variables
- Comprehensive logging system
- Custom exception classes for error handling
- Command-line interface (CLI)
- Full test suite with pytest
- Code quality tools configuration (Black, isort, Ruff, mypy)
- Pre-commit hooks with detect-secrets
- MIT License
- Comprehensive documentation (README, CONTRIBUTING)
- Security disclaimer

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
