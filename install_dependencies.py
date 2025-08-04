#!/usr/bin/env python3
"""
Dependency Installation Helper

This script helps install and verify dependencies for the PDF to Markdown converter.
It provides an interactive way to set up the environment and check for optional dependencies.
"""

import subprocess
import sys
import importlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def check_python_version() -> bool:
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"   Current version: {sys.version}")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def install_requirements() -> bool:
    """Install requirements from requirements.txt."""
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        print("📦 Installing requirements...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True, check=True)
        
        print("✅ Requirements installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        print(f"   Error output: {e.stderr}")
        return False


def check_dependencies() -> Dict[str, bool]:
    """Check if all dependencies are available."""
    dependencies = {
        "fitz": "PyMuPDF (PDF processing)",
        "PIL": "Pillow (Image processing)", 
        "torch": "PyTorch (AI models)",
        "transformers": "Transformers (AI models)",
        "tqdm": "TQDM (Progress bars)",
        "requests": "Requests (HTTP client)"
    }
    
    optional_dependencies = {
        "pytesseract": "Tesseract OCR (Optional OCR support)"
    }
    
    results = {}
    
    print("\\n🔍 Checking core dependencies:")
    for module, description in dependencies.items():
        try:
            importlib.import_module(module)
            print(f"✅ {description}")
            results[module] = True
        except ImportError:
            print(f"❌ {description}")
            results[module] = False
    
    print("\\n🔍 Checking optional dependencies:")
    for module, description in optional_dependencies.items():
        try:
            importlib.import_module(module)
            print(f"✅ {description}")
            results[module] = True
        except ImportError:
            print(f"⚠️  {description} (not installed)")
            results[module] = False
    
    return results


def check_gpu_support() -> Dict[str, bool]:
    """Check GPU support availability."""
    gpu_info = {}
    
    print("\\n🖥️  Checking GPU support:")
    
    try:
        import torch
        gpu_info["torch_available"] = True
        
        if torch.cuda.is_available():
            print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
            gpu_info["cuda"] = True
        else:
            print("ℹ️  CUDA not available")
            gpu_info["cuda"] = False
        
        if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✅ Apple Metal Performance Shaders (MPS) available")
            gpu_info["mps"] = True
        else:
            gpu_info["mps"] = False
            
    except ImportError:
        print("❌ PyTorch not available")
        gpu_info["torch_available"] = False
        gpu_info["cuda"] = False
        gpu_info["mps"] = False
    
    return gpu_info


def check_disk_space() -> bool:
    """Check available disk space for model downloads."""
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (1024**3)
        
        print(f"\\n💾 Available disk space: {free_gb} GB")
        
        if free_gb < 5:
            print("⚠️  Warning: Less than 5GB free space available")
            print("   AI models may require additional storage")
            return False
        else:
            print("✅ Sufficient disk space available")
            return True
            
    except Exception as e:
        print(f"⚠️  Could not check disk space: {e}")
        return True


def run_basic_test() -> bool:
    """Run a basic functionality test."""
    print("\\n🧪 Running basic functionality test...")
    
    try:
        from src.config import config
        from src.utils import sanitize_filename
        from src.converter import PDFToMarkdownConverter
        
        # Test basic functionality
        test_filename = sanitize_filename("test_file.pdf")
        if test_filename != "test_file":
            raise ValueError("Filename sanitization failed")
        
        # Test converter initialization
        converter = PDFToMarkdownConverter()
        validation = converter.validate_configuration()
        
        print("✅ Basic functionality test passed")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False


def create_sample_env_file() -> None:
    """Create a sample .env file if it doesn't exist."""
    env_file = Path(".env")
    
    if env_file.exists():
        print("ℹ️  .env file already exists")
        return
    
    env_content = '''# PDF to Markdown Converter - Environment Configuration
# Adjust the values as needed

# Model caching directory (optional)
# MODEL_CACHE_DIR=/path/to/model/cache

# Device selection for AI processing
# Options: auto, cpu, cuda, mps
DEVICE=auto

# Enable verbose logging by default
VERBOSE=false
'''
    
    try:
        env_file.write_text(env_content)
        print("✅ Created sample .env file")
    except Exception as e:
        print(f"⚠️  Could not create .env file: {e}")


def main():
    """Main setup function."""
    print("🚀 PDF to Markdown Converter - Setup Helper")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Ask user if they want to install requirements
    response = input("\\n📦 Install requirements from requirements.txt? (y/n): ").lower()
    if response in ('y', 'yes'):
        if not install_requirements():
            print("\\n❌ Setup failed due to dependency installation errors")
            sys.exit(1)
    
    # Check dependencies
    dep_results = check_dependencies()
    
    # Check GPU support
    gpu_results = check_gpu_support()
    
    # Check disk space
    check_disk_space()
    
    # Create sample env file
    create_sample_env_file()
    
    # Run basic test
    if not run_basic_test():
        print("\\n❌ Setup completed with errors")
        sys.exit(1)
    
    # Summary
    print("\\n" + "=" * 50)
    print("📋 Setup Summary:")
    
    core_deps_ok = all(dep_results.get(dep, False) for dep in ["fitz", "PIL", "torch", "transformers"])
    
    if core_deps_ok:
        print("✅ All core dependencies are available")
        print("✅ Setup completed successfully!")
        
        print("\\n🎯 Next steps:")
        print("1. Place PDF files in the 'imports/' directory")
        print("2. Run: python main.py")
        print("3. Check output in the 'exports/' directory")
        
        if gpu_results.get("cuda") or gpu_results.get("mps"):
            print("\\n⚡ GPU acceleration is available for faster processing!")
        
    else:
        print("❌ Some core dependencies are missing")
        print("   Please install missing dependencies and run this script again")
        sys.exit(1)


if __name__ == "__main__":
    main()