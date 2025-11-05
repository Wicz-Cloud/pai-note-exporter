"""Command-line interface for Pai Note Exporter."""

import argparse
import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Any

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


class ProgressIndicator:
    """A colorful progress indicator with spinner and timing information."""

    def __init__(self) -> None:
        self.spinner_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.colors = {
            "reset": "\033[0m",
            "red": "\033[31m",
            "green": "\033[32m",
            "yellow": "\033[33m",
            "blue": "\033[34m",
            "magenta": "\033[35m",
            "cyan": "\033[36m",
            "white": "\033[37m",
        }
        self.is_running = False
        self.thread = None
        self.start_time: float | None = None
        self.poll_count = 0
        self.last_poll_time: float | None = None
        self.message = "Processing"

    def start(self, message: str = "Processing") -> None:
        """Start the progress indicator."""
        self.is_running = True
        self.message = message
        self.start_time = time.time()
        self.poll_count = 0

    def update_poll(self) -> None:
        """Update the poll count and time."""
        self.poll_count += 1
        self.last_poll_time = time.time()

    def stop(self, message: str = "Completed") -> None:
        """Stop the progress indicator."""
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)
        print(f"\n{message}")

    def _spin(self, message: str) -> None:
        """Run the spinner animation."""
        idx = 0
        while self.is_running:
            elapsed = time.time() - (self.start_time or time.time())
            elapsed_str = f"{elapsed:.1f}s"

            # Calculate polling info
            poll_info = ""
            if self.poll_count > 0:
                time_since_last_poll = time.time() - (self.last_poll_time or time.time())
                poll_freq = self.poll_count / elapsed if elapsed > 0 else 0
                poll_info = f" | Polls: {self.poll_count} ({poll_freq:.1f}/s, {time_since_last_poll:.1f}s ago)"

            # Create progress line
            spinner = self.colors["cyan"] + self.spinner_chars[idx] + self.colors["reset"]
            progress_line = f"\r{spinner} {message} | Elapsed: {elapsed_str}{poll_info}"

            print(progress_line, end="", flush=True)

            idx = (idx + 1) % len(self.spinner_chars)
            time.sleep(0.1)


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

  # Export and trigger generation for recordings without transcriptions
  pai-note-exporter export --generate-if-needed

  # Generate transcriptions and summaries
  pai-note-exporter generate

  # Generate with custom options
  pai-note-exporter generate --limit 5 --all

  # Generate and exit immediately without waiting
  pai-note-exporter generate --no-wait
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

    # Generate command
    generate_parser = subparsers.add_parser(
        "generate", help="Generate transcriptions and summaries for recordings"
    )
    generate_parser.add_argument(
        "--env-file",
        type=Path,
        help="Path to .env file (default: .env in current directory)",
    )
    generate_parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of recent recordings to show (default: 10)",
    )
    generate_parser.add_argument(
        "--all",
        action="store_true",
        help="Generate for all recordings without prompting for selection",
    )
    generate_parser.add_argument(
        "--force",
        action="store_true",
        help="Force regeneration even if transcription/summary already exists",
    )
    generate_parser.add_argument(
        "--no-wait",
        action="store_true",
        help="Trigger generation and exit immediately without waiting for completion",
    )
    generate_parser.add_argument(
        "--max-wait-time",
        type=int,
        default=300,
        help="Maximum time to wait for generation completion in seconds (default: 300)",
    )
    generate_parser.add_argument(
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


async def export_single_file(
    exporter: PlaudAIExporter,
    file_info: dict[str, Any],
    output_dir: Path,
    export_format: str,
    include_audio: bool,
    skip_transcription: bool,
    text_processor: TextProcessor,
    logger: logging.Logger,
) -> None:
    """Export a single file's transcription and/or audio.

    Args:
        exporter: The PlaudAIExporter instance
        file_info: File information dictionary
        output_dir: Directory to save files
        export_format: Format for transcription export
        include_audio: Whether to download audio
        skip_transcription: Whether to skip transcription export
        text_processor: Text processing utility
        logger: Logger instance
    """
    file_id = file_info["id"]
    filename = file_info["filename"]

    # Export transcription if not skipped
    if not skip_transcription:
        has_transcription = file_info.get("is_trans", False)
        has_summary = file_info.get("is_summary", False)

        if has_transcription or has_summary:
            # Try to download transcription first, then summary if that fails
            transcription_data: str | bytes | None = None
            export_type = None

            if has_transcription:
                try:
                    print("  📝 Downloading transcription...")
                    transcription_data = await exporter.download_transcription(file_id)
                    if transcription_data:
                        export_type = "transcription"
                    else:
                        print(
                            "  ⚠️ Transcription download returned empty content, trying summary..."
                        )
                except Exception as e:
                    logger.warning(f"Failed to download transcription: {e}")
                    print("  ⚠️ Transcription download failed, trying summary...")

            # If transcription failed or wasn't available, try summary
            if transcription_data is None and has_summary:
                try:
                    if export_type != "transcription":
                        print("  📝 Downloading summary...")
                    # For summary, we still need to use export API since download_transcription seems to be for transcription only
                    transcription_data = await exporter.export_transcription(
                        file_id=file_id,
                        prompt_type="summary",
                        to_format=export_format.upper(),
                        title=filename,
                        content=file_info.get("summary_result", ""),
                        with_speaker=1,
                        with_timestamp=1,
                    )
                    export_type = "summary"
                except Exception as e:
                    logger.error(f"Failed to export summary: {e}")
                    print("  ✗ Summary export also failed")
                    return

            # Process transcription/summary content for better readability
            try:
                if isinstance(transcription_data, str):
                    # transcription_data is already a string from download_transcription
                    raw_text = transcription_data
                else:
                    # transcription_data is bytes from export_transcription
                    raw_text = transcription_data.decode("utf-8")  # type: ignore[union-attr]

                processed_text = text_processor.process_transcription(raw_text)
                transcription_data = processed_text.encode("utf-8")
                print(f"  ✓ {export_type.title()} processed and cleaned")  # type: ignore[union-attr]
            except Exception as e:
                logger.warning(f"Failed to process {export_type} text: {e}")
                print(f"  ⚠️ {export_type.title()} processing failed, saving raw content")  # type: ignore[union-attr]

                # Ensure transcription_data is bytes for file writing
                if isinstance(transcription_data, str):
                    transcription_data = transcription_data.encode("utf-8")

            # Save transcription/summary
            content_type = "transcript" if export_type == "transcription" else "summary"
            trans_filename = f"{filename}_{content_type}.{export_format.lower()}"
            trans_path = output_dir / trans_filename
            with open(trans_path, "wb") as f:
                f.write(transcription_data)  # type: ignore[arg-type]
            print(f"  ✓ {export_type.title()} saved to {trans_path}")  # type: ignore[union-attr]
        else:
            print("  📝 Skipping transcription export (file not transcribed)")
    else:
        print("  📝 Skipping transcription export (--skip-transcription)")

    # Export audio if requested
    if include_audio:
        print("  🎵 Downloading audio file...")
        temp_url = await exporter.get_temp_url(file_id)
        audio_path = await exporter.download_file(temp_url, f"{filename}.mp3", output_dir)
        print(f"  ✓ Audio saved: {audio_path}")
    else:
        print("  🎵 Skipping audio download (use --include-audio to download)")


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
                            selection = (
                                input(
                                    f"\nEnter recording numbers to export (1-{len(files)}, comma-separated, or 'all'): "
                                )
                                .strip()
                                .lower()
                            )

                            if selection == "all":
                                selected_indices = list(range(len(files)))
                                break
                            elif selection == "":
                                print("No recordings selected. Exiting.")
                                return 0
                            else:
                                indices: list[int] = []
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

                # Separate files into those with and without transcripts
                # Use the is_trans field from file metadata (most reliable indicator)
                files_with_transcripts = []
                files_needing_transcription = []

                print("  📊 Checking transcription availability for selected recordings...")

                for idx in selected_indices:
                    file_info = files[idx]
                    filename = file_info["filename"]

                    # Check the is_trans field from the file metadata
                    has_transcription = file_info.get("is_trans", False)

                    if has_transcription:
                        files_with_transcripts.append((idx, file_info))
                        print(f"  ✓ {filename[:50]}...: transcription available")
                    else:
                        files_needing_transcription.append((idx, file_info))
                        print(f"  ⚠️ {filename[:50]}...: transcription not ready")

                # Phase 1: Export files that already have transcripts
                if files_with_transcripts:
                    print(
                        f"\n� Phase 1: Exporting {len(files_with_transcripts)} recording(s) with existing transcripts..."
                    )
                    output_dir.mkdir(parents=True, exist_ok=True)

                    for i, (_idx, file_info) in enumerate(files_with_transcripts, 1):
                        file_id = file_info["id"]
                        filename = file_info["filename"]

                        print(f"\n[{i}/{len(files_with_transcripts)}] Processing: {filename}")

                        try:
                            await export_single_file(
                                exporter,
                                file_info,
                                output_dir,
                                export_format,
                                include_audio,
                                skip_transcription,
                                text_processor,
                                logger,
                            )
                        except APIError as e:
                            print(f"  ✗ Failed to export {filename}: {e}")
                            continue

                # Phase 2: Handle files needing transcription
                if files_needing_transcription:
                    print(
                        f"\n📝 Phase 2: {len(files_needing_transcription)} recording(s) need transcription"
                    )

                    # Show which files need transcription
                    print("\nRecordings needing transcription:")
                    print("-" * 80)
                    for i, (_idx, file_info) in enumerate(files_needing_transcription, 1):
                        print(f"{i:2d}. {exporter.format_file_info(file_info)}")
                    print("-" * 80)

                    # Prompt user about transcription generation
                    while True:
                        try:
                            response = (
                                input(
                                    f"\nGenerate transcriptions for these {len(files_needing_transcription)} recording(s)? "
                                    "[Y]es (wait for completion), [n]o, [s]elect specific: "
                                )
                                .strip()
                                .lower()
                            )

                            if response in ("y", "yes", ""):  # Default is yes
                                selected_for_generation = files_needing_transcription
                                wait_for_completion = True
                                break
                            elif response in ("n", "no"):
                                print("Skipping transcription generation.")
                                selected_for_generation = []
                                break
                            elif response == "s":
                                # Let user select specific recordings
                                selection = input(
                                    f"Enter recording numbers (1-{len(files_needing_transcription)}, comma-separated): "
                                ).strip()

                                if not selection:
                                    print("No recordings selected for generation.")
                                    selected_for_generation = []
                                    break

                                indices = []
                                for part in selection.split(","):
                                    part = part.strip()
                                    try:
                                        idx = int(part.strip()) - 1
                                        if 0 <= idx < len(files_needing_transcription):
                                            indices.append(idx)
                                        else:
                                            print(f"Warning: Invalid index {idx + 1}, skipping")
                                    except ValueError:
                                        print(f"Warning: Invalid input '{part}', skipping")

                                selected_for_generation = [
                                    files_needing_transcription[i] for i in indices
                                ]
                                if selected_for_generation:
                                    wait_for_completion = True
                                    break
                                else:
                                    print("No valid recordings selected. Please try again.")
                            else:
                                print(
                                    "Please enter 'y' (yes), 'n' (no), 's' (select), or press Enter for yes."
                                )

                        except (ValueError, KeyboardInterrupt):
                            print("\nInvalid input. Please try again.")

                    # Generate transcriptions for selected files
                    if selected_for_generation:
                        print(
                            f"\n🚀 Generating transcriptions for {len(selected_for_generation)} recording(s)..."
                        )

                        for i, (_idx, file_info) in enumerate(selected_for_generation, 1):
                            file_id = file_info["id"]
                            filename = file_info["filename"]

                            print(f"\n[{i}/{len(selected_for_generation)}] Processing: {filename}")

                            try:
                                # Check current status first
                                summary_status = await exporter.get_summary_status(file_id)

                                if summary_status == "completed":
                                    print("  ✓ Transcription already completed")
                                elif summary_status == "processing":
                                    print("  ⏳ Transcription already in progress")
                                else:
                                    # Trigger generation
                                    print("  ⏳ Starting transcription and summary generation...")
                                    success = await exporter.generate_transcription_and_summary(
                                        file_id
                                    )
                                    if success:
                                        print("  ✓ Transcription and summary generation triggered")
                                    else:
                                        print("  ✗ Failed to trigger generation")
                                        continue

                                # Wait for completion if requested
                                if wait_for_completion and summary_status != "completed":
                                    progress = ProgressIndicator()
                                    progress.start(f"Waiting for {filename}")

                                    poll_interval = 5
                                    max_polls = 300 // poll_interval  # 5 minutes max

                                    for _poll_num in range(max_polls):
                                        progress.update_poll()

                                        status = await exporter.check_generation_status(file_id)

                                        if status == "completed":
                                            progress.stop("  ✓ Generation completed successfully!")
                                            break
                                        elif status == "failed":
                                            progress.stop("  ✗ Generation failed")
                                            break
                                        elif status == "unknown":
                                            progress.stop(
                                                "  ⚠️ Unable to determine generation status"
                                            )
                                            break

                                        await asyncio.sleep(poll_interval)
                                    else:
                                        progress.stop("  ⏰ Generation timed out")

                            except APIError as e:
                                print(f"  ✗ Failed to generate for {filename}: {e}")
                                continue

                        # Now export the newly transcribed files
                        if selected_for_generation:
                            print("\n📝 Exporting newly transcribed recording(s)...")

                            for i, (_idx, file_info) in enumerate(selected_for_generation, 1):
                                file_id = file_info["id"]
                                filename = file_info["filename"]

                                print(
                                    f"\n[{i}/{len(selected_for_generation)}] Exporting: {filename}"
                                )

                                try:
                                    await export_single_file(
                                        exporter,
                                        file_info,
                                        output_dir,
                                        export_format,
                                        include_audio,
                                        skip_transcription,
                                        text_processor,
                                        logger,
                                    )
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


async def generate_command(
    env_file: Path | None = None,
    limit: int = 10,
    export_all: bool = False,
    force: bool = False,
    wait_for_completion: bool = True,  # Changed default to True
    max_wait_time: int = 300,
    log_level: str | None = None,
) -> int:
    """Execute the generate command.

    Args:
        env_file: Optional path to .env file
        limit: Maximum number of recordings to show
        export_all: Whether to generate for all recordings without prompting
        force: Whether to force regeneration even if content already exists
        wait_for_completion: Whether to wait for generation to complete
        max_wait_time: Maximum time to wait for generation completion
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
        logger.info("Starting Pai Note Exporter - Generate Mode")

        # First, login to get the auth token
        print("🔐 Logging into Plaud.ai...")
        async with PlaudAILogin(config) as login:
            success, token = await login.login()

            if not success or not token:
                print("\n✗ Login failed - cannot proceed with generation")
                return 1

            print("✓ Login successful!")

            # Now list recent files
            print(f"\n📋 Fetching {limit} most recent recordings...")
            async with PlaudAIExporter(config, token) as exporter:
                all_files = await exporter.list_files(limit=limit)

                if not all_files:
                    print("\n📭 No recordings found")
                    return 0

                # Filter files based on transcription status and force flag
                if force:
                    # Show all files when force is enabled
                    files = all_files
                    filter_message = "(showing all recordings, including already transcribed)"
                else:
                    # Filter out files that already have transcriptions
                    files = []
                    for file_info in all_files:
                        has_transcription = file_info.get("is_trans", False)
                        if not has_transcription:
                            files.append(file_info)

                    if len(files) < len(all_files):
                        skipped_count = len(all_files) - len(files)
                        filter_message = (
                            f"(filtered out {skipped_count} already transcribed recording(s))"
                        )
                    else:
                        filter_message = ""

                if not files:
                    if force:
                        print("\n📭 No recordings found")
                    else:
                        print("\n📭 No recordings found that need transcription")
                        print("💡 Use --force to regenerate existing transcriptions")
                    return 0

                print(f"\n📋 Found {len(files)} recordings {filter_message}:")
                print("-" * 80)

                for i, file_info in enumerate(files, 1):
                    print(f"{i:2d}. {exporter.format_file_info(file_info)}")

                print("-" * 80)

                # Handle selection
                if export_all:
                    selected_indices = list(range(len(files)))
                    print(f"📋 Auto-selecting all {len(files)} recordings for generation")
                else:
                    # Prompt user for selection
                    while True:
                        try:
                            selection = (
                                input(
                                    f"\nEnter recording numbers to generate (1-{len(files)}, comma-separated, or 'all'): "
                                )
                                .strip()
                                .lower()
                            )

                            if selection == "all":
                                selected_indices = list(range(len(files)))
                                break
                            elif selection == "":
                                print("No recordings selected. Exiting.")
                                return 0
                            else:
                                indices: list[int] = []
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

                # Generate transcriptions and summaries for selected files
                print(f"\n🚀 Generating for {len(selected_indices)} recording(s)...")

                for i, idx in enumerate(selected_indices, 1):
                    file_info = files[idx]
                    file_id = file_info["id"]
                    filename = file_info["filename"]

                    print(f"\n[{i}/{len(selected_indices)}] Processing: {filename}")

                    try:
                        # First check if transcription/summary already exists
                        async with PlaudAIExporter(config, token) as exporter:
                            # Check both transcription and summary status
                            has_transcription = file_info.get("is_trans", False)
                            summary_status = await exporter.get_summary_status(file_id)

                            if has_transcription and summary_status == "completed" and not force:
                                print("  ℹ️ Recording already has transcription and summary")
                                if not wait_for_completion:
                                    print("  ✓ Skipping generation (content already available)")
                                    continue
                                else:
                                    print("  ✓ Content already completed, no need to wait")
                                    continue
                            elif has_transcription and summary_status == "processing" and not force:
                                print(
                                    "  ℹ️ Recording has transcription, summary generation already in progress"
                                )
                                if wait_for_completion:
                                    print(
                                        "  ⏳ Waiting for existing summary generation to complete..."
                                    )
                                else:
                                    print("  ✓ Summary generation already in progress")
                                    continue
                            elif (
                                has_transcription
                                and summary_status not in ["completed", "processing"]
                                and not force
                            ):
                                print("  ℹ️ Recording has transcription but no summary")
                                if wait_for_completion:
                                    print("  ⏳ Generating summary for existing transcription...")
                                else:
                                    print(
                                        "  ⏳ Triggering summary generation for existing transcription..."
                                    )

                                success = await exporter.generate_transcription_and_summary(file_id)
                                if not success:
                                    print("  ✗ Failed to trigger summary generation")
                                    continue
                                print("  ✓ Summary generation triggered")
                            else:
                                # Need to trigger generation (either doesn't exist or force is True)
                                if force and has_transcription and summary_status == "completed":
                                    print(
                                        "  🔄 Forcing regeneration (overriding existing transcription and summary)..."
                                    )
                                elif force and has_transcription and summary_status == "processing":
                                    print(
                                        "  🔄 Forcing regeneration (overriding existing transcription and in-progress summary)..."
                                    )
                                elif force and has_transcription:
                                    print(
                                        "  🔄 Forcing regeneration (overriding existing transcription)..."
                                    )
                                else:
                                    print("  ⏳ Starting transcription and summary generation...")

                                success = await exporter.generate_transcription_and_summary(file_id)
                                if not success:
                                    print("  ✗ Failed to trigger generation")
                                    continue
                                print("  ✓ Transcription and summary generation triggered")

                        # Wait for completion if requested
                        if wait_for_completion:
                            if has_transcription and summary_status == "completed":
                                print("  ✓ Content already completed")
                            elif has_transcription and summary_status == "processing":
                                print("  ⏳ Waiting for existing summary generation to complete...")
                                progress = ProgressIndicator()
                                progress.start(f"Waiting for {filename}")

                                async with PlaudAIExporter(config, token) as exporter:
                                    poll_interval = 5  # Check every 5 seconds
                                    max_polls = max_wait_time // poll_interval

                                    for _poll_num in range(max_polls):
                                        # Update progress with poll info
                                        progress.update_poll()

                                        status = await exporter.check_generation_status(file_id)

                                        if status == "completed":
                                            progress.stop(
                                                "  ✓ Summary generation completed successfully!"
                                            )
                                            break
                                        elif status == "failed":
                                            progress.stop("  ✗ Summary generation failed")
                                            break
                                        elif status == "unknown":
                                            progress.stop(
                                                "  ⚠️ Unable to determine summary generation status"
                                            )
                                            break

                                        # Wait before next poll
                                        await asyncio.sleep(poll_interval)
                                    else:
                                        # Timeout reached
                                        progress.stop("  ⏰ Summary generation timed out")
                            else:
                                # Just triggered generation, now wait
                                progress = ProgressIndicator()
                                progress.start(f"Waiting for {filename}")

                                async with PlaudAIExporter(config, token) as exporter:
                                    poll_interval = 5  # Check every 5 seconds
                                    max_polls = max_wait_time // poll_interval

                                    for _poll_num in range(max_polls):
                                        # Update progress with poll info
                                        progress.update_poll()

                                        status = await exporter.check_generation_status(file_id)

                                        if status == "completed":
                                            progress.stop("  ✓ Generation completed successfully!")
                                            break
                                        elif status == "failed":
                                            progress.stop("  ✗ Generation failed")
                                            break
                                        elif status == "unknown":
                                            progress.stop(
                                                "  ⚠️ Unable to determine generation status"
                                            )
                                            break

                                        # Wait before next poll
                                        await asyncio.sleep(poll_interval)
                                    else:
                                        # Timeout reached
                                        progress.stop("  ⏰ Generation timed out")
                        else:
                            print("  ✓ Generation triggered (not waiting for completion)")

                    except APIError as e:
                        print(f"  ✗ Failed to generate for {filename}: {e}")
                        continue

                print("\n✅ Generation triggered! Check Plaud.ai for progress.")
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
        print("\n\n⚠️  Generation cancelled by user")
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
    elif args.command == "generate":
        return asyncio.run(
            generate_command(
                env_file=args.env_file,
                limit=args.limit,
                export_all=args.all,
                wait_for_completion=not args.no_wait,  # Invert the logic
                max_wait_time=args.max_wait_time,
                log_level=args.log_level,
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
