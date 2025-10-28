# ML System Initialization Troubleshooting Guide

## What This Guide Is For

If you're stuck at the initialization phase when trying to run the ML processor, this guide will help you diagnose and fix the issue step-by-step.

**Common symptoms:**
- Script appears to hang with no output
- "Initializing..." message but nothing happens
- Process runs for 10+ minutes with no progress
- Console window shows no updates

---

## Understanding Initialization

### What Happens During Initialization?

When you run `python ml_processor.py video.mp4`, the system must:

1. **Load Python packages** (~2-3 seconds)
   - Import cv2, pandas, numpy, torch

2. **Download YOLO model** (first run only, ~30-60 seconds)
   - Downloads yolov8n.pt (~6.2 MB)
   - Subsequent runs skip this step

3. **Initialize YOLO** (~3-5 seconds)
   - Load model into memory
   - Setup detection pipeline

4. **Initialize DeepSORT** (~3-5 seconds)
   - Load tracking algorithm
   - Setup Kalman filters

**Expected total time:** 10-15 seconds (after first download)
**First run total time:** 40-75 seconds (includes model download)

---

## Step-by-Step Diagnostic Process

### Step 1: Check Python Installation

**Test command:**
```bash
python --version
```

**Expected output:**
```
Python 3.9.x or Python 3.10.x or Python 3.11.x
```

**If you see an error:**
- Python is not installed or not in PATH
- **Solution:** Follow ENVIRONMENT_SETUP.md Section 1

**If version is wrong:**
- Python 3.8 or older → Too old, install Python 3.9+
- Python 3.12+ → May have compatibility issues, use 3.9-3.11
- **Solution:** Install correct Python version

---

### Step 2: Verify Package Installation

**Test command:**
```bash
python -c "import cv2, torch, ultralytics, pandas, numpy; print('All packages imported successfully')"
```

**Expected output:**
```
All packages imported successfully
```

**If you see ModuleNotFoundError:**
```
ModuleNotFoundError: No module named 'cv2'
```

**Solution:** Install missing packages
```bash
# Install all required packages
pip install -r requirements.txt

# Or install individually:
pip install ultralytics opencv-python torch pandas numpy deep-sort-realtime
```

**After installation, test again** - all imports should work.

---

### Step 3: Test YOLO Initialization Alone

Create a simple test file to isolate YOLO loading.

**Create file: `test_yolo.py`**
```python
import time
print("Starting YOLO test...")

print("Step 1: Importing ultralytics...")
start = time.time()
from ultralytics import YOLO
print(f"  Success! ({time.time()-start:.1f}s)")

print("Step 2: Loading YOLO model...")
start = time.time()
model = YOLO('yolov8n.pt')
print(f"  Success! ({time.time()-start:.1f}s)")

print("\nYOLO initialized successfully!")
```

**Run the test:**
```bash
python test_yolo.py
```

**Expected output:**
```
Starting YOLO test...
Step 1: Importing ultralytics...
  Success! (0.8s)
Step 2: Loading YOLO model...
Downloading https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt...
  Success! (45.2s)  # Only on first run

YOLO initialized successfully!
```

**Possible issues:**

#### Issue A: Download fails
```
Error: Failed to download model
```
**Solution:**
- Check internet connection
- Download manually from: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
- Place file in project directory
- Run test again

#### Issue B: Import error
```
ImportError: cannot import name 'YOLO' from 'ultralytics'
```
**Solution:**
```bash
pip uninstall ultralytics
pip install ultralytics>=8.0.0
```

#### Issue C: Takes extremely long (>5 minutes)
**Solution:**
- System is too slow
- YOLO model may be corrupted
- Delete `yolov8n.pt` and try again
- Consider using faster computer

---

### Step 4: Test DeepSORT Initialization

**Create file: `test_deepsort.py`**
```python
import time
print("Starting DeepSORT test...")

print("Step 1: Importing deep_sort_realtime...")
start = time.time()
from deep_sort_realtime.deepsort_tracker import DeepSort
print(f"  Success! ({time.time()-start:.1f}s)")

print("Step 2: Initializing DeepSORT tracker...")
start = time.time()
tracker = DeepSort(
    max_age=30,
    n_init=3,
    nms_max_overlap=1.0,
    max_cosine_distance=0.3,
    nn_budget=None,
    gating_only_position=False,
    embedder="mobilenet",
    half=False
)
print(f"  Success! ({time.time()-start:.1f}s)")

print("\nDeepSORT initialized successfully!")
```

