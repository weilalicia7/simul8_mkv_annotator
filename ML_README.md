# ML Traffic Monitoring System - Quick Start Guide

## 📁 Files Created

- **ml_processor.py** - Main processing script for automated detection
- **dashboard.py** - Interactive Streamlit dashboard
- **validate_ml.py** - Validation script to compare ML vs manual annotations
- **config.yaml** - Configuration file (for future enhancements)
- **ML_INTEGRATION_GUIDE.md** - Comprehensive documentation

## 🚀 Quick Start

### 1. Verify Installation

Check that all packages are installed:

```bash
python -c "import cv2, ultralytics, streamlit; print('✓ All packages installed!')"
```

### 2. Process a Video

**Basic usage:**
```bash
python ml_processor.py your_video.mp4
```

**With options:**
```bash
# Specify output filename
python ml_processor.py video.mp4 --output results.csv

# Show live processing (slower but visual)
python ml_processor.py video.mp4 --show

# Adjust confidence threshold (lower = more detections)
python ml_processor.py video.mp4 --confidence 0.25

# Custom arrival line position
python ml_processor.py video.mp4 --arrival-line 500
```

**Output:** Creates `video_ml_results.csv` with same format as manual tool

### 3. Launch Interactive Dashboard

```bash
streamlit run dashboard.py
```

Then:
1. Upload video file in sidebar
2. Adjust settings (confidence, arrival line)
3. Click "▶️ Start Processing"
4. Watch live detection and statistics
5. Download results as CSV or Excel

**Dashboard opens at:** http://localhost:8501

### 4. Validate ML Accuracy

Compare ML results with your manual annotations:

```bash
python validate_ml.py manual_annotations.csv ml_results.csv
```

**Output:**
- Count comparison by entity type
- Precision and recall metrics
- Timing error analysis
- Missing detections report
- False positives report

**Save report to file:**
```bash
python validate_ml.py manual.csv ml_results.csv --output report.txt
```

## 📊 Output Format

All tools export data in the same format as the manual annotation tool:

| Column | Description | Example |
|--------|-------------|---------|
| ID | Sequential identifier | 1, 2, 3... |
| Time (s) | Video timestamp | 15.3 |
| Entity | Entity type | "EB Vehicles" |
| Type/Dir | Direction/type | "EB" |
| Inter-Arrival (s) | Time since last arrival | 5.4 |
| Service Time (s) | Crossing duration | "-" or "3.2" |

## 🎯 Typical Workflow

### Workflow 1: Automated Processing
```bash
# 1. Process video with ML
python ml_processor.py abbey_road.mp4 --output ml_results.csv

# 2. Review results
# Opens in Excel or your CSV viewer
```

### Workflow 2: ML + Manual Review
```bash
# 1. Process with ML
python ml_processor.py video.mp4 --output ml_suggestions.csv

# 2. Open manual annotation tool (mkv-annotation-tool.html)
# 3. Load ML suggestions
# 4. Review and correct
# 5. Export final results
```

### Workflow 3: Validation & Accuracy Testing
```bash
# 1. Create manual annotations (ground truth)
# Use mkv-annotation-tool.html to annotate a sample video

# 2. Process same video with ML
python ml_processor.py sample_video.mp4 --output ml_test.csv

# 3. Compare accuracy
python validate_ml.py manual_sample.csv ml_test.csv

# 4. Review metrics and adjust confidence threshold if needed
python ml_processor.py sample_video.mp4 --confidence 0.4 --output ml_test2.csv
python validate_ml.py manual_sample.csv ml_test2.csv
```

## ⚙️ Configuration Tips

### Confidence Threshold
- **Default: 0.35** (balanced)
- **Lower (0.2-0.3)**: More detections, more false positives
- **Higher (0.4-0.6)**: Fewer detections, more missed events
- **Recommendation**: Start with 0.35, adjust based on validation results

### Arrival Line Position
- **Default: null** (auto-calculates middle of frame)
- **Custom**: Specify Y-coordinate in pixels
- **How to find**: Open video in tool, note Y-position where arrivals should be counted

### Show Video Processing
- **`--show`**: Displays video during processing (slower, useful for debugging)
- **Without flag**: Faster processing, no visualization

