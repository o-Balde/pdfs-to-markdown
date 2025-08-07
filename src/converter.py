"""
Main Converter Module using Docling

This module contains the simplified PDFToMarkdownConverter class that uses
docling for document conversion to markdown.
"""

import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
import time

from docling.document_converter import DocumentConverter
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import PdfFormatOption

from .config import config, SUPPORTED_FORMATS, ERROR_MESSAGES
from .utils import (
    validate_imports_directory,
    setup_logging,
    discover_processing_folders,
    generate_timestamp_filename,
    check_folder_already_converted,
    get_existing_converted_files
)

logger = logging.getLogger(__name__)


class ConversionResult:
    """Container for conversion results and statistics."""

    def __init__(self):
        self.success: bool = False
        self.output_files: List[Path] = []
        self.processed_folders: Dict[str, List[str]] = {}
        self.skipped_folders: Dict[str, List[str]] = {}
        self.failed_files: List[str] = []
        self.total_pages: int = 0
        self.total_images: int = 0
        self.processing_time: float = 0.0
        self.error_message: Optional[str] = None

    @property
    def output_file(self) -> Optional[Path]:
        """Backwards compatibility property."""
        return self.output_files[0] if self.output_files else None

    @property
    def processed_files(self) -> List[str]:
        """Backwards compatibility property."""
        all_files = []
        for files in self.processed_folders.values():
            all_files.extend(files)
        return all_files


