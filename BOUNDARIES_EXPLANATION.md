# Detection Boundaries and Parameters Explanation

## Overview

This document explains the spatial boundaries, classification thresholds, and detection parameters used in the ML-based traffic monitoring system. These parameters define how the system detects, tracks, and classifies vehicles and pedestrians at the Abbey Road crossing.

---

## 1. Spatial Boundaries

### 1.1 Frame Dimensions
- **Width**: 1280 pixels (0 to 1279)
- **Height**: 720 pixels (0 to 719)
- **Origin**: Top-left corner (0, 0)

### 1.2 Arrival Detection Line
**Location**: Y = 360 pixels (horizontal line at middle of frame)

**Purpose**: Detects when entities cross into the monitoring zone

**How it works**:
- System tracks each entity's Y-position (vertical location)
- When entity crosses Y=360 for the first time, it's counted as an "arrival"
- Only the first crossing is counted (prevents double-counting)

**Visual representation**:
```
Frame Top (Y=0)
|
|  (Objects detected here but not counted yet)
|
+------ ARRIVAL LINE (Y=360) ------
|
|  (Objects counted as "arrivals" after crossing this line)
|
Frame Bottom (Y=719)
```

---

## 2. Vehicle Classification

### 2.1 Direction Classification (Eastbound vs Westbound)

**Boundary**: X = 640 pixels (vertical line at center of frame)

**Classification rules**:
- **Eastbound (EB)**: X-position < 640 (left half of screen)
- **Westbound (WB)**: X-position ≥ 640 (right half of screen)

**Visual representation**:
```
       X=0                    X=640                   X=1279
        |                       |                        |
        |    EASTBOUND (EB)     |    WESTBOUND (WB)     |
        |    Vehicles           |    Vehicles           |
        |    [Left half]        |    [Right half]       |
```

**Detection process**:
1. System detects vehicle using YOLO (car, motorcycle, bus, truck)
2. Gets vehicle's center X-coordinate
3. Compares with X=640 boundary
4. Assigns direction based on which side of boundary

**Example**:
- Vehicle at X=450 → Eastbound (450 < 640)
- Vehicle at X=850 → Westbound (850 ≥ 640)

### 2.2 Vehicle Types Detected
- **Car** (COCO class 2)
- **Motorcycle** (COCO class 3)
- **Bus** (COCO class 5)
- **Truck** (COCO class 7)

All vehicle types are grouped together as "EB Vehicles" or "WB Vehicles" based on their direction.

---

## 3. Pedestrian Classification

### 3.1 Crosser vs Poser Classification

**Two criteria must be met for "Poser" classification**:

#### Criterion 1: Duration Threshold
- **Threshold**: 8 seconds
- **Logic**: Pedestrian visible for more than 8 seconds

#### Criterion 2: Movement Variance
- **Threshold**: 100 square pixels (px²)
- **Logic**: Low movement variance indicates stationary behavior
- **Calculation**: Statistical variance of X and Y positions over time

**Classification decision tree**:
```
Is pedestrian visible > 8 seconds?
├─ NO  → Crosser
└─ YES → Check movement variance
          ├─ Variance < 100 px² → Poser (stationary)
          └─ Variance ≥ 100 px² → Crosser (moving)
```

**Real-world interpretation**:
- **Crosser**: Person actively crossing the street (normal pedestrian behavior)
- **Poser**: Person standing still for photo/video (tourist behavior at Abbey Road)

### 3.2 Movement Variance Explained

**What it measures**: How much a person moves around while being tracked

**Low variance (< 100 px²)**:
- Person stays in roughly same position
- Small movements (shifting weight, slight repositions)
- Typical of someone posing for photo

**High variance (≥ 100 px²)**:
- Person moves significantly across frame
- Walking motion with position changes
- Typical of someone crossing street

**Example calculations**:
- Person at positions [(500,300), (502,305), (498,302)] → Variance ≈ 8 px² → Poser
- Person at positions [(400,300), (450,320), (520,350)] → Variance ≈ 2400 px² → Crosser

---

## 4. Detection Parameters

### 4.1 Confidence Threshold
- **Value**: 0.35 (35%)
- **Purpose**: Filter out uncertain detections
- **Effect**: Only objects detected with >35% confidence are processed

**Why 0.35?**
- Lower threshold → More detections, more false positives
- Higher threshold → Fewer false positives, might miss real objects
- 0.35 is balanced for outdoor traffic scenarios

### 4.2 Detection Classes
Only specific COCO dataset classes are monitored:
- **Class 0**: Person (pedestrians)
- **Class 2**: Car
- **Class 3**: Motorcycle
- **Class 5**: Bus
- **Class 7**: Truck

Other objects (bikes, animals, etc.) are ignored.

---

## 5. Inter-Arrival Time Calculation

**Definition**: Time elapsed between consecutive arrivals of the same entity type

**Calculation method**:
1. Record timestamp when entity crosses arrival line (Y=360)
2. When next entity of same type arrives, calculate difference
3. First arrival of each type has inter-arrival time = 0.0

**Example sequence**:
```
Time  Entity          Inter-Arrival Time
7.1s  EB Vehicle      0.0s (first EB vehicle)
9.8s  EB Vehicle      2.7s (9.8 - 7.1)
12.3s EB Vehicle      2.5s (12.3 - 9.8)
15.2s Crosser         0.0s (first Crosser)
21.3s Crosser         6.1s (21.3 - 15.2)
```

