"""Tests for exceptions module."""

import pytest
from pai_note_exporter.exceptions import (
    AuthenticationError,
    BrowserError,
    ConfigurationError,
    PaiNoteExporterError,
    TimeoutError,
)


class TestExceptions:
    """Test cases for custom exceptions."""

    def test_base_exception(self) -> None:
        """Test base PaiNoteExporterError exception."""
        error = PaiNoteExporterError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_authentication_error(self) -> None:
        """Test AuthenticationError exception."""
        error = AuthenticationError("Auth failed")
        assert str(error) == "Auth failed"
        assert isinstance(error, PaiNoteExporterError)
        assert isinstance(error, Exception)

    def test_configuration_error(self) -> None:
        """Test ConfigurationError exception."""
        error = ConfigurationError("Config invalid")
        assert str(error) == "Config invalid"
        assert isinstance(error, PaiNoteExporterError)

    def test_browser_error(self) -> None:
        """Test BrowserError exception."""
        error = BrowserError("Browser failed")
        assert str(error) == "Browser failed"
        assert isinstance(error, PaiNoteExporterError)

    def test_timeout_error(self) -> None:
        """Test TimeoutError exception."""
        error = TimeoutError("Operation timed out")
        assert str(error) == "Operation timed out"
        assert isinstance(error, PaiNoteExporterError)

    def test_exception_raising(self) -> None:
        """Test that exceptions can be raised and caught."""
        with pytest.raises(AuthenticationError, match="Login failed"):
            raise AuthenticationError("Login failed")

        with pytest.raises(BrowserError, match="Browser crashed"):
            raise BrowserError("Browser crashed")

        with pytest.raises(ConfigurationError, match="Missing config"):
            raise ConfigurationError("Missing config")

        with pytest.raises(TimeoutError, match="Timeout"):
            raise TimeoutError("Timeout")

    def test_exception_inheritance(self) -> None:
        """Test that all custom exceptions inherit from base exception."""
        exceptions = [
            AuthenticationError("test"),
            BrowserError("test"),
            ConfigurationError("test"),
            TimeoutError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, PaiNoteExporterError)
            assert isinstance(exc, Exception)
