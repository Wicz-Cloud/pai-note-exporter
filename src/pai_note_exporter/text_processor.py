"""Text processing utilities for Plaud.ai transcription exports."""

import json
import re
from typing import Any

from pai_note_exporter.logger import setup_logger


class TextProcessor:
    """Process and clean transcription text from Plaud.ai exports.

    This class handles extracting content from JSON responses, cleaning formatting,
    and making transcriptions more readable for users.
    """

    def __init__(self, log_level: str = "INFO", log_file: str = "pai_note_exporter.log") -> None:
        """Initialize the TextProcessor instance.

        Args:
            log_level: Logging level for the processor
            log_file: Path to log file
        """
        self.logger = setup_logger(
            name=__name__,
            log_level=log_level,
            log_file=log_file,
        )

    def process_transcription(self, raw_content: str | dict[str, Any]) -> str:
        """Process raw transcription content into clean, readable text.

        Args:
            raw_content: Raw content from API (JSON string, dict, or plain text)

        Returns:
            Cleaned and formatted transcription text

        Raises:
            ValueError: If content cannot be processed
        """
        try:
            # Handle different input types
            if isinstance(raw_content, dict):
                # Already parsed JSON dict
                transcription_text = self._extract_transcription_text(raw_content)
                if not transcription_text:
                    raise ValueError("No transcription content found in dict")
            elif isinstance(raw_content, str):
                # Could be JSON string or plain text
                try:
                    # Try to parse as JSON first
                    data = json.loads(raw_content)
                    transcription_text = self._extract_transcription_text(data)
                    if not transcription_text:
                        # If JSON parsing succeeds but no content found, treat as plain text
                        transcription_text = raw_content
                except json.JSONDecodeError:
                    # Not JSON, treat as plain text
                    self.logger.debug("Content is not valid JSON, treating as plain text")
                    transcription_text = raw_content
            else:
                raise ValueError(f"Unsupported content type: {type(raw_content)}")

            # Clean and format the text
            cleaned_text = self._clean_text(transcription_text)

            self.logger.debug(f"Processed transcription: {len(cleaned_text)} characters")
            return cleaned_text

        except Exception as e:
            self.logger.error(f"Failed to process transcription: {e}")
            raise ValueError(f"Failed to process transcription: {e}") from e

    def _extract_transcription_text(self, data: dict[str, Any]) -> str | None:
        """Extract transcription text from various API response formats.

        Args:
            data: Parsed JSON response data

        Returns:
            Extracted transcription text, or None if not found
        """
        # Try different possible locations for transcription content
        possible_keys = [
            "ai_content",  # Current format
            "content",     # Alternative format
            "transcription",  # Alternative format
            "text",        # Alternative format
        ]

        for key in possible_keys:
            if key in data and isinstance(data[key], str) and data[key].strip():
                self.logger.debug(f"Found transcription content in '{key}' field")
                return data[key]

        # Check for nested structures
        if "data" in data and isinstance(data["data"], dict):
            return self._extract_transcription_text(data["data"])

        # Check for list of segments (older format)
        if "data" in data and isinstance(data["data"], list):
            segments = data["data"]
            if segments and isinstance(segments[0], dict):
                content_parts = []
                for segment in segments:
                    if "content" in segment and isinstance(segment["content"], str):
                        content_parts.append(segment["content"])
                if content_parts:
                    return " ".join(content_parts)

        self.logger.warning(f"No transcription content found in response structure: {list(data.keys())}")
        return None

    def _clean_text(self, text: str) -> str:
        """Clean and format transcription text for better readability.

        Args:
            text: Raw transcription text

        Returns:
            Cleaned and formatted text
        """
        if not text:
            return ""

        # Decode unicode escape sequences
        text = self._decode_unicode(text)

        # Clean up common formatting issues
        text = self._clean_formatting(text)

        # Ensure proper line endings
        text = self._normalize_line_endings(text)

        return text.strip()

    def _decode_unicode(self, text: str) -> str:
        """Decode unicode escape sequences in text.

        Args:
            text: Text with potential unicode escapes

        Returns:
            Text with unicode characters properly decoded
        """
        try:
            # Handle common unicode escape sequences
            text = text.replace("\\u2019", "'")  # Right single quotation mark
            text = text.replace("\\u201c", '"')  # Left double quotation mark
            text = text.replace("\\u201d", '"')  # Right double quotation mark
            text = text.replace("\\u2013", "–")  # En dash
            text = text.replace("\\u2014", "—")  # Em dash
            text = text.replace("\\u2026", "…")  # Horizontal ellipsis
            text = text.replace("\\u00a0", " ")  # Non-breaking space
            text = text.replace("\\u00ad", "")   # Soft hyphen

            # Handle any remaining \uXXXX sequences
            text = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), text)

            return text
        except Exception as e:
            self.logger.warning(f"Failed to decode unicode in text: {e}")
            return text

    def _clean_formatting(self, text: str) -> str:
        """Clean up common formatting issues in transcription text.

        Args:
            text: Text to clean

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple blank lines
        text = re.sub(r' +', ' ', text)  # Multiple spaces

        # Fix common markdown issues
        text = re.sub(r'\n- ', '\n\n- ', text)  # Ensure list items have proper spacing
        text = re.sub(r'\n\d+\. ', '\n\n1. ', text)  # Fix numbered lists

        # Clean up header formatting
        text = re.sub(r'#{1,6}\s*', lambda m: m.group(0).strip() + ' ', text)

        return text

    def _normalize_line_endings(self, text: str) -> str:
        """Normalize line endings to Unix style.

        Args:
            text: Text with potentially mixed line endings

        Returns:
            Text with normalized line endings
        """
        # Convert Windows (\r\n) and Mac (\r) line endings to Unix (\n)
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        return text
