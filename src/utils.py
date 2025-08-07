"""
Utility functions for the PDF to Markdown converter.

This module contains helper functions used across the application.
"""

import logging
import re
from pathlib import Path
from typing import List, Dict
import hashlib
from datetime import datetime

logger = logging.getLogger(__name__)


def setup_logging(logging_config: dict) -> None:
    """
    Set up logging configuration.

    Args:
        logging_config: Logging configuration dictionary
    """
    import logging.config as log_config
    log_config.dictConfig(logging_config)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing or replacing invalid characters.

    Args:
        filename: Original filename to sanitize

    Returns:
        Sanitized filename safe for use in markdown headers
    """
    # Remove file extension
    name = Path(filename).stem

    # Replace problematic characters with underscores
    sanitized = re.sub(r'[^\w\s-]', '_', name)

    # Replace multiple whitespace/underscores with single underscore
    sanitized = re.sub(r'[\s_]+', '_', sanitized)

    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')

    return sanitized if sanitized else "untitled"


def get_file_hash(file_path: Path) -> str:
    """
    Calculate MD5 hash of a file for caching purposes.

    Args:
        file_path: Path to the file

    Returns:
        MD5 hash string
    """
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        logger.warning("Could not calculate hash for %s: %s", file_path, e)
        return ""


def format_section_header(filename: str) -> str:
    """
    Format a section header for the markdown output.

    Args:
        filename: Original filename

    Returns:
        Formatted markdown header
    """
    sanitized_name = sanitize_filename(filename)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return f"# {sanitized_name}\n\n*Source: {filename}*  \n*Processed: {timestamp}*\n\n"


def generate_timestamp_filename(base_name: str, extension: str = ".md") -> str:
    """
    Generate a filename with timestamp.

    Args:
        base_name: Base name for the file
        extension: File extension (default: .md)

    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    sanitized_base = sanitize_filename(base_name)
    return f"{sanitized_base}_{timestamp}{extension}"


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing excessive whitespace and fixing common issues.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Replace multiple newlines with double newlines (paragraph breaks)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Fix hyphenated words at line breaks
    text = text.replace('-\n', '')

    # Remove excessive spaces
    text = re.sub(r' +', ' ', text)

    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]

    # Remove empty lines at the beginning and end
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    return '\n'.join(lines)


def discover_processing_folders(imports_dir: Path) -> Dict[str, List[Path]]:
    """
    Discover folders and supported document files to process in the imports directory.

    Args:
        imports_dir: Path to imports directory

    Returns:
        Dictionary mapping folder names to lists of supported document files

    Raises:
        FileNotFoundError: If imports directory doesn't exist
        ValueError: If no supported files found
    """
    if not imports_dir.exists():
        raise FileNotFoundError(f"Imports directory not found: {imports_dir}")

    # Import supported formats from config
    from .config import SUPPORTED_FORMATS

    processing_map = {}

    # Check for supported files directly in imports directory
    direct_files = []
    for format_ext in SUPPORTED_FORMATS:
        direct_files.extend(imports_dir.glob(f"*{format_ext}"))

    if direct_files:
        processing_map["_root"] = sorted(direct_files)
        logger.info("Found %d supported files in root imports directory",
                    len(direct_files))

    # Check for subdirectories containing supported files
    for item in imports_dir.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            supported_files = []
            for format_ext in SUPPORTED_FORMATS:
                supported_files.extend(item.glob(f"*{format_ext}"))

            if supported_files:
                processing_map[item.name] = sorted(supported_files)
                logger.info("Found %d supported files in folder '%s'",
                            len(supported_files), item.name)

    if not processing_map:
        supported_exts = ", ".join(sorted(SUPPORTED_FORMATS))
        raise ValueError(
            f"No supported files found in imports directory or its subdirectories. "
            f"Supported formats: {supported_exts}")

    total_files = sum(len(files) for files in processing_map.values())
    logger.info("Discovered %d folders with %d total supported files",
                len(processing_map), total_files)

    return processing_map


def validate_imports_directory(imports_dir: Path) -> List[Path]:
    """
    Validate imports directory and return list of supported files.

    Args:
        imports_dir: Path to imports directory

    Returns:
        List of valid document files

    Raises:
        FileNotFoundError: If imports directory doesn't exist
        ValueError: If no supported files found
    """
    processing_map = discover_processing_folders(imports_dir)

    # Return flattened list for backwards compatibility
    all_files = []
    for files in processing_map.values():
        all_files.extend(files)

    return all_files


def check_folder_already_converted(folder_name: str, exports_dir: Path) -> bool:
    """
    Check if a folder has already been converted by looking for existing markdown files.

    Args:
        folder_name: Name of the folder to check
        exports_dir: Path to exports directory

    Returns:
        True if folder has already been converted, False otherwise
    """
    if not exports_dir.exists():
        return False

    # Sanitize folder name to match the naming convention
    sanitized_folder_name = sanitize_filename(folder_name)

    # Look for existing markdown files that start with the folder name
    pattern = f"{sanitized_folder_name}_*.md"
    existing_files = list(exports_dir.glob(pattern))

    if existing_files:
        logger.info("Found %d existing export file(s) for folder '%s': %s",
                    len(existing_files), folder_name, [f.name for f in existing_files])
        return True

    return False


def get_existing_converted_files(folder_name: str, exports_dir: Path) -> List[Path]:
    """
    Get list of existing converted files for a specific folder.

    Args:
        folder_name: Name of the folder to check
        exports_dir: Path to exports directory

    Returns:
        List of existing converted markdown files for the folder
    """
    if not exports_dir.exists():
        return []

    # Sanitize folder name to match the naming convention
    sanitized_folder_name = sanitize_filename(folder_name)

    # Look for existing markdown files that start with the folder name
    pattern = f"{sanitized_folder_name}_*.md"
    existing_files = list(exports_dir.glob(pattern))

    # Sort by modification time (newest first)
    existing_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    return existing_files


def safe_create_directory(directory: Path) -> None:
    """
    Safely create a directory if it doesn't exist.

    Args:
        directory: Path to create
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        logger.debug("Ensured directory exists: %s", directory)
    except OSError as e:
        logger.error("Failed to create directory %s: %s", directory, e)
        raise
