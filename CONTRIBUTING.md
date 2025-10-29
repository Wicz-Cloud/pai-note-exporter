# Contributing to Pai Note Exporter

Thank you for your interest in contributing to Pai Note Exporter! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

This project follows a code of conduct that all contributors are expected to adhere to:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members
- Accept constructive criticism gracefully

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/pai-note-exporter.git
   cd pai-note-exporter
   ```
3. **Add the upstream repository**:
   ```bash
   git remote add upstream https://github.com/Wicz-Cloud/pai-note-exporter.git
   ```

## Development Setup

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install Playwright browsers**:
   ```bash
   python -m playwright install chromium
   ```

4. **Set up pre-commit hooks**:
   ```bash
   pre-commit install
   ```

5. **Create a .env file** for testing:
   ```bash
   cp .env.example .env
   # Add test credentials (do not use production credentials)
   ```

## Making Changes

1. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the coding standards below

3. **Add tests** for any new functionality

4. **Run tests** to ensure everything works:
   ```bash
   pytest
   ```

5. **Run code quality tools**:
   ```bash
   black src tests
   isort src tests
   ruff check src tests
   mypy src
   ```

6. **Commit your changes** with clear commit messages:
   ```bash
   git add .
   git commit -m "Add feature: description of your feature"
   ```

## Coding Standards

### Python Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines
- Use [Black](https://github.com/psf/black) for code formatting (line length: 100)
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [Ruff](https://github.com/astral-sh/ruff) for linting
- Use [mypy](http://mypy-lang.org/) for type checking

### Documentation

- Add docstrings to all modules, classes, and functions
- Use Google-style docstrings
- Keep docstrings clear and concise
- Update README.md if adding new features

### Example Docstring

```python
def example_function(arg1: str, arg2: int) -> bool:
    """Brief description of what the function does.

    More detailed description if needed. Explain the purpose,
    behavior, and any important details.

    Args:
        arg1: Description of the first argument
        arg2: Description of the second argument

    Returns:
        Description of the return value

    Raises:
        ValueError: Description of when this exception is raised
        TypeError: Description of when this exception is raised

    Example:
        >>> result = example_function("test", 42)
        >>> print(result)
        True
    """
    # Implementation
    pass
```

### Type Hints

- Use type hints for all function parameters and return values
- Import types from `typing` module when needed
- Use `Optional[T]` for nullable values
- Use `Union[T1, T2]` for multiple possible types

### Error Handling

- Use custom exceptions from `exceptions.py`
- Catch specific exceptions rather than bare `except:`
- Log errors with appropriate detail
- Provide helpful error messages

## Testing

### Writing Tests

- Write tests for all new functionality
- Use pytest for testing
- Follow the existing test structure
- Aim for high test coverage (>80%)

### Test Structure

```python
"""Tests for module_name."""

import pytest

from pai_note_exporter.module_name import ClassName


class TestClassName:
    """Test cases for ClassName."""

    @pytest.fixture
    def setup_data(self):
        """Create test data."""
        return {"key": "value"}

    def test_feature_name(self, setup_data):
        """Test specific feature behavior."""
        # Arrange
        expected = "expected_value"
        
        # Act
        result = function_to_test(setup_data)
        
        # Assert
        assert result == expected
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/pai_note_exporter --cov-report=html

# Run specific test
pytest tests/test_config.py::TestConfig::test_config_from_env

# Run with verbose output
pytest -v
```

## Submitting Changes

1. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template with:
     - Description of changes
     - Related issues
     - Testing performed
     - Screenshots (if applicable)

3. **Respond to review feedback**:
   - Address all comments
   - Make requested changes
   - Push updates to your branch

4. **Wait for approval**:
   - At least one maintainer must approve
   - All CI checks must pass
   - No merge conflicts

## Reporting Issues

### Bug Reports

When reporting bugs, include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**:
  - Python version
  - Operating system
  - Package versions
- **Logs**: Relevant log output (sanitize credentials!)
- **Screenshots**: If applicable

### Feature Requests

When requesting features, include:

- **Description**: Clear description of the feature
- **Use Case**: Why this feature would be useful
- **Proposed Solution**: How you think it should work
- **Alternatives**: Other solutions you've considered

## Security Issues

**DO NOT** open public issues for security vulnerabilities. Instead:

1. Email the maintainers privately
2. Provide detailed information about the vulnerability
3. Wait for a response before disclosing publicly

## Questions?

If you have questions:

- Check the [README.md](README.md)
- Search existing issues
- Open a new issue with the "question" label

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Pai Note Exporter! 🎉