**Run the test:**
```bash
python test_deepsort.py
```

**Expected output:**
```
Starting DeepSORT test...
Step 1: Importing deep_sort_realtime...
  Success! (1.2s)
Step 2: Initializing DeepSORT tracker...
  Success! (4.3s)

DeepSORT initialized successfully!
```

**Possible issues:**

#### Issue A: ModuleNotFoundError
```
ModuleNotFoundError: No module named 'deep_sort_realtime'
```
**Solution:**
```bash
pip install deep-sort-realtime
```

#### Issue B: TensorFlow/Keras errors
```
ImportError: cannot import name 'get_file' from 'keras.utils'
```
**Solution:**
```bash
pip install tensorflow==2.12.0
pip install keras==2.12.0
```

---

### Step 5: Test Video File Access

**Create file: `test_video.py`**
```python
import cv2
import sys

video_path = sys.argv[1] if len(sys.argv) > 1 else "test_30sec.mp4"
print(f"Testing video access: {video_path}")

# Try to open video
video = cv2.VideoCapture(video_path)

if not video.isOpened():
    print("ERROR: Cannot open video file!")
    print("Possible issues:")
    print("  - File doesn't exist")
    print("  - File path is wrong")
    print("  - File is corrupted")
    print("  - Missing video codec")
    sys.exit(1)

# Get video properties
fps = video.get(cv2.CAP_PROP_FPS)
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(f"Video opened successfully!")
print(f"  Resolution: {width}x{height}")
print(f"  FPS: {fps}")
print(f"  Total frames: {frame_count}")
print(f"  Duration: {frame_count/fps:.1f} seconds")

# Try to read first frame
ret, frame = video.read()
if ret:
    print(f"  First frame read successfully!")
else:
    print("  ERROR: Cannot read frames from video!")

video.release()
```

**Run the test:**
```bash
python test_video.py "your_video.mp4"
```

**Expected output:**
```
Testing video access: your_video.mp4
Video opened successfully!
  Resolution: 1280x720
  FPS: 30.0
  Total frames: 900
  Duration: 30.0 seconds
  First frame read successfully!
```

**Possible issues:**

#### Issue A: File not found
```
ERROR: Cannot open video file!
```
**Solution:**
- Check file path is correct
- Use quotes around filename if it has spaces: `python test_video.py "file with spaces.mp4"`
- Verify file exists: `ls` (Mac/Linux) or `dir` (Windows)

#### Issue B: Cannot read frames
```
Video opened successfully!
...
ERROR: Cannot read frames from video!
```
**Solution:**
- Video file may be corrupted
- Missing codec: Install ffmpeg
  ```bash
  # Windows (using chocolatey)
  choco install ffmpeg

  # Mac
  brew install ffmpeg

  # Linux
  sudo apt install ffmpeg
  ```

---

### Step 6: Run Full Initialization Test

Use the provided initialization test script.

**Run command:**
```bash
python init_test.py
```

**Expected output:**
```
======================================================================
INITIALIZATION TEST - Testing ML System Startup
======================================================================

[1/5] Importing basic packages...
    [OK] Basic packages loaded (2.3s)

[2/5] Importing YOLO...
    [OK] YOLO imported (1.1s)

[3/5] Loading YOLO model...
    [OK] YOLO model loaded (3.8s)

[4/5] Importing DeepSORT...
    [OK] DeepSORT imported (0.9s)

[5/5] Initializing DeepSORT tracker...
    [OK] DeepSORT initialized (4.2s)

======================================================================
SUCCESS: All components initialized in 12.3 seconds
======================================================================
```

**If this succeeds:**
- Initialization is working correctly
- Problem may be with video processing, not initialization
- See "The Output Buffering Problem" section below

**If this fails:**
- Note which step fails
- Go back to corresponding test above
- Follow troubleshooting for that component

---

## The Output Buffering Problem

### Symptom
Script appears to hang after initialization with no output for 10+ minutes.

### What's Actually Happening
Python buffers output by default on Windows. The script IS running, but you can't see the progress updates.

### Solution: Use Unbuffered Mode

**Instead of:**
```bash
python ml_processor.py video.mp4
```

**Use:**
```bash
python -u ml_processor.py video.mp4
```

The `-u` flag disables output buffering, showing progress updates in real-time.

