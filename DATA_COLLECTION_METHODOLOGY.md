# Abbey Road Crossing - Data Collection Methodology

## 1. Overview

This document outlines the methodology for collecting traffic and pedestrian data at Abbey Road crossing for simulation modeling purposes. The data will be used to build a discrete event simulation model in Simul8 to analyze crossing behavior, traffic flow, and system performance.

---

## 2. Data Collection Principle

### 2.1 Core Principle: Recording Arrivals

**CRITICAL:** This study records **ARRIVAL EVENTS**, not departure or successful passage events.

- **What to record:** When an entity (vehicle or pedestrian) arrives at the crossing
- **What NOT to record:** Whether they successfully pass through

### 2.2 Rationale

The simulation model requires arrival data to accurately model:
- **Queue formation:** Vehicles waiting for pedestrians
- **Blocking behavior:** How pedestrians affect traffic flow
- **Inter-arrival times:** Statistical distributions of arrival patterns
- **System capacity:** Maximum throughput under various conditions

If we only recorded successful passages, we would:
- ❌ Miss queuing behavior
- ❌ Underestimate arrival rates
- ❌ Lose temporal clustering information
- ❌ Cannot model blocking interactions

---

## 3. Entity Types

The system models four distinct entity types:

### 3.1 EB Vehicles (Eastbound)
- **Definition:** Vehicles traveling east (left to right)
- **Data captured:** Arrival time, inter-arrival time
- **Recording:** Press Q or O when vehicle enters the observation zone

### 3.2 WB Vehicles (Westbound)
- **Definition:** Vehicles traveling west (right to left)
- **Data captured:** Arrival time, inter-arrival time
- **Recording:** Press W or P when vehicle enters the observation zone

### 3.3 Crossers
- **Definition:** Pedestrians who cross directly without stopping
- **Data captured:** Start time, service time (crossing duration), inter-arrival time
- **Recording:**
  - Press A or K when pedestrian starts crossing
  - Press S when pedestrian completes crossing

### 3.4 Posers
- **Definition:** Pedestrians who stop on the crossing for photos/selfies
- **Data captured:** Start time, service time (time on crossing), inter-arrival time
- **Recording:**
  - Press A or K when pedestrian starts crossing
  - Press L when pedestrian leaves the crossing

---

## 4. Critical Data Collection Rule

### 4.1 Vehicle-Pedestrian Interactions

**RULE:** Count ALL vehicles that arrive, even when pedestrians are occupying the crossing.

#### Scenario Example:
```
Time    Event
00:00   Pedestrian starts crossing (occupying road)
00:03   EB Vehicle arrives → COUNT IT ✓
00:05   WB Vehicle arrives → COUNT IT ✓
00:08   Pedestrian finishes crossing
```

#### Why This Matters:

1. **Vehicles at 00:03 and 00:05 DID arrive** - They must wait, but their arrival is real
2. **Inter-arrival times remain accurate** - Shows true traffic flow rate
3. **Timestamps capture blocking** - The simulation will see vehicles arrived while crossing was occupied
4. **Queue length is implicit** - Multiple vehicles during one crossing = queue formation

### 4.2 What the Simulation Will Do

The simulation software will:
- Detect that vehicles arrived during pedestrian service time
- Automatically create queues
- Calculate waiting times
- Model the blocking interaction

**Your job:** Record when things arrive
**Simulation's job:** Model what happens when they interact

---

## 5. Data Structure

### 5.1 Recorded Attributes

Each entry contains:

| Attribute | Description | Example |
|-----------|-------------|---------|
| **ID** | Unique sequential identifier | 1, 2, 3... |
| **Time (s)** | Video timestamp when event occurred | 15.3 |
| **Entity** | Type of entity | "EB Vehicles", "Crossers" |
| **Type/Dir** | Subtype or direction | "EB", "Crosser" |
| **Inter-Arrival (s)** | Time since last entity of same type | 5.4 |
| **Service Time (s)** | Duration on crossing (pedestrians only) | 3.2 |

### 5.2 Inter-Arrival Time Calculation

**Definition:** Time between consecutive arrivals of the **same entity type**

**Examples:**
- EB Vehicle at 10.5s, next EB at 15.9s → Inter-arrival = 5.4s
- WB Vehicle at 12.0s does NOT affect EB inter-arrival
- First entity of each type → Inter-arrival = 0.0

### 5.3 Service Time (Pedestrians Only)

**Definition:** Time pedestrian occupies the crossing

**Calculation:**
- Service Time = End Time - Start Time
- Example: Start at 20.3s, end at 23.5s → Service Time = 3.2s

**For vehicles:** Service time = "-" (not applicable)

---

## 6. Data Collection Procedure

### 6.1 Setup Phase

1. Load video file (local, YouTube, or direct URL)
2. Review the Quick Usage Guide
3. Identify observation zone boundaries
4. Test keyboard shortcuts

### 6.2 Recording Phase

1. **Start video playback**
2. **Watch for entity arrivals** in real-time
3. **Press corresponding key** immediately when event occurs
4. **Continue until video ends** or observation period complete

### 6.3 Key Presses

| Key | Action |
|-----|--------|
| Q/O | EB Vehicle arrives |
| W/P | WB Vehicle arrives |
| A/K | Pedestrian starts crossing |
| S | Crosser finishes |
| L | Poser finishes |
| Space | Play/Pause video |
| ← → | Skip ±5 seconds |

### 6.4 Quality Control

