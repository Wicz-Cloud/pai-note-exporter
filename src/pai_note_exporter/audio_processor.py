"""Audio processing module for generating summaries/transcriptions for audio-only recordings in Plaud.ai."""

from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx

from pai_note_exporter.config import Config
from pai_note_exporter.exceptions import APIError
from pai_note_exporter.logger import setup_logger


class PlaudAudioProcessor:
    """Handle audio file processing for recordings already in Plaud.ai account.

    This class provides methods to find audio-only recordings (without transcriptions)
    and generate transcriptions and summaries using Plaud.ai's API.

    Attributes:
        config: Configuration object with credentials and settings
        logger: Logger instance for this class
        client: HTTP client for API calls
        token: Authentication token for API requests
        base_url: Base URL for Plaud.ai API
    """

    BASE_URL = "https://api.plaud.ai"

    def __init__(self, config: Config, token: str) -> None:
        """Initialize the PlaudAudioProcessor instance.

        Args:
            config: Configuration object with credentials and settings
            token: Authentication token from login
        """
        self.config = config
        self.token = token
        self.logger = setup_logger(
            name=__name__,
            log_level=config.log_level,
            log_file=config.log_file,
        )
        self.client = httpx.AsyncClient(
            timeout=300.0,  # Longer timeout for processing
            headers={
                "Authorization": f"Bearer {token}",
                "edit-from": "web",
                "app-platform": "web",
            },
        )

    async def __aenter__(self) -> "PlaudAudioProcessor":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Async context manager exit."""
        await self.client.aclose()

    async def get_recordings(self, limit: int = 50) -> list[dict[str, Any]]:
        """Get list of recordings from Plaud.ai account.

        Args:
            limit: Maximum number of recordings to retrieve

        Returns:
            List of recording dictionaries

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/file/list"

        try:
            self.logger.debug(f"Fetching recordings (limit: {limit})")
            response = await self.client.post(
                url, json={"page": 1, "page_size": limit, "sort": "create_time", "order": "desc"}
            )
            response.raise_for_status()

            data = response.json()
            if data.get("status") == 0 and "data" in data:
                recordings = data["data"].get("list", [])

                # Filter out files in trash as additional safety measure
                recordings = [r for r in recordings if not r.get("is_trash", False)]

                self.logger.info(f"Retrieved {len(recordings)} recordings (filtered out trash)")
                return recordings
            else:
                raise APIError(f"Failed to get recordings: {data.get('msg', 'Unknown error')}")

        except httpx.HTTPStatusError as e:
            self.logger.error(
                f"API error getting recordings: {e.response.status_code} - {e.response.text}"
            )
            raise APIError(f"Failed to get recordings: {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error getting recordings: {e}")
            raise APIError(f"Unexpected error getting recordings: {e}") from e

    def filter_audio_only_recordings(
        self, recordings: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Filter recordings to find audio-only ones (without transcriptions).

        Args:
            recordings: List of all recordings

        Returns:
            List of audio-only recordings
        """
        audio_only = []
        for recording in recordings:
            # Check if it's an audio file and doesn't have transcription
            file_type = recording.get("file_type", "").lower()
            has_transcription = recording.get("is_trans", False)

            if file_type in ["mp3", "wav", "m4a", "aac", "ogg"] and not has_transcription:
                audio_only.append(recording)

        self.logger.info(f"Found {len(audio_only)} audio-only recordings")
        return audio_only

    async def generate_transcription(self, file_id: str, to_format: str = "TXT") -> bytes:
        """Generate transcription for a recording.

        Args:
            file_id: ID of the recording file
            to_format: Export format ("TXT", "DOCX", "PDF", "SRT")

        Returns:
            Transcription content as bytes

        Raises:
            APIError: If the API request fails
        """
        return await self._export_content(file_id, "trans", to_format)

    async def generate_summary(self, file_id: str, to_format: str = "TXT") -> bytes:
        """Generate summary for a recording.

        Args:
            file_id: ID of the recording file
            to_format: Export format ("TXT", "DOCX", "PDF", "SRT")

        Returns:
            Summary content as bytes

        Raises:
            APIError: If the API request fails
        """
        return await self._export_content(file_id, "summary", to_format)

    async def trigger_transcription_and_summary(self, file_id: str) -> bool:
        """Trigger transcription and summary generation for a recording.

        Args:
            file_id: ID of the recording file

        Returns:
            True if the request was successful

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/ai/transsumm/{file_id}"

        payload = {
            "is_reload": 0,
            "summ_type": "AUTO-SELECT",
            "summ_type_type": "system",
            "info": '{"language":"auto","diarization":1,"llm":"auto"}',
            "support_mul_summ": True,
        }

        try:
            self.logger.debug(f"Triggering transcription and summary for file: {file_id}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == 0:
                self.logger.info(
                    f"Successfully triggered transcription and summary for file {file_id}"
                )
                return True
            else:
                raise APIError(
                    f"Failed to trigger transcription: {data.get('msg', 'Unknown error')}"
                )

        except httpx.HTTPStatusError as e:
            self.logger.error(
                f"API error triggering transcription: {e.response.status_code} - {e.response.text}"
            )
            raise APIError(f"Failed to trigger transcription: {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error triggering transcription: {e}")
            raise APIError(f"Unexpected error triggering transcription: {e}") from e

    async def _export_content(
        self,
        file_id: str,
        prompt_type: str,
        to_format: str = "TXT",
        title: str | None = None,
        create_time: str | None = None,
        with_speaker: int = 0,
        with_timestamp: int = 0,
        content: str | list[str] | None = None,
    ) -> bytes:
        """Export transcription/summary content for a file.

        Args:
            file_id: ID of the file
            prompt_type: Type of content ("trans" for transcription, "summary" for summary)
            to_format: Export format ("TXT", "DOCX", "PDF", "SRT")
            title: Title for the export
            create_time: Creation time string
            with_speaker: Include speaker labels (0 or 1)
            with_timestamp: Include timestamps (0 or 1)
            content: Content to export

        Returns:
            Exported file content as bytes

        Raises:
            APIError: If the API request fails
        """
        url = f"{self.BASE_URL}/file/document/export"

        payload: dict[str, Any] = {
            "file_id": file_id,
            "prompt_type": prompt_type,
            "to_format": to_format.upper(),
            "title": title,
            "create_time": create_time or "",
            "with_speaker": with_speaker,
            "with_timestamp": with_timestamp,
        }

        if prompt_type == "trans" and content:
            payload["trans_content"] = content if isinstance(content, list) else [content]
        elif prompt_type == "summary" and content:
            payload["summary_content"] = content

        try:
            self.logger.debug(f"Exporting {prompt_type} for file {file_id} as {to_format}")
            response = await self.client.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            if data.get("status") == 0 and "data" in data:
                content = data["data"]
                if isinstance(content, str):
                    return content.encode("utf-8")
                elif isinstance(content, bytes):
                    return content
                else:
                    return str(content).encode("utf-8")
            elif data.get("status") == -1:
                raise APIError(f"Export failed: {data.get('msg', 'Unknown error')}")
            else:
                self.logger.debug(f"Response content type: {response.headers.get('content-type')}")
                self.logger.debug(f"Response headers: {dict(response.headers)}")
                if hasattr(response, "content") and response.content:
                    return response.content
                else:
                    raise APIError(f"Unexpected response format: {data}")

        except httpx.HTTPStatusError as e:
            self.logger.error(
                f"API error exporting {prompt_type}: {e.response.status_code} - {e.response.text}"
            )
            raise APIError(f"Failed to export {prompt_type}: {e.response.status_code}") from e
        except Exception as e:
            self.logger.error(f"Unexpected error exporting {prompt_type}: {e}")
            raise APIError(f"Unexpected error exporting {prompt_type}: {e}") from e

    async def process_audio_recordings(
        self,
        limit: int = 50,
        generate_transcription: bool = True,
        generate_summary: bool = True,
        output_dir: Path | None = None,
        progress_callback: Callable | None = None,
    ) -> list[dict[str, Any]]:
        """Process audio-only recordings: find them and generate transcription/summary.

        Args:
            limit: Maximum number of recordings to check
            generate_transcription: Whether to generate transcription
            generate_summary: Whether to generate summary
            output_dir: Directory to save outputs (optional)
            progress_callback: Optional callback for progress

        Returns:
            List of processing results for each recording
        """
        self.logger.info("Starting audio recording processing...")

        # Get all recordings
        recordings = await self.get_recordings(limit)

        # Filter for audio-only recordings
        audio_recordings = self.filter_audio_only_recordings(recordings)

        if not audio_recordings:
            self.logger.info("No audio-only recordings found")
            return []

        results = []

        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)

        # Process each audio recording
        for i, recording in enumerate(audio_recordings, 1):
            file_id = recording["id"]
            filename = recording.get("filename", f"recording_{file_id}")

            self.logger.info(f"Processing recording {i}/{len(audio_recordings)}: {filename}")

            if progress_callback:
                progress_callback(i, len(audio_recordings), filename)

            result = {
                "file_id": file_id,
                "filename": filename,
                "processed": False,
                "transcription_path": None,
                "summary_path": None,
                "error": None,
            }

            try:
                # Generate transcription if requested
                if generate_transcription:
                    self.logger.info(f"Generating transcription for {filename}...")
                    trans_content = await self.generate_transcription(file_id)
                    result["transcription"] = trans_content

                    if output_dir:
                        trans_path = output_dir / f"{Path(filename).stem}_transcription.txt"
                        with open(trans_path, "wb") as f:
                            f.write(trans_content)
                        result["transcription_path"] = str(trans_path)
                        self.logger.info(f"Transcription saved: {trans_path}")

                # Generate summary if requested
                if generate_summary:
                    self.logger.info(f"Generating summary for {filename}...")
                    summary_content = await self.generate_summary(file_id)
                    result["summary"] = summary_content

                    if output_dir:
                        summary_path = output_dir / f"{Path(filename).stem}_summary.txt"
                        with open(summary_path, "wb") as f:
                            f.write(summary_content)
                        result["summary_path"] = str(summary_path)
                        self.logger.info(f"Summary saved: {summary_path}")

                result["processed"] = True
                self.logger.info(f"Successfully processed {filename}")

            except Exception as e:
                result["error"] = str(e)
                self.logger.error(f"Failed to process {filename}: {e}")

            results.append(result)

        self.logger.info(
            f"Audio processing completed. Processed {len([r for r in results if r['processed']])}/{len(audio_recordings)} recordings"
        )
        return results