**Expected output with `-u` flag:**
```
ML Traffic Monitoring System
Processing: video.mp4

Initializing system...
[OK] Basic packages loaded
[OK] YOLO model loaded
[OK] DeepSORT initialized

Processing video...
Progress: 100/1000 frames (10.0%) - 0.5 FPS - 8 detections
Progress: 200/1000 frames (20.0%) - 0.6 FPS - 15 detections
Progress: 300/1000 frames (30.0%) - 0.5 FPS - 23 detections
...
```

---

## GPU vs CPU Performance

### Checking Your Hardware

**Run this to check for GPU:**
```bash
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'None')"
```

**Output examples:**

**With GPU:**
```
CUDA available: True
GPU: NVIDIA GeForce RTX 4060
```

**Without GPU (CPU only):**
```
CUDA available: False
GPU: None
```

### Expected Processing Times

**30-second video (900 frames @ 30 FPS):**
- **With GPU (RTX 4060):** 30-90 seconds (10-30 FPS)
- **With CPU only:** 10-20 minutes (1-2 FPS)

**1-hour video (108,000 frames):**
- **With GPU:** 1-3 hours
- **With CPU:** 15-30 hours

### If You Only Have CPU

**Options:**
1. **Process short clips** - Use `quick_test.py` to extract 30-60 second segments
2. **Use faster computer** - Transfer to machine with GPU
3. **Be patient** - It WILL complete, just takes longer
4. **Run overnight** - Let it process while you sleep

**To extract test clip:**
```bash
python quick_test.py "full_video.mkv" 30
```
This creates `test_30sec.mp4` for faster testing.

---

## Common Error Messages and Solutions

### Error 1: "No module named 'X'"
**Cause:** Package not installed
**Solution:**
```bash
pip install X
# Or reinstall all:
pip install -r requirements.txt
```

### Error 2: "CUDA out of memory"
**Cause:** GPU ran out of memory
**Solution:**
- Close other GPU-using programs
- Reduce batch size (edit ml_processor.py)
- Use smaller YOLO model (yolov8n.pt instead of yolov8s.pt)

### Error 3: "Unable to open video file"
**Cause:** File not found or corrupted
**Solution:**
- Check file path
- Use absolute path: `python ml_processor.py "C:\full\path\to\video.mp4"`
- Test with different video file

### Error 4: "AttributeError: module 'cv2' has no attribute 'VideoCapture'"
**Cause:** opencv-python not installed correctly
**Solution:**
```bash
pip uninstall opencv-python opencv-python-headless opencv-contrib-python
pip install opencv-python
```

### Error 5: Script exits immediately with no error
**Cause:** Python syntax error or wrong Python version
**Solution:**
```bash
# Check Python version
python --version

# Run with verbose error output
python -u ml_processor.py video.mp4 2>&1
```

### Error 6: "RuntimeError: Attempting to deserialize object on a CUDA device"
**Cause:** Model was saved on GPU but trying to load on CPU
**Solution:**
- Delete yolov8n.pt and re-download
- Or add `device='cpu'` parameter in code

---

## Step-by-Step First Run

If you're running the system for the very first time, follow this exact sequence:

### 1. Install Python (if needed)
```bash
# Check if you have Python
python --version

# If not, download from python.org
# Install Python 3.9, 3.10, or 3.11
```

### 2. Navigate to project folder
```bash
cd path/to/simul8_mkv_annotator
```

### 3. Install packages
```bash
pip install -r requirements.txt
```
**Wait for:** "Successfully installed..." message (2-5 minutes)

### 4. Test initialization
```bash
python init_test.py
```
**Expected time:** 10-15 seconds (first run may take 60s for model download)

### 5. Extract test clip
```bash
python quick_test.py "your_video.mkv" 30
```
**Creates:** test_30sec.mp4

### 6. Process test clip
```bash
python -u ml_processor.py test_30sec.mp4
```
**Expected time:**
- GPU: 30-90 seconds
- CPU: 10-20 minutes

### 7. Check results
```bash
# View first 10 lines of output
head results.csv
```

### 8. Process full video (if test succeeded)
```bash
python -u ml_processor.py "your_full_video.mkv" --output final_results.csv
```

---

## Verification Checklist

Before processing full video, verify each item:

