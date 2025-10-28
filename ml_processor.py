"""
ML Traffic Analyzer - Automated Vehicle and Pedestrian Detection
Processes video files to detect and track vehicles and pedestrians
Compatible with manual annotation tool output format
"""

import cv2
import pandas as pd
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np
import argparse
from pathlib import Path
import sys


class PedestrianAnalyzer:
    """Analyzes pedestrian behavior to classify as Crosser or Poser"""

    def __init__(self):
        self.pedestrians = {}

    def update(self, track_id, bbox, timestamp):
        """Update pedestrian tracking data"""
        center_x = (bbox[0] + bbox[2]) / 2
        center_y = (bbox[1] + bbox[3]) / 2

        if track_id not in self.pedestrians:
            self.pedestrians[track_id] = {
                'start_time': timestamp,
                'positions': [(center_x, center_y)],
                'first_bbox': bbox
            }
        else:
            self.pedestrians[track_id]['positions'].append((center_x, center_y))

    def classify(self, track_id, timestamp):
        """Classify pedestrian as Crosser or Poser"""
        if track_id not in self.pedestrians:
            return "Crossers"

        data = self.pedestrians[track_id]
        duration = timestamp - data['start_time']

        # Calculate movement variance
        if len(data['positions']) > 1:
            x_positions = [p[0] for p in data['positions']]
            movement_variance = np.var(x_positions)
        else:
            movement_variance = 0

        # Decision logic: long duration + low movement = Poser
        if duration > 8.0 and movement_variance < 100:
            return "Posers"
        else:
            return "Crossers"

    def get_service_time(self, track_id, timestamp):
        """Calculate how long pedestrian occupied crossing"""
        if track_id not in self.pedestrians:
            return None
        return round(timestamp - self.pedestrians[track_id]['start_time'], 1)


class ArrivalDetector:
    """Detects when entities cross the arrival line"""

    def __init__(self, arrival_line_y=400):
        self.arrival_line = arrival_line_y
        self.recorded_arrivals = set()
        self.last_positions = {}

    def check_arrival(self, track_id, bbox, timestamp):
        """
        Detect if entity crossed arrival line
        Returns: (crossed, timestamp) or (False, None)
        """
        bottom_y = bbox[3]

        # Check if already recorded
        if track_id in self.recorded_arrivals:
            return False, None

        # Check previous position
        if track_id in self.last_positions:
            prev_y = self.last_positions[track_id]

            # Crossed line from top to bottom
            if prev_y < self.arrival_line <= bottom_y:
                self.recorded_arrivals.add(track_id)
                return True, timestamp

        # Update position
        self.last_positions[track_id] = bottom_y
        return False, None

    def reset(self):
        """Reset detector for new video"""
        self.recorded_arrivals.clear()
        self.last_positions.clear()


