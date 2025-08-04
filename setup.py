"""
Setup script for PDF to Markdown Converter.

This script provides installation and packaging support for the PDF to Markdown
converter project.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = requirements_path.read_text(encoding="utf-8").strip().split("\\n")
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith("#")]

setup(
    name="pdf-to-markdown",
    version="1.0.0",
    author="PDF to Markdown Converter",
    author_email="developer@example.com",
    description="Convert PDF files to markdown format with AI-generated image descriptions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pdf-to-markdown",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Markup",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Office Suites",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.7.0",
            "flake8>=6.0.0",
        ],
        "ocr": [
            "pytesseract>=0.3.10",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf-to-markdown=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="pdf markdown converter ai image description nlp",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/pdf-to-markdown/issues",
        "Source": "https://github.com/yourusername/pdf-to-markdown",
        "Documentation": "https://github.com/yourusername/pdf-to-markdown#readme",
    },
)