**Separate tracking**: Each entity type tracks inter-arrival times independently:
- EB Vehicles track their own sequence
- WB Vehicles track their own sequence
- Crossers track their own sequence
- Posers track their own sequence

---

## 6. Tracking Parameters

### 6.1 DeepSORT Configuration
- **Max age**: 30 frames (entity can be lost for 30 frames before deletion)
- **Min hits**: 3 (object must be detected 3 times before confirmed tracking)
- **IoU threshold**: 0.3 (minimum overlap for matching detections to tracks)

### 6.2 Why These Values?
- **Max age = 30**: Handles brief occlusions (1 second at 30 FPS)
- **Min hits = 3**: Reduces false positives from noise/reflections
- **IoU = 0.3**: Allows tracking objects even with partial overlap

---

## 7. Output Format

### 7.1 CSV Columns
Each arrival is recorded with the following information:

| Column | Description | Example |
|--------|-------------|---------|
| ID | Sequential arrival number | 1, 2, 3... |
| Time (s) | When entity crossed arrival line | 7.1 |
| Entity | Type of entity | "EB Vehicles" |
| Type/Dir | Specific classification | "EB" or "Crosser" |
| Inter-Arrival (s) | Time since last same-type arrival | 2.6 |
| Service Time (s) | Always "-" (not applicable) | - |

### 7.2 Entity Type Names
- **EB Vehicles** - Eastbound vehicles (cars, motorcycles, buses, trucks)
- **WB Vehicles** - Westbound vehicles (cars, motorcycles, buses, trucks)
- **Crossers** - Pedestrians actively crossing
- **Posers** - Pedestrians standing still (>8s, variance <100px²)

---

## 8. Common Scenarios

### Scenario 1: Fast-Moving Vehicle
```
Frame 100: Vehicle detected at X=200, Y=100 (above arrival line)
Frame 105: Vehicle at X=220, Y=250 (still above line)
Frame 110: Vehicle at X=240, Y=365 (CROSSED arrival line at Y=360)
           → COUNTED as arrival at time = 110/30 = 3.67s
           → Classification: X=240 < 640 → Eastbound
```

### Scenario 2: Pedestrian Crossing Quickly
```
Frames 50-80: Person detected, moving from Y=200 to Y=400
Frame 70: Crosses Y=360 → Counted as arrival
Duration: (80-50)/30 = 1.0 second
Variance: High (moving positions)
Classification: Crosser (duration <8s, so automatically Crosser)
```

### Scenario 3: Tourist Posing for Photo
```
Frames 100-400: Person detected at roughly X=640, Y=380
Duration: (400-100)/30 = 10 seconds
Position variance: ~15 px² (barely moving)
Classification: Poser (duration >8s AND variance <100px²)
```

---

## 9. Parameter Tuning

If you need to adjust the system for different scenarios:

### Adjust in `ml_processor.py`:

**Change arrival line location**:
```python
ARRIVAL_LINE_Y = 360  # Change to move detection line up/down
```

**Change direction boundary**:
```python
def classify_entity(track_id, class_id, positions):
    x_pos = positions[-1][0]
    if class_id in [2, 3, 5, 7]:  # Vehicles
        direction = "EB" if x_pos < 640 else "WB"  # Change 640
```

**Change pedestrian thresholds**:
```python
duration_threshold = 8.0  # seconds
variance_threshold = 100  # pixels squared
```

**Change detection confidence**:
```python
results = model(frame, verbose=False, conf=0.35)  # Change 0.35
```

---

## 10. Limitations and Considerations

### 10.1 Edge Cases
- **Object exactly at X=640**: Classified as Westbound (≥ boundary)
- **Object exactly at Y=360**: Counted as crossing the line
- **Partial occlusion**: May cause tracking ID to change (counted as new arrival)

### 10.2 Camera Perspective Matters
These boundaries assume:
- Camera is centered on crossing
- Eastbound traffic is on left, Westbound on right
- Y=360 represents meaningful crossing point

**If camera angle changes, boundaries must be recalibrated.**

### 10.3 Frame Rate Impact
System is designed for 30 FPS video:
- Duration thresholds (8 seconds) assume 30 FPS
- Inter-arrival times calculated assuming 30 FPS
- Different frame rates may require threshold adjustments

---

## 11. Validation

### How to verify boundaries are correct:

1. **Visual check**: Open video and note frame dimensions
2. **Test arrival line**: Verify Y=360 is at desired detection point
3. **Test direction**: Manually classify few vehicles, compare with ML output
4. **Test pedestrian**: Time pedestrians manually, compare with classification

### Quick validation script:
```python
import cv2
video = cv2.VideoCapture("your_video.mp4")
ret, frame = video.read()
print(f"Frame dimensions: {frame.shape[1]}x{frame.shape[0]}")  # Width x Height
# Draw arrival line
cv2.line(frame, (0, 360), (1279, 360), (0, 255, 0), 2)
# Draw direction boundary
cv2.line(frame, (640, 0), (640, 719), (0, 0, 255), 2)
cv2.imwrite("boundaries_visual.jpg", frame)
```

---

## Summary

**Key boundaries**:
- Arrival detection: Y = 360 pixels
- Direction classification: X = 640 pixels
- Confidence threshold: 0.35
- Poser duration: > 8 seconds
- Poser variance: < 100 px²

These parameters are optimized for the Abbey Road crossing video format (1280x720, 30 FPS) and can be adjusted as needed for different scenarios.
