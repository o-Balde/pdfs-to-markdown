"""
Basic functionality tests for the PDF to Markdown converter.

These tests verify the core functionality without requiring actual PDF files
or AI models, using mocks and sample data.
"""

import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile
import shutil

from src.config import Config
from src.utils import sanitize_filename, clean_text, format_section_header
from src.pdf_processor import PDFContent
from src.markdown_formatter import MarkdownFormatter
from src.converter import PDFToMarkdownConverter, ConversionResult


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        test_cases = [
            ("document.pdf", "document"),
            ("My Document!.pdf", "My_Document_"),
            ("file with spaces.pdf", "file_with_spaces"),
            ("special@#$%chars.pdf", "special____chars"),
            ("multiple___underscores.pdf", "multiple_underscores"),
            ("", "untitled"),
        ]

        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_filename(input_name)
                self.assertEqual(result, expected)

    def test_clean_text(self):
        """Test text cleaning functionality."""
        test_text = "  This is   a test\\n\\n\\n\\nwith-\\nexcessive spacing.  "

        result = clean_text(test_text)
        self.assertIn("This is", result)
        self.assertNotIn("   ", result)  # No excessive spaces

    def test_format_section_header(self):
        """Test section header formatting."""
        filename = "test_document.pdf"
        header = format_section_header(filename)

        self.assertIn("# test_document", header)
        self.assertIn("*Source: test_document.pdf*", header)
        self.assertIn("*Processed:", header)


class TestMarkdownFormatter(unittest.TestCase):
    """Test markdown formatting functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.formatter = MarkdownFormatter()

        # Create sample PDF content
        self.sample_content = PDFContent(
            filename="test.pdf",
            text="This is sample text from a PDF document.",
            images=[],
            metadata={"title": "Test Document", "author": "Test Author"},
            page_count=1,
            file_hash="abc123"
        )

    def test_format_pdf_content_without_images(self):
        """Test formatting PDF content without images."""
        result = self.formatter.format_pdf_content(self.sample_content)

        self.assertIn("# test", result)
        self.assertIn("*Source: test.pdf*", result)
        self.assertIn("This is sample text", result)
        self.assertIn("**Title**: Test Document", result)
        self.assertIn("**Author**: Test Author", result)

    def test_combine_documents(self):
        """Test combining multiple documents."""
        contents = [self.sample_content, self.sample_content]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            temp_path = Path(f.name)

        try:
            result = self.formatter.combine_documents(contents, temp_path)

            self.assertIn("# Combined PDF Documents", result)
            self.assertIn("## Table of Contents", result)
            self.assertIn("Total documents: 2", result)
            self.assertTrue(temp_path.exists())

        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_create_summary_report(self):
        """Test summary report generation."""
        contents = [self.sample_content]
        summary = self.formatter.create_summary_report(contents)

        self.assertIn("# Processing Summary", summary)
        self.assertIn("Documents processed**: 1", summary)
        self.assertIn("test.pdf", summary)


class TestConverter(unittest.TestCase):
    """Test main converter functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.imports_dir = self.temp_dir / "imports"
        self.exports_dir = self.temp_dir / "exports"

        self.imports_dir.mkdir()
        self.exports_dir.mkdir()

        # Create a test config
        self.test_config = Config()
        self.test_config.IMPORTS_DIR = self.imports_dir
        self.test_config.EXPORTS_DIR = self.exports_dir

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    @patch('src.converter.PDFProcessor')
    @patch('src.converter.ImageProcessor')
    def test_converter_initialization(self, _mock_image_proc, _mock_pdf_proc):
        """Test converter initialization."""
        converter = PDFToMarkdownConverter(self.test_config)

        self.assertIsNotNone(converter.pdf_processor)
        self.assertIsNotNone(converter.image_processor)
        self.assertIsNotNone(converter.markdown_formatter)

    def test_validate_configuration(self):
        """Test configuration validation."""
        converter = PDFToMarkdownConverter(self.test_config)
        result = converter.validate_configuration()

        self.assertIn("valid", result)
        self.assertIn("errors", result)
        self.assertIn("warnings", result)
        self.assertIn("info", result)

    def test_get_supported_formats(self):
        """Test supported formats retrieval."""
        converter = PDFToMarkdownConverter(self.test_config)
        formats = converter.get_supported_formats()

        self.assertIn(".pdf", formats)
        self.assertIsInstance(formats, set)


class TestConversionResult(unittest.TestCase):
    """Test conversion result container."""

    def test_conversion_result_initialization(self):
        """Test ConversionResult initialization."""
        result = ConversionResult()

        self.assertFalse(result.success)
        self.assertIsNone(result.output_file)
        self.assertEqual(result.processed_files, [])
        self.assertEqual(result.failed_files, [])
        self.assertEqual(result.total_pages, 0)
        self.assertEqual(result.total_images, 0)
        self.assertEqual(result.processing_time, 0.0)
        self.assertIsNone(result.error_message)


if __name__ == '__main__':
    unittest.main()
