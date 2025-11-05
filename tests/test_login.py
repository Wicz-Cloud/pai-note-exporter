"""Tests for login module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pai_note_exporter.config import Config
from pai_note_exporter.exceptions import BrowserError
from pai_note_exporter.login import PlaudAILogin


class TestPlaudAILogin:
    """Test cases for PlaudAILogin class."""

    @pytest.fixture
    def config(self) -> Config:
        """Create a test configuration."""
        return Config(
            plaud_email="test@example.com",
            plaud_password="test_password",
            log_level="INFO",
            headless=True,
            browser_timeout=30000,
        )

    def test_login_init(self, config: Config) -> None:
        """Test initialization of PlaudAILogin."""
        login = PlaudAILogin(config)

        assert login.config == config
        assert login.browser is None
        assert login.context is None
        assert login.page is None
        assert login.logger is not None

    @pytest.mark.asyncio
    async def test_login_without_browser_raises_error(self, config: Config) -> None:
        """Test that API-based login works without browser initialization."""
        login = PlaudAILogin(config)

        # With API-based login, this should work without browser initialization
        # The test expectation needs to be updated for the new implementation
        with patch("httpx.AsyncClient.post") as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": 0,
                "access_token": "test_token"
            }
            mock_post.return_value = mock_response
            
            success, token = await login.login()
            assert success is True
            assert token == "test_token"

    @pytest.mark.asyncio
    async def test_get_current_url_without_page_raises_error(self, config: Config) -> None:
        """Test that getting URL without page raises error."""
        login = PlaudAILogin(config)

        with pytest.raises(BrowserError, match="Page not initialized"):
            await login.get_current_url()

    @pytest.mark.asyncio
    async def test_take_screenshot_without_page_raises_error(self, config: Config) -> None:
        """Test that taking screenshot without page raises error."""
        login = PlaudAILogin(config)

        with pytest.raises(BrowserError, match="Page not initialized"):
            await login.take_screenshot("test.png")

    @pytest.mark.asyncio
    async def test_context_manager(self, config: Config) -> None:
        """Test async context manager functionality."""
        login = PlaudAILogin(config)

        with (
            patch.object(login, "start_browser", new_callable=AsyncMock),
            patch.object(login, "close_browser", new_callable=AsyncMock),
        ):
            async with login as login_instance:
                assert login_instance is login
                login.start_browser.assert_called_once()
            login.close_browser.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_browser_handles_none_objects(self, config: Config) -> None:
        """Test that close_browser handles None objects gracefully."""
        login = PlaudAILogin(config)

        # Should not raise any exceptions
        await login.close_browser()

    @pytest.mark.asyncio
    async def test_close_browser_handles_exceptions(self, config: Config) -> None:
        """Test that close_browser handles exceptions during cleanup."""
        login = PlaudAILogin(config)
        login.page = MagicMock()
        login.page.close = AsyncMock(side_effect=Exception("Close failed"))

        # Should not raise exceptions, just log warnings
        await login.close_browser()

    def test_plaud_login_url(self) -> None:
        """Test that PLAUD_LOGIN_URL is correctly set."""
        assert PlaudAILogin.PLAUD_LOGIN_URL == "https://www.plaud.ai/login"
