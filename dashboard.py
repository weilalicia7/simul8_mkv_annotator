"""
Abbey Road Live Traffic Monitor Dashboard
Interactive Streamlit dashboard for visualizing ML detection results
"""

import streamlit as st
import pandas as pd
import cv2
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import time
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="Abbey Road Live Monitor",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        font-size: 48px !important;
        font-weight: bold !important;
        color: #C8102E !important;
    }
    .status-running {
        color: #00ff00;
        font-weight: bold;
    }
    .status-stopped {
        color: #ff0000;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'model' not in st.session_state:
    st.session_state.model = None
    st.session_state.tracker = None
    st.session_state.arrivals = []
    st.session_state.stats = {
        'EB Vehicles': 0,
        'WB Vehicles': 0,
        'Crossers': 0,
        'Posers': 0
    }
    st.session_state.processing = False
    st.session_state.frame_count = 0
    st.session_state.arrival_times = []
    st.session_state.prev_positions = {}


def load_models():
    """Load ML models (cached)"""
    if st.session_state.model is None:
        with st.spinner("Loading YOLO model..."):
            st.session_state.model = YOLO('yolov8n.pt')
            st.session_state.tracker = DeepSort(max_age=30, n_init=3)
        st.success("✓ Models loaded successfully!")


def process_frame(frame, arrival_line_y, confidence):
    """Process single frame and return annotated frame"""
    results = st.session_state.model(frame, verbose=False, conf=confidence)

    # Draw detections
    annotated_frame = frame.copy()

    # Draw arrival line
    cv2.line(annotated_frame, (0, arrival_line_y), (frame.shape[1], arrival_line_y),
            (0, 255, 0), 3)
    cv2.putText(annotated_frame, "ARRIVAL LINE", (10, arrival_line_y - 10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Prepare detections for tracker
    detections = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        class_id = int(box.cls[0])

        # Draw bounding box
        if class_id == 0:  # Person
            color = (255, 0, 0)  # Blue
            label = f"Person {conf:.2f}"
        elif class_id in [2, 3, 5, 7]:  # Vehicle
            color = (0, 0, 255)  # Red
            label = f"Vehicle {conf:.2f}"
        else:
            continue

        cv2.rectangle(annotated_frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(annotated_frame, label, (int(x1), int(y1) - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Add to detections for tracking
        if class_id in [0, 2, 3, 5, 7]:
            detections.append(([x1, y1, x2-x1, y2-y1], conf, class_id))

    # Update tracker
    if st.session_state.tracker is not None:
        tracks = st.session_state.tracker.update_tracks(detections, frame=frame)

        # Draw track IDs
        for track in tracks:
            if track.is_confirmed():
                track_id = track.track_id
                bbox = track.to_ltrb()
                x1, y1, x2, y2 = map(int, bbox)

                cv2.putText(annotated_frame, f"ID: {track_id}", (x1, y2 + 20),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    # Draw stats on frame
    stats_text = f"Detections: {len(detections)} | Total Arrivals: {len(st.session_state.arrivals)}"
    cv2.putText(annotated_frame, stats_text, (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    return annotated_frame


def create_entity_chart():
    """Create bar chart of entity counts"""
    if not st.session_state.arrivals:
        # Empty chart
        fig = go.Figure()
        fig.add_trace(go.Bar(x=['EB Vehicles', 'WB Vehicles', 'Crossers', 'Posers'],
                            y=[0, 0, 0, 0]))
        fig.update_layout(height=300, title="Entity Distribution", showlegend=False)
        return fig

    df = pd.DataFrame(st.session_state.arrivals)
    entity_counts = df['Entity'].value_counts()

    colors = ['#C8102E', '#0033A0', '#FFD700', '#228B22']  # Red, Blue, Gold, Green

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=entity_counts.index,
        y=entity_counts.values,
        marker_color=colors[:len(entity_counts)],
        text=entity_counts.values,
        textposition='outside'
    ))

    fig.update_layout(
        height=300,
        title="Entity Distribution",
        xaxis_title="Entity Type",
        yaxis_title="Count",
        showlegend=False
    )

    return fig


def create_timeline_chart():
    """Create timeline chart of arrivals"""
    if not st.session_state.arrivals:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[], y=[]))
        fig.update_layout(height=300, title="Arrival Timeline")
        return fig

    df = pd.DataFrame(st.session_state.arrivals)

    # Create cumulative count by entity type
    fig = go.Figure()

    for entity in df['Entity'].unique():
        entity_data = df[df['Entity'] == entity].sort_values('Time (s)')
        cumulative = list(range(1, len(entity_data) + 1))

        fig.add_trace(go.Scatter(
            x=entity_data['Time (s)'],
            y=cumulative,
            mode='lines+markers',
            name=entity,
            line=dict(width=2)
        ))

    fig.update_layout(
        height=300,
        title="Cumulative Arrivals Over Time",
        xaxis_title="Time (seconds)",
        yaxis_title="Cumulative Count",
        hovermode='x unified'
    )

    return fig


# ============================================================================
# MAIN DASHBOARD LAYOUT
# ============================================================================

# Title and status
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🚦 Abbey Road Live Traffic Monitor")
with col2:
    if st.session_state.processing:
        st.markdown('<p class="status-running">● PROCESSING</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p class="status-stopped">● STOPPED</p>', unsafe_allow_html=True)

st.markdown("---")

# Sidebar - Configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # File uploader
    uploaded_file = st.file_uploader("Upload Video", type=['mp4', 'avi', 'mov', 'mkv'])

    # Detection settings
    st.subheader("Detection Settings")
    confidence = st.slider("Confidence Threshold", 0.1, 1.0, 0.35, 0.05)
    arrival_line_y = st.slider("Arrival Line Y-Position", 100, 800, 400, 10)

    # Processing controls
    st.subheader("Controls")
    start_btn = st.button("▶️ Start Processing", disabled=uploaded_file is None)
    stop_btn = st.button("⏹️ Stop")
    clear_btn = st.button("🗑️ Clear Data")

    if clear_btn:
        st.session_state.arrivals = []
        st.session_state.stats = {'EB Vehicles': 0, 'WB Vehicles': 0, 'Crossers': 0, 'Posers': 0}
        st.session_state.frame_count = 0
        st.rerun()

    # Export section
    st.subheader("📥 Export Data")
    if st.session_state.arrivals:
        df = pd.DataFrame(st.session_state.arrivals)

        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            "Download CSV",
            csv,
            f"ml_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "text/csv",
            key='download-csv'
        )

        # Excel export
        from io import BytesIO
        buffer = BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        excel_data = buffer.getvalue()

        st.download_button(
            "Download Excel",
            excel_data,
            f"ml_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key='download-excel'
        )

# Main content area
# Top metrics
metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
with metric_col1:
    st.metric("Total Arrivals", len(st.session_state.arrivals))
with metric_col2:
    st.metric("EB Vehicles", st.session_state.stats['EB Vehicles'])
with metric_col3:
    st.metric("WB Vehicles", st.session_state.stats['WB Vehicles'])
with metric_col4:
    st.metric("Crossers", st.session_state.stats['Crossers'])
with metric_col5:
    st.metric("Posers", st.session_state.stats['Posers'])

st.markdown("---")

# Video and charts
video_col, chart_col = st.columns([3, 2])

with video_col:
    st.subheader("📹 Live Feed")
    video_placeholder = st.empty()

with chart_col:
    st.subheader("📊 Statistics")
    chart_placeholder = st.empty()

st.markdown("---")

# Timeline chart
st.subheader("📈 Arrival Timeline")
timeline_placeholder = st.empty()

st.markdown("---")

# Data table
st.subheader("📋 Recent Arrivals")
table_col1, table_col2 = st.columns([3, 1])
with table_col2:
    show_count = st.selectbox("Show last N entries", [10, 25, 50, 100], index=0)

table_placeholder = st.empty()

# Progress bar
progress_bar = st.empty()
status_text = st.empty()

# ============================================================================
# PROCESSING LOGIC
# ============================================================================

if start_btn and uploaded_file is not None:
    # Load models
    load_models()

    # Save uploaded file temporarily
    temp_path = Path("temp_video.mp4")
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.read())

    # Open video
    cap = cv2.VideoCapture(str(temp_path))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    st.session_state.processing = True
    st.session_state.frame_count = 0

    frame_skip = 2  # Process every 2nd frame for speed

    try:
        while st.session_state.processing:
            ret, frame = cap.read()
            if not ret:
                st.session_state.processing = False
                break

            st.session_state.frame_count += 1

            # Skip frames for speed
            if st.session_state.frame_count % frame_skip != 0:
                continue

            timestamp = st.session_state.frame_count / fps

            # Process frame
            annotated_frame = process_frame(frame, arrival_line_y, confidence)

            # Convert BGR to RGB for display
            frame_rgb = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

            # Update video display
            video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)

            # Update charts (every 10 frames)
            if st.session_state.frame_count % 10 == 0:
                chart_placeholder.plotly_chart(create_entity_chart(), use_container_width=True)
                timeline_placeholder.plotly_chart(create_timeline_chart(), use_container_width=True)

            # Update data table
            if st.session_state.arrivals:
                df = pd.DataFrame(st.session_state.arrivals)
                recent_df = df.tail(show_count).iloc[::-1]  # Newest first
                table_placeholder.dataframe(recent_df, use_container_width=True)

            # Update progress
            progress = st.session_state.frame_count / total_frames
            progress_bar.progress(progress)
            status_text.text(f"Processing: {st.session_state.frame_count}/{total_frames} frames "
                           f"({progress*100:.1f}%) | Time: {timestamp:.1f}s")

            # Check stop button
            if stop_btn:
                st.session_state.processing = False
                break

            # Small delay for display
            time.sleep(0.01)

    except Exception as e:
        st.error(f"Error during processing: {e}")
        import traceback
        st.code(traceback.format_exc())

    finally:
        cap.release()
        st.session_state.processing = False
        status_text.text("✓ Processing complete!")

        # Cleanup
        if temp_path.exists():
            temp_path.unlink()

        st.rerun()

# Display current data even when not processing
if not st.session_state.processing:
    if st.session_state.arrivals:
        chart_placeholder.plotly_chart(create_entity_chart(), use_container_width=True)
        timeline_placeholder.plotly_chart(create_timeline_chart(), use_container_width=True)

        df = pd.DataFrame(st.session_state.arrivals)
        recent_df = df.tail(show_count).iloc[::-1]  # Newest first
        table_placeholder.dataframe(recent_df, use_container_width=True)
    else:
        video_placeholder.info("👆 Upload a video file and click 'Start Processing' to begin")
        chart_placeholder.info("No data yet. Start processing to see statistics.")
        timeline_placeholder.info("Timeline will appear after processing begins.")
        table_placeholder.info("Arrival data will be displayed here.")
