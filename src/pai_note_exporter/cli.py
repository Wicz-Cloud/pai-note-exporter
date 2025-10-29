"""Command-line interface for Pai Note Exporter."""

import argparse
import asyncio
import sys
from pathlib import Path

from pai_note_exporter.config import Config
from pai_note_exporter.exceptions import (
    AuthenticationError,
    BrowserError,
    ConfigurationError,
    TimeoutError,
)
from pai_note_exporter.logger import setup_logger
from pai_note_exporter.login import PlaudAILogin


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(
        description="Pai Note Exporter - Log into Plaud.ai and export notes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Login with credentials from .env file
  pai-note-exporter login

  # Login with specific .env file
  pai-note-exporter login --env-file /path/to/.env

  # Login with visible browser
  pai-note-exporter login --no-headless

  # Take a screenshot after login
  pai-note-exporter login --screenshot screenshot.png
        """,
    )

    parser.add_argument(
        "--version",
        action="version",
        version="pai-note-exporter 0.1.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    login_parser = subparsers.add_parser("login", help="Login to Plaud.ai")
    login_parser.add_argument(
        "--env-file",
        type=Path,
        help="Path to .env file (default: .env in current directory)",
    )
    login_parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in headed mode (visible)",
    )
    login_parser.add_argument(
        "--screenshot",
        type=str,
        help="Take a screenshot after login and save to this path",
    )
    login_parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set logging level (overrides .env)",
    )

    return parser.parse_args()


async def login_command(
    env_file: Path | None = None,
    headless: bool = True,
    screenshot_path: str | None = None,
    log_level: str | None = None,
) -> int:
    """Execute the login command.

    Args:
        env_file: Optional path to .env file
        headless: Whether to run browser in headless mode
        screenshot_path: Optional path to save screenshot
        log_level: Optional log level override

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # Load configuration
        config = Config.from_env(env_file)

        # Override settings from command line
        if not headless:
            config.headless = False
        if log_level:
            config.log_level = log_level

        # Validate configuration
        config.validate()

        # Set up logger
        logger = setup_logger(__name__, config.log_level, config.log_file)
        logger.info("Starting Pai Note Exporter")

        # Perform login
        async with PlaudAILogin(config) as login:
            success = await login.login()

            if success:
                logger.info("Login successful!")
                current_url = await login.get_current_url()
                logger.info(f"Current URL: {current_url}")

                # Take screenshot if requested
                if screenshot_path:
                    await login.take_screenshot(screenshot_path)

                print("\n✓ Successfully logged into Plaud.ai")
                return 0
            else:
                logger.error("Login failed")
                print("\n✗ Login failed")
                return 1

    except ConfigurationError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nPlease check your .env file or environment variables.")
        print("See .env.example for reference.")
        return 1
    except AuthenticationError as e:
        print(f"\n✗ Authentication error: {e}")
        print("\nPlease check your credentials in the .env file.")
        return 1
    except BrowserError as e:
        print(f"\n✗ Browser error: {e}")
        print("\nPlease ensure Playwright browsers are installed:")
        print("  python -m playwright install chromium")
        return 1
    except TimeoutError as e:
        print(f"\n✗ Timeout error: {e}")
        print("\nThe operation took too long. Please try again.")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return 1


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        int: Exit code
    """
    args = parse_args()

    if not args.command:
        print("Error: Please specify a command. Use --help for more information.")
        return 1

    if args.command == "login":
        return asyncio.run(
            login_command(
                env_file=args.env_file,
                headless=not args.no_headless,
                screenshot_path=args.screenshot,
                log_level=args.log_level,
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
