# Examples

Practical examples showing how to use Pai Note Exporter in various scenarios.

## Basic Usage

### Simple Export Script

```python
#!/usr/bin/env python3
"""
Basic export example - export all recordings to default directory
"""
import asyncio
from pai_note_exporter import PlaudClient, Exporter

async def main():
    # Initialize client
    client = PlaudClient(
        email="your-email@example.com",
        password="your-password"
    )

    try:
        # Login
        print("🔐 Logging in...")
        await client.login()
        print("✅ Login successful")

        # Create exporter
        exporter = Exporter(client)

        # Export all recordings
        print("📥 Exporting recordings...")
        result = await exporter.export_all()

        print(f"✅ Export complete: {result.successful}/{result.total} successful")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    finally:
        await client.close()

    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
```

### Selective Export

```python
#!/usr/bin/env python3
"""
Export only recent recordings or recordings matching criteria
"""
import asyncio
from datetime import datetime, timedelta
from pai_note_exporter import PlaudClient, Exporter

async def export_recent_recordings(days: int = 7):
    """Export recordings from the last N days"""
    client = PlaudClient("email", "password")

    try:
        await client.login()

        # Get all recordings
        recordings = await client.get_recordings()

        # Filter recent recordings
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_recordings = [
            r for r in recordings
            if r.created_at > cutoff_date
        ]

        print(f"📁 Found {len(recent_recordings)} recordings from last {days} days")

        if not recent_recordings:
            print("No recent recordings found")
            return

        # Export recent recordings
        exporter = Exporter(client)
        successful = 0

        for recording in recent_recordings:
            try:
                result = await exporter.export_recording(recording)
                if result:
                    successful += 1
                    print(f"✅ Exported: {recording.name}")
                else:
                    print(f"❌ Failed: {recording.name}")
            except Exception as e:
                print(f"❌ Error exporting {recording.name}: {e}")

        print(f"📊 Exported {successful}/{len(recent_recordings)} recordings")

    finally:
        await client.close()

async def export_by_duration(min_duration: int = 300):
    """Export recordings longer than specified duration (seconds)"""
    client = PlaudClient("email", "password")

    try:
        await client.login()

        recordings = await client.get_recordings()
        long_recordings = [r for r in recordings if r.duration > min_duration]

        print(f"📁 Found {len(long_recordings)} recordings longer than {min_duration}s")

        exporter = Exporter(client, include_audio=True)

        for recording in long_recordings:
            await exporter.export_recording(recording)
            print(f"✅ Exported: {recording.name} ({recording.duration}s)")

    finally:
        await client.close()

if __name__ == "__main__":
    # Export recordings from last 7 days
    asyncio.run(export_recent_recordings(7))

    # Export recordings longer than 5 minutes
    asyncio.run(export_by_duration(300))
```

## Advanced Examples

### Custom Export with Metadata

```python
#!/usr/bin/env python3
"""
Export recordings with custom metadata and organization
"""
import asyncio
import json
import os
from pathlib import Path
from pai_note_exporter import PlaudClient, Exporter

class CustomExporter:
    """Enhanced exporter with metadata and organization"""

    def __init__(self, client, base_dir="organized_exports"):
        self.client = client
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(exist_ok=True)

    async def export_with_metadata(self, recording):
        """Export recording with JSON metadata"""
        # Create subdirectory by date
        date_dir = self.base_dir / recording.created_at.strftime("%Y-%m-%d")
        date_dir.mkdir(exist_ok=True)

        # Export transcription
        exporter = Exporter(self.client, output_dir=str(date_dir))
        success = await exporter.export_recording(recording)

        if success:
            # Create metadata file
            metadata = {
                "id": recording.id,
                "name": recording.name,
                "duration": recording.duration,
                "created_at": recording.created_at.isoformat(),
                "status": recording.status,
                "has_audio": recording.has_audio,
                "has_transcription": recording.has_transcription,
                "exported_at": datetime.now().isoformat(),
                "file_path": str(date_dir / recording.get_filename("txt"))
            }

            metadata_file = date_dir / f"{recording.name}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            print(f"✅ Exported with metadata: {recording.name}")

        return success

    async def export_all_organized(self):
        """Export all recordings organized by date"""
        recordings = await self.client.get_recordings()

        # Group by date
        by_date = {}
        for recording in recordings:
            date_key = recording.created_at.strftime("%Y-%m-%d")
            if date_key not in by_date:
                by_date[date_key] = []
            by_date[date_key].append(recording)

        # Export by date
        total_exported = 0
        for date, date_recordings in by_date.items():
            print(f"📅 Processing {date}: {len(date_recordings)} recordings")

            for recording in date_recordings:
                success = await self.export_with_metadata(recording)
                if success:
                    total_exported += 1

        print(f"📊 Total exported: {total_exported} recordings")

async def main():
    client = PlaudClient("email", "password")

    try:
        await client.login()

        custom_exporter = CustomExporter(client)
        await custom_exporter.export_all_organized()

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Audio Processing Pipeline

```python
#!/usr/bin/env python3
"""
Export audio files and process them (requires additional dependencies)
"""
import asyncio
import subprocess
from pathlib import Path
from pai_note_exporter import PlaudClient, Exporter