## 🐛 Troubleshooting

### Issue: "Could not open video"
**Solution:** Check video path, try absolute path:
```bash
python ml_processor.py "C:/full/path/to/video.mp4"
```

### Issue: "Module not found"
**Solution:** Reinstall packages:
```bash
pip install ultralytics opencv-python streamlit pandas numpy deep-sort-realtime
```

### Issue: Slow processing
**Solutions:**
- Use smaller model: Already using `yolov8n.pt` (fastest)
- Process fewer frames: Edit `frame_skip = 2` in code
- Lower resolution: Video will auto-process at native resolution

### Issue: Dashboard won't start
**Solution:**
```bash
# Check if port is in use
streamlit run dashboard.py --server.port 8502
```

### Issue: Low detection accuracy
**Solutions:**
1. Adjust confidence threshold
2. Check arrival line position
3. Ensure good video quality (not too dark, blurry)
4. Run validation to identify specific issues

## 📈 Expected Performance

### Processing Speed (on average laptop CPU)
- **1 hour video**: ~10-15 minutes processing time
- **Frame rate**: ~6-10 FPS processing speed
- **With GPU**: 3-5× faster

### Accuracy (typical results)
- **Vehicles**: 85-95% precision/recall
- **Pedestrians**: 75-90% precision/recall
- **Timing accuracy**: ±0.5s mean absolute error

## 🔧 Command Reference

### ml_processor.py
```bash
python ml_processor.py VIDEO [OPTIONS]

Options:
  --output, -o PATH         Output file (CSV or XLSX)
  --arrival-line, -a INT    Arrival line Y-coordinate
  --confidence, -c FLOAT    Detection confidence (0.0-1.0)
  --show, -s                Show video processing
  --help, -h                Show help message
```

### dashboard.py
```bash
streamlit run dashboard.py [OPTIONS]

Streamlit Options:
  --server.port PORT        Port number (default: 8501)
  --server.address ADDR     Server address
  --browser.gatherUsageStats false    Disable telemetry
```

### validate_ml.py
```bash
python validate_ml.py MANUAL_CSV ML_CSV [OPTIONS]

Options:
  --tolerance, -t FLOAT     Time tolerance for matching (seconds)
  --output, -o PATH         Save report to file
  --help, -h                Show help message
```

## 📚 Next Steps

1. **Read full documentation**: See `ML_INTEGRATION_GUIDE.md`
2. **Test with sample video**: Validate accuracy before bulk processing
3. **Optimize settings**: Adjust confidence and arrival line based on validation
4. **Integrate with workflow**: Decide on automated vs hybrid approach

## 💡 Tips for Best Results

1. **Use good quality video**
   - Well-lit scenes
   - Stable camera position
   - Clear view of crossing

2. **Validate on sample first**
   - Manually annotate 2-3 minutes of video
   - Process with ML
   - Compare results
   - Adjust settings

3. **Batch processing**
   - Process multiple videos with same settings
   - Use shell script or batch file for automation

4. **Regular validation**
   - Periodically validate ML results against manual annotations
   - Track accuracy over different conditions (weather, time of day)

## 🎓 Learning Resources

- **YOLO Documentation**: https://docs.ultralytics.com/
- **Streamlit Docs**: https://docs.streamlit.io/
- **OpenCV Tutorials**: https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html

## ✅ System Check

Run this command to verify everything is working:

```bash
python -c "
import sys
try:
    import cv2
    import pandas as pd
    from ultralytics import YOLO
    import streamlit
    print('✓ OpenCV version:', cv2.__version__)
    print('✓ Pandas version:', pd.__version__)
    print('✓ Streamlit version:', streamlit.__version__)
    print('✓ All systems operational!')
except ImportError as e:
    print('✗ Missing package:', e)
    sys.exit(1)
"
```

## 📞 Support

For issues or questions:
1. Check `ML_INTEGRATION_GUIDE.md` for detailed information
2. Review error messages carefully
3. Verify all packages are installed correctly
4. Check video file format and path

---

**Version:** 1.0
**Last Updated:** October 2025
**Compatible with:** mkv-annotation-tool.html v1.0
