"""Domain model representing a single run of the conversion pipeline.

The class is intentionally *data-only* (no behaviour other than convenience
helpers) so that the rest of the application can treat it as an immutable value
object.  This aligns with the "Model" slice of the DMOT architecture.  Any
business logic that produces or mutates these models belongs either to the
Transformer layer (pure functions) or the Orchestrator layer (imperative glue
code).
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

__all__ = ["ConversionResult"]


@dataclass
class ConversionResult:
    """Container for conversion results and basic statistics.

    This is largely a 1-to-1 port of the previous implementation found in
    ``src.converter`` but stripped of any logging or side-effects.  Those
    responsibilities now live in the Orchestrator or higher layers.
    """

    # Success flag
    success: bool = False

    # IO artefacts
    output_files: List[Path] = field(default_factory=list)
    processed_folders: Dict[str, List[str]] = field(default_factory=dict)
    skipped_folders: Dict[str, List[str]] = field(default_factory=dict)
    failed_files: List[str] = field(default_factory=list)

    # Stats – note that docling does not expose these yet but we keep them for
    # future extensibility.
    total_pages: int = 0
    total_images: int = 0

    # Time taken in seconds
    processing_time: float = 0.0

    # Error state
    error_message: Optional[str] = None

    # ---------------------------------------------------------------------
    # Convenience helpers – kept for backwards compatibility with the older
    # codebase.  These do *not* mutate internal state and therefore play well
    # with the dataclass semantics.
    # ---------------------------------------------------------------------
    @property
    def output_file(self) -> Optional[Path]:
        """Return the first (and in most cases only) output file."""
        return self.output_files[0] if self.output_files else None

    @property
    def processed_files(self) -> List[str]:
        """Flatten ``processed_folders`` into a single list of file names."""
        all_files: List[str] = []
        for files in self.processed_folders.values():
            all_files.extend(files)
        return all_files

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------
    @classmethod
    def start_timer(cls) -> float:
        """Utility helper used by Orchestrator to measure execution time."""
        return time.time()

    def stop_timer(self, start_time: float) -> None:
        """Compute total run time using the *monotonic* `time` API."""
        self.processing_time = time.time() - start_time
