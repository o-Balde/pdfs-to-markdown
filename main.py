#!/usr/bin/env python3
"""
Document to Markdown Converter - Main Entry Point

A comprehensive tool for converting documents to markdown format using Docling.
Supports PDF, DOCX, PPTX, XLSX, HTML, and other formats with advanced
document understanding capabilities.

Usage:
    python main.py [options]
    
Examples:
    # Basic conversion with default settings
    python main.py
    
    # Convert with custom paths
    python main.py --imports /path/to/documents --exports /path/to/output
    
    # Disable OCR for faster processing
    python main.py --no-ocr
    
    # Verbose output
    python main.py --verbose
"""

from src.utils import setup_logging
from src.config import config
from src.pdf_to_markdown.orchestrator import Orchestrator
from src.pdf_to_markdown.model import ConversionResult
from pathlib import Path
import argparse
import logging
import sys
import warnings

# Suppress the "pin_memory" warning on Apple‐Silicon machines (MPS backend)
warnings.filterwarnings(
    "ignore",
    message=r".*pin_memory.*not supported on MPS.*",
    category=UserWarning,
    module=r"torch.utils.data.dataloader",
)


logger = logging.getLogger(__name__)


def create_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure the command-line argument parser.

    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Convert documents to markdown format using Docling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                      # Basic conversion
  %(prog)s --imports ./docs --exports ./out    # Custom directories
  %(prog)s --no-ocr --verbose                  # Fast conversion with logging
  %(prog)s --output combined.md                # Custom output filename
        """
    )

    # Input/Output options
    parser.add_argument(
        "--imports", "-i",
        type=Path,
        default=config.IMPORTS_DIR,
        help=f"Directory containing document files (default: {config.IMPORTS_DIR})"
    )

    parser.add_argument(
        "--exports", "-e",
        type=Path,
        default=config.EXPORTS_DIR,
        help=f"Output directory for markdown file (default: {config.EXPORTS_DIR})"
    )

    parser.add_argument(
        "--output", "-o",
        type=str,
        default=config.OUTPUT_FILENAME,
        help=f"Output filename (default: {config.OUTPUT_FILENAME})"
    )

    # Processing options
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Disable OCR for scanned documents (faster processing)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )

    # Utility options
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration and exit"
    )

    parser.add_argument(
        "--list-files",
        action="store_true",
        help="List supported document files in imports directory and exit"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Document to Markdown Converter 2.0.0 (Docling-powered)"
    )

    return parser


def setup_application_logging(verbose: bool = False) -> None:
    """
    Set up application logging based on verbosity level.

    Args:
        verbose: Whether to enable verbose (DEBUG) logging
    """
    from src.config import LOGGING_CONFIG
    log_config = LOGGING_CONFIG.copy()

    if verbose:
        log_config["handlers"]["default"]["level"] = "DEBUG"
        log_config["loggers"][""]["level"] = "DEBUG"

    setup_logging(log_config)


def validate_configuration(converter: Orchestrator) -> bool:
    """
    Validate the application configuration.

    Args:
        converter: Orchestrator instance

    Returns:
        True if configuration is valid, False otherwise
    """
    validation_result = converter.validate_configuration()

    print("Configuration Validation Results:")
    print("=" * 40)

    # Print info
    if validation_result["info"]:
        print("Information:")
        for key, value in validation_result["info"].items():
            print(f"  • {key.replace('_', ' ').title()}: {value}")
        print()

    # Print warnings
    if validation_result["warnings"]:
        print("Warnings:")
        for warning in validation_result["warnings"]:
            print(f"  ⚠️  {warning}")
        print()

    # Print errors
    if validation_result["errors"]:
        print("Errors:")
        for error in validation_result["errors"]:
            print(f"  ❌ {error}")
        print()

    # Print overall result
    if validation_result["valid"]:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration has errors that must be fixed")

    return validation_result["valid"]


def list_document_files(imports_dir: Path) -> None:
    """
    List all supported document files in the imports directory and its subdirectories.

    Args:
        imports_dir: Path to imports directory
    """
    try:
        if not imports_dir.exists():
            print(f"❌ Imports directory does not exist: {imports_dir}")
            return

        from src.utils import discover_processing_folders

        processing_map = discover_processing_folders(imports_dir)

        print(f"Document Files Structure in {imports_dir}:")
        print("=" * 50)

        if not processing_map:
            print("No supported document files found.")
            return

        total_files = 0

        for folder_name, doc_files in processing_map.items():
            if folder_name == "_root":
                print("📁 Root Directory:")
            else:
                print(f"📁 {folder_name}/:")

            if not doc_files:
                print("   (no supported document files)")
            else:
                for i, doc_file in enumerate(doc_files, 1):
                    file_size = doc_file.stat().st_size
                    size_mb = file_size / (1024 * 1024)
                    print(f"   {i:2d}. {doc_file.name} ({size_mb:.1f} MB)")
                total_files += len(doc_files)

            print()  # Add blank line between folders

        print(
            f"Total: {len(processing_map)} folders, {total_files} document files")

    except Exception as e:
        print(f"❌ Error listing files: {e}")


def print_conversion_results(result: ConversionResult) -> None:
    """
    Print detailed conversion results.

    Args:
        result: ConversionResult object
    """
    print("\nConversion Results:")
    print("=" * 40)

    if result.success:
        print("✅ Conversion completed successfully!")
        print(f"   Processing time: {result.processing_time:.2f} seconds")
        print(f"   Folders processed: {len(result.processed_folders)}")
        print(f"   Output files generated: {len(result.output_files)}")
        print(f"   Total pages: {result.total_pages}")
        print(f"   Total images: {result.total_images}")

        # Show output files
        print("\n   📄 Generated files:")
        for output_file in result.output_files:
            print(f"     • {output_file.name}")

        # Show folder processing details
        if len(result.processed_folders) > 1:
            print("\n   📁 Folder details:")
            for folder_name, files in result.processed_folders.items():
                display_name = "Root Directory" if folder_name == "_root" else folder_name
                print(f"     • {display_name}: {len(files)} files")

        if result.failed_files:
            print(f"\n   ❌ Failed files: {len(result.failed_files)}")
            for failed_file in result.failed_files:
                print(f"     • {failed_file}")
    else:
        print("❌ Conversion failed!")
        print(f"   Error: {result.error_message}")
        print(f"   Processing time: {result.processing_time:.2f} seconds")

        if result.processed_files:
            print(
                f"   Partially processed: {len(result.processed_files)} files")


def main() -> int:
    """
    Main entry point for the PDF to Markdown converter.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Parse command line arguments
        parser = create_argument_parser()
        args = parser.parse_args()

        # Setup logging
        setup_application_logging(args.verbose)

        # Handle utility commands
        if args.list_files:
            list_document_files(args.imports)
            return 0

        # Initialize converter
        logger.info("Initializing Document to Markdown converter")
        converter = Orchestrator(verbose=args.verbose)

        # Handle validation command
        if args.validate:
            is_valid = validate_configuration(converter)
            return 0 if is_valid else 1

        # Validate configuration before processing
        validation_result = converter.validate_configuration()
        if not validation_result["valid"]:
            print("❌ Configuration validation failed:")
            for error in validation_result["errors"]:
                print(f"   • {error}")
            return 1

        # Show warnings if any
        if validation_result["warnings"]:
            print("⚠️  Configuration warnings:")
            for warning in validation_result["warnings"]:
                print(f"   • {warning}")
            print()

        # Perform conversion
        print("🚀 Starting Document to Markdown conversion...")

        # Re-create orchestrator with updated OCR flag if requested
        if args.no_ocr:
            logger.info("Re-instantiating orchestrator with OCR disabled")
            from dataclasses import replace
            new_cfg = replace(converter.cfg, ENABLE_OCR=False)
            converter = Orchestrator(cfg=new_cfg, verbose=args.verbose)

        result = converter.convert(
            imports_dir=args.imports,
            exports_dir=args.exports,
            output_filename=args.output,
        )

        # Print results
        print_conversion_results(result)

        return 0 if result.success else 1

    except KeyboardInterrupt:
        print("\n⏹️  Conversion interrupted by user")
        return 1

    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
