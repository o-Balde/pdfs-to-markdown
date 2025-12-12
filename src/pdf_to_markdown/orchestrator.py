"""Pipeline Orchestrator – the *O* in DMOT.

Responsible for coordinating the end-to-end flow:

1. Discover input files (Data layer)
2. Delegate per-file transformations to the Transformer layer
3. Persist artefacts and generate summary reports (still considered IO / Data)
4. Return a rich :class:`pdf_to_markdown.model.ConversionResult` object.

This class MUST remain thin and declarative – avoid business logic here unless
it is workflow-oriented.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Optional

from src.utils import (
    generate_timestamp_filename,
    check_folder_already_converted,
    get_existing_converted_files,
)
from src.utils import setup_logging  # re-export for CLI convenience
from src.config import config as default_config, LOGGING_CONFIG

from .data.file_discovery import discover_processing_folders_grouped
from .model import ConversionResult
from .transformers.pdf_to_markdown import PDFToMarkdownTransformer

__all__ = ["Orchestrator"]

logger = logging.getLogger(__name__)


class Orchestrator:
    """Coordinates the conversion pipeline following SOLID principles."""

    def __init__(self, *, cfg=default_config, verbose: bool | None = None):
        # ------------------------------------------------------------------
        # Configuration & logging
        # ------------------------------------------------------------------
        self.cfg = cfg
        log_cfg = LOGGING_CONFIG.copy()
        if verbose or (verbose is None and cfg.VERBOSE):
            log_cfg["handlers"]["default"]["level"] = "DEBUG"
            log_cfg["loggers"][""]["level"] = "DEBUG"
        setup_logging(log_cfg)

        # ------------------------------------------------------------------
        # Collaborators
        # ------------------------------------------------------------------
        self.transformer = PDFToMarkdownTransformer(
            enable_ocr=self.cfg.ENABLE_OCR, cfg=cfg)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    # Legacy alias for backwards compatibility with old CLI
    def convert(self, *args, **kwargs):  # noqa: D401, E501 – keep simple
        """Alias to :pyfunc:`run` maintained to avoid breaking existing code."""
        return self.run(*args, **kwargs)

    def run(
        self,
        *,
        imports_dir: Optional[Path] = None,
        exports_dir: Optional[Path] = None,
        output_filename: Optional[str] = None,
    ) -> ConversionResult:
        start_time = time.time()
        result = ConversionResult()

        imports_path = imports_dir or self.cfg.IMPORTS_DIR
        exports_path = exports_dir or self.cfg.EXPORTS_DIR
        exports_path.mkdir(parents=True, exist_ok=True)

        logger.info("📂 Scanning imports directory: %s", imports_path)
        processing_map = discover_processing_folders_grouped(imports_path)

        for folder_name, files in processing_map.items():
            if self.cfg.SKIP_ALREADY_CONVERTED and check_folder_already_converted(folder_name, exports_path):
                existing = get_existing_converted_files(
                    folder_name, exports_path)
                result.skipped_folders[folder_name] = [f.name for f in files]
                result.output_files.extend(existing)
                logger.info(
                    "⏭️  Skipped '%s' – already converted", folder_name)
                continue

            logger.info("🔄 Processing folder '%s' (%d files)",
                        folder_name, len(files))
            # Determine output file name
            out_name = (
                output_filename if folder_name == "_root" else f"{folder_name}.md"
            )
            out_path = exports_path / out_name
            
            logger.info("🔄 Processing folder '%s' (%d files) -> %s",
                        folder_name, len(files), out_name)

            # Open file for writing - wipes existing content
            try:
                with open(out_path, "w", encoding="utf-8") as out_f:
                    # Write Header
                    display_name = "Root Directory" if folder_name == "_root" else folder_name
                    header = f"# Combined Documents – {display_name}\n\n" f"*Generated from {len(files)} document(s)*\n\n"
                    out_f.write(header)

                    for file_path in files:
                        try:
                            # Force garbage collection if needed, but scope cleanup should handle most
                            blob = self.transformer.transform(file_path)
                            
                            # Write immediately
                            out_f.write(blob)
                            
                            # Add separator
                            out_f.write("\n\n----------------\n\n")
                            
                            result.processed_folders.setdefault(
                                folder_name, []).append(file_path.name)
                                
                            # Optional: Log progress for large folders
                            logger.debug("   Written %s", file_path.name)
                            
                        except Exception as exc:
                            logger.exception(
                                "Failed converting %s: %s", file_path, exc)
                            result.failed_files.append(file_path.name)

                result.output_files.append(out_path)
            
            except Exception as e:
                logger.error("Failed to write to %s: %s", out_path, e)
                # If we can't write the file, mark whole folder as failed or handle appropriately


        # Finalise result
        result.stop_timer(start_time)
        result.success = bool(result.output_files)
        self._generate_summary_report(result, exports_path)

        return result

    # ------------------------------------------------------------------
    # Ancillary utilities – kept for backwards-compat with legacy CLI
    # ------------------------------------------------------------------
    def validate_configuration(self):
        """Lightweight configuration validation mainly for the CLI entry-point."""
        from src.utils import discover_processing_folders
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {},
        }

        try:
            if not self.cfg.IMPORTS_DIR.exists():
                validation_result["warnings"].append(
                    f"Imports directory does not exist: {self.cfg.IMPORTS_DIR}"
                )

            try:
                processing_map = discover_processing_folders(
                    self.cfg.IMPORTS_DIR)
                total_files = sum(len(f) for f in processing_map.values())
                validation_result["info"]["folders_found"] = len(
                    processing_map)
                validation_result["info"]["supported_files_found"] = total_files
                if total_files == 0:
                    validation_result["warnings"].append(
                        "No supported documents found in imports directory."
                    )
            except ValueError as exc:
                validation_result["warnings"].append(str(exc))

            # Ensure exports dir
            try:
                self.cfg.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
            except Exception as exc:
                validation_result["errors"].append(
                    f"Cannot create exports directory: {exc}"
                )
                validation_result["valid"] = False

        except Exception as exc:
            validation_result["errors"].append(
                f"Unexpected validation error: {exc}")
            validation_result["valid"] = False

        return validation_result

    # ------------------------------------------------------------------
    # Pure helpers (kept **private** inside orchestrator)
    # ------------------------------------------------------------------
    def _save_combined_markdown(self, markdown_sections: List[str], output_path: Path, folder_name: str) -> None:
        display_name = "Root Directory" if folder_name == "_root" else folder_name
        header = f"# Combined Documents – {display_name}\n\n" f"*Generated from {len(markdown_sections)} document(s)*\n\n"
        combined = header + "\n".join(markdown_sections)
        output_path.write_text(combined, encoding="utf-8")
        logger.info("💾 Wrote combined markdown → %s", output_path.name)

    def _generate_summary_report(self, result: ConversionResult, exports_dir: Path) -> None:
        summary_path = exports_dir / \
            f"processing_summary_{int(time.time())}.md"
        lines: List[str] = [
            "# Processing Summary",
            "",
            f"**Runtime:** {result.processing_time:.2f} s",
            f"**Output files:** {len(result.output_files)}",
            f"**Folders processed:** {len(result.processed_folders)}",
            f"**Folders skipped:** {len(result.skipped_folders)}",
            "",
        ]
        if result.failed_files:
            lines.append("## Failed files")
            lines.extend([f"- {fname}" for fname in result.failed_files])
            lines.append("")

        lines.append("## Output files")
        lines.extend([f"- {p.name}" for p in result.output_files])

        summary_path.write_text("\n".join(lines), encoding="utf-8")
        logger.info("📋 Summary report generated: %s", summary_path.name)
