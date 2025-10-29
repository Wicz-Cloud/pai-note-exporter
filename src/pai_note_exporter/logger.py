"""Logging configuration for Pai Note Exporter."""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    log_level: str = "INFO",
    log_file: Optional[str] = None,
) -> logging.Logger:
    """Set up a logger with console and optional file output.

    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file

    Returns:
        logging.Logger: Configured logger instance

    Example:
        >>> logger = setup_logger("my_app", "DEBUG", "app.log")
        >>> logger.info("Application started")
    """
    logger = logging.getLogger(name)

    # Prevent duplicate handlers if logger is already configured
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (if log_file is provided)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance by name.

    Args:
        name: Name of the logger to retrieve

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)
