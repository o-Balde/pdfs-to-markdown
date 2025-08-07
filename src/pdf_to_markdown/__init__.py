# pdf_to_markdown package adhering to DMOT architecture

"""High-level package that exposes the public API for the pdf-to-markdown
project after the refactor to DMOT (Data / Model / Orchestrator / Transformer)
architecture.

Modules:
    data:    Data–layer utilities for file I/O and discovery.
    model:   Domain models and dataclasses.
    transformers:   Stateless transformation logic.
    orchestrator:   High-level pipeline coordination.

End-users are expected to interact with the `Orchestrator` class, which offers
an easy imperative interface as well as a `run_cli()` helper used by `main.py`.

At runtime we lazily import the orchestrator to avoid circular imports during
the initial bootstrapping phase.
"""

# PEP-563 – postponed evaluation of annotations
from __future__ import annotations

__all__ = [
    "Orchestrator",
]


# Lazily import to prevent issues while the package is being gradually filled
# out during the refactor.
try:
    from .orchestrator import Orchestrator  # noqa: E402
except (ModuleNotFoundError, ImportError):
    # Allow partial builds during the incremental refactor.
    Orchestrator = None  # type: ignore
