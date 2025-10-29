"""Custom exceptions for Pai Note Exporter."""


class PaiNoteExporterError(Exception):
    """Base exception for Pai Note Exporter errors."""

    pass


class AuthenticationError(PaiNoteExporterError):
    """Raised when authentication fails."""

    pass


class ConfigurationError(PaiNoteExporterError):
    """Raised when configuration is invalid or missing."""

    pass


class BrowserError(PaiNoteExporterError):
    """Raised when browser operations fail."""

    pass


class TimeoutError(PaiNoteExporterError):
    """Raised when operations timeout."""

    pass


class APIError(PaiNoteExporterError):
    """Raised when API operations fail."""

    pass
