# Usage Guide - PDF to Markdown Converter

## 🚀 Enhanced Folder-Based Processing

The PDF to Markdown converter now supports **folder-based processing**, allowing you to organize your PDFs by project, topic, or any structure you prefer, and get separate timestamped output files for each folder.

## 📁 Folder Structure Setup

### 1. Create Your Project Folders

```bash
# Create example folder structure
mkdir -p imports/game_design
mkdir -p imports/research_papers  
mkdir -p imports/technical_docs
```

### 2. Organize Your PDFs

```
imports/
├── game_design/           # Game development PDFs
│   ├── concept_art.pdf
│   ├── mechanics_guide.pdf
│   └── level_design.pdf
├── research_papers/       # Academic papers
│   ├── ai_study.pdf
│   ├── machine_learning.pdf
│   └── neural_networks.pdf
├── technical_docs/        # Technical documentation
│   ├── api_reference.pdf
│   └── user_manual.pdf
└── quick_reference.pdf    # Optional: files in root
```

## 🎯 Processing Behavior

### What Happens When You Run the Converter:

1. **Folder Discovery**: Scans `imports/` for subdirectories containing PDFs
2. **Individual Processing**: Each folder is processed separately
3. **Timestamped Outputs**: Each folder gets its own markdown file with timestamp
4. **Root Files**: PDFs directly in `imports/` are processed as a single group

### Example Output:

```
exports/
├── game_design_2024-01-15_14-30-25.md       # All game design PDFs
├── research_papers_2024-01-15_14-32-10.md   # All research papers
├── technical_docs_2024-01-15_14-33-45.md    # All technical docs
├── combined_documents.md                      # Root PDFs (if any)
└── processing_summary_1705337425.md          # Overall processing report
```

## 💻 Command Examples

### Basic Commands

```bash
# Process all folders - creates separate timestamped files
python main.py

# List your folder structure before processing
python main.py --list-files

# Validate setup before running
python main.py --validate
```

### Advanced Options

```bash
# Fast processing without image descriptions
python main.py --no-images

# Verbose output to see detailed progress
python main.py --verbose

# Custom directories
python main.py --imports /path/to/your/pdfs --exports /path/to/output
```

## 📊 Example Output Structure

### Individual Folder Output (`game_design_2024-01-15_14-30-25.md`):

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

[Document content with embedded images and descriptions...]

___

# Mechanics Guide

*Source: mechanics_guide.pdf*
*Processed: 2024-01-15 14:30:25*

[Document content...]
```

### Overall Summary Report (`processing_summary_*.md`):

```markdown
# Overall Processing Summary

- **Processing completed**: 2024-01-15 14:30:25
- **Total processing time**: 45.23 seconds
- **Folders processed**: 3
- **Output files generated**: 3
- **Total pages processed**: 127
- **Total images extracted**: 24

## Folder Processing Details

### Game Design
- Files processed: 3
- Status: ✅ Success
- Files:
  - concept_art.pdf
  - mechanics_guide.pdf
  - level_design.pdf

### Research Papers
- Files processed: 3
- Status: ✅ Success
[...]
```

## 🎯 Use Cases

### Perfect For:

1. **Project Management**: Separate outputs for different projects
2. **Research Organization**: Group papers by topic or field
3. **Documentation**: Organize manuals, guides, and references
4. **Content Creation**: Separate game design, art, and technical docs
5. **Academic Work**: Organize by subject, semester, or research area

### Example Workflows:

```bash
# Game Development Studio
imports/
├── concept_art/
├── design_docs/
├── technical_specs/
└── marketing_materials/

# Research Lab
imports/
├── 2024_papers/
├── conference_proceedings/
├── grant_proposals/
└── literature_review/

# Technical Documentation
imports/
├── user_manuals/
├── api_documentation/
├── troubleshooting_guides/
└── release_notes/
```

## 🔧 Installation & Setup

1. **Install Dependencies**:
```bash
python install_dependencies.py
# OR manually:
pip install -r requirements.txt
```

2. **Verify Setup**:
```bash
python main.py --validate
```

3. **Test Folder Discovery**:
```bash
python main.py --list-files
```

## 💡 Tips for Best Results

1. **Organize by Purpose**: Group related PDFs in meaningful folders
2. **Use Descriptive Names**: Folder names become part of output filenames
3. **Check Structure**: Use `--list-files` to verify your organization
4. **Start Small**: Test with a few files before processing large collections
5. **GPU Acceleration**: Install CUDA/MPS for faster image processing

## 🚨 Important Notes

- **Timestamps**: Output files include timestamps to prevent overwrites
- **Backwards Compatible**: Old single-file workflow still works with root PDFs
- **Image Processing**: Can be disabled with `--no-images` for faster processing
- **Memory Usage**: Large collections may require processing in batches

## 📈 Performance Tips

```bash
# For large collections - disable image descriptions
python main.py --no-images

# Process specific folder only
# (move other folders temporarily out of imports/)

# Monitor with verbose output
python main.py --verbose
```

This enhanced folder-based processing makes the PDF to Markdown converter perfect for organizing and converting large collections of PDFs while keeping your outputs organized and accessible! 🎉