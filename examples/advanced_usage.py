#!/usr/bin/env python3
"""
Advanced Usage Example for Pai Note Exporter

This example demonstrates advanced features including:
- Custom configuration
- Batch processing
- Error handling
- Progress tracking
- Selective export based on criteria
"""

import asyncio
import os
import time
from pathlib import Path
from typing import List, Dict, Any

from pai_note_exporter.config import Config
from pai_note_exporter.login import login
from pai_note_exporter.export import PlaudAIExporter
from pai_note_exporter.exceptions import PlaudAIError


class AdvancedExporter:
    """Advanced exporter with batch processing and filtering capabilities."""

    def __init__(self, token: str, config: Config):
        self.exporter = PlaudAIExporter(token, config)
        self.config = config

    async def get_recordings_with_criteria(
        self,
        min_duration: int = 0,
        max_duration: int = None,
        has_transcription: bool = None,
        limit: int = None
    ) -> List[Dict[str, Any]]:
        """Get recordings filtered by criteria."""
        print("Fetching recordings with filters...")
        all_files = await self.exporter.list_files()

        filtered_files = []
        for file_info in all_files:
            duration = file_info.get('duration', 0)
            is_trans = file_info.get('is_trans', False)

            # Apply filters
            if duration < min_duration:
                continue
            if max_duration and duration > max_duration:
                continue
            if has_transcription is not None and is_trans != has_transcription:
                continue

            filtered_files.append(file_info)

            if limit and len(filtered_files) >= limit:
                break

        return filtered_files

    async def export_batch(
        self,
        files: List[Dict[str, Any]],
        include_audio: bool = False,
        batch_size: int = 5
    ) -> Dict[str, Any]:
        """Export files in batches with progress tracking."""
        total_files = len(files)
        successful_exports = 0
        failed_exports = 0
        errors = []

        print(f"Starting batch export of {total_files} files (batch size: {batch_size})")

        for i in range(0, total_files, batch_size):
            batch = files[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (total_files + batch_size - 1) // batch_size

            print(f"\nProcessing batch {batch_num}/{total_batches} ({len(batch)} files)")

            # Process batch concurrently
            tasks = []
            for file_info in batch:
                task = self._export_single_file_safe(file_info, include_audio)
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for j, result in enumerate(results):
                file_info = batch[j]
                file_name = file_info.get('name', 'Unknown')

                if isinstance(result, Exception):
                    print(f"✗ Failed to export '{file_name}': {result}")
                    failed_exports += 1
                    errors.append({
                        'file': file_name,
                        'error': str(result)
                    })
                else:
                    print(f"✓ Successfully exported '{file_name}'")
                    successful_exports += 1

            # Small delay between batches to be respectful
            if i + batch_size < total_files:
                print("Waiting 2 seconds before next batch...")
                await asyncio.sleep(2)

        return {
            'total': total_files,
            'successful': successful_exports,
            'failed': failed_exports,
            'errors': errors
        }

    async def _export_single_file_safe(self, file_info: Dict[str, Any], include_audio: bool) -> None:
        """Safely export a single file with error handling."""
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                await self.exporter.download_file(file_info, include_audio)
                return  # Success
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e  # Last attempt failed
                print(f"  Retry {attempt + 1}/{max_retries} for '{file_info.get('name', 'Unknown')}': {e}")
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff


async def main():
    """Main function demonstrating advanced export functionality."""
    print("Pai Note Exporter - Advanced Usage Example")
    print("=" * 55)

    # Custom configuration
    config = Config(
        email=os.getenv("PLAUD_EMAIL", "your-email@example.com"),
        password=os.getenv("PLAUD_PASSWORD", "your-password"),
        log_level="INFO",
        export_dir="./advanced_exports",
        api_timeout=60
    )

    # Validate configuration
    try:
        config.validate()
        print("✓ Configuration validated")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return

    # Create export directory
    export_path = Path(config.export_dir)
    export_path.mkdir(exist_ok=True)
    print(f"✓ Export directory: {export_path.absolute()}")

    # Authenticate
    try:
        print("Authenticating with Plaud.ai...")
        start_time = time.time()
        token = await login(config)
        auth_time = time.time() - start_time
        print(".2f")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return

    # Create advanced exporter
    advanced_exporter = AdvancedExporter(token, config)

    # Get recordings with filters
    try:
        # Filter for recordings longer than 5 minutes with transcriptions
        filtered_files = await advanced_exporter.get_recordings_with_criteria(
            min_duration=300,  # 5 minutes
            has_transcription=True,
            limit=20  # Limit to 20 files for this example
        )

        print(f"✓ Found {len(filtered_files)} recordings matching criteria")

        if not filtered_files:
            print("No recordings match the specified criteria.")
            print("Try adjusting the filters or ensure you have transcribed recordings.")
            return

    except Exception as e:
        print(f"✗ Failed to fetch recordings: {e}")
        return

    # Display filtered recordings
    print("\nFiltered recordings:")
    print("-" * 40)
    total_duration = 0
    for i, file_info in enumerate(filtered_files, 1):
        name = file_info.get('name', 'Unknown')
        duration = file_info.get('duration', 0)
        total_duration += duration

        hours, remainder = divmod(duration, 3600)
        minutes, seconds = divmod(remainder, 60)

        duration_str = f"{hours}:{minutes:02d}:{seconds:02d}" if hours else f"{minutes}:{seconds:02d}"

        print(f"{i:2d}. {name}")
        print(f"    Duration: {duration_str}")
        print()

    # Calculate total duration
    total_hours, remainder = divmod(total_duration, 3600)
    total_minutes, total_seconds = divmod(remainder, 60)
    total_str = f"{total_hours}:{total_minutes:02d}:{total_seconds:02d}" if total_hours else f"{total_minutes}:{total_seconds:02d}"
    print(f"Total duration: {total_str}")

    # Confirm export
    response = input(f"\nExport {len(filtered_files)} recordings? (y/N): ").lower().strip()
    if response not in ('y', 'yes'):
        print("Export cancelled.")
        return

    # Perform batch export
    start_time = time.time()
    results = await advanced_exporter.export_batch(
        filtered_files,
        include_audio=False,  # Set to True to include audio files
        batch_size=3  # Process 3 files concurrently
    )
    export_time = time.time() - start_time

    # Display results
    print("
Export Results:")
    print("-" * 20)
    print(f"Total files: {results['total']}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(".2f")
    print(".2f")

    if results['errors']:
        print(f"\nErrors ({len(results['errors'])}):")
        for error in results['errors'][:5]:  # Show first 5 errors
            print(f"  - {error['file']}: {error['error']}")
        if len(results['errors']) > 5:
            print(f"  ... and {len(results['errors']) - 5} more errors")

    # Show exported files
    exported_files = list(export_path.glob("*"))
    if exported_files:
        print(f"\nExported files in {export_path}:")
        for file_path in sorted(exported_files):
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(".1f")

    print("\nAdvanced example completed!")


if __name__ == "__main__":
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent)  # Go to project root

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        raise