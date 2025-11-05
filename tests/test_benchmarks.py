"""Benchmark tests for performance regression testing."""

import pytest

from pai_note_exporter.config import Config
from pai_note_exporter.text_processor import TextProcessor


class TestBenchmarks:
    """Benchmark tests for performance-critical functions."""

    @pytest.fixture
    def sample_transcription_data(self) -> dict:
        """Sample transcription data for benchmarking."""
        return {
            "text": "This is a sample transcription text that contains multiple sentences. "
            "It has various punctuation marks and formatting that needs to be processed. "
            "The text processor should handle this efficiently and quickly. "
            "Performance is important for large transcription files."
        }

    @pytest.fixture
    def text_processor(self) -> TextProcessor:
        """Text processor instance for benchmarking."""
        return TextProcessor(log_level="ERROR")  # Minimize logging overhead

    def test_text_processing_performance(
        self, benchmark, text_processor, sample_transcription_data
    ):
        """Benchmark text processing performance."""
        benchmark(text_processor.process_transcription, sample_transcription_data)

    def test_config_validation_performance(self, benchmark):
        """Benchmark configuration validation performance."""
        config = Config(
            plaud_email="test@example.com",
            plaud_password="test_password",  # pragma: allowlist secret - test data only
            log_level="INFO",
            browser_timeout=30,
            headless=True,
        )

        benchmark(config.validate)
