"""File discovery utilities (Data layer).

These functions act as an anti-corruption layer between the low-level IO code
found in ``src.utils`` and the higher-level orchestration logic.  Keeping these
functions in a dedicated *data* module improves the testability of the
Orchestrator while still allowing us to reuse the battle-tested code from the
legacy implementation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from src.utils import discover_processing_folders as _discover_processing_folders

__all__ = ["discover_processing_folders_flat",
           "discover_processing_folders_grouped"]


def discover_processing_folders_grouped(imports_dir: Path) -> Dict[str, List[Path]]:
    """Return a mapping ``{folder_name: [Path, …]}`` for files to process."""
    return _discover_processing_folders(imports_dir)


def discover_processing_folders_flat(imports_dir: Path) -> List[Path]:
    """Flattened list version of :pyfunc:`discover_processing_folders_grouped`."""
    mapping = discover_processing_folders_grouped(imports_dir)
    files: List[Path] = []
    for file_list in mapping.values():
        files.extend(file_list)
    return files
