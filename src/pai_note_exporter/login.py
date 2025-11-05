"""Plaud.ai login functionality using direct API calls."""

import json

import httpx

from pai_note_exporter.config import Config
from pai_note_exporter.exceptions import AuthenticationError, TimeoutError
from pai_note_exporter.logger import setup_logger


class PlaudAILogin:
    """Handle authentication with Plaud.ai using direct API calls.

    This class provides methods to log into Plaud.ai using direct API calls
    instead of browser automation for better reliability and speed.

    Attributes:
        config: Configuration object with credentials and settings
        logger: Logger instance for this class

    Example:
        >>> from pai_note_exporter.config import Config
        >>> from pai_note_exporter.login import PlaudAILogin
        >>> config = Config.from_env()
        >>> async with PlaudAILogin(config) as login:
        ...     success, token = await login.login()
        ...     print(f"Login {'successful' if success else 'failed'}")
    """

    LOGIN_URL = "https://api.plaud.ai/auth/access-token"

    def __init__(self, config: Config) -> None:
        """Initialize the PlaudAILogin instance.

        Args:
            config: Configuration object with credentials and settings
        """
        self.config = config
        self.logger = setup_logger(
            name=__name__,
            log_level=config.log_level,
            log_file=config.log_file,
        )
        self._token: str | None = None

    async def __aenter__(self) -> "PlaudAILogin":
        """Async context manager entry.

        Returns:
            PlaudAILogin: This instance
        """
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        pass  # No cleanup needed for direct API calls

    async def login(self) -> tuple[bool, str | None]:
        """Log into Plaud.ai using direct API call.

        Returns:
            tuple[bool, str | None]: (success, token) where token is the access token if successful

        Raises:
            AuthenticationError: If login fails
            TimeoutError: If request times out
        """
        try:
            self.logger.info("Logging into Plaud.ai via API...")

            # Prepare login data - try plain password first
            login_data = {
                "username": self.config.plaud_email,
                "password": self.config.plaud_password,
                "client_id": "web",
                "password_encrypted": "false",
            }

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Origin": "https://app.plaud.ai",
                "Referer": "https://app.plaud.ai/",
            }

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.LOGIN_URL, data=login_data, headers=headers)

                self.logger.debug(f"Login response status: {response.status_code}")

                if response.status_code == 200:
                    try:
                        result = response.json()
                        self.logger.debug(f"Login response: {result}")

                        if result.get("status") == 0 and "access_token" in result:
                            self._token = result["access_token"]
                            self.logger.info("Login successful!")
                            return True, self._token
                        else:
                            self.logger.error(f"Login failed: {result}")
                            return False, None
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse login response: {e}")
                        return False, None
                else:
                    self.logger.error(
                        f"Login request failed with status {response.status_code}: {response.text}"
                    )
                    return False, None

        except httpx.TimeoutException as e:
            self.logger.error(f"Login request timed out: {e}")
            raise TimeoutError("Login request timed out") from e
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {e}")
            raise AuthenticationError(f"Login failed with unexpected error: {e}") from e

    def get_token(self) -> str | None:
        """Get the stored access token.

        Returns:
            str | None: The access token if available
        """
        return self._token

    # Legacy methods for compatibility - these do nothing now
    async def get_current_url(self) -> str:
        """Get current URL (legacy method, returns empty string)."""
        return ""

    async def take_screenshot(self, path: str) -> None:
        """Take screenshot (legacy method, does nothing)."""
        pass
