"""Configuration management for Pai Note Exporter."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Config:
    """Configuration settings for the Plaud.ai login application.

    Attributes:
        plaud_email: Email address for Plaud.ai authentication
        plaud_password: Password for Plaud.ai authentication
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        headless: Whether to run browser in headless mode
        browser_timeout: Browser timeout in milliseconds
    """

    plaud_email: str
    plaud_password: str
    log_level: str = "INFO"
    log_file: str = "pai_note_exporter.log"
    headless: bool = True
    browser_timeout: int = 30000

    @classmethod
    def from_env(cls, env_file: Optional[Path] = None) -> "Config":
        """Load configuration from environment variables.

        Args:
            env_file: Optional path to .env file. If not provided, looks for .env
                     in the current directory.

        Returns:
            Config: Configuration object populated from environment variables

        Raises:
            ValueError: If required environment variables are missing
        """
        # Load .env file if it exists
        if env_file:
            load_dotenv(env_file)
        else:
            load_dotenv()

        # Get required variables
        plaud_email = os.getenv("PLAUD_EMAIL")
        plaud_password = os.getenv("PLAUD_PASSWORD")

        if not plaud_email or not plaud_password:
            raise ValueError(
                "PLAUD_EMAIL and PLAUD_PASSWORD must be set in environment variables or .env file"
            )

        # Get optional variables with defaults
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        log_file = os.getenv("LOG_FILE", "pai_note_exporter.log")
        headless = os.getenv("HEADLESS", "true").lower() == "true"
        browser_timeout = int(os.getenv("BROWSER_TIMEOUT", "30000"))

        return cls(
            plaud_email=plaud_email,
            plaud_password=plaud_password,
            log_level=log_level,
            log_file=log_file,
            headless=headless,
            browser_timeout=browser_timeout,
        )

    def validate(self) -> None:
        """Validate configuration settings.

        Raises:
            ValueError: If configuration settings are invalid
        """
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.log_level not in valid_log_levels:
            raise ValueError(
                f"Invalid log level: {self.log_level}. "
                f"Must be one of {', '.join(valid_log_levels)}"
            )

        if self.browser_timeout <= 0:
            raise ValueError("Browser timeout must be greater than 0")

        if not self.plaud_email or not self.plaud_password:
            raise ValueError("Email and password cannot be empty")
