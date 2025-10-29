"""Tests for logger module."""

import logging
import tempfile
from pathlib import Path

from pai_note_exporter.logger import get_logger, setup_logger


class TestLogger:
    """Test cases for logger module."""

    def test_setup_logger_console_only(self) -> None:
        """Test setting up logger with console output only."""
        logger = setup_logger("test_logger_console", "INFO")

        assert logger.name == "test_logger_console"
        assert logger.level == logging.INFO
        assert len(logger.handlers) >= 1
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_setup_logger_with_file(self) -> None:
        """Test setting up logger with file output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "test.log"
            logger = setup_logger("test_logger_file", "DEBUG", str(log_file))

            assert logger.level == logging.DEBUG
            assert len(logger.handlers) >= 2
            assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
            assert log_file.exists()

    def test_setup_logger_prevents_duplicate_handlers(self) -> None:
        """Test that calling setup_logger twice doesn't add duplicate handlers."""
        logger_name = "test_logger_duplicate"
        logger1 = setup_logger(logger_name, "INFO")
        handler_count_1 = len(logger1.handlers)

        logger2 = setup_logger(logger_name, "INFO")
        handler_count_2 = len(logger2.handlers)

        assert logger1 is logger2
        assert handler_count_1 == handler_count_2

    def test_get_logger(self) -> None:
        """Test getting an existing logger."""
        logger_name = "test_logger_get"
        setup_logger(logger_name, "INFO")

        retrieved_logger = get_logger(logger_name)
        assert retrieved_logger.name == logger_name

    def test_logger_levels(self) -> None:
        """Test different log levels."""
        log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]

        for level in log_levels:
            logger_name = f"test_logger_{level.lower()}"
            logger = setup_logger(logger_name, level)
            assert logger.level == getattr(logging, level)

    def test_logger_creates_directory(self) -> None:
        """Test that logger creates parent directories for log file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = Path(tmpdir) / "nested" / "dir" / "test.log"
            setup_logger("test_logger_nested", "INFO", str(log_file))

            assert log_file.exists()
            assert log_file.parent.exists()
