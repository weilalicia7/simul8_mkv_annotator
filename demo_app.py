import streamlit as st
import pandas as pd
import cv2
import os
from pathlib import Path

st.set_page_config(page_title="ML Traffic Monitor Demo", layout="wide")

st.title("🚗 ML Traffic Monitoring System - Live Demo")
st.markdown("---")

# Sidebar
st.sidebar.header("About")
st.sidebar.info("""
This demo shows the ML-based traffic monitoring system
using YOLOv8 + DeepSORT for automated vehicle and
pedestrian detection at Abbey Road crossing.
""")

st.sidebar.header("System Specs")
st.sidebar.markdown("""
- **Model:** YOLOv8n (pre-trained)
- **Tracker:** DeepSORT
- **Detection:** Person, Car, Bus, Truck, Motorcycle
- **Classification:** Direction + Behavior
""")

# Main content - Two columns
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📹 Input Video Frames")

    # Display video frames as images (more reliable than video playback)
    video_path = "test_30sec.mp4"

    if os.path.exists("frame_first.jpg"):
        st.image("frame_first.jpg", caption="Frame 28 - Sample from video (blurred for privacy)", width='stretch')

        with st.expander("View more frames"):
            col_a, col_b = st.columns(2)
            with col_a:
                if os.path.exists("frame_middle.jpg"):
                    st.image("frame_middle.jpg", caption="Frame 900 - Middle (blurred)", width='stretch')
            with col_b:
                if os.path.exists("frame_last.jpg"):
                    st.image("frame_last.jpg", caption="Frame 1800 - End (blurred)", width='stretch')

        st.caption("30-second test clip from Abbey Road crossing (content blurred for ethical reasons)")

        # Download button for blurred video
        blurred_video_path = "test_30sec_blurred.mp4"
        if os.path.exists(blurred_video_path):
            with open(blurred_video_path, 'rb') as f:
                st.download_button(
                    label="📥 Download Blurred Video",
                    data=f,
                    file_name="test_30sec_blurred.mp4",
                    mime="video/mp4"
                )
    else:
        st.warning("Video frames not found. Run extract_frames.py first.")

    st.markdown("### Video Details")
    if os.path.exists(video_path):
        video = cv2.VideoCapture(video_path)
        fps = video.get(cv2.CAP_PROP_FPS)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps
        video.release()

        st.metric("Resolution", f"{width}×{height}")
        st.metric("Frame Rate", f"{fps} FPS")
        st.metric("Duration", f"{duration:.1f} seconds")
        st.metric("Total Frames", f"{frame_count:,}")

with col2:
    st.header("📊 ML Detection Results")

    # Load results
    results_path = "test_results_30sec.csv"
    if os.path.exists(results_path):
        df = pd.read_csv(results_path)

        st.markdown("### Summary Statistics")
        col_a, col_b, col_c = st.columns(3)

        total_arrivals = len(df)
        eb_vehicles = len(df[df['Entity'] == 'EB Vehicles'])
        wb_vehicles = len(df[df['Entity'] == 'WB Vehicles'])
        crossers = len(df[df['Entity'] == 'Crossers'])
        posers = len(df[df['Entity'] == 'Posers'])

        col_a.metric("Total Arrivals", total_arrivals,
                     delta=None, delta_color="off")
        col_b.metric("EB Vehicles", eb_vehicles,
                     delta=None, delta_color="off")
        col_c.metric("Crossers", crossers,
                     delta=None, delta_color="off")

        st.markdown("### Detection Timeline")
        st.dataframe(df, width='stretch', height=300)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Results CSV",
            data=csv,
            file_name="ml_results.csv",
            mime="text/csv"
        )

    else:
        st.warning("Results file not found. Run ML processor first:")
        st.code("python -u ml_processor.py test_30sec.mp4 --output test_results_30sec.csv")

st.markdown("---")

# Technical Details
with st.expander("🔬 Technical Details"):
    st.markdown("""
    ### Detection Pipeline

    1. **Object Detection (YOLOv8n)**
       - Confidence threshold: 0.35
       - Detects: person, car, motorcycle, bus, truck
       - Processing: Frame-by-frame analysis

    2. **Object Tracking (DeepSORT)**
       - Tracks each detected object across frames
       - Assigns unique ID to each entity
       - Maintains tracking through brief occlusions

    3. **Classification Logic**
       - **Vehicles:** Direction based on X-position (X<640=EB, X≥640=WB)
       - **Pedestrians:** Behavior based on duration + movement variance
         - Crosser: Active movement (duration ≤8s OR variance ≥100px²)
         - Poser: Stationary (duration >8s AND variance <100px²)

    4. **Arrival Detection**
       - Virtual line at Y=360 pixels
       - Entity counted when first crossing line
       - Inter-arrival time calculated for same entity type

    ### Performance Metrics

    **Test Results (30-second clip):**
    - Processing time: ~20 minutes (CPU)
    - Processing speed: 1.5 FPS
    - Detections: 8 arrivals
    - Accuracy: Verified against manual count

    **GPU Performance (RTX 4060):**
    - Expected speed: 25-40 FPS
    - 30-second clip: 30-90 seconds
    - 6.9-hour video: 1-3 hours
    """)

with st.expander("📖 How to Use This System"):
    st.markdown("""
    ### For GPU Users

    1. **Clone repository:**
       ```bash
       git clone https://github.com/weilalicia7/simul8_mkv_annotator.git
       cd simul8_mkv_annotator
       ```

    2. **Install dependencies:**
       ```bash
       pip install -r requirements.txt
       ```

    3. **Process video:**
       ```bash
       python -u ml_processor.py "your_video.mp4" --output results.csv
       ```

    4. **View results:**
       - CSV file contains all detections
       - Use dashboard.py for interactive visualization
       - Use validate_ml.py to verify format

    ### Documentation

    - **GPU_PROCESSING_GUIDE.md** - Complete setup instructions
    - **BOUNDARIES_EXPLANATION.md** - Detection parameters explained
    - **INITIALIZATION_TROUBLESHOOTING.md** - Solving common issues
    - **TRAINING_GUIDE.md** - Custom training (if needed)

    Repository: https://github.com/weilalicia7/simul8_mkv_annotator
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>ML Traffic Monitoring System | YOLOv8 + DeepSORT</p>
    <p>Cardiff University | October 2025</p>
</div>
""", unsafe_allow_html=True)
