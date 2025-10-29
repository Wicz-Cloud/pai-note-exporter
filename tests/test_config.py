"""Tests for configuration module."""

import os
from unittest.mock import patch

import pytest

from pai_note_exporter.config import Config


class TestConfig:
    """Test cases for Config class."""

    def test_config_from_env_with_all_values(self) -> None:
        """Test loading config from environment with all values set."""
        env_vars = {
            "PLAUD_EMAIL": "test@example.com",
            "PLAUD_PASSWORD": "test_password",
            "LOG_LEVEL": "DEBUG",
            "LOG_FILE": "test.log",
            "HEADLESS": "false",
            "BROWSER_TIMEOUT": "60000",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()

        assert config.plaud_email == "test@example.com"
        assert config.plaud_password == "test_password"
        assert config.log_level == "DEBUG"
        assert config.log_file == "test.log"
        assert config.headless is False
        assert config.browser_timeout == 60000

    def test_config_from_env_with_defaults(self) -> None:
        """Test loading config from environment with default values."""
        env_vars = {
            "PLAUD_EMAIL": "test@example.com",
            "PLAUD_PASSWORD": "test_password",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = Config.from_env()

        assert config.plaud_email == "test@example.com"
        assert config.plaud_password == "test_password"
        assert config.log_level == "INFO"
        assert config.log_file == "pai_note_exporter.log"
        assert config.headless is True
        assert config.browser_timeout == 30000

    def test_config_from_env_missing_email(self) -> None:
        """Test that ValueError is raised when email is missing."""
        env_vars = {
            "PLAUD_PASSWORD": "test_password",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="PLAUD_EMAIL and PLAUD_PASSWORD"):
                Config.from_env()

    def test_config_from_env_missing_password(self) -> None:
        """Test that ValueError is raised when password is missing."""
        env_vars = {
            "PLAUD_EMAIL": "test@example.com",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(ValueError, match="PLAUD_EMAIL and PLAUD_PASSWORD"):
                Config.from_env()

    def test_config_validate_valid(self) -> None:
        """Test validation with valid configuration."""
        config = Config(
            plaud_email="test@example.com",
            plaud_password="test_password",
        )
        # Should not raise any exception
        config.validate()

    def test_config_validate_invalid_log_level(self) -> None:
        """Test validation with invalid log level."""
        config = Config(
            plaud_email="test@example.com",
            plaud_password="test_password",
            log_level="INVALID",
        )
        with pytest.raises(ValueError, match="Invalid log level"):
            config.validate()

    def test_config_validate_invalid_timeout(self) -> None:
        """Test validation with invalid timeout."""
        config = Config(
            plaud_email="test@example.com",
            plaud_password="test_password",
            browser_timeout=0,
        )
        with pytest.raises(ValueError, match="Browser timeout must be greater than 0"):
            config.validate()

    def test_config_validate_empty_email(self) -> None:
        """Test validation with empty email."""
        config = Config(
            plaud_email="",
            plaud_password="test_password",
        )
        with pytest.raises(ValueError, match="Email and password cannot be empty"):
            config.validate()

    def test_config_validate_empty_password(self) -> None:
        """Test validation with empty password."""
        config = Config(
            plaud_email="test@example.com",
            plaud_password="",
        )
        with pytest.raises(ValueError, match="Email and password cannot be empty"):
            config.validate()

    def test_config_headless_parsing(self) -> None:
        """Test parsing of HEADLESS environment variable."""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("false", False),
            ("False", False),
            ("FALSE", False),
            ("1", False),  # Not "true" exactly
            ("yes", False),  # Not "true" exactly
        ]

        for headless_value, expected in test_cases:
            env_vars = {
                "PLAUD_EMAIL": "test@example.com",
                "PLAUD_PASSWORD": "test_password",
                "HEADLESS": headless_value,
            }

            with patch.dict(os.environ, env_vars, clear=True):
                config = Config.from_env()
                assert config.headless == expected, f"Failed for value: {headless_value}"