**During collection:**
- Use "Undo Last" (↩️) for immediate corrections
- Use "Delete" button to remove specific incorrect entries
- Check Entity Comparison chart periodically for reasonableness

**After collection:**
- Review "All Data" table for obvious errors
- Check for unrealistic inter-arrival times (e.g., 0.1s for vehicles)
- Verify pedestrian service times are plausible (typically 3-10s)

---

## 7. Data Export

### 7.1 Export Options

Each table can be exported individually:
- **CSV format:** Click 📄 CSV button
- **Excel format:** Click 📊 Excel button

### 7.2 Available Exports

1. **All Data** - Complete dataset with all entity types
2. **EB Vehicles** - Filtered: Only eastbound vehicles
3. **WB Vehicles** - Filtered: Only westbound vehicles
4. **Crossers** - Filtered: Only crossing pedestrians
5. **Posers** - Filtered: Only photo-stopping pedestrians

### 7.3 Export Format

**On-screen display:** Newest entries first (for easy review)
**Export order:** Oldest to newest (chronological for analysis)

### 7.4 Export Procedure

1. Click CSV or Excel button next to desired table
2. **Ignore system security warnings** - these are safe local files
3. **Save immediately** to local drive
4. Verify file opens correctly
5. Keep backup copies

---

## 8. Data Quality Criteria

### 8.1 Completeness
- ✓ All visible arrivals recorded
- ✓ No obvious gaps in timeline
- ✓ Both directions captured

### 8.2 Accuracy
- ✓ Timestamps match video events
- ✓ Entity types correctly classified
- ✓ Pedestrian start/end times properly paired

### 8.3 Consistency
- ✓ Inter-arrival times reasonable (not too short)
- ✓ Service times plausible (pedestrians: 2-15s typical)
- ✓ No duplicate entries

### 8.4 Validity Checks

**Red flags to investigate:**
- Vehicle inter-arrival < 1 second (possible duplicate)
- Pedestrian service time < 2 seconds (unlikely)
- Pedestrian service time > 30 seconds (check for Poser classification)
- Large gaps (>60s) without any entities (check video didn't pause)

---

## 9. Common Scenarios and Rules

### 9.1 Pedestrian Halfway, Vehicles Arriving
**Rule:** COUNT the vehicles
**Rationale:** They arrived, even if blocked

### 9.2 Multiple Vehicles Queuing
**Rule:** Record each vehicle separately with actual arrival time
**Rationale:** Simulation needs individual arrival times to model queue

### 9.3 Pedestrian Changes Mind
**Scenario:** Pedestrian starts but returns to curb
**Rule:** Delete the entry (they didn't actually cross)

### 9.4 Group of Pedestrians
**Rule:** Record when first person starts, when last person finishes
**Rationale:** Models entire group as one blocking event

### 9.5 Vehicle Turns Before Crossing
**Rule:** Do NOT count
**Rationale:** Not an arrival at the crossing

---

## 10. Statistical Output

### 10.1 Summary Statistics Generated

The tool automatically calculates:
- **Total entries:** Overall count
- **Entity breakdown:** Count per type
- **Percentage distribution:** Proportion of each entity
- **Visual comparison:** Bar chart for quick assessment

### 10.2 Statistical Distributions

For simulation input, calculate (external to tool):
- **Inter-arrival time distributions:** Exponential, Weibull, etc.
- **Service time distributions:** Normal, Log-normal, etc.
- **Goodness-of-fit tests:** Chi-square, Kolmogorov-Smirnov

---

## 11. Limitations and Assumptions

### 11.1 Limitations
- Manual recording introduces human reaction time delay (~0.2-0.5s)
- Small/distant vehicles may be missed
- Observer fatigue affects accuracy in long sessions
- Video quality affects visibility

### 11.2 Assumptions
- Observation zone is clearly defined
- Video playback is continuous (no skipping)
- Timestamp precision is adequate for simulation (0.1s)
- Entities are mutually exclusive (no misclassification)

### 11.3 Mitigation Strategies
- Take breaks every 15-20 minutes
- Use two observers for validation (multi-user feature)
- Review and correct after initial pass
- Use slow playback (0.5-0.75×) for high-traffic periods

---

## 12. Version Control

**Document Version:** 2.0
**Last Updated:** October 2025
**Tool Version:** mkv-annotation-tool.html v1.0
**Author:** Data Collection Team

### Changelog:
- **v2.0 (Oct 2025):** Updated methodology to emphasize arrival recording principle, clarified vehicle-pedestrian interaction rules
- **v1.0 (Initial):** Original methodology document

---

## 13. References

For simulation modeling theory:
- Banks, J., et al. (2010). *Discrete-Event System Simulation*. Pearson.
- Law, A. M. (2015). *Simulation Modeling and Analysis*. McGraw-Hill.

For data collection best practices:
- Turner, S., et al. (2007). *Manual of Transportation Engineering Studies*. ITE.

---

## Appendix A: Quick Reference Card

### COUNT ALL ARRIVALS
✓ Vehicle arrives while pedestrian crossing → **COUNT IT**
✓ Multiple vehicles queuing → **COUNT EACH ONE**
✓ Vehicle blocked but waiting → **COUNT IT**

### DO NOT COUNT
✗ Vehicle turns before reaching crossing
✗ Pedestrian starts but returns to curb
✗ Same vehicle counted twice

### REMEMBER
🎯 **Arrivals, not passages**
🎯 **Play video while recording**
🎯 **Export and save immediately**
🎯 **Review before finalizing**
