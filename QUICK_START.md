# 🚀 Quick Start Guide

## ✅ **SOLVED: PyMuPDF Issue Fixed!**

**Problem**: PyMuPDF import errors due to virtual environment issues.  
**Solution**: Use the correct commands to ensure virtual environment is active.

## 🎯 **Three Ways to Run (Choose One):**

### 1. **Easy Way - Use Helper Script (Recommended)**
```bash
./run.sh --list-files       # List PDF files
./run.sh --validate         # Validate setup
./run.sh                    # Convert PDFs
./run.sh --no-images        # Fast conversion
```

### 2. **Manual Virtual Environment**
```bash
source .venv/bin/activate   # Activate virtual environment
python3 main.py --list-files
python3 main.py             # Convert PDFs
```

### 3. **Direct Python3 Command**
```bash
# Only works if virtual environment is already active
python3 main.py --list-files
python3 main.py
```

## ⚠️ **Important Notes:**

- **Never use `python main.py`** - it uses system Python without PyMuPDF
- **Always use `python3 main.py`** or **`./run.sh`**
- The helper script automatically handles virtual environment activation

## 📁 **Your Current Setup:**
- ✅ 19 PDF files ready to process
- ✅ 2 folders: `rule_books` (15 files) + `game_design_roguelikes` (4 files)
- ✅ PyMuPDF installed and working
- ✅ Virtual environment configured

## 🎯 **Ready to Convert!**
Run: `./run.sh` to convert all your PDFs to timestamped markdown files.

---
*This guide fixes the "No module named 'fitz'" error permanently.*