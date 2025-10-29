"""
Pai Note Exporter - A Python program to log into Plaud.ai and export notes.

This package provides functionality to authenticate with Plaud.ai using Playwright
and export notes from the platform.
"""

__version__ = "0.1.0"
__author__ = "Wicz-Cloud"
__license__ = "MIT"

from pai_note_exporter.login import PlaudAILogin

__all__ = ["PlaudAILogin"]
