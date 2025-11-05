#!/usr/bin/env python3
"""
Basic Usage Example for Pai Note Exporter

This example demonstrates the basic usage of the Pai Note Exporter library
to authenticate with Plaud.ai and export recordings with transcriptions.
"""

import asyncio
import os
from pathlib import Path

from pai_note_exporter.config import Config
from pai_note_exporter.login import login
from pai_note_exporter.export import PlaudAIExporter


async def main():
    """Main function demonstrating basic export functionality."""
    print("Pai Note Exporter - Basic Usage Example")
    print("=" * 50)

    # Load configuration from environment
    try:
        config = Config.from_env()
        print("✓ Configuration loaded successfully")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        print("Make sure your .env file contains PLAUD_EMAIL and PLAUD_PASSWORD")
        return

    # Authenticate with Plaud.ai
    try:
        print("Authenticating with Plaud.ai...")
        token = await login(config)
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return

    # Create exporter instance
    exporter = PlaudAIExporter(token, config)

    # List available recordings
    try:
        print("Fetching available recordings...")
        files = await exporter.list_files()
        print(f"✓ Found {len(files)} recordings")

        if not files:
            print("No recordings found. Please ensure you have recordings in your Plaud.ai account.")
            return

    except Exception as e:
        print(f"✗ Failed to list files: {e}")
        return

    # Display available recordings
    print("\nAvailable recordings:")
    print("-" * 30)
    for i, file_info in enumerate(files[:10], 1):  # Show first 10
        name = file_info.get('name', 'Unknown')
        duration = file_info.get('duration', 0)
        has_transcription = file_info.get('is_trans', False)
        status = "✓ Transcribed" if has_transcription else "○ Not transcribed"

        print(f"{i:2d}. {name}")
        print(f"    Duration: {duration // 60}:{duration % 60:02d}")
        print(f"    Status: {status}")
        print()

    if len(files) > 10:
        print(f"... and {len(files) - 10} more recordings")

    # Export the first recording
    if files:
        print("Exporting first recording...")
        try:
            await exporter.download_file(files[0], include_audio=False)
            print("✓ Export completed successfully")

            # Show exported files
            export_dir = Path(config.export_dir)
            if export_dir.exists():
                exported_files = list(export_dir.glob("*"))
                if exported_files:
                    print(f"Exported files in {export_dir}:")
                    for file_path in exported_files:
                        print(f"  - {file_path.name}")

        except Exception as e:
            print(f"✗ Export failed: {e}")

    print("\nExample completed!")


if __name__ == "__main__":
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir.parent)  # Go to project root

    asyncio.run(main())