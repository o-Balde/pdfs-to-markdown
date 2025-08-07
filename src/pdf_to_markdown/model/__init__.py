# Domain models for pdf_to_markdown project
from __future__ import annotations

__all__ = [
    "ConversionResult",
]

# Re-export for convenience once implemented
try:
    from .result import ConversionResult  # noqa: E402
except (ModuleNotFoundError, ImportError):
    ConversionResult = None  # type: ignore
