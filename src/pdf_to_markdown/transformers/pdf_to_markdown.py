"""Transformer layer – converts a single document to markdown using Docling.

The transformer **does not** perform any IO other than reading the input file
and returns pure textual output so that it remains as side-effect-free as
possible given the external Docling dependency.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from docling.datamodel.base_models import ConversionStatus, InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from src.config import config as default_config
from src.utils import format_section_header, clean_text

__all__ = ["PDFToMarkdownTransformer"]

logger = logging.getLogger(__name__)


class PDFToMarkdownTransformer:
    """Stateless transformer that converts *one* document to markdown text."""

    def __init__(self, *, enable_ocr: bool | None = None, cfg=default_config) -> None:
        self.cfg = cfg
        # Allow caller to toggle OCR at runtime (e.g. CLI flag).
        self.enable_ocr: bool = enable_ocr if enable_ocr is not None else cfg.ENABLE_OCR

        # Lazily initialised Docling converter – heavy object, instantiate once.
        self._doc_converter: Optional[DocumentConverter] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def transform(self, doc_file: Path) -> str:
        """Convert *doc_file* into cleaned markdown string.

        Raises:
            RuntimeError: If Docling reports a conversion failure.
        """
        converter = self._get_or_create_converter()
        logger.debug("Converting %s to markdown …", doc_file)

        conversion_result = converter.convert(str(doc_file))
        if conversion_result.status != ConversionStatus.SUCCESS:
            raise RuntimeError(
                f"Docling failed for {doc_file.name} with status {conversion_result.status}"
            )

        markdown_body: str = conversion_result.document.export_to_markdown()
        markdown_body = clean_text(markdown_body)
        header = format_section_header(doc_file.name)
        return header + markdown_body

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_or_create_converter(self) -> DocumentConverter:
        if self._doc_converter is None:
            pdf_options = PdfPipelineOptions(
                do_ocr=self.enable_ocr,
                do_table_structure=self.cfg.DO_TABLE_STRUCTURE,
                artifacts_path=self.cfg.ARTIFACTS_PATH,
            )
            format_options = {InputFormat.PDF: PdfFormatOption(
                pipeline_options=pdf_options)}
            self._doc_converter = DocumentConverter(
                format_options=format_options)
        return self._doc_converter
