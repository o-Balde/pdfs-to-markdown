# PDF to Markdown Converter

A comprehensive Python tool that converts PDF files to markdown format with AI-generated image descriptions. This tool extracts text and images from PDFs, generates natural language descriptions for images using AI models, and combines everything into a single, well-formatted markdown document.

## Features

- **📄 PDF Text Extraction**: Extracts text content from PDF files with proper formatting
- **🖼️ Image Processing**: Extracts images from PDFs and generates AI descriptions
- **🤖 AI Image Descriptions**: Uses BLIP model to generate natural language descriptions for images
- **📝 Markdown Output**: Combines multiple PDFs into a single, well-formatted markdown document
- **⚡ Modular Architecture**: Clean, extensible code with proper type hints and documentation
- **🔧 Configurable**: Extensive configuration options for customization
- **📊 Progress Tracking**: Detailed progress reporting and summary generation
- **🛡️ Error Handling**: Robust error handling with detailed logging

## Requirements

- Python 3.8+
- PyTorch (for AI image descriptions)
- PyMuPDF (for PDF processing)
- Transformers (for AI models)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd pdf-to-markdown
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) For OCR capabilities, install Tesseract:
```bash
# On macOS
brew install tesseract

# On Ubuntu/Debian
sudo apt-get install tesseract-ocr

# On Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

## Quick Start

1. **Organize your PDF files**: Create folders in the `imports/` directory for different projects:
```
imports/
├── game_design/
│   ├── concept_art.pdf
│   └── mechanics_guide.pdf
├── research_papers/
│   ├── ai_study.pdf
│   └── machine_learning.pdf
└── manual.pdf  (optional: files in root)
```

2. **Run the converter**:
```bash
python main.py
```

3. **Check your results** in the `exports/` directory:
```
exports/
├── game_design_2024-01-15_14-30-25.md
├── research_papers_2024-01-15_14-32-10.md
├── combined_documents.md  (for root files)
└── processing_summary_1705337425.md
```

## Usage

### Basic Usage

```bash
# Convert all folders in imports/ to separate markdown files
python main.py

# Specify custom directories
python main.py --imports /path/to/pdfs --exports /path/to/output

# Custom output filename for root files only
python main.py --output my_documents.md
```

### Advanced Options

```bash
# Disable image descriptions for faster processing
python main.py --no-images

# Enable verbose logging
python main.py --verbose

# Validate configuration
python main.py --validate

# List available PDF files and folder structure
python main.py --list-files
```

### Programmatic Usage

```python
from src.converter import PDFToMarkdownConverter
from pathlib import Path

# Initialize converter
converter = PDFToMarkdownConverter()

# Convert PDFs
result = converter.convert(
    imports_dir=Path("my_pdfs"),
    exports_dir=Path("output"),
    output_filename="combined_docs.md",
    enable_image_descriptions=True
)

if result.success:
    print(f"Conversion successful! Output: {result.output_file}")
else:
    print(f"Conversion failed: {result.error_message}")
```

## Configuration

The application can be configured through the `src/config.py` file or environment variables:

### Key Configuration Options

- `IMPORTS_DIR`: Directory containing PDF files (default: `imports/`)
- `EXPORTS_DIR`: Output directory (default: `exports/`)
- `OUTPUT_FILENAME`: Output file name (default: `combined_documents.md`)
- `EXTRACT_IMAGES`: Enable image extraction (default: `True`)
- `IMAGE_DESCRIPTION_MODEL`: AI model for image descriptions
- `MAX_IMAGE_SIZE`: Maximum image dimensions for processing
- `ENABLE_OCR`: Enable OCR for text in images

### Environment Variables

Create a `.env` file in the project root:

```bash
MODEL_CACHE_DIR=/path/to/model/cache
DEVICE=cuda  # or cpu, auto
VERBOSE=true
```

## Project Structure

```
pdf-to-markdown/
├── src/
│   ├── __init__.py
│   ├── config.py              # Configuration settings
│   ├── utils.py               # Utility functions
│   ├── pdf_processor.py       # PDF text/image extraction
│   ├── image_processor.py     # AI image description generation
│   ├── markdown_formatter.py  # Markdown formatting
│   └── converter.py           # Main conversion orchestrator
├── imports/                   # Input PDF files (create this)
├── exports/                   # Output markdown files
├── main.py                   # CLI entry point
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Output Format

