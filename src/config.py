"""
Configuration module for the PDF to Markdown converter using Docling.

This module contains simplified configuration settings for the docling-based converter.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    """Configuration settings for the PDF to Markdown converter."""

    # Directory paths
    IMPORTS_DIR: Path = Path("imports")
    EXPORTS_DIR: Path = Path("exports")

    # Output settings
    OUTPUT_FILENAME: str = "combined_documents.md"
    SECTION_SEPARATOR: str = "___"

    # Processing settings
    VERBOSE: bool = True
    ENABLE_OCR: bool = True
    SKIP_ALREADY_CONVERTED: bool = True

    # Docling pipeline options
    DO_TABLE_STRUCTURE: bool = True
    DO_FIGURE_ENRICHMENT: bool = True

    # Environment variable for artifacts path (for offline usage)
    ARTIFACTS_PATH: Optional[str] = os.getenv("DOCLING_ARTIFACTS_PATH")

    def __post_init__(self):
        """Ensure directories exist after initialization."""
        self.IMPORTS_DIR.mkdir(exist_ok=True)
        self.EXPORTS_DIR.mkdir(exist_ok=True)


# Supported file formats (docling supports many more, but we'll focus on these common ones)
SUPPORTED_FORMATS = {".pdf", ".docx", ".pptx", ".xlsx", ".html", ".md", ".txt"}

# Logging configuration
LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default"],
            "level": "INFO",
            "propagate": False
        }
    }
}

# Error messages
ERROR_MESSAGES = {
    "NO_FILES_FOUND": "No supported files found in the imports directory.",
    "INVALID_FILE_FORMAT": "File format not supported: {}",
    "PROCESSING_ERROR": "Error processing file {}: {}",
    "EXPORT_ERROR": "Failed to export markdown file: {}",
}

# Default configuration instance
config = Config()
