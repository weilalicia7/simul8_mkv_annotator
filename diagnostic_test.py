"""
Diagnostic test - Step by step initialization of ml_processor
"""
import time
import sys

print("="*70)
print("DIAGNOSTIC TEST - Finding the bottleneck")
print("="*70)

# Step 1: Import basic packages
print("\n[1/6] Importing basic packages...")
start = time.time()
import cv2
import pandas as pd
import numpy as np
print(f"    [OK] Basic packages loaded ({time.time()-start:.1f}s)")

# Step 2: Import YOLO
print("\n[2/6] Importing YOLO...")
start = time.time()
from ultralytics import YOLO
print(f"    [OK] YOLO imported ({time.time()-start:.1f}s)")

# Step 3: Load YOLO model
print("\n[3/6] Loading YOLO model...")
start = time.time()
model = YOLO('yolov8n.pt')
print(f"    [OK] YOLO model loaded ({time.time()-start:.1f}s)")

# Step 4: Import DeepSORT
print("\n[4/6] Importing DeepSORT...")
start = time.time()
from deep_sort_realtime.deepsort_tracker import DeepSort
print(f"    [OK] DeepSORT imported ({time.time()-start:.1f}s)")

# Step 5: Initialize DeepSORT
print("\n[5/6] Initializing DeepSORT tracker...")
start = time.time()
tracker = DeepSort(max_age=30, n_init=3)
print(f"    [OK] DeepSORT initialized ({time.time()-start:.1f}s)")

# Step 6: Open video file
print("\n[6/6] Opening video file...")
start = time.time()
cap = cv2.VideoCapture('test_30sec.mp4')
if not cap.isOpened():
    print("    [ERROR] Could not open video file")
    sys.exit(1)
fps = cap.get(cv2.CAP_PROP_FPS)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
print(f"    [OK] Video opened ({time.time()-start:.1f}s)")
print(f"    Video: {total_frames} frames at {fps:.1f} FPS")

# Step 7: Read first frame
print("\n[7/7] Reading first frame...")
start = time.time()
ret, frame = cap.read()
if not ret:
    print("    [ERROR] Could not read first frame")
    sys.exit(1)
print(f"    [OK] First frame read ({time.time()-start:.1f}s)")
print(f"    Frame shape: {frame.shape}")

# Step 8: Run YOLO on first frame
print("\n[8/8] Running YOLO detection on first frame...")
start = time.time()
results = model(frame, verbose=False, conf=0.35)
print(f"    [OK] YOLO detection complete ({time.time()-start:.1f}s)")
detections = results[0].boxes
print(f"    Detected {len(detections)} objects in first frame")

cap.release()

print("\n" + "="*70)
print("[SUCCESS] All diagnostic steps completed!")
print("="*70)
print("\nIf all steps completed quickly, the bottleneck is in the")
print("main processing loop, not initialization.")