The converter generates **separate markdown files for each folder**, plus an overall summary:

### Folder-Based Processing

For each folder in `imports/`, you get:
- **Individual markdown file** named `{folder_name}_{timestamp}.md`
- **Organized content** with all PDFs from that folder
- **Timestamped filename** to avoid conflicts

### File Structure Example

```
exports/
├── game_design_2024-01-15_14-30-25.md
├── research_papers_2024-01-15_14-32-10.md 
├── combined_documents.md (for root files)
└── processing_summary_1705337425.md
```

### Document Format

Each generated markdown file contains:

1. **Folder Header**: Folder name, generation timestamp, and statistics
2. **Table of Contents**: Links to each document section
3. **Document Sections**: Each PDF becomes a section with:
   - Original filename and metadata
   - Extracted text with proper formatting
   - Embedded images with AI-generated descriptions
   - Page markers for navigation

Example output structure:

```markdown
# PDF Documents from 'game_design'

*Generated on: 2024-01-15 14:30:25*
*Total documents: 3*
*Total pages: 47*

## Table of Contents

1. [Concept_Art](#concept-art)
2. [Mechanics_Guide](#mechanics-guide)
3. [Level_Design](#level-design)

___

# Concept Art

*Source: concept_art.pdf*
*Processed: 2024-01-15 14:30:25*

## Document Information
- **Pages**: 15
- **Author**: Art Team

[Document text content here...]

![Image 1 (Page 3): A detailed character design sketch showing the main protagonist with armor details and weapon specifications.](data:image/png;base64,...)

[More content...]
```

## AI Image Descriptions

The tool uses the BLIP (Bootstrapping Language-Image Pre-training) model to generate natural language descriptions for images. Features include:

- **Automatic Detection**: Extracts images from PDF pages
- **Context-Aware**: Generates relevant descriptions based on image content
- **Configurable**: Choose different AI models or disable descriptions
- **Performance Optimized**: Supports GPU acceleration when available

## Error Handling and Logging

The application provides comprehensive error handling and logging:

- **Detailed Logs**: Track processing progress and issues
- **Graceful Degradation**: Continue processing even if some files fail
- **Summary Reports**: Generate processing summaries with statistics
- **Validation**: Validate configuration and inputs before processing

## Performance Considerations

- **GPU Acceleration**: Automatically uses CUDA/MPS when available
- **Memory Management**: Processes images efficiently to avoid memory issues
- **Batch Processing**: Optimized for handling multiple large PDF files
- **Caching**: Model caching to avoid repeated downloads

## Troubleshooting

### Common Issues

1. **Out of Memory Errors**:
   - Reduce `MAX_IMAGE_SIZE` in config
   - Use `--no-images` flag
   - Process files in smaller batches

2. **Model Download Issues**:
   - Check internet connection
   - Set `MODEL_CACHE_DIR` environment variable
   - Use `--validate` to check configuration

3. **PDF Processing Errors**:
   - Ensure PDFs are not corrupted
   - Check file permissions
   - Use `--verbose` for detailed error messages

### Getting Help

1. Use `--validate` to check your configuration
2. Enable `--verbose` logging for detailed output
3. Check the generated summary report for processing details

## Contributing

This project follows clean code principles and is designed for extensibility:

- **Type Hints**: Full type annotation throughout
- **Documentation**: Comprehensive docstrings and comments
- **Modular Design**: Easy to extend with new features
- **Error Handling**: Robust error handling and recovery
- **Testing**: Structured for easy unit testing

To add new features:

1. Follow the existing modular structure
2. Add proper type hints and documentation
3. Include error handling and logging
4. Update configuration as needed

## License

This project is open source and available under the MIT License.

## Acknowledgments

- **PyMuPDF**: Excellent PDF processing capabilities
- **Hugging Face Transformers**: AI model infrastructure
- **BLIP Model**: Image captioning capabilities
- **PyTorch**: Deep learning framework