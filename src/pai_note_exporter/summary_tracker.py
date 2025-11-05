"""Summary tracking system for managing pending audio processing jobs."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from pai_note_exporter.logger import setup_logger


class SummaryTracker:
    """Track pending summary generation jobs for audio recordings.

    This class manages a local tracking file that stores information about
    recordings that have had summary generation triggered but not yet completed.

    Attributes:
        tracking_file: Path to the JSON file storing tracking data
        logger: Logger instance
    """

    def __init__(self, tracking_file: Path = Path("./pending_summaries.json")):
        """Initialize the SummaryTracker.

        Args:
            tracking_file: Path to the tracking file (default: ./pending_summaries.json)
        """
        self.tracking_file = tracking_file
        self.logger = setup_logger(__name__)

        # Ensure the tracking file exists
        if not self.tracking_file.exists():
            self._save_tracking_data({})

    def _load_tracking_data(self) -> dict[str, Any]:
        """Load tracking data from file.

        Returns:
            Dictionary containing tracking data
        """
        try:
            with open(self.tracking_file) as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_tracking_data(self, data: dict[str, Any]) -> None:
        """Save tracking data to file.

        Args:
            data: Tracking data to save
        """
        self.tracking_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tracking_file, "w") as f:
            json.dump(data, f, indent=2, default=str)

    def add_pending_summary(
        self, file_id: str, filename: str, triggered_at: datetime | None = None
    ) -> None:
        """Add a recording to the pending summaries tracking.

        Args:
            file_id: ID of the recording file
            filename: Name of the recording file
            triggered_at: When the summary was triggered (default: now)
        """
        if triggered_at is None:
            triggered_at = datetime.now()

        data = self._load_tracking_data()
        data[file_id] = {
            "filename": filename,
            "triggered_at": triggered_at.isoformat(),
            "status": "pending",
        }
        self._save_tracking_data(data)
        self.logger.info(f"Added pending summary tracking for file {file_id}: {filename}")

    def mark_summary_complete(self, file_id: str) -> None:
        """Mark a summary as completed and remove from tracking.

        Args:
            file_id: ID of the recording file
        """
        data = self._load_tracking_data()
        if file_id in data:
            filename = data[file_id]["filename"]
            del data[file_id]
            self._save_tracking_data(data)
            self.logger.info(
                f"Marked summary complete and removed tracking for file {file_id}: {filename}"
            )

    def get_pending_summaries(self, max_age_hours: int = 24) -> list[dict[str, Any]]:
        """Get list of pending summaries that are not too old.

        Args:
            max_age_hours: Maximum age in hours for pending summaries (default: 24)

        Returns:
            List of pending summary records
        """
        data = self._load_tracking_data()
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        pending = []
        to_remove = []

        for file_id, record in data.items():
            try:
                triggered_at = datetime.fromisoformat(record["triggered_at"])
                if triggered_at > cutoff_time:
                    record_copy = record.copy()
                    record_copy["file_id"] = file_id
                    pending.append(record_copy)
                else:
                    # Too old, remove from tracking
                    to_remove.append(file_id)
            except (ValueError, KeyError):
                # Invalid record, remove it
                to_remove.append(file_id)

        # Clean up old/invalid records
        if to_remove:
            for file_id in to_remove:
                del data[file_id]
            self._save_tracking_data(data)
            self.logger.info(f"Cleaned up {len(to_remove)} old/invalid pending summary records")

        return pending

    def is_pending(self, file_id: str) -> bool:
        """Check if a file ID is in the pending summaries list.

        Args:
            file_id: ID of the recording file

        Returns:
            True if the file is pending summary generation
        """
        data = self._load_tracking_data()
        return file_id in data

    def get_pending_count(self) -> int:
        """Get the count of pending summaries.

        Returns:
            Number of pending summaries
        """
        return len(self.get_pending_summaries())

    def clear_all_pending(self) -> None:
        """Clear all pending summaries (for testing/debugging)."""
        self._save_tracking_data({})
        self.logger.info("Cleared all pending summary tracking")
