"""Plaud.ai login functionality using Playwright."""

import asyncio
from typing import Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from pai_note_exporter.config import Config
from pai_note_exporter.exceptions import AuthenticationError, BrowserError, TimeoutError
from pai_note_exporter.logger import get_logger, setup_logger


class PlaudAILogin:
    """Handle authentication with Plaud.ai using Playwright.

    This class provides methods to log into Plaud.ai using a headless or headed browser.
    It includes error handling, logging, and configurable timeouts.

    Attributes:
        config: Configuration object with credentials and settings
        logger: Logger instance for this class
        browser: Playwright browser instance
        context: Browser context
        page: Current page object

    Example:
        >>> from pai_note_exporter.config import Config
        >>> from pai_note_exporter.login import PlaudAILogin
        >>> config = Config.from_env()
        >>> async with PlaudAILogin(config) as login:
        ...     await login.login()
        ...     print("Successfully logged in!")
    """

    PLAUD_LOGIN_URL = "https://www.plaud.ai/login"

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
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._playwright = None

    async def __aenter__(self) -> "PlaudAILogin":
        """Async context manager entry.

        Returns:
            PlaudAILogin: This instance
        """
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit.

        Args:
            exc_type: Exception type
            exc_val: Exception value
            exc_tb: Exception traceback
        """
        await self.close_browser()

    async def start_browser(self) -> None:
        """Start the Playwright browser.

        Raises:
            BrowserError: If browser fails to start
        """
        try:
            self.logger.info("Starting browser...")
            self._playwright = await async_playwright().start()
            self.browser = await self._playwright.chromium.launch(
                headless=self.config.headless
            )
            self.context = await self.browser.new_context(
                viewport={"width": 1280, "height": 720},
            )
            self.context.set_default_timeout(self.config.browser_timeout)
            self.page = await self.context.new_page()
            self.logger.info("Browser started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start browser: {e}")
            raise BrowserError(f"Failed to start browser: {e}") from e

    async def close_browser(self) -> None:
        """Close the browser and clean up resources."""
        try:
            if self.page:
                await self.page.close()
                self.logger.debug("Page closed")
            if self.context:
                await self.context.close()
                self.logger.debug("Browser context closed")
            if self.browser:
                await self.browser.close()
                self.logger.debug("Browser closed")
            if self._playwright:
                await self._playwright.stop()
                self.logger.debug("Playwright stopped")
            self.logger.info("Browser cleanup completed")
        except Exception as e:
            self.logger.warning(f"Error during browser cleanup: {e}")

    async def login(self) -> bool:
        """Perform login to Plaud.ai.

        Returns:
            bool: True if login was successful

        Raises:
            BrowserError: If browser is not initialized
            AuthenticationError: If login fails
            TimeoutError: If login times out
        """
        if not self.page:
            raise BrowserError("Browser not initialized. Call start_browser() first.")

        try:
            self.logger.info(f"Navigating to {self.PLAUD_LOGIN_URL}")
            await self.page.goto(self.PLAUD_LOGIN_URL)
            self.logger.info("Login page loaded")

            # Wait for the page to load
            await self.page.wait_for_load_state("networkidle")

            # Look for email input field - try multiple possible selectors
            self.logger.debug("Looking for email input field")
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="email" i]',
                'input[id*="email" i]',
            ]

            email_input = None
            for selector in email_selectors:
                try:
                    email_input = await self.page.wait_for_selector(
                        selector, timeout=5000, state="visible"
                    )
                    if email_input:
                        self.logger.debug(f"Found email input with selector: {selector}")
                        break
                except Exception:
                    continue

            if not email_input:
                raise AuthenticationError("Could not find email input field on login page")

            # Fill email
            self.logger.debug("Filling email field")
            await email_input.fill(self.config.plaud_email)
            await asyncio.sleep(0.5)  # Small delay for UI responsiveness

            # Look for password input field
            self.logger.debug("Looking for password input field")
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[placeholder*="password" i]',
                'input[id*="password" i]',
            ]

            password_input = None
            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(
                        selector, timeout=5000, state="visible"
                    )
                    if password_input:
                        self.logger.debug(f"Found password input with selector: {selector}")
                        break
                except Exception:
                    continue

            if not password_input:
                raise AuthenticationError("Could not find password input field on login page")

            # Fill password
            self.logger.debug("Filling password field")
            await password_input.fill(self.config.plaud_password)
            await asyncio.sleep(0.5)

            # Look for login button
            self.logger.debug("Looking for login button")
            login_button_selectors = [
                'button[type="submit"]',
                'button:has-text("Log in")',
                'button:has-text("Sign in")',
                'button:has-text("Login")',
                'input[type="submit"]',
            ]

            login_button = None
            for selector in login_button_selectors:
                try:
                    login_button = await self.page.wait_for_selector(
                        selector, timeout=5000, state="visible"
                    )
                    if login_button:
                        self.logger.debug(f"Found login button with selector: {selector}")
                        break
                except Exception:
                    continue

            if not login_button:
                raise AuthenticationError("Could not find login button on login page")

            # Click login button
            self.logger.info("Attempting to log in...")
            await login_button.click()

            # Wait for navigation or error message
            try:
                # Wait for either successful navigation or error message
                await self.page.wait_for_load_state("networkidle", timeout=15000)

                # Check if we're still on the login page (which might indicate failure)
                current_url = self.page.url
                if "login" in current_url.lower():
                    # Look for error messages
                    error_selectors = [
                        '[class*="error"]',
                        '[class*="alert"]',
                        '[role="alert"]',
                    ]
                    for selector in error_selectors:
                        error_elements = await self.page.query_selector_all(selector)
                        if error_elements:
                            error_text = await error_elements[0].text_content()
                            self.logger.error(f"Login failed with error: {error_text}")
                            raise AuthenticationError(
                                f"Login failed: {error_text or 'Invalid credentials'}"
                            )

                    self.logger.warning(
                        "Still on login page after submission - credentials may be incorrect"
                    )
                    raise AuthenticationError(
                        "Login failed: Still on login page after submission"
                    )

                self.logger.info(f"Login successful! Current URL: {current_url}")
                return True

            except asyncio.TimeoutError as e:
                self.logger.error("Login operation timed out")
                raise TimeoutError("Login operation timed out") from e

        except AuthenticationError:
            raise
        except TimeoutError:
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during login: {e}")
            raise AuthenticationError(f"Login failed with unexpected error: {e}") from e

    async def get_current_url(self) -> str:
        """Get the current page URL.

        Returns:
            str: Current page URL

        Raises:
            BrowserError: If page is not initialized
        """
        if not self.page:
            raise BrowserError("Page not initialized")
        return self.page.url

    async def take_screenshot(self, path: str) -> None:
        """Take a screenshot of the current page.

        Args:
            path: Path to save the screenshot

        Raises:
            BrowserError: If page is not initialized
        """
        if not self.page:
            raise BrowserError("Page not initialized")
        await self.page.screenshot(path=path)
        self.logger.info(f"Screenshot saved to {path}")