class PDFToMarkdownConverter:
    """
    Main converter class using Docling for document processing.

    This class provides a simplified interface for converting documents
    to markdown using docling's advanced document understanding capabilities.
    """

    def __init__(self, custom_config: Optional[Any] = None) -> None:
        """
        Initialize the converter with docling.

        Args:
            custom_config: Optional custom configuration object
        """
        self.config = custom_config or config

        # Setup logging
        from .config import LOGGING_CONFIG
        setup_logging(LOGGING_CONFIG)

        # Initialize docling converter
        self._setup_docling_converter()

        logger.info(
            "🚀 Docling-based converter initialized and ready to process your documents!")

    def _setup_docling_converter(self) -> None:
        """Set up the docling document converter with appropriate options."""
        try:
            # Configure PDF pipeline options
            pdf_options = PdfPipelineOptions(
                do_ocr=self.config.ENABLE_OCR,
                do_table_structure=self.config.DO_TABLE_STRUCTURE,
                # artifacts_path can be set for offline usage
                artifacts_path=self.config.ARTIFACTS_PATH
            )

            # Create format options
            format_options = {
                InputFormat.PDF: PdfFormatOption(pipeline_options=pdf_options)
            }

            # Initialize the document converter
            self.doc_converter = DocumentConverter(
                format_options=format_options
            )

            logger.debug(
                "⚙️ Docling converter configured successfully with all your settings!")

        except Exception as e:
            logger.error(
                "⚠️ Oops! Failed to initialize docling converter: %s", e)
            logger.info(
                "🔧 No worries! Falling back to default converter settings...")
            # Fall back to default converter
            self.doc_converter = DocumentConverter()

    def convert(
        self,
        imports_dir: Optional[Path] = None,
        exports_dir: Optional[Path] = None,
        output_filename: Optional[str] = None,
        # enable_image_descriptions: bool = True,  # Keep for compatibility
        verbose: bool = None
    ) -> ConversionResult:
        """
        Convert documents in the imports directory to markdown files.

        Args:
            imports_dir: Directory containing documents (defaults to config)
            exports_dir: Directory to save output (defaults to config)
            output_filename: Name of output file for root files (defaults to config)
            enable_image_descriptions: Kept for compatibility (docling handles this)
            verbose: Whether to enable verbose logging (defaults to config)

        Returns:
            ConversionResult object containing results and statistics
        """
        start_time = time.time()
        result = ConversionResult()

        try:
            # Use provided paths or fall back to config
            imports_path = imports_dir or self.config.IMPORTS_DIR
            exports_path = exports_dir or self.config.EXPORTS_DIR
            output_name = output_filename or self.config.OUTPUT_FILENAME
            verbose_mode = verbose if verbose is not None else self.config.VERBOSE

            if verbose_mode:
                logging.getLogger().setLevel(logging.DEBUG)

            logger.info("✨ Starting your document conversion journey!")
            logger.info("📂 Looking for documents in: %s", imports_path)
            logger.info(
                "💾 Your markdown files will be saved to: %s", exports_path)

            # Discover processing folders
            processing_map = discover_processing_folders(imports_path)
            exports_path.mkdir(parents=True, exist_ok=True)

            # Process each folder separately
            for folder_name, files in processing_map.items():
                logger.info(
                    "📁 Checking folder: '%s' with %d document%s 🎯", folder_name, len(files), 's' if len(files) != 1 else '')

                # Check if folder has already been converted
                if self.config.SKIP_ALREADY_CONVERTED and check_folder_already_converted(folder_name, exports_path):
                    existing_files = get_existing_converted_files(
                        folder_name, exports_path)
                    logger.info(
                        "⏭️  Skipping folder '%s' - already converted! Latest file: %s",
                        folder_name, existing_files[0].name if existing_files else "unknown")

                    # Track skipped folders and add existing files to output
                    file_names = [f.name for f in files]
                    result.skipped_folders[folder_name] = file_names
                    if existing_files:
                        result.output_files.extend(existing_files)
                    continue

                logger.info(
                    "🔄 Processing folder: '%s' with %d document%s", folder_name, len(files), 's' if len(files) != 1 else '')

                # Convert documents for this folder
                folder_result = ConversionResult()
                markdown_contents = self._process_documents(
                    files, folder_result)

                if not markdown_contents:
                    logger.warning(
                        "🤔 Hmm, no valid documents found in folder: '%s'. Let's check the next one...", folder_name)
                    continue

                # Generate output filename
                if folder_name == "_root":
                    output_filename = output_name
                else:
                    output_filename = generate_timestamp_filename(folder_name)

                output_path = exports_path / output_filename

                # Combine and save markdown
                self._save_combined_markdown(
                    markdown_contents, output_path, folder_name)

                # Update overall result
                result.output_files.append(output_path)
                result.processed_folders[folder_name] = folder_result.processed_files
                result.failed_files.extend(folder_result.failed_files)
                # Note: docling doesn't expose page/image counts directly, but provides rich content

                logger.info(
                    "✅ Successfully completed folder '%s'! 📄 → %s", folder_name, output_path)

            # Generate overall summary report
            summary_path = exports_path / \
                f"processing_summary_{int(start_time)}.md"
            self._generate_summary_report(result, summary_path, start_time)

            # Update final result
            result.success = len(result.output_files) > 0
            result.processing_time = time.time() - start_time

            if result.success:
                logger.info(
                    "🎉 Conversion completed successfully in %.2f seconds! ⚡", result.processing_time)
                logger.info(
                    "📚 Generated %d markdown file%s!", len(result.output_files), 's' if len(result.output_files) != 1 else '')
                logger.info("📋 Summary report saved to: %s", summary_path)
            else:
                result.error_message = "😕 No valid folders or files were processed. Please check your imports directory!"

        except Exception as e:
            logger.error(
                "💥 Oops! Something went wrong during conversion: %s", e)
            result.error_message = str(e)
            result.processing_time = time.time() - start_time

        return result

    def _process_documents(
        self,
        document_files: List[Path],
        result: ConversionResult
    ) -> List[str]:
        """
        Process all documents using docling and extract markdown content.

        Args:
            document_files: List of document file paths
            result: ConversionResult to update

        Returns:
            List of markdown content strings
        """
        logger.info(
            "📄 Getting ready to process %d document%s with the power of docling! 🔮", len(document_files), 's' if len(document_files) != 1 else '')

        markdown_contents = []

        for doc_file in document_files:
            try:
                logger.info("🔄 Now working on: %s ...", doc_file.name)

                # Convert document using docling
                conversion_result = self.doc_converter.convert(str(doc_file))

                # Check if conversion was successful
                from docling.datamodel.base_models import ConversionStatus
                if conversion_result.status == ConversionStatus.SUCCESS:
                    # Extract markdown content
                    markdown_content = conversion_result.document.export_to_markdown()

                    # Add document header
                    doc_header = f"\n\n{self.config.SECTION_SEPARATOR}\n\n# {doc_file.stem}\n\n"
                    full_content = doc_header + markdown_content

                    markdown_contents.append(full_content)
                    result.processed_files.append(doc_file.name)

                    logger.debug(
                        "✅ Successfully converted '%s' (%s characters) 🎯", doc_file.name, f"{len(markdown_content):,}")
                else:
                    logger.error(
                        "❌ Oops! Conversion failed for '%s'. Status: %s 😞", doc_file.name, conversion_result.status)
                    result.failed_files.append(doc_file.name)

            except Exception as e:
                logger.error(
                    "💥 Unexpected error processing '%s': %s", doc_file.name, e)
                result.failed_files.append(doc_file.name)
                continue

        if len(result.failed_files) == 0:
            logger.info(
                "🎉 All done! Successfully processed all %d document%s! 🏆", len(markdown_contents), 's' if len(markdown_contents) != 1 else '')
        else:
            logger.info(
                "📊 Processing complete! ✅ %d successful, ❌ %d failed", len(markdown_contents), len(result.failed_files))

        return markdown_contents

    def _save_combined_markdown(
        self,
        markdown_contents: List[str],
        output_path: Path,
        folder_name: str = ""
    ) -> None:
        """
        Save combined markdown content to file.

        Args:
            markdown_contents: List of markdown content strings
            output_path: Path to save the output file
            folder_name: Name of the folder being processed
        """
        try:
            # Create header
            display_name = "Root Directory" if folder_name == "_root" else folder_name
            header = f"# Combined Documents - {display_name}\n\n"
            header += f"*Generated from {len(markdown_contents)} document(s)*\n\n"

            # Combine all content
            combined_content = header + "\n".join(markdown_contents)

            # Save to file
            output_path.write_text(combined_content, encoding='utf-8')

            logger.info(
                "💾 Successfully saved markdown file: %s (%s characters) ✨", output_path, f"{len(combined_content):,}")

        except Exception as e:
            logger.error(
                "💥 Oh no! Failed to save markdown to %s: %s", output_path, e)
            raise

    def _generate_summary_report(
        self,
        result: ConversionResult,
        summary_path: Path,
        # start_time: float
    ) -> None:
        """
        Generate a processing summary report.

        Args:
            result: ConversionResult containing processing information
            summary_path: Path to save the summary report
            start_time: Processing start time
        """
        try:
            # Generate summary content
            summary_lines = [
                "# Processing Summary Report",
                "",
                f"**Generated at:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
                f"**Processing time:** {result.processing_time:.2f} seconds",
                f"**Total output files:** {len(result.output_files)}",
                f"**Folders processed:** {len(result.processed_folders)}",
                f"**Folders skipped:** {len(result.skipped_folders)}",
                "",
                "## Processed Folders",
                ""
            ]

            for folder_name, files in result.processed_folders.items():
                display_name = "Root Directory" if folder_name == "_root" else folder_name
                summary_lines.append(f"### {display_name}")
                summary_lines.append(f"- **Files processed:** {len(files)}")
                if files:
                    summary_lines.append("- **File list:**")
                    for file in files:
                        summary_lines.append(f"  - {file}")
                summary_lines.append("")

            if result.skipped_folders:
                summary_lines.extend([
                    "## Skipped Folders (Already Converted)",
                    ""
                ])
                for folder_name, files in result.skipped_folders.items():
                    display_name = "Root Directory" if folder_name == "_root" else folder_name
                    summary_lines.append(f"### {display_name}")
                    summary_lines.append(
                        f"- **Files in folder:** {len(files)}")
                    summary_lines.append(
                        "- **Reason:** Already converted (existing markdown found)")
                    if files:
                        summary_lines.append("- **File list:**")
                        for file in files:
                            summary_lines.append(f"  - {file}")
                    summary_lines.append("")

            if result.failed_files:
                summary_lines.extend([
                    "## Failed Files",
                    ""
                ])
                for failed_file in result.failed_files:
                    summary_lines.append(f"- {failed_file}")
                summary_lines.append("")

            summary_lines.extend([
                "## Output Files",
                ""
            ])
            for output_file in result.output_files:
                summary_lines.append(
                    f"- [{output_file.name}](./{output_file.name})")

            summary_content = "\n".join(summary_lines)
            summary_path.write_text(summary_content, encoding='utf-8')

            logger.debug(
                "📋 Summary report saved to: %s ✅", summary_path)

        except Exception as e:
            logger.warning(
                "⚠️ Couldn't generate the summary report (but your files are safe!): %s", e)

    def get_supported_formats(self) -> set:
        """
        Get the set of supported file formats.

        Returns:
            Set of supported file extensions
        """
        return SUPPORTED_FORMATS.copy()

    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate the current configuration and return status.

        Returns:
            Dictionary containing validation results
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }

        try:
            # Check directories
            if not self.config.IMPORTS_DIR.exists():
                validation_result["warnings"].append(
                    f"📂 Heads up! Imports directory doesn't exist yet: {self.config.IMPORTS_DIR}"
                )

            # Check for supported files and folders
            try:
                processing_map = discover_processing_folders(
                    self.config.IMPORTS_DIR)
                total_files = sum(len(files)
                                  for files in processing_map.values())
                validation_result["info"]["folders_found"] = len(
                    processing_map)
                validation_result["info"]["supported_files_found"] = total_files

                if total_files == 0:
                    validation_result["warnings"].append(
                        "🔍 No supported documents found yet! Add some PDFs or other documents to get started! 📄"
                    )
            except ValueError as e:
                validation_result["warnings"].append(str(e))

            # Check output directory
            try:
                self.config.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
                validation_result["info"]["exports_dir_writable"] = True
            except Exception as e:
                validation_result["errors"].append(
                    f"❌ Can't create exports directory (check permissions?): {e}")
                validation_result["valid"] = False

            # Check docling availability
            try:
                # Test docling by creating a converter
                # test_converter = DocumentConverter()
                validation_result["info"]["docling_available"] = True
                validation_result["info"]["docling_ocr_enabled"] = self.config.ENABLE_OCR
            except ImportError:
                validation_result["errors"].append(
                    "🚫 Docling is missing! Please run 'pip install docling' to get started! 🔧")
                validation_result["valid"] = False
            except Exception as e:
                validation_result["warnings"].append(
                    f"⚠️ Docling setup hiccup (but it might still work): {e}")

        except Exception as e:
            validation_result["errors"].append(
                f"💥 Something went wrong with validation: {e}")
            validation_result["valid"] = False

        return validation_result
