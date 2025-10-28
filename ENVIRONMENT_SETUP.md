# Complete Environment Setup Guide

**ML Traffic Monitoring System - Full Installation Guide**

**Last Updated:** October 28, 2025
**Status:** Complete setup instructions from scratch

---

## 📋 Table of Contents

- [System Requirements](#system-requirements)
- [Python Installation](#python-installation)
- [Package Installation](#package-installation)
- [GPU Setup (Optional)](#gpu-setup-optional)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)
- [Quick Reference](#quick-reference)

---

## 💻 System Requirements

### Minimum Requirements (CPU Processing)

**Operating System:**
- Windows 10/11 (64-bit)
- macOS 10.14+ (Mojave or later)
- Linux (Ubuntu 18.04+, Debian 10+, or equivalent)

**Hardware:**
- Processor: Quad-core CPU (Intel i5/AMD Ryzen 5 or better)
- RAM: 8GB minimum, 16GB recommended
- Storage: 10GB free space for packages and models
- Display: Any resolution (1280×720 or higher recommended)

**Software:**
- Python 3.8 - 3.12 (see Python Installation section)
- Internet connection (for package downloads)

### Recommended Requirements (GPU Processing)

**Operating System:**
- Windows 10/11 (64-bit) recommended
- Linux (Ubuntu 20.04+ with NVIDIA drivers)

**Hardware:**
- GPU: NVIDIA GPU with 4GB+ VRAM (GTX 1650, RTX 3050, RTX 4060, or better)
- Processor: Quad-core CPU or better
- RAM: 16GB recommended
- Storage: 15GB free space (includes CUDA)

**Software:**
- Python 3.8 - 3.12
- CUDA Toolkit 11.x or 12.x
- NVIDIA GPU drivers (latest)

---

## 🐍 Python Installation

### Checking if Python is Already Installed

**Windows:**
```cmd
python --version
```

**macOS/Linux:**
```bash
python3 --version
```

**Expected output:**
```
Python 3.10.x (or 3.8.x - 3.12.x)
```

**If you see "command not found" or "not recognized":** Python is not installed.

---

### Installing Python

#### Windows Installation

**Method 1: Official Python Installer (Recommended)**

1. **Visit:** https://www.python.org/downloads/

2. **Download:**
   - Click "Download Python 3.11.x" (or 3.10.x)
   - Choose Windows installer (64-bit)

3. **Run Installer:**
   - Double-click downloaded `.exe` file
   - **IMPORTANT:** ☑ Check "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation (5-10 minutes)

4. **Verify Installation:**
   ```cmd
   python --version
   pip --version
   ```

**Method 2: Microsoft Store (Easier)**

1. Open Microsoft Store
2. Search "Python 3.11"
3. Click "Get" to install
4. Automatically adds to PATH

**Method 3: Winget (Windows Package Manager)**

```cmd
winget install Python.Python.3.11
```

#### macOS Installation

**Method 1: Official Installer**

1. Visit: https://www.python.org/downloads/
2. Download macOS installer
3. Run `.pkg` file
4. Follow installation wizard

**Method 2: Homebrew (Recommended for developers)**

```bash
# Install Homebrew first (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11
```

**Verify:**
```bash
python3 --version
pip3 --version
```

#### Linux Installation

**Ubuntu/Debian:**

```bash
# Update package list
sudo apt update

# Install Python 3.11 (or 3.10)
sudo apt install python3.11 python3.11-venv python3-pip

# Verify
python3.11 --version
pip3 --version
```

**Fedora/CentOS:**

```bash
sudo dnf install python3.11 python3-pip
```

**Arch Linux:**

```bash
sudo pacman -S python python-pip
```

---

### Python Version Recommendations

**Best Choices:**
- ✅ **Python 3.11** - Most stable, best compatibility
- ✅ **Python 3.10** - Very stable, excellent support
- ✅ **Python 3.12** - Latest, works well (minor compatibility checks needed)

**Also Works:**
- ✅ Python 3.9 - Good, slightly older
- ✅ Python 3.8 - Minimum supported version

**Avoid:**
- ❌ Python 3.7 or older - Packages dropping support
- ❌ Python 3.13+ - Too new, potential compatibility issues

---

### Setting Up Virtual Environment (Recommended)

**Why use virtual environment?**
- Isolates project dependencies
- Prevents conflicts with other Python projects
- Easy to reproduce environment

**Create Virtual Environment:**

**Windows:**
```cmd
# Navigate to project folder
cd C:\path\to\simul8_mkv_annotator

# Create virtual environment
python -m venv venv

# Activate
venv\Scripts\activate

# You'll see (venv) in command prompt
```

**macOS/Linux:**
```bash
# Navigate to project folder
cd /path/to/simul8_mkv_annotator

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# You'll see (venv) in terminal prompt
```

**Deactivate (when done):**
```bash
deactivate
```

---

## 📦 Package Installation

### Quick Install (All Packages)

**If you have the `requirements.txt` file:**

```bash
# CPU version (no GPU)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

**For GPU (NVIDIA):**
```bash
# GPU version with CUDA 12.1
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

### Manual Installation (Step-by-Step)

If you don't have `requirements.txt`, install packages individually:

#### Step 1: Install Core Packages

```bash
pip install ultralytics
pip install opencv-python
pip install pandas
pip install numpy
```

**Expected time:** 5-10 minutes
**Download size:** ~500MB

#### Step 2: Install PyTorch

**For CPU:**
```bash
pip install torch torchvision
```

**For GPU (CUDA 12.1):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**For GPU (CUDA 11.8):**
```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Expected time:** 10-15 minutes
**Download size:** ~2GB (CPU) or ~3GB (GPU)

#### Step 3: Install Tracking Package

```bash
pip install deep-sort-realtime
```

**Expected time:** 2-3 minutes
**Download size:** ~50MB

#### Step 4: Install Optional Packages

**For Dashboard:**
```bash
pip install streamlit
```

**For Enhanced Features:**
```bash
pip install mediapipe plotly PyYAML openpyxl
```

---

### Package Versions (Tested & Verified)

```
ultralytics>=8.0.0          # YOLOv8 - Object detection
opencv-python>=4.8.0        # Video processing
torch>=2.0.0                # Deep learning framework
torchvision>=0.15.0         # Vision utilities
deep-sort-realtime>=1.3.0   # Multi-object tracking
pandas>=2.0.0               # Data manipulation
numpy>=1.24.0               # Numerical operations
streamlit>=1.20.0           # Dashboard (optional)
PyYAML>=6.0                 # Config files (optional)
openpyxl>=3.1.0             # Excel export (optional)
plotly>=5.14.0              # Visualizations (optional)
mediapipe>=0.10.0           # CV utilities (optional)
```

---

## 🎮 GPU Setup (Optional)

**Only needed if you have NVIDIA GPU and want 15-25× speedup**

### Check if You Have NVIDIA GPU

**Windows:**
```cmd
# Open Device Manager
# Look for "Display adapters"
# Should see "NVIDIA GeForce..." or "NVIDIA RTX..."
```

**Alternative (all platforms):**
```bash
nvidia-smi
```

**If you see GPU info:** You have NVIDIA GPU ✅
**If you see "command not found":** Need to install CUDA toolkit

---

### Installing CUDA Toolkit

#### Windows CUDA Installation

**1. Check GPU Compatibility:**
- Visit: https://developer.nvidia.com/cuda-gpus
- Verify your GPU is CUDA-capable (most NVIDIA GPUs since 2010 are)

**2. Download CUDA Toolkit:**
- Visit: https://developer.nvidia.com/cuda-downloads
- Select:
  - Operating System: Windows
  - Architecture: x86_64
  - Version: 10 or 11
  - Installer Type: exe (local)

**3. Download CUDA 12.1 (Recommended):**
- Direct link: https://developer.nvidia.com/cuda-12-1-0-download-archive
- File size: ~3GB
- Download time: 10-30 minutes (depends on internet speed)

**4. Run Installer:**
- Run downloaded `.exe` file
- Choose "Express Installation" (recommended)
- Installation time: 15-30 minutes
- May require restart

**5. Verify CUDA Installation:**
```cmd
nvcc --version
```

**Expected output:**
```
nvcc: NVIDIA (R) Cuda compiler driver
...
Cuda compilation tools, release 12.1, V12.1.xxx
```

**6. Verify GPU with PyTorch:**
```bash
python -c "import torch; print('CUDA Available:', torch.cuda.is_available()); print('GPU Count:', torch.cuda.device_count()); print('GPU Name:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Expected output:**
```
CUDA Available: True
GPU Count: 1
GPU Name: NVIDIA GeForce RTX 4060
```

#### macOS GPU Support

**Apple Silicon (M1/M2/M3):**
- Use Metal Performance Shaders (MPS) backend
- PyTorch automatically detects and uses MPS
- No CUDA installation needed

```python
import torch
print("MPS Available:", torch.backends.mps.is_available())
```

#### Linux CUDA Installation

**Ubuntu/Debian:**

```bash
# Download CUDA toolkit
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
sudo apt-get update
sudo apt-get install cuda

# Add to PATH
echo 'export PATH=/usr/local/cuda/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Verify
nvcc --version
```

---

### Updating GPU Drivers

**Windows:**
1. Visit: https://www.nvidia.com/drivers
2. Select your GPU model
3. Download and install latest driver
4. Restart computer

**Or use GeForce Experience:**
- Download: https://www.nvidia.com/en-us/geforce/geforce-experience/
- Automatic driver updates

**Linux:**
```bash
# Ubuntu
sudo apt install nvidia-driver-535

# Or latest
sudo ubuntu-drivers autoinstall
```

---

## ✅ Verification

### Complete System Check

**Run this verification script:**

```bash
python -c "
import sys
print('Python version:', sys.version)
print()

# Check packages
packages = [
    'ultralytics',
    'cv2',
    'torch',
    'pandas',
    'numpy',
    'deep_sort_realtime'
]

print('Package versions:')
for pkg in packages:
    try:
        if pkg == 'cv2':
            import cv2
            print(f'  opencv-python: {cv2.__version__}')
        else:
            mod = __import__(pkg)
            print(f'  {pkg}: {mod.__version__}')
    except ImportError:
        print(f'  {pkg}: NOT INSTALLED')
    except AttributeError:
        print(f'  {pkg}: Installed (version not accessible)')

print()

# Check GPU
import torch
print('GPU Information:')
print(f'  CUDA Available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'  CUDA Version: {torch.version.cuda}')
    print(f'  GPU Count: {torch.cuda.device_count()}')
    print(f'  GPU Name: {torch.cuda.get_device_name(0)}')
    print(f'  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('  Running on CPU (no GPU detected)')
"
```

**Expected output (CPU):**
```
Python version: 3.11.x

Package versions:
  ultralytics: 8.3.x
  opencv-python: 4.12.x
  torch: 2.9.x
  pandas: 2.3.x
  numpy: 2.2.x
  deep_sort_realtime: 1.3.x

GPU Information:
  CUDA Available: False
  Running on CPU (no GPU detected)
```

**Expected output (GPU):**
```
Python version: 3.11.x

Package versions:
  ultralytics: 8.3.x
  opencv-python: 4.12.x
  torch: 2.9.x
  pandas: 2.3.x
  numpy: 2.2.x
  deep_sort_realtime: 1.3.x

GPU Information:
  CUDA Available: True
  CUDA Version: 12.1
  GPU Count: 1
  GPU Name: NVIDIA GeForce RTX 4060
  GPU Memory: 6.0 GB
```

---

### Test ML System Initialization

```bash
# If you have the project files
python init_test.py
```

**Expected output:**
```
======================================================================
INITIALIZATION TEST - Testing ML System Startup
======================================================================

[1/5] Importing basic packages...
    [OK] Basic packages loaded (1.9s)

[2/5] Importing YOLO (ultralytics)...
    [OK] YOLO imported (4.6s)

[3/5] Loading YOLO model...
    [OK] YOLO model loaded (0.3s)

[4/5] Importing DeepSORT...
    [OK] DeepSORT imported (1.0s)

[5/5] Initializing DeepSORT tracker...
    [OK] DeepSORT initialized (3.9s)

======================================================================
[SUCCESS] ALL COMPONENTS INITIALIZED SUCCESSFULLY!
======================================================================
```

---

## 🔧 Troubleshooting

### Common Installation Issues

#### Issue 1: "python not found" or "command not recognized"

**Symptom:**
```
'python' is not recognized as an internal or external command
```

**Solution:**
1. **Verify Python is installed:**
   - Open Control Panel → Programs → Check for Python

2. **Add Python to PATH manually:**
   - Find Python installation (usually `C:\Users\[name]\AppData\Local\Programs\Python\Python311`)
   - Add to System PATH:
     - Right-click "This PC" → Properties
     - Advanced system settings → Environment Variables
     - Edit "Path" variable
     - Add Python installation directory
     - Add Python Scripts directory

3. **Alternative:** Try `python3` instead of `python`

4. **Last resort:** Reinstall Python with "Add to PATH" checked

---

#### Issue 2: "pip not found"

**Symptom:**
```
'pip' is not recognized as an internal or external command
```

**Solution:**

**Windows:**
```cmd
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

**macOS/Linux:**
```bash
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip
```

---

#### Issue 3: Permission Denied During Installation

**Symptom:**
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Solution:**

**Option 1: Install for user only (recommended)**
```bash
pip install --user package_name
```

**Option 2: Use admin/sudo (not recommended)**
```bash
# Windows: Run CMD as Administrator
pip install package_name

# macOS/Linux
sudo pip install package_name
```

**Option 3: Use virtual environment (best practice)**
```bash
python -m venv venv
# Activate venv, then install
```

---

#### Issue 4: CUDA/GPU Not Detected

**Symptom:**
```python
torch.cuda.is_available()  # Returns False
```

**Solution:**

**Step 1: Verify GPU exists**
```cmd
nvidia-smi
```

**If this fails:** Install/update NVIDIA drivers

**Step 2: Check CUDA installation**
```cmd
nvcc --version
```

**If this fails:** Install CUDA Toolkit

**Step 3: Reinstall PyTorch with CUDA**
```bash
pip uninstall torch torchvision
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**Step 4: Restart computer**
- Sometimes CUDA requires restart to initialize

---

#### Issue 5: Package Conflicts

**Symptom:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
```

**Solution:**

**Option 1: Create fresh virtual environment**
```bash
# Deactivate current environment
deactivate

# Create new clean environment
python -m venv fresh_env
fresh_env\Scripts\activate  # Windows
source fresh_env/bin/activate  # macOS/Linux

# Install packages
pip install -r requirements.txt
```

**Option 2: Update pip**
```bash
python -m pip install --upgrade pip
```

**Option 3: Force reinstall**
```bash
pip install --force-reinstall -r requirements.txt
```

---

#### Issue 6: Slow Installation

**Symptom:**
- Package installation takes hours
- Downloads frequently stall

**Solution:**

**Use different PyPI mirror:**
```bash
# Use Tsinghua mirror (faster in Asia)
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# Use Alibaba mirror
pip install -i https://mirrors.aliyun.com/pypi/simple/ package_name
```

**Or set permanent mirror:**
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

---

#### Issue 7: "No module named 'X'" After Installation

**Symptom:**
```python
ImportError: No module named 'cv2'
```

**But you installed it:**
```bash
pip install opencv-python  # Shows already installed
```

**Solution:**

**Issue:** Multiple Python installations

**Check which Python/pip you're using:**
```bash
which python  # macOS/Linux
where python  # Windows

which pip
where pip
```

**Fix:** Use Python's module syntax
```bash
python -m pip install opencv-python
```

**Or:** Specify Python version explicitly
```bash
python3.11 -m pip install opencv-python
```

---

#### Issue 8: Out of Disk Space

**Symptom:**
```
ERROR: Could not install packages due to an OSError: [Errno 28] No space left on device
```

**Solution:**

**Check available space:**
```bash
# Windows
dir C:\

# macOS/Linux
df -h
```

**Clean pip cache:**
```bash
pip cache purge
```

**Free up space:**
- Delete old Python packages: `pip list` → `pip uninstall old_package`
- Clean temp files
- Uninstall unused programs

**Minimum space needed:** 10GB for complete installation

---

### Getting Help

**If problems persist:**

1. **Check error message carefully**
   - Copy full error text
   - Search on Google/Stack Overflow

2. **Verify system requirements**
   - Python version compatible?
   - Enough disk space?
   - Internet connection stable?

3. **Try fresh installation**
   - Create new virtual environment
   - Install one package at a time

4. **Check GitHub Issues**
   - Visit: https://github.com/weilalicia7/simul8_mkv_annotator/issues
   - Search for similar problems
   - Post new issue if needed

5. **System Information to Include:**
   ```bash
   python --version
   pip --version
   pip list
   # OS version
   # Error message (full text)
   ```

---

## 📝 Quick Reference

### Essential Commands

**Check Python:**
```bash
python --version
pip --version
```

**Install packages:**
```bash
# All at once
pip install -r requirements.txt

# Individual
pip install ultralytics opencv-python pandas numpy deep-sort-realtime
```

**GPU setup:**
```bash
# Install CUDA PyTorch
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Verify GPU
python -c "import torch; print(torch.cuda.is_available())"
```

**Virtual environment:**
```bash
# Create
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Deactivate
deactivate
```

**Update packages:**
```bash
pip install --upgrade package_name
pip list --outdated
```

---

### Installation Checklist

Use this checklist to track your installation:

**Python Setup:**
- [ ] Python 3.8-3.12 installed
- [ ] Python added to PATH
- [ ] pip working (`pip --version`)
- [ ] Virtual environment created (recommended)

**Core Packages:**
- [ ] ultralytics installed
- [ ] opencv-python installed
- [ ] pandas installed
- [ ] numpy installed
- [ ] torch installed (CPU or GPU version)
- [ ] deep-sort-realtime installed

**GPU Setup (if applicable):**
- [ ] NVIDIA GPU available
- [ ] NVIDIA drivers updated
- [ ] CUDA Toolkit installed
- [ ] PyTorch detects GPU (`torch.cuda.is_available()`)

**Verification:**
- [ ] All packages import without errors
- [ ] init_test.py runs successfully (if available)
- [ ] GPU shows correct name and memory (if GPU setup)

**Ready to Use!** ✅

---

### Environment Summary

**Minimum (CPU):**
```
Python 3.8+
ultralytics
opencv-python
pandas
numpy
torch (CPU)
deep-sort-realtime

Total install time: ~20-30 minutes
Total disk space: ~3-4GB
Processing speed: 1.5 FPS
```

**Recommended (GPU):**
```
Python 3.10-3.11
CUDA Toolkit 12.1
NVIDIA GPU drivers (latest)
ultralytics
opencv-python
pandas
numpy
torch (CUDA)
deep-sort-realtime

Total install time: ~45-60 minutes
Total disk space: ~6-8GB
Processing speed: 25-40 FPS (RTX 4060)
```

---

## 🎯 Next Steps

**After successful installation:**

1. **Clone repository:**
   ```bash
   git clone https://github.com/weilalicia7/simul8_mkv_annotator.git
   cd simul8_mkv_annotator
   ```

2. **Read documentation:**
   - `README.md` - Project overview
   - `GPU_PROCESSING_GUIDE.md` - How to process videos
   - `ML_README.md` - ML system quick start

3. **Test with sample:**
   ```bash
   python init_test.py
   ```

4. **Process your first video:**
   ```bash
   python -u ml_processor.py your_video.mp4 --output results.csv
   ```

---

**Installation Status:** ✅ Complete
**Environment Ready:** ✅ Ready to process videos
**Documentation:** ✅ Available in repository

---

*For processing instructions, see GPU_PROCESSING_GUIDE.md*
*For ML system details, see ML_README.md*
*For troubleshooting, see this document's Troubleshooting section*