- [ ] Python 3.9-3.11 installed (`python --version`)
- [ ] All packages installed (`pip list | grep ultralytics`)
- [ ] YOLO test passes (`python test_yolo.py`)
- [ ] DeepSORT test passes (`python test_deepsort.py`)
- [ ] Video file opens (`python test_video.py video.mp4`)
- [ ] Full init test passes (`python init_test.py`)
- [ ] Test clip processes successfully (`python -u ml_processor.py test_30sec.mp4`)
- [ ] Output CSV file created (`ls results.csv`)

**If all checks pass:** System is ready for full video processing!

---

## Still Stuck?

If you've followed all steps and still cannot initialize:

### 1. Collect diagnostic information

**Create file: `diagnostics.py`**
```python
import sys
import platform

print("=== System Diagnostics ===")
print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.machine()}")

print("\n=== Package Versions ===")
try:
    import cv2
    print(f"OpenCV: {cv2.__version__}")
except Exception as e:
    print(f"OpenCV: ERROR - {e}")

try:
    import torch
    print(f"PyTorch: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
except Exception as e:
    print(f"PyTorch: ERROR - {e}")

try:
    import ultralytics
    print(f"Ultralytics: {ultralytics.__version__}")
except Exception as e:
    print(f"Ultralytics: ERROR - {e}")

try:
    from deep_sort_realtime.deepsort_tracker import DeepSort
    print(f"DeepSORT: Installed")
except Exception as e:
    print(f"DeepSORT: ERROR - {e}")

print("\n=== File Check ===")
import os
files = ['ml_processor.py', 'requirements.txt', 'init_test.py']
for f in files:
    status = "Found" if os.path.exists(f) else "MISSING"
    print(f"{f}: {status}")
```

**Run:**
```bash
python diagnostics.py > diagnostics_output.txt
```

### 2. Common solutions for persistent issues

**Solution A: Fresh install**
```bash
# Uninstall all packages
pip uninstall ultralytics opencv-python torch deep-sort-realtime pandas numpy -y

# Clear pip cache
pip cache purge

# Reinstall
pip install -r requirements.txt
```

**Solution B: Use virtual environment**
```bash
# Create clean environment
python -m venv ml_env

# Activate it
# Windows:
ml_env\Scripts\activate
# Mac/Linux:
source ml_env/bin/activate

# Install packages
pip install -r requirements.txt

# Test again
python init_test.py
```

**Solution C: Use different Python version**
- If using Python 3.12 → Install Python 3.11
- If using Python 3.8 → Install Python 3.10

### 3. Hardware requirements

**Minimum:**
- CPU: Any modern processor (Intel Core i5 or equivalent)
- RAM: 8 GB
- Storage: 10 GB free space
- OS: Windows 10/11, macOS 10.15+, Linux

**Recommended for full video:**
- CPU: Intel Core i7 or AMD Ryzen 7
- RAM: 16 GB
- GPU: NVIDIA RTX 2060 or better (6GB+ VRAM)
- Storage: 50 GB free space

---

## Quick Reference Commands

```bash
# Check Python version
python --version

# Install packages
pip install -r requirements.txt

# Test initialization only
python init_test.py

# Process video with visible progress
python -u ml_processor.py video.mp4

# Extract test clip
python quick_test.py video.mkv 30

# Check GPU availability
python -c "import torch; print(torch.cuda.is_available())"

# Validate output
python validate_ml.py results.csv

# View results
head results.csv  # Mac/Linux
type results.csv | more  # Windows
```

---

## Success Indicators

You'll know initialization is successful when:

1. **init_test.py completes in 10-20 seconds**
2. **No error messages appear**
3. **All 5 components show [OK]**
4. **Test video processes to completion**
5. **results.csv file is created**
6. **CSV contains detection data with proper columns**

**Example successful result:**
```csv
ID,Time (s),Entity,Type/Dir,Inter-Arrival (s),Service Time (s)
1,7.1,EB Vehicles,EB,0.0,-
2,9.8,EB Vehicles,EB,2.6,-
3,12.3,EB Vehicles,EB,2.5,-
```

If you see this, initialization and processing are both working correctly!

---

## Next Steps After Successful Initialization

1. **Process full video** (if you have GPU)
2. **Review BOUNDARIES_EXPLANATION.md** - Understand detection parameters
3. **Use dashboard.py** - Visualize results interactively
4. **Adjust thresholds** - Fine-tune for your specific video
5. **Validate results** - Compare ML output with manual annotations

Good luck! The system is designed to work reliably once initialization completes successfully.
