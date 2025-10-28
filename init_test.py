"""
Simple initialization test - just loads components, no video processing
"""
import time

print("="*70)
print("INITIALIZATION TEST - Testing ML System Startup")
print("="*70)

# Step 1: Import basic packages
print("\n[1/5] Importing basic packages...")
start = time.time()
import cv2
import pandas as pd
import numpy as np
print(f"    [OK] Basic packages loaded ({time.time()-start:.1f}s)")

# Step 2: Import YOLO
print("\n[2/5] Importing YOLO (ultralytics)...")
start = time.time()
from ultralytics import YOLO
print(f"    [OK] YOLO imported ({time.time()-start:.1f}s)")

# Step 3: Load YOLO model
print("\n[3/5] Loading YOLO model...")
start = time.time()
model = YOLO('yolov8n.pt')
print(f"    [OK] YOLO model loaded ({time.time()-start:.1f}s)")

# Step 4: Import DeepSORT
print("\n[4/5] Importing DeepSORT...")
start = time.time()
from deep_sort_realtime.deepsort_tracker import DeepSort
print(f"    [OK] DeepSORT imported ({time.time()-start:.1f}s)")

# Step 5: Initialize DeepSORT
print("\n[5/5] Initializing DeepSORT tracker...")
start = time.time()
tracker = DeepSort(max_age=30, n_init=3)
print(f"    [OK] DeepSORT initialized ({time.time()-start:.1f}s)")

print("\n" + "="*70)
print("[SUCCESS] ALL COMPONENTS INITIALIZED SUCCESSFULLY!")
print("="*70)
print("\nSystem is ready to process video.")
print("Time to initialize: Check times above")
print("\nTo process a video:")
print("  python ml_processor.py video.mp4")
