# Development Scripts

This directory contains utility scripts for development, testing, and release management.

## Scripts Overview

### `setup_dev.sh`

**Purpose:** Automated development environment setup

**What it does:**
- Creates and activates a Python virtual environment
- Installs the package in development mode with all dependencies
- Installs Playwright browsers for testing
- Sets up pre-commit hooks
- Generates secrets baseline for security scanning
- Creates `.env` file from template
- Runs basic validation checks

**Usage:**
```bash
./scripts/setup_dev.sh
```

**Prerequisites:**
- Python 3.11+
- bash shell
- Internet connection for downloading dependencies

### `prepare_release.sh`

**Purpose:** Automated release preparation and validation

**What it does:**
- Validates repository state (clean working directory, correct branch)
- Runs comprehensive test suite with coverage requirements
- Executes all code quality checks (linting, type checking, security)
- Updates version in `pyproject.toml`
- Validates CHANGELOG.md entries
- Builds distribution packages
- Tests package installation
- Creates git tag for the release

**Usage:**
```bash
./scripts/prepare_release.sh
```

**Interactive prompts:**
- Confirms branch (if not main/master)
- Requests new version number
- Validates version format (semantic versioning)

**Prerequisites:**
- All development dependencies installed
- Clean git working directory
- CHANGELOG.md updated with new version entry

## Development Workflow

### Setting Up Development Environment

1. **Clone the repository**
2. **Run setup script:**
   ```bash
   ./scripts/setup_dev.sh
   ```
3. **Configure credentials:**
   Edit `.env` with your Plaud.ai credentials
4. **Start developing!**

### Preparing a Release

1. **Update CHANGELOG.md** with new version notes
2. **Ensure all tests pass** and code is ready
3. **Run release preparation:**
   ```bash
   ./scripts/prepare_release.sh
   ```
4. **Follow the prompts** to set the new version
5. **Push changes and tag:**
   ```bash
   git push origin main
   git push origin v1.2.3  # Replace with actual version
   ```
6. **Create GitHub release** with the changelog

## Adding New Scripts

When adding new scripts to this directory:

1. **Use bash** for shell scripts (most portable)
2. **Include shebang** (`#!/bin/bash`)
3. **Make executable** (`chmod +x script.sh`)
4. **Add error handling** (`set -e`)
5. **Include documentation** in this README
6. **Follow naming convention** (`snake_case.sh`)
7. **Test on multiple environments** (Linux, macOS if applicable)

### Script Template

```bash
#!/bin/bash
# Script Name
# Brief description of what the script does

set -e  # Exit on any error

echo "📝 Script Name"
echo "==============="

# Check prerequisites
if [ ! -f "required_file" ]; then
    echo "❌ Error: required_file not found"
    exit 1
fi

# Main logic here
echo "✅ Script completed successfully"
```

## Common Patterns

### Error Handling

```bash
# Exit on any error
set -e

# Custom error messages
if [ ! -f "file.txt" ]; then
    echo "❌ Error: file.txt not found"
    exit 1
fi
```

### User Interaction

```bash
# Simple yes/no prompt
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Input with validation
read -p "Enter version: " VERSION
if [ -z "$VERSION" ]; then
    echo "❌ No version provided"
    exit 1
fi
```

### Progress Indicators

```bash
echo "🔄 Processing..."
# Do work
echo "✅ Processing complete"
```

## Troubleshooting

### Setup Script Issues

- **Permission denied**: Run `chmod +x scripts/setup_dev.sh`
- **Python version too old**: Install Python 3.11+ or update PATH
- **Virtual environment issues**: Delete `venv/` and re-run script
- **Package installation fails**: Check internet connection and proxy settings

### Release Script Issues

- **Uncommitted changes**: Commit or stash changes before running
- **Tests failing**: Fix test failures before release
- **Version format invalid**: Use semantic versioning (e.g., 1.2.3)
- **CHANGELOG.md missing entry**: Add version entry to CHANGELOG.md

### General Issues

- **Scripts not found**: Ensure you're in the project root directory
- **Command not found**: Check if required tools are installed (python, pip, git, etc.)
- **Permission issues**: Avoid running scripts as root unless necessary