"""Command-line interface for Pai Note Exporter."""

import argparse
import asyncio
import sys
from pathlib import Path

from pai_note_exporter.config import Config
from pai_note_exporter.exceptions import (
    APIError,
    AuthenticationError,
    BrowserError,
    ConfigurationError,
    TimeoutError,
)
from pai_note_exporter.export import PlaudAIExporter
from pai_note_exporter.logger import setup_logger
from pai_note_exporter.login import PlaudAILogin
from pai_note_exporter.text_processor import TextProcessor


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

  # Export recent recordings
  pai-note-exporter export

  # Export with custom options
  pai-note-exporter export --limit 20 --format pdf --include-audio --output-dir ./my-exports

  # Export all recordings automatically (non-interactive)
  pai-note-exporter export --all
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

    # Export command
    export_parser = subparsers.add_parser("export", help="Export recordings from Plaud.ai")
    export_parser.add_argument(
        "--env-file",
        type=Path,
        help="Path to .env file (default: .env in current directory)",
    )
    export_parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("./exports"),
        help="Directory to save exported files (default: ./exports)",
    )
    export_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of recent recordings to show (default: 10)",
    )
    export_parser.add_argument(
        "--format",
        choices=["txt", "docx", "pdf", "srt"],
        default="txt",
        help="Export format for transcriptions (default: txt)",
    )
    export_parser.add_argument(
        "--include-audio",
        action="store_true",
        help="Also download audio files",
    )
    export_parser.add_argument(
        "--all",
        action="store_true",
        help="Export all recordings without prompting for selection",
    )
    export_parser.add_argument(
        "--skip-transcription",
        action="store_true",
        help="Skip transcription export (only download audio if requested)",
    )
    export_parser.add_argument(
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
            success, token = await login.login()

            if success:
                logger.info("Login successful!")
                current_url = await login.get_current_url()
                logger.info(f"Current URL: {current_url}")

                # Store token for potential reuse
                if token:
                    logger.info("Auth token extracted and available for API calls")
                else:
                    logger.warning("No auth token extracted")

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


async def export_command(
    env_file: Path | None = None,
    output_dir: Path = Path("./exports"),
    limit: int = 10,
    export_format: str = "txt",
    include_audio: bool = False,
    export_all: bool = False,
    skip_transcription: bool = False,
    log_level: str | None = None,
) -> int:
    """Execute the export command.

    Args:
        env_file: Optional path to .env file
        output_dir: Directory to save exported files
        limit: Maximum number of recordings to show
        export_format: Format for transcription export
        include_audio: Whether to download audio files
        export_all: Whether to export all recordings without prompting
        skip_transcription: Whether to skip transcription export
        log_level: Optional log level override

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    try:
        # Load configuration
        config = Config.from_env(env_file)

        # Override settings from command line
        if log_level:
            config.log_level = log_level

        # Validate configuration
        config.validate()

        # Set up logger
        logger = setup_logger(__name__, config.log_level, config.log_file)
        logger.info("Starting Pai Note Exporter - Export Mode")

        # Initialize text processor for cleaning transcription content
        text_processor = TextProcessor(config.log_level, config.log_file)

        # First, login to get the auth token
        print("🔐 Logging into Plaud.ai...")
        async with PlaudAILogin(config) as login:
            success, token = await login.login()

            if not success or not token:
                print("\n✗ Login failed - cannot proceed with export")
                return 1

            print("✓ Login successful!")

            # Now list recent files
            print(f"\n📋 Fetching {limit} most recent recordings...")
            async with PlaudAIExporter(config, token) as exporter:
                files = await exporter.list_files(limit=limit)

                if not files:
                    print("\n📭 No recordings found")
                    return 0

                print(f"\n📋 Found {len(files)} recordings:")
                print("-" * 80)

                for i, file_info in enumerate(files, 1):
                    print(f"{i:2d}. {exporter.format_file_info(file_info)}")

                print("-" * 80)

                # Handle selection
                if export_all:
                    selected_indices = list(range(len(files)))
                    print(f"📋 Auto-selecting all {len(files)} recordings for export")
                else:
                    # Prompt user for selection
                    while True:
                        try:
                            selection = input(
                                f"\nEnter recording numbers to export (1-{len(files)}, comma-separated, or 'all'): "
                            ).strip().lower()

                            if selection == "all":
                                selected_indices = list(range(len(files)))
                                break
                            elif selection == "":
                                print("No recordings selected. Exiting.")
                                return 0
                            else:
                                indices = []
                                for part in selection.split(","):
                                    part = part.strip()
                                    if "-" in part:
                                        # Handle ranges like "1-3"
                                        start, end = part.split("-")
                                        start_idx = int(start.strip()) - 1
                                        end_idx = int(end.strip()) - 1
                                        indices.extend(range(start_idx, end_idx + 1))
                                    else:
                                        indices.append(int(part.strip()) - 1)

                                # Validate indices
                                selected_indices = []
                                for idx in indices:
                                    if 0 <= idx < len(files):
                                        selected_indices.append(idx)
                                    else:
                                        print(f"Warning: Invalid index {idx + 1}, skipping")

                                if selected_indices:
                                    break
                                else:
                                    print("No valid recordings selected. Please try again.")

                        except (ValueError, KeyboardInterrupt):
                            print("\nInvalid input. Please try again.")

                # Export selected files
                print(f"\n🚀 Exporting {len(selected_indices)} recording(s)...")
                output_dir.mkdir(parents=True, exist_ok=True)

                for i, idx in enumerate(selected_indices, 1):
                    file_info = files[idx]
                    file_id = file_info["id"]
                    filename = file_info["filename"]

                    print(f"\n[{i}/{len(selected_indices)}] Processing: {filename}")

                    try:
                        # Export transcription if not skipped
                        if not skip_transcription:
                            # Check if file has transcription
                            has_transcription = file_info.get("is_trans", False)

                            if has_transcription:
                                # Export transcription
                                print(f"  📝 Exporting transcription as {export_format.upper()}...")
                                transcription_data = await exporter.export_transcription(
                                    file_id=file_id,
                                    prompt_type="trans",
                                    to_format=export_format.upper(),
                                    title=filename,
                                    content=file_info.get("trans_result", ""),
                                    with_speaker=1,
                                    with_timestamp=1,
                                )

                                # Process transcription content for better readability
                                try:
                                    raw_text = transcription_data.decode('utf-8')
                                    processed_text = text_processor.process_transcription(raw_text)
                                    transcription_data = processed_text.encode('utf-8')
                                    print("  ✓ Transcription processed and cleaned")
                                except Exception as e:
                                    logger.warning(f"Failed to process transcription text: {e}")
                                    print("  ⚠️ Transcription processing failed, saving raw content")

                                # Save transcription
                                trans_filename = f"{filename}_transcript.{export_format.lower()}"
                                trans_path = output_dir / trans_filename
                                with open(trans_path, "wb") as f:
                                    f.write(transcription_data)
                                print(f"  ✓ Transcription saved: {trans_path}")
                            else:
                                print("  📝 Skipping transcription export (file not transcribed)")
                        else:
                            print("  📝 Skipping transcription export (--skip-transcription)")

                        # Export audio if requested
                        if include_audio:
                            print("  🎵 Downloading audio file...")
                            temp_url = await exporter.get_temp_url(file_id)
                            audio_path = await exporter.download_file(
                                temp_url, f"{filename}.mp3", output_dir
                            )
                            print(f"  ✓ Audio saved: {audio_path}")
                        else:
                            print("  🎵 Skipping audio download (use --include-audio to download)")

                    except APIError as e:
                        print(f"  ✗ Failed to export {filename}: {e}")
                        continue

                print(f"\n✅ Export completed! Files saved to: {output_dir.absolute()}")
                return 0

    except ConfigurationError as e:
        print(f"\n✗ Configuration error: {e}")
        print("\nPlease check your .env file or environment variables.")
        print("See .env.example for reference.")
        return 1
    except AuthenticationError as e:
        print(f"\n✗ Authentication error: {e}")
        print("\nPlease check your credentials in the .env file.")
        return 1
    except APIError as e:
        print(f"\n✗ API error: {e}")
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
    except KeyboardInterrupt:
        print("\n\n⚠️  Export cancelled by user")
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
    elif args.command == "export":
        return asyncio.run(
            export_command(
                env_file=args.env_file,
                output_dir=args.output_dir,
                limit=args.limit,
                export_format=args.format,
                include_audio=args.include_audio,
                export_all=args.all,
                skip_transcription=args.skip_transcription,
                log_level=args.log_level,
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