class TrafficAnalyzer:
    """Main analyzer class for processing videos"""

    def __init__(self, video_path, arrival_line_y=None, confidence=0.35, show_video=False):
        self.video_path = video_path
        self.show_video = show_video

        # Initialize ML models
        print("Loading YOLO model...")
        self.model = YOLO('yolov8n.pt')
        self.tracker = DeepSort(max_age=30, n_init=3)

        # Data storage
        self.arrivals = []
        self.last_arrival_times = {
            'EB Vehicles': None,
            'WB Vehicles': None,
            'Crossers': None,
            'Posers': None
        }

        # Tracking state
        self.prev_positions = {}
        self.pedestrian_analyzer = PedestrianAnalyzer()

        # Video properties
        self.cap = cv2.VideoCapture(str(video_path))
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")

        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_count = 0
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Auto-calculate arrival line if not specified (middle of frame)
        if arrival_line_y is None:
            arrival_line_y = self.frame_height // 2

        self.arrival_detector = ArrivalDetector(arrival_line_y=arrival_line_y)
        self.confidence_threshold = confidence

        print(f"Video loaded: {self.frame_width}x{self.frame_height} @ {self.fps:.1f} FPS")
        print(f"Total frames: {self.total_frames}")
        print(f"Arrival line at Y={arrival_line_y}")

    def process_video(self):
        """Process entire video and extract arrival data"""
        print("\nStarting video processing...")
        print("Press 'q' to stop early (if show_video=True)\n")

        try:
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break

                self.frame_count += 1
                timestamp = self.frame_count / self.fps

                # Run YOLO detection
                results = self.model(frame, verbose=False, conf=self.confidence_threshold)

                # Prepare detections for tracker
                detections = []
                for box in results[0].boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    class_id = int(box.cls[0])

                    # Filter: only vehicles (2,3,5,7) and persons (0)
                    if class_id in [0, 2, 3, 5, 7]:
                        detections.append(([x1, y1, x2-x1, y2-y1], conf, class_id))

                # Update tracker
                tracks = self.tracker.update_tracks(detections, frame=frame)

                # Process each track
                for track in tracks:
                    if not track.is_confirmed():
                        continue

                    track_id = track.track_id
                    bbox = track.to_ltrb()
                    class_id = track.get_det_class()

                    # Update pedestrian analyzer for persons
                    if class_id == 0:
                        self.pedestrian_analyzer.update(track_id, bbox, timestamp)

                    # Check for arrival
                    crossed, arrival_time = self.arrival_detector.check_arrival(
                        track_id, bbox, timestamp
                    )

                    if crossed:
                        self.record_arrival(track_id, class_id, bbox, arrival_time)

                # Optional: Display video with detections
                if self.show_video:
                    display_frame = self.draw_detections(frame, tracks, timestamp)
                    cv2.imshow('ML Traffic Analyzer', display_frame)

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("\nStopped by user")
                        break

                # Progress indicator
                if self.frame_count % 100 == 0:
                    progress = (self.frame_count / self.total_frames) * 100
                    print(f"Progress: {progress:.1f}% ({self.frame_count}/{self.total_frames} frames) - "
                          f"Detected: {len(self.arrivals)} arrivals")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")

        finally:
            self.cap.release()
            if self.show_video:
                cv2.destroyAllWindows()

        print(f"\n✓ Processing complete!")
        print(f"Total arrivals detected: {len(self.arrivals)}")
        self.print_summary()

        return self.get_dataframe()

    def record_arrival(self, track_id, class_id, bbox, timestamp):
        """Record arrival event"""
        # Determine entity type
        if class_id in [2, 3, 5, 7]:  # Vehicle
            direction = self.classify_vehicle_direction(track_id, bbox)
            entity_type = f"{direction} Vehicles"
            type_dir = direction
            service_time = "-"
        elif class_id == 0:  # Pedestrian
            # Classify behavior
            behavior = self.pedestrian_analyzer.classify(track_id, timestamp)
            entity_type = behavior
            type_dir = behavior[:-1]  # Remove 's' (Crosser/Poser)

            # Service time will be calculated when they leave
            # For now, estimate based on average (will update later)
            service_time = "-"
        else:
            return  # Ignore other classes

        # Calculate inter-arrival time
        last_time = self.last_arrival_times.get(entity_type)
        if last_time is not None:
            inter_arrival = timestamp - last_time
        else:
            inter_arrival = 0.0

        self.last_arrival_times[entity_type] = timestamp

        # Store arrival
        arrival_data = {
            'ID': len(self.arrivals) + 1,
            'Time (s)': round(timestamp, 1),
            'Entity': entity_type,
            'Type/Dir': type_dir,
            'Inter-Arrival (s)': round(inter_arrival, 1),
            'Service Time (s)': service_time
        }

        self.arrivals.append(arrival_data)

    def classify_vehicle_direction(self, track_id, bbox):
        """Classify vehicle as EB or WB based on movement"""
        center_x = (bbox[0] + bbox[2]) / 2

        if track_id in self.prev_positions:
            prev_x = self.prev_positions[track_id]
            # Moving right = EB, moving left = WB
            direction = "EB" if center_x > prev_x else "WB"
        else:
            # First detection: use position (left side = WB, right side = EB)
            direction = "EB" if center_x > self.frame_width / 2 else "WB"

        self.prev_positions[track_id] = center_x
        return direction

    def draw_detections(self, frame, tracks, timestamp):
        """Draw bounding boxes and arrival line on frame"""
        display_frame = frame.copy()

        # Draw arrival line
        cv2.line(display_frame, (0, self.arrival_detector.arrival_line),
                (self.frame_width, self.arrival_detector.arrival_line),
                (0, 255, 0), 2)
        cv2.putText(display_frame, "ARRIVAL LINE", (10, self.arrival_detector.arrival_line - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # Draw tracks
        for track in tracks:
            if not track.is_confirmed():
                continue

            track_id = track.track_id
            bbox = track.to_ltrb()
            class_id = track.get_det_class()

            # Color based on class
            if class_id == 0:  # Person
                color = (255, 0, 0)  # Blue
                label = f"Person #{track_id}"
            else:  # Vehicle
                color = (0, 0, 255)  # Red
                label = f"Vehicle #{track_id}"

            # Draw box
            x1, y1, x2, y2 = map(int, bbox)
            cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(display_frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Draw info
        info_text = f"Frame: {self.frame_count} | Time: {timestamp:.1f}s | Arrivals: {len(self.arrivals)}"
        cv2.putText(display_frame, info_text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return display_frame

    def get_dataframe(self):
        """Convert arrivals to pandas DataFrame"""
        if not self.arrivals:
            print("\nWarning: No arrivals detected!")
            return pd.DataFrame(columns=['ID', 'Time (s)', 'Entity', 'Type/Dir',
                                        'Inter-Arrival (s)', 'Service Time (s)'])

        df = pd.DataFrame(self.arrivals)
        return df

    def print_summary(self):
        """Print summary statistics"""
        if not self.arrivals:
            return

        df = self.get_dataframe()
        print("\n" + "="*50)
        print("SUMMARY STATISTICS")
        print("="*50)

        entity_counts = df['Entity'].value_counts()
        for entity, count in entity_counts.items():
            percentage = (count / len(df)) * 100
            print(f"{entity:20s}: {count:4d} ({percentage:5.1f}%)")

        print("="*50)

    def export_csv(self, output_path):
        """Export results to CSV"""
        df = self.get_dataframe()
        df.to_csv(output_path, index=False)
        print(f"\n✓ Results exported to: {output_path}")

    def export_excel(self, output_path):
        """Export results to Excel"""
        df = self.get_dataframe()
        df.to_excel(output_path, index=False, engine='openpyxl')
        print(f"\n✓ Results exported to: {output_path}")


def main():
    """Main function with command-line interface"""
    parser = argparse.ArgumentParser(
        description='ML Traffic Analyzer - Automated vehicle and pedestrian detection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python ml_processor.py video.mp4

  # Specify output filename
  python ml_processor.py video.mp4 --output results.csv

  # Show live video processing
  python ml_processor.py video.mp4 --show

  # Adjust arrival line position
  python ml_processor.py video.mp4 --arrival-line 500

  # Export to Excel
  python ml_processor.py video.mp4 --output results.xlsx
        """
    )

    parser.add_argument('video', type=str, help='Path to video file')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='Output file path (CSV or XLSX)')
    parser.add_argument('--arrival-line', '-a', type=int, default=None,
                       help='Y-coordinate of arrival line (default: middle of frame)')
    parser.add_argument('--confidence', '-c', type=float, default=0.35,
                       help='Detection confidence threshold (0.0-1.0, default: 0.35)')
    parser.add_argument('--show', '-s', action='store_true',
                       help='Show video processing in real-time')

    args = parser.parse_args()

    # Validate video file
    video_path = Path(args.video)
    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}")
        sys.exit(1)

    # Determine output path
    if args.output is None:
        output_path = video_path.stem + "_ml_results.csv"
    else:
        output_path = args.output

    output_path = Path(output_path)

    try:
        # Initialize analyzer
        analyzer = TrafficAnalyzer(
            video_path,
            arrival_line_y=args.arrival_line,
            confidence=args.confidence,
            show_video=args.show
        )

        # Process video
        results_df = analyzer.process_video()

        # Export results
        if output_path.suffix.lower() in ['.xlsx', '.xls']:
            analyzer.export_excel(output_path)
        else:
            analyzer.export_csv(output_path)

        print(f"\n✓ Analysis complete! Results saved to: {output_path.absolute()}")

    except Exception as e:
        print(f"\nError during processing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
