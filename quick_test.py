"""Quick test of ML processor on first 30 seconds of video"""

import cv2
import sys
sys.path.insert(0, '.')
from ml_processor import TrafficAnalyzer

print("="*70)
print("QUICK TEST - Processing first 30 seconds only")
print("="*70)

video_path = "2025-10-20 08-50-33.mkv"

# Create temporary short video (first 30 seconds)
print("\n1. Creating 30-second test clip...")
cap = cv2.VideoCapture(video_path)
fps = cap.get(cv2.CAP_PROP_FPS)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('test_30sec.mp4', fourcc, fps,
                     (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                      int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

frame_count = 0
max_frames = int(30 * fps)  # 30 seconds

while frame_count < max_frames:
    ret, frame = cap.read()
    if not ret:
        break
    out.write(frame)
    frame_count += 1
    if frame_count % 300 == 0:
        print(f"  Extracted {frame_count}/{max_frames} frames...")

cap.release()
out.release()
print(f"  ✓ Created test_30sec.mp4 ({frame_count} frames)\n")

# Process the short video
print("2. Running ML detection on 30-second clip...")
analyzer = TrafficAnalyzer('test_30sec.mp4', confidence=0.35, show_video=False)
results = analyzer.process_video()

# Export results
print("\n3. Exporting results...")
analyzer.export_csv('test_results_30sec.csv')

print("\n" + "="*70)
print("✓ QUICK TEST COMPLETE!")
print("="*70)
print(f"\nResults saved to: test_results_30sec.csv")
print(f"Total detections: {len(results)}")
print("\nTo process the full 6.9-hour video, use:")
print("  python ml_processor.py \"2025-10-20 08-50-33.mkv\"")
print("  (This will take several hours on CPU)")