class AudioProcessor:
    """Process exported audio files"""

    def __init__(self, export_dir="exports"):
        self.export_dir = Path(export_dir)

    def convert_to_wav(self, mp3_path: Path) -> Path:
        """Convert MP3 to WAV format"""
        wav_path = mp3_path.with_suffix('.wav')

        # Requires ffmpeg
        cmd = [
            'ffmpeg', '-i', str(mp3_path),
            '-acodec', 'pcm_s16le', '-ar', '16000',
            str(wav_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return wav_path
        else:
            raise Exception(f"Conversion failed: {result.stderr}")

    def get_audio_duration(self, file_path: Path) -> float:
        """Get audio duration using ffprobe"""
        cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json',
            '-show_format', str(file_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            import json
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        else:
            raise Exception(f"Failed to get duration: {result.stderr}")

    def compress_audio(self, file_path: Path, quality=128) -> Path:
        """Compress audio file"""
        compressed_path = file_path.parent / f"{file_path.stem}_compressed.mp3"

        cmd = [
            'ffmpeg', '-i', str(file_path),
            '-b:a', f'{quality}k', str(compressed_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return compressed_path
        else:
            raise Exception(f"Compression failed: {result.stderr}")

async def export_and_process_audio():
    """Export audio files and process them"""
    client = PlaudClient("email", "password")
    processor = AudioProcessor()

    try:
        await client.login()

        # Export with audio
        exporter = Exporter(client, include_audio=True)
        recordings = await client.get_recordings()

        for recording in recordings[:3]:  # Process first 3
            print(f"🎵 Processing: {recording.name}")

            # Export audio
            success = await exporter.export_recording(recording)
            if not success:
                continue

            # Get exported file path
            mp3_path = Path(exporter.get_export_path(recording, "mp3"))

            if mp3_path.exists():
                try:
                    # Convert to WAV
                    wav_path = processor.convert_to_wav(mp3_path)
                    print(f"  ✅ Converted to WAV: {wav_path.name}")

                    # Get duration
                    duration = processor.get_audio_duration(wav_path)
                    print(f"  📊 Duration: {duration:.1f}s")

                    # Compress
                    compressed_path = processor.compress_audio(mp3_path)
                    print(f"  📦 Compressed: {compressed_path.name}")

                except Exception as e:
                    print(f"  ❌ Processing failed: {e}")

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(export_and_process_audio())
```

### Database Integration

```python
#!/usr/bin/env python3
"""
Export recordings and store metadata in SQLite database
"""
import asyncio
import sqlite3
from datetime import datetime
from pathlib import Path
from pai_note_exporter import PlaudClient, Exporter

class DatabaseExporter:
    """Export recordings and track them in a database"""

    def __init__(self, db_path="recordings.db"):
        self.db_path = Path(db_path)
        self.init_database()

    def init_database(self):
        """Initialize SQLite database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS recordings (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    duration INTEGER,
                    created_at TIMESTAMP,
                    status TEXT,
                    has_audio BOOLEAN,
                    has_transcription BOOLEAN,
                    exported_at TIMESTAMP,
                    file_path TEXT,
                    transcription_preview TEXT
                )
            ''')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS export_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recording_id TEXT,
                    export_type TEXT,
                    export_time TIMESTAMP,
                    success BOOLEAN,
                    error_message TEXT,
                    FOREIGN KEY (recording_id) REFERENCES recordings(id)
                )
            ''')

    def record_exists(self, recording_id: str) -> bool:
        """Check if recording is already in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT id FROM recordings WHERE id = ?",
                (recording_id,)
            )
            return cursor.fetchone() is not None

    def save_recording(self, recording, file_path: str = None):
        """Save recording metadata to database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO recordings
                (id, name, duration, created_at, status, has_audio,
                 has_transcription, exported_at, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                recording.id,
                recording.name,
                recording.duration,
                recording.created_at,
                recording.status,
                recording.has_audio,
                recording.has_transcription,
                datetime.now(),
                file_path
            ))

    def save_transcription_preview(self, recording_id: str, preview: str):
        """Save first few lines of transcription"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE recordings
                SET transcription_preview = ?
                WHERE id = ?
            ''', (preview, recording_id))

    def log_export(self, recording_id: str, export_type: str,
                   success: bool, error: str = None):
        """Log export attempt"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO export_history
                (recording_id, export_type, export_time, success, error_message)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                recording_id,
                export_type,
                datetime.now(),
                success,
                error
            ))

    async def smart_export(self, client: PlaudClient):
        """Export only new or updated recordings"""
        recordings = await client.get_recordings()
        exporter = Exporter(client)

        new_recordings = [r for r in recordings if not self.record_exists(r.id)]

        print(f"📁 Found {len(new_recordings)} new recordings")

        for recording in new_recordings:
            try:
                # Export recording
                success = await exporter.export_recording(recording)
                file_path = exporter.get_export_path(recording, "txt")

                # Save to database
                self.save_recording(recording, file_path)

                # Read transcription preview
                if success and Path(file_path).exists():
                    with open(file_path, 'r') as f:
                        preview = ''.join(f.readlines()[:3])  # First 3 lines
                        self.save_transcription_preview(recording.id, preview)

                # Log export
                self.log_export(recording.id, "full", success)

                print(f"✅ Exported: {recording.name}")

            except Exception as e:
                error_msg = str(e)
                self.log_export(recording.id, "full", False, error_msg)
                print(f"❌ Failed: {recording.name} - {error_msg}")

async def main():
    client = PlaudClient("email", "password")
    db_exporter = DatabaseExporter()

    try:
        await client.login()
        await db_exporter.smart_export(client)

        # Query database
        with sqlite3.connect(db_exporter.db_path) as conn:
            recordings = conn.execute(
                "SELECT name, duration, exported_at FROM recordings ORDER BY exported_at DESC LIMIT 5"
            ).fetchall()

            print("\n📊 Recent exports:")
            for name, duration, exported_at in recordings:
                print(f"  {name}: {duration}s (exported: {exported_at})")

    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Webhook Integration

```python
#!/usr/bin/env python3
"""
Export recordings and send notifications via webhook
"""
import asyncio
import json
import httpx
from pai_note_exporter import PlaudClient, Exporter

class WebhookNotifier:
    """Send notifications about export progress"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self.client = httpx.AsyncClient()

    async def notify(self, event: str, data: dict):
        """Send webhook notification"""
        payload = {
            "event": event,
            "timestamp": datetime.now().isoformat(),
            "data": data
        }

        try:
            response = await self.client.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
        except Exception as e:
            print(f"⚠️  Webhook notification failed: {e}")

    async def close(self):
        await self.client.aclose()

async def export_with_notifications():
    """Export with webhook notifications"""
    client = PlaudClient("email", "password")
    exporter = Exporter(client)
    notifier = WebhookNotifier("https://your-webhook-url.com/notify")

    try:
        # Notify start
        await notifier.notify("export_started", {"message": "Starting recording export"})

        await client.login()
        recordings = await client.get_recordings()

        await notifier.notify("recordings_found", {
            "count": len(recordings),
            "total_duration": sum(r.duration for r in recordings)
        })

        successful = 0
        failed = 0

        for i, recording in enumerate(recordings, 1):
            try:
                result = await exporter.export_recording(recording)
                if result:
                    successful += 1
                    await notifier.notify("recording_exported", {
                        "recording": recording.name,
                        "duration": recording.duration,
                        "progress": f"{i}/{len(recordings)}"
                    })
                else:
                    failed += 1
                    await notifier.notify("recording_failed", {
                        "recording": recording.name,
                        "error": "Export failed"
                    })

            except Exception as e:
                failed += 1
                await notifier.notify("recording_error", {
                    "recording": recording.name,
                    "error": str(e)
                })

        # Final notification
        await notifier.notify("export_completed", {
            "successful": successful,
            "failed": failed,
            "total": len(recordings)
        })

    finally:
        await client.close()
        await notifier.close()

if __name__ == "__main__":
    asyncio.run(export_with_notifications())
```

### Docker Integration

```dockerfile
# Dockerfile for automated exports
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash exporter
USER exporter

# Create exports directory
RUN mkdir -p exports

# Set environment variables
ENV PLAUD_EXPORT_DIR=/app/exports
ENV PLAUD_TIMEOUT=60

# Run export
CMD ["python", "-c", "
import asyncio
from pai_note_exporter import PlaudClient, Exporter
import os

async def main():
    client = PlaudClient(
        email=os.getenv('PLAUD_EMAIL'),
        password=os.getenv('PLAUD_PASSWORD')
    )
    try:
        await client.login()
        exporter = Exporter(client)
        result = await exporter.export_all()
        print(f'Exported {result.successful} recordings')
    finally:
        await client.close()

asyncio.run(main())
"]
```

```bash
# Run with Docker
docker build -t pai-exporter .
docker run --rm \
  -e PLAUD_EMAIL="your-email@example.com" \
  -e PLAUD_PASSWORD="your-password" \
  -v $(pwd)/exports:/app/exports \
  pai-exporter
```

### Cron Job Setup

```bash
#!/bin/bash
# Daily export cron job script

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/export_$(date +%Y%m%d).log"
EXPORT_DIR="$SCRIPT_DIR/daily_exports/$(date +%Y-%m-%d)"

# Create export directory
mkdir -p "$EXPORT_DIR"

# Run export
cd "$SCRIPT_DIR"
python -c "
import asyncio
from pai_note_exporter import PlaudClient, Exporter
import os

async def main():
    client = PlaudClient(
        email=os.getenv('PLAUD_EMAIL'),
        password=os.getenv('PLAUD_PASSWORD')
    )
    try:
        await client.login()
        exporter = Exporter(client, output_dir='$EXPORT_DIR')
        result = await exporter.export_all()
        print(f'Success: {result.successful}/{result.total} recordings exported')
    except Exception as e:
        print(f'Error: {e}')
        raise
    finally:
        await client.close()

asyncio.run(main())
" >> \"$LOG_FILE\" 2>&1

# Check if export was successful
if [ $? -eq 0 ]; then
    echo \"✅ Daily export completed successfully\" >> \"$LOG_FILE\"
else
    echo \"❌ Daily export failed\" >> \"$LOG_FILE\"
    # Send notification (requires mailutils)
    # echo \"Pai Note Exporter daily export failed\" | mail -s \"Export Failed\" admin@example.com
fi
```

```bash
# Install cron job (run daily at 2 AM)
(crontab -l ; echo "0 2 * * * $SCRIPT_DIR/daily_export.sh") | crontab -
```

## Integration Examples

### Nextcloud Integration

```python
#!/usr/bin/env python3
"""
Export recordings and upload to Nextcloud
"""
import asyncio
from pathlib import Path
from pai_note_exporter import PlaudClient, Exporter
import nextcloud_client  # pip install nextcloud-api

async def export_to_nextcloud():
    """Export recordings and upload to Nextcloud"""
    client = PlaudClient("email", "password")
    exporter = Exporter(client)

    # Nextcloud configuration
    nc = nextcloud_client.Client("https://your-nextcloud.com")
    nc.login("username", "password")

    try:
        await client.login()
        recordings = await client.get_recordings()

        for recording in recordings[:5]:  # First 5 for demo
            # Export locally
            success = await exporter.export_recording(recording)
            if not success:
                continue

            # Get file paths
            txt_path = Path(exporter.get_export_path(recording, "txt"))

            # Upload to Nextcloud
            remote_dir = f"/Recordings/{recording.created_at.strftime('%Y-%m-%d')}"

            # Create remote directory
            nc.create_folder(remote_dir)

            # Upload transcription
            with open(txt_path, 'rb') as f:
                nc.put_file(
                    f"{remote_dir}/{recording.name}.txt",
                    f.read()
                )

            print(f"✅ Uploaded to Nextcloud: {recording.name}")

    finally:
        await client.close()
        nc.logout()

if __name__ == "__main__":
    asyncio.run(export_to_nextcloud())
```

### Telegram Bot Integration

```python
#!/usr/bin/env python3
"""
Telegram bot for recording exports
"""
import asyncio
import os
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from pai_note_exporter import PlaudClient, Exporter

class TelegramExporterBot:
    """Telegram bot for Pai Note Exporter"""

    def __init__(self, token: str):
        self.token = token
        self.client = None
        self.exporter = None

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        await update.message.reply_text(
            "🎵 Pai Note Exporter Bot\n\n"
            "Commands:\n"
            "/login - Authenticate with Plaud.ai\n"
            "/status - Check login status\n"
            "/export - Export recordings\n"
            "/count - Show recording count\n"
            "/help - Show this help"
        )

    async def login(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /login command"""
        await update.message.reply_text("🔐 Logging in...")

        try:
            self.client = PlaudClient(
                email=os.getenv('PLAUD_EMAIL'),
                password=os.getenv('PLAUD_PASSWORD')
            )
            await self.client.login()
            self.exporter = Exporter(self.client)

            await update.message.reply_text("✅ Login successful!")

        except Exception as e:
            await update.message.reply_text(f"❌ Login failed: {e}")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if self.client is None:
            await update.message.reply_text("❌ Not logged in. Use /login first.")
            return

        await update.message.reply_text("✅ Logged in and ready to export")

    async def count(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /count command"""
        if self.client is None:
            await update.message.reply_text("❌ Not logged in. Use /login first.")
            return

        try:
            recordings = await self.client.get_recordings()
            total_duration = sum(r.duration for r in recordings)

            await update.message.reply_text(
                f"📊 Found {len(recordings)} recordings\n"
                f"⏱️  Total duration: {total_duration // 3600}h {(total_duration % 3600) // 60}m"
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def export(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /export command"""
        if self.client is None:
            await update.message.reply_text("❌ Not logged in. Use /login first.")
            return

        await update.message.reply_text("📥 Starting export...")

        try:
            result = await self.exporter.export_all()

            await update.message.reply_text(
                f"✅ Export complete!\n"
                f"📊 {result.successful}/{result.total} recordings exported\n"
                f"⏱️  Duration: {result.duration:.1f}s"
            )

        except Exception as e:
            await update.message.reply_text(f"❌ Export failed: {e}")

    def run(self):
        """Run the bot"""
        application = Application.builder().token(self.token).build()

        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("login", self.login))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(CommandHandler("count", self.count))
        application.add_handler(CommandHandler("export", self.export))
        application.add_handler(CommandHandler("help", self.start))

        application.run_polling()

if __name__ == "__main__":
    bot = TelegramExporterBot(os.getenv('TELEGRAM_TOKEN'))
    bot.run()
```

These examples demonstrate various ways to integrate Pai Note Exporter into different workflows and systems. Each example includes error handling and can be adapted for specific use cases.