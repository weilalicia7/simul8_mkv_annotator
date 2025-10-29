# Abbey Road Crossing - Data Collection Methodology
## Version 3.0 - Academic Coursework Edition

---

## 1. Executive Summary

This document outlines the systematic methodology for collecting traffic and pedestrian data at Abbey Road crossing for discrete event simulation modeling in Simul8. The approach uses a custom-built web-based video annotation tool to ensure accurate, timestamped data collection suitable for academic research and simulation parameter estimation.

**Key Features:**
- Custom HTML-based video annotator with multi-user support
- Real-time timestamping with 0.1-second precision
- Automated inter-arrival and service time calculations
- Export capability compatible with statistical analysis software
- Validation and quality control mechanisms

---

## 2. Research Objectives

### 2.1 Primary Objectives

1. **Quantify traffic flow patterns** at Abbey Road pedestrian crossing
2. **Measure pedestrian crossing behavior** and classify user types
3. **Collect temporal data** for statistical distribution fitting
4. **Generate simulation input parameters** for Simul8 modeling

### 2.2 Research Questions

- What are the arrival rate distributions for vehicles in each direction?
- How long do pedestrians occupy the crossing (service times)?
- What proportion of pedestrians are "Crossers" vs "Posers"?
- How do pedestrian crossings impact vehicle queue formation?
- What are the inter-arrival time distributions for simulation inputs?

### 2.3 Scope and Limitations

**Scope:**
- Focus on Abbey Road zebra crossing in St John's Wood, London
- Analysis of video footage during daylight hours
- Classification of four entity types: EB Vehicles, WB Vehicles, Crossers, Posers
- Temporal analysis for simulation parameter estimation

**Limitations:**
- Video-based observation (not real-time field observation)
- Limited to visible entities in camera frame
- Weather and lighting conditions affect data quality
- Manual recording introduces human reaction time delay (±0.2-0.5s)
- Observer fatigue may affect accuracy in extended sessions

---

## 3. Data Collection Principle

### 3.1 Core Philosophy: Recording Arrivals

**CRITICAL PRINCIPLE:** This study records **ARRIVAL EVENTS**, not departure or successful passage events.

**Definition of Arrival:**
- **Vehicles:** When the front of the vehicle enters the observation zone (crosses the defined arrival line)
- **Pedestrians:** When the pedestrian steps onto the crossing from the curb

**What We DO Record:**
✅ Timestamp when entity arrives at the crossing
✅ All arrivals, including those that must wait/queue
✅ Entity type and direction of travel

**What We DO NOT Record:**
❌ Whether the entity successfully passes through
❌ How long vehicles wait in queue (simulation calculates this)
❌ Entities that turn away before reaching the crossing

### 3.2 Rationale for Arrival-Based Recording

The simulation model requires arrival data to accurately model:

1. **Queue Formation:** Vehicles waiting for pedestrians to clear
2. **Blocking Behavior:** How pedestrians affect traffic flow
3. **Inter-Arrival Times:** Statistical distributions of arrival patterns
4. **System Capacity:** Maximum throughput under various conditions
5. **Temporal Clustering:** Rush periods and quiet periods

**Why This Matters:**

If we only recorded successful passages, we would:
- ❌ Miss queuing behavior entirely
- ❌ Underestimate true arrival rates
- ❌ Lose information about temporal clustering
- ❌ Cannot model blocking interactions between entities
- ❌ Produce invalid simulation parameters

**Example Scenario:**
```
Time     Event                              Action
00:00    Pedestrian starts crossing        → RECORD pedestrian arrival
00:03    EB Vehicle arrives (must wait)    → RECORD vehicle arrival ✓
00:05    WB Vehicle arrives (must wait)    → RECORD vehicle arrival ✓
00:08    Pedestrian finishes crossing      → RECORD service time
00:09    EB Vehicle passes through         → Do NOT record (already counted at 00:03)
00:10    WB Vehicle passes through         → Do NOT record (already counted at 00:05)
```

**Key Point:** Vehicles at 00:03 and 00:05 DID arrive - they must wait, but their arrival is real. The simulation software will detect that they arrived during pedestrian service time and automatically create queues and calculate waiting times.

---

## 4. Entity Classification System

### 4.1 Entity Types

The system models four distinct entity types:

#### 4.1.1 EB Vehicles (Eastbound)
- **Definition:** Motorized vehicles traveling east (left to right on screen)
- **Includes:** Cars, motorcycles, trucks, buses
- **Excludes:** Bicycles, pedestrians
- **Data Captured:** Arrival timestamp, inter-arrival time
- **Recording Method:** Press Q or O when vehicle front enters observation zone

#### 4.1.2 WB Vehicles (Westbound)
- **Definition:** Motorized vehicles traveling west (right to left on screen)
- **Includes:** Cars, motorcycles, trucks, buses
- **Excludes:** Bicycles, pedestrians
- **Data Captured:** Arrival timestamp, inter-arrival time
- **Recording Method:** Press W or P when vehicle front enters observation zone

#### 4.1.3 Crossers
- **Definition:** Pedestrians who cross the road directly without stopping
- **Behavior:** Walk continuously from one side to the other
- **Purpose:** Transportation (getting to the other side)
- **Data Captured:** Start time, end time, service time (crossing duration), inter-arrival time
- **Recording Method:** 
  - Press A or K when pedestrian steps onto crossing
  - Press S when pedestrian reaches opposite curb

#### 4.1.4 Posers
- **Definition:** Pedestrians who stop on the crossing for photos/selfies
- **Behavior:** Walk onto crossing, stop in middle, take photos, then continue
- **Purpose:** Tourism/recreation (recreating Beatles album cover)
- **Data Captured:** Start time, end time, service time (time on crossing), inter-arrival time
- **Recording Method:**
  - Press A or K when pedestrian steps onto crossing
  - Press L when pedestrian completely leaves the crossing

### 4.2 Classification Decision Rules

**Distinguishing Crossers from Posers:**

| Characteristic | Crosser | Poser |
|----------------|---------|-------|
| **Movement** | Continuous walking | Stops in middle |
| **Purpose** | Transportation | Photo opportunity |
| **Service Time** | Typically 3-7 seconds | Typically 8-20+ seconds |
| **Behavior** | Direct path across | Poses, arranges group, takes photos |
| **Speed** | Normal walking pace | Slow, with pauses |

**Edge Cases:**
- Pedestrian stops briefly to check phone → **Crosser** (incidental, not intentional posing)
- Pedestrian walks slowly but continuously → **Crosser** (no stopping)
- Group crosses together without stopping → **Crosser** (record when first person starts, last person finishes)
- Pedestrian starts to pose but is hurried along by traffic → **Poser** (intention matters)

---

## 5. Data Collection Tool: Web-Based Video Annotator

### 5.1 Tool Overview

**Tool Name:** Abbey Road Multi-User Video Annotator
**Format:** HTML5 web application (runs in browser, no installation required)
**Platform Compatibility:** Windows, macOS, Linux (any modern browser)
**Key Innovation:** Dual-user keyboard layout for collaborative annotation

### 5.2 Technical Features

#### 5.2.1 Video Input Options
- **Local Video Files:** .mkv, .mp4, .webm, .avi, .mov formats
- **YouTube URLs:** Direct integration with YouTube player
- **Direct Video URLs:** Stream from any accessible video URL

#### 5.2.2 Playback Controls
- **Variable Speed:** 0.25×, 0.5×, 0.75×, 1× playback speeds
- **Frame-by-Frame Navigation:** Skip ±5 seconds with arrow keys
- **Play/Pause:** Spacebar for quick control
- **Time Display:** Real-time current time and total duration display

#### 5.2.3 Data Entry Interface

**Multi-User Keyboard Layout:**

| User | Position | Vehicle EB | Vehicle WB | Ped Start | Crosser End | Poser End |
|------|----------|------------|------------|-----------|-------------|-----------|
| **User 1** | Left hand | Q | W | A | S | - |
| **User 2** | Right hand | O | P | K | - | L |

**Advantages of Dual-User Design:**
- Two observers can work simultaneously
- Reduces individual observer fatigue
- Increases accuracy through redundancy
- One user focuses on vehicles, other on pedestrians
- Natural hand position (ergonomic)

#### 5.2.4 Automated Calculations

The tool automatically calculates:

**Inter-Arrival Time:**
- Time since last entity of the **same type** arrived
- Calculated separately for: EB Vehicles, WB Vehicles, Crossers, Posers
- Formula: `Inter-Arrival = Current_Time - Last_Arrival_Time_For_Type`
- First entity of each type: Inter-Arrival = 0.0

**Service Time (Pedestrians Only):**
- Duration pedestrian occupies the crossing
- Calculated as: `Service_Time = End_Time - Start_Time`
- Visual timer displays elapsed time during crossing
- Automatically recorded when pedestrian end button pressed

**Example Calculation:**
```
Event Sequence:
- EB Vehicle arrives at 10.5s → Inter-Arrival = 0.0 (first EB)
- WB Vehicle arrives at 12.0s → Inter-Arrival = 0.0 (first WB)
- EB Vehicle arrives at 15.9s → Inter-Arrival = 5.4s (15.9 - 10.5)
- Crosser starts at 20.3s → Inter-Arrival = 0.0 (first Crosser)
- Crosser ends at 23.5s → Service Time = 3.2s (23.5 - 20.3)
- EB Vehicle arrives at 24.7s → Inter-Arrival = 8.8s (24.7 - 15.9)
```

#### 5.2.5 Real-Time Feedback

**Visual Indicators:**
- Button flash animation on key press (confirmation of input)
- Active button highlighting during pedestrian timing
- Live pedestrian timer showing elapsed crossing time
- Running total of entities by type

**Statistical Dashboard:**
- Total entries counter (large display)
- Entity comparison bar chart with:
  - Absolute counts for each entity type
  - Percentage distribution
  - Dynamic Y-axis scaling
  - Color-coded bars (vehicles = grey, pedestrians = red)

#### 5.2.6 Data Quality Controls

**Edit Functions:**
- **Edit Button:** Modify timestamp of any entry
- **Delete Button:** Remove individual incorrect entries
- **Undo Last:** Quick removal of most recent entry (keyboard shortcut)
- **Delete Mode:** Toggle for rapid deletion of multiple entries

**Validation Features:**
- Prevents starting new pedestrian timing while one is in progress
- Warns if pedestrian end pressed without start
- Timestamps automatically rounded to 0.1s precision
- Unique sequential ID assignment

### 5.3 Data Tables and Views

**Five Data Views:**

1. **All Data Table**
   - Complete dataset with all entity types
   - Columns: ID, Time (s), Entity, Type/Dir, Inter-Arrival (s), Service Time (s), Actions
   - On-screen: Reverse chronological (newest first, for easy review)
   - Export: Chronological (oldest first, for analysis)

2. **EB Vehicles Table**
   - Filtered view: Only eastbound vehicles
   - Columns: ID, Time (s), Inter-Arrival (s), Actions
   - Simplified display focused on arrival patterns

3. **WB Vehicles Table**
   - Filtered view: Only westbound vehicles
   - Columns: ID, Time (s), Inter-Arrival (s), Actions
   - Simplified display focused on arrival patterns

4. **Crossers Table**
   - Filtered view: Only crossing pedestrians
   - Columns: ID, Time (s), Service Time (s), Inter-Arrival (s), Actions
   - Includes crossing duration data

5. **Posers Table**
   - Filtered view: Only photo-stopping pedestrians
   - Columns: ID, Time (s), Service Time (s), Inter-Arrival (s), Actions
   - Includes time-on-crossing data

**Tab Navigation:**
- Click tab buttons to switch between views
- Active tab highlighted in red
- Each table independently scrollable
- Maximum 400px height with scroll for large datasets

### 5.4 Export Functionality

**Export Formats:**

**CSV (Comma-Separated Values):**
- Click 📄 CSV button next to any table
- Opens/downloads immediately
- Compatible with: Excel, R, Python pandas, SPSS, Minitab
- Proper field quoting for text containing commas
- UTF-8 encoding for special characters

**Excel (.xls):**
- Click 📊 Excel button next to any table
- HTML table format compatible with Excel
- Styled headers (red background, white text)
- Formatted for immediate use
- Note: Modern Excel may show security warning (safe to ignore)

**Export Characteristics:**
- **Individual table export:** Each of the 5 tables can be exported separately
- **Chronological order:** All exports are oldest-to-newest (regardless of on-screen display)
- **Consistent formatting:** All decimal values rounded to 0.1s
- **Automatic filename:** Includes timestamp in filename (e.g., `abbey_road_EB_Vehicles_2024-10-27T14-30-15`)

**Export Procedure:**
1. Click CSV or Excel button next to desired table
2. Browser prompts to open/save file
3. **Ignore any security warnings** (files are locally generated, completely safe)
4. Save immediately to designated project folder
5. Verify file opens correctly in target software
6. Create backup copy for data security

---

## 6. Data Collection Procedure

### 6.1 Pre-Collection Setup

**Step 1: Workspace Preparation**
- Quiet environment with minimal distractions
- Comfortable seating and ergonomic keyboard position
- Good lighting to prevent eye strain
- Adequate screen size for video clarity
- Water and breaks planned (every 15-20 minutes)

**Step 2: Tool Setup**
- Open `mkv-annotation-tool.html` in web browser (Chrome or Firefox recommended)
- Load video file (local, YouTube, or URL)
- Verify video plays correctly and audio is clear (if applicable)
- Test keyboard shortcuts to ensure all keys responsive
- Verify export functions work (test export empty data)

**Step 3: Observation Zone Definition**
- Watch video several times to identify:
  - Arrival line for vehicles (where to start counting)
  - Crossing boundaries for pedestrians (curb to curb)
  - Any obstructions or blind spots
- Mark reference points on video player or notes
- Decide if slow-motion playback needed (0.5× or 0.75× for busy periods)

**Step 4: Observer Briefing (Multi-User Setup)**
- Assign roles:
  - **Observer 1 (Left hand - QWAS):** Typically focuses on one direction or entity type
  - **Observer 2 (Right hand - OPKL):** Complements Observer 1's focus
- Review entity classification criteria together
- Practice session on first 30 seconds of video
- Discuss and resolve any classification disagreements

### 6.2 Active Data Collection

**Real-Time Annotation Protocol:**

1. **Start Video Playback**
   - Press spacebar or click play
   - Begin at normal speed (1×)
   - Reduce to 0.5× or 0.75× if events are too rapid

2. **Record Arrivals in Real-Time**
   - Press corresponding key **immediately** when entity arrives
   - Visual confirmation: Button flashes briefly
   - Continue watching video without pausing (unless absolutely necessary)

3. **Pedestrian Timing Workflow**
   - Press A or K when pedestrian steps onto crossing
   - Visual confirmation: "Ped Start" button stays highlighted
   - Live timer appears showing elapsed time
   - Press S (Crosser) or L (Poser) when pedestrian clears crossing
   - Timer stops and service time recorded automatically

4. **Handling Rapid Events**
   - If multiple vehicles arrive quickly, press keys in quick succession
   - Tool timestamps each press independently
   - Use slow-motion (0.5×) if too fast to record accurately
   - Pause video only if absolutely necessary (reduces flow continuity)

5. **Error Correction**
   - **Immediate error:** Press "↩️ Undo Last" button or keyboard shortcut
   - **Discovered later:** Use "Edit" button to modify timestamp
   - **Wrong entity type:** Delete and re-enter correctly
   - **Missed entity:** Pause video, return to missed event, record, continue

6. **Periodic Quality Checks**
   - Every 2-3 minutes, glance at Entity Comparison chart
   - Verify counts seem reasonable (e.g., roughly balanced EB/WB vehicles)
   - Check for anomalies (e.g., zero Crossers despite seeing many)
   - Review recent entries in All Data table for obvious errors

### 6.3 Challenging Scenarios

**Scenario 1: Simultaneous Arrivals**
- **Multiple vehicles from same direction:** Record each separately, as fast as possible
- **Vehicles from both directions:** Two observers press Q/O and W/P simultaneously
- **Vehicle + Pedestrian:** Record both, priority to pedestrian start (harder to catch)

**Scenario 2: Ambiguous Pedestrian Behavior**
- **Starts to cross, returns to curb:** Delete the entry (did not actually cross)
- **Crosses very slowly:** Still a Crosser if continuous movement
- **Brief pause mid-crossing:** Use judgment - if <2 seconds and not posing, classify as Crosser
- **Group crossing:** Record when first person starts, last person finishes

**Scenario 3: Vehicle Turning Before Crossing**
- **Do NOT count** vehicles that turn into side streets before reaching crossing
- **Do count** vehicles that turn after passing the crossing line

**Scenario 4: Obscured View**
- **Partially visible vehicle:** Count if you can confirm it's a vehicle
- **Completely obscured:** Do not count (cannot confirm arrival)
- **Pedestrian behind object:** Wait until visible on crossing to record start

**Scenario 5: High Traffic Volume**
- **Consider slow-motion:** 0.5× or 0.75× speed
- **Pause if overwhelmed:** Better to pause briefly than miss entities
- **Post-collection review:** Watch again and add any missed entities with correct timestamps

### 6.4 Post-Collection Quality Assurance

**Step 1: Immediate Review**
- Watch final 2 minutes of video again
- Verify all visible entities were recorded
- Check for duplicate entries (same entity counted twice)

**Step 2: Data Validation Checks**

**Statistical Plausibility:**
- EB and WB vehicle counts should be roughly similar (unless one-way road)
- Inter-arrival times should not be impossibly short (<1 second for vehicles)
- Service times for Crossers should typically be 3-10 seconds
- Service times for Posers should typically be 8-30 seconds

**Anomaly Detection:**
- Sort by Inter-Arrival time (ascending) and check for values <0.5s (likely duplicates)
- Sort by Service Time and check for pedestrians with <2s or >60s (likely errors)
- Review any entries with Inter-Arrival = 0.0 (should only be first of each type)

**Missing Data:**
- Verify no large time gaps (>60s) with zero entities (suggests video paused)
- Check that both directions represented (unless one-way)
- Confirm at least some Crossers recorded (Abbey Road is famous, should have pedestrians)

**Step 3: Export All Data**
- Export all 5 tables (All Data, EB, WB, Crossers, Posers)
- Save to project folder with descriptive filenames
- Create backup copies immediately
- Do NOT close browser until exports confirmed saved

**Step 4: Documentation**
- Record metadata:
  - Date and time of data collection session
  - Video source and filename
  - Observer names
  - Session duration
  - Any notable incidents or issues
  - Weather/lighting conditions (if visible in video)

---

## 7. Data Structure and Format

### 7.1 Primary Data Fields

Each recorded entry contains the following attributes:

| Field | Type | Description | Example | Constraints |
|-------|------|-------------|---------|-------------|
| **ID** | Integer | Unique sequential identifier | 1, 2, 3... | Auto-incremented, never reused |
| **Time (s)** | Float | Video timestamp when event occurred | 15.3 | Rounded to 0.1s, always positive |
| **Entity** | String | Entity type category | "EB Vehicles", "Crossers" | One of 4 fixed values |
| **Type/Dir** | String | Subtype or direction abbreviation | "EB", "Crosser" | Derived from Entity |
| **Inter-Arrival (s)** | Float | Time since last entity of same type | 5.4 | 0.0 for first of type, otherwise positive |
| **Service Time (s)** | Float or null | Duration on crossing (pedestrians only) | 3.2 | Only populated for Crossers/Posers |

### 7.2 Entity Type Values

**Fixed Values:**
- `"EB Vehicles"` - Eastbound motorized vehicles
- `"WB Vehicles"` - Westbound motorized vehicles
- `"Crossers"` - Pedestrians who cross directly
- `"Posers"` - Pedestrians who stop for photos

**Type/Dir Abbreviations:**
- `"EB"` - Eastbound
- `"WB"` - Westbound
- `"Crosser"` - Crossing pedestrian
- `"Poser"` - Photo-stopping pedestrian

### 7.3 Service Time Rules

**When Populated:**
- Crossers: Service Time = End Time - Start Time
- Posers: Service Time = End Time - Start Time

**When Null (displayed as "-"):**
- EB Vehicles: Service time not applicable
- WB Vehicles: Service time not applicable

**Typical Ranges:**
- Crossers: 3-10 seconds (normal walking speed)
- Posers: 8-30+ seconds (includes posing time)

### 7.4 Inter-Arrival Time Calculation

**Formula:**
```
If first entity of this type:
    Inter-Arrival = 0.0
Else:
    Inter-Arrival = Current_Time - Last_Arrival_Time_For_This_Type
```

**Key Points:**
- Calculated **separately** for each entity type
- EB Vehicle at time 10s does NOT affect WB Vehicle inter-arrival calculation
- Crosser and Poser inter-arrivals calculated separately
- Always non-negative

**Example Sequence:**
```
ID  Time   Entity        Inter-Arrival  Calculation
1   5.0    EB Vehicles   0.0            (first EB)
2   7.5    WB Vehicles   0.0            (first WB)
3   8.2    EB Vehicles   3.2            (8.2 - 5.0)
4   9.0    Crossers      0.0            (first Crosser)
5   11.5   EB Vehicles   3.3            (11.5 - 8.2)
6   12.0   WB Vehicles   4.5            (12.0 - 7.5)
```

### 7.5 Export File Formats

**CSV Structure:**
```csv
ID,Time (s),Entity,Type/Dir,Inter-Arrival (s),Service Time (s)
1,5.0,"EB Vehicles",EB,0.0,-
2,7.5,"WB Vehicles",WB,0.0,-
3,8.2,"EB Vehicles",EB,3.2,-
4,9.0,Crossers,Crosser,0.0,3.5
```

**Excel Structure:**
- Same column order as CSV
- Headers styled with red background (#C8102E), white text
- Alternating row colors for readability
- Borders on all cells
- Numeric columns formatted to 1 decimal place

---

## 8. Critical Data Collection Rules

### 8.1 The Golden Rule: Count ALL Arrivals

**RULE:** Record every entity that arrives at the crossing, regardless of whether they can immediately pass through.

**Applies To:**
- ✅ Vehicles that must wait for pedestrians
- ✅ Vehicles queuing behind other vehicles
- ✅ Multiple vehicles arriving while crossing is occupied
- ✅ Pedestrians who must wait for other pedestrians to clear

**Does NOT Apply To:**
- ❌ Entities that turn away before reaching crossing
- ❌ Entities outside observation zone
- ❌ Same entity counted twice (tracking error)

### 8.2 Vehicle-Pedestrian Interaction Rule

**RULE:** Count vehicles even when pedestrians are occupying the crossing.

**Scenario Example:**
```
Time    Event                                Action
00:00   Pedestrian starts crossing          → RECORD (A or K key)
00:02   Pedestrian in middle of crossing    → Continue timing
00:03   EB Vehicle arrives (must wait)      → RECORD (Q or O key) ✓
00:04   Another EB Vehicle arrives          → RECORD (Q or O key) ✓
00:05   WB Vehicle arrives (must wait)      → RECORD (W or P key) ✓
00:08   Pedestrian finishes crossing        → RECORD (S or L key)
00:09   First EB Vehicle passes through     → Do nothing (already counted at 00:03)
00:10   Second EB Vehicle passes through    → Do nothing (already counted at 00:04)
00:11   WB Vehicle passes through           → Do nothing (already counted at 00:05)
```

**Why This Matters:**
1. Vehicles at 00:03, 00:04, and 00:05 **DID arrive** at the crossing
2. They must wait due to the pedestrian, but their arrival is real
3. Inter-arrival times remain accurate (5.4s, 1.0s, 1.0s in this example)
4. The simulation will detect overlap and automatically create queues
5. Waiting times will be calculated by simulation based on overlapping timestamps

**What the Simulation Will Do:**
- Detect that vehicles arrived during pedestrian service time
- Calculate waiting time = (Pedestrian End Time) - (Vehicle Arrival Time)
- Accumulate queue length = Count of vehicles arrived before pedestrian cleared
- Model blocking interactions and delays

**Your Responsibility:**
- Record arrivals accurately with correct timestamps
- Let the simulation handle the interaction analysis

### 8.3 Multiple Entities Queueing

**RULE:** Record each entity separately with its own arrival timestamp.

**Example: Three Vehicles Arrive While Crossing Occupied**
```
Time    Event                       Record
00:00   Pedestrian starts          → ID 1: Crosser, Time 0.0
00:05   EB Vehicle #1 arrives      → ID 2: EB Vehicles, Time 5.0, Inter-Arrival 0.0
00:07   EB Vehicle #2 arrives      → ID 3: EB Vehicles, Time 7.0, Inter-Arrival 2.0
00:09   EB Vehicle #3 arrives      → ID 4: EB Vehicles, Time 9.0, Inter-Arrival 2.0
00:10   Pedestrian finishes        → Update ID 1: Service Time 10.0
```

**Simulation Analysis:**
- Vehicle #1 waits: 10.0 - 5.0 = 5.0 seconds
- Vehicle #2 waits: 10.0 - 7.0 = 3.0 seconds (plus time behind Vehicle #1)
- Vehicle #3 waits: 10.0 - 9.0 = 1.0 second (plus time behind Vehicles #1 and #2)
- Queue length: 3 vehicles

### 8.4 Edge Cases and Special Situations

**Case 1: Pedestrian Changes Mind**
- **Scenario:** Pedestrian starts to cross but returns to curb without fully crossing
- **Action:** Delete the entry (they did not actually cross)
- **Rationale:** No service time consumed, no traffic impact

**Case 2: Group of Pedestrians**
- **Scenario:** 4 people cross together in a group
- **Action:** Record when first person starts, when last person finishes
- **Rationale:** Models the entire group as one blocking event

**Case 3: Vehicle Slows But Doesn't Stop**
- **Scenario:** Pedestrian is halfway across, vehicle slows but passes behind them
- **Action:** Count the vehicle arrival normally
- **Rationale:** Vehicle did arrive and had to react (slow down) even if didn't fully stop

**Case 4: Very Slow Pedestrian**
- **Scenario:** Elderly person crosses very slowly (15 seconds)
- **Action:** Record as Crosser if continuous movement
- **Rationale:** Speed doesn't matter, lack of stopping defines Crosser

**Case 5: Pedestrian Stops to Tie Shoe**
- **Scenario:** Pedestrian stops mid-crossing for non-photo reason
- **Action:** Use judgment - if brief (<3s), classify as Crosser; if extended, classify as Poser
- **Rationale:** Focus on impact to traffic (service time) rather than intention

### 8.5 What NOT to Count

**Do NOT Record:**
- ❌ Bicycles (not motorized vehicles)
- ❌ Motorcycles in bicycle lane (if separate from main road)
- ❌ Pedestrians walking parallel to road (not crossing)
- ❌ Vehicles turning before reaching crossing
- ❌ Emergency vehicles with sirens (different behavior patterns)
- ❌ Vehicles reversing or making U-turns
- ❌ Same entity counted twice (tracking failure)

---

## 9. Statistical Analysis and Distribution Fitting

### 9.1 Descriptive Statistics

After data collection, calculate the following for each entity type:

**For All Entity Types:**
- **Count (n):** Total number of arrivals
- **Mean Inter-Arrival Time:** Average time between arrivals
- **Standard Deviation:** Variability in inter-arrival times
- **Minimum/Maximum:** Range of inter-arrival times
- **Coefficient of Variation (CV):** StdDev / Mean (indicates randomness)

**For Pedestrians Only:**
- **Mean Service Time:** Average crossing duration
- **Standard Deviation:** Variability in service times
- **Minimum/Maximum:** Range of service times
- **Proportions:** % Crossers vs % Posers

**Example Summary Table:**
```
Entity Type     Count   Mean Inter-Arrival (s)   StdDev   Mean Service (s)   StdDev
EB Vehicles     45      8.2                      4.1      -                  -
WB Vehicles     42      8.7                      4.5      -                  -
Crossers        28      12.5                     6.8      4.2                1.1
Posers          15      23.1                     12.4     14.7               5.3
```

### 9.2 Distribution Fitting for Simul8

**Objective:** Determine which probability distribution best fits your data for use as Simul8 input parameters.

#### 9.2.1 Inter-Arrival Time Distributions

**Candidate Distributions:**

1. **Exponential Distribution**
   - **When to use:** Random, memoryless arrivals (most common for traffic)
   - **Parameter:** λ (rate) = 1 / Mean Inter-Arrival Time
   - **Simul8 Entry:** Use "Exponential" distribution, enter mean
   - **Check:** CV should be ≈ 1.0

2. **Erlang Distribution**
   - **When to use:** More regular arrivals (CV < 1.0)
   - **Parameters:** k (shape), λ (rate)
   - **Simul8 Entry:** May need custom or approximation with Normal
   - **Check:** CV = 1/√k

3. **Gamma Distribution**
   - **When to use:** Flexible fit for various patterns
   - **Parameters:** α (shape), β (scale)
   - **Simul8 Entry:** Use "Gamma" if available, or fit to Erlang/Normal
   - **Check:** CV = 1/√α

4. **Weibull Distribution**
   - **When to use:** Arrival rate changes over time
   - **Parameters:** k (shape), λ (scale)
   - **Simul8 Entry:** "Weibull" distribution
   - **Check:** CV varies with shape parameter

5. **Normal Distribution**
   - **When to use:** Very regular arrivals (CV < 0.5), symmetric
   - **Parameters:** μ (mean), σ (standard deviation)
   - **Simul8 Entry:** "Normal" distribution
   - **Warning:** Can produce negative values (truncate at 0)

**Fitting Procedure:**

**Step 1: Visual Inspection**
- Create histogram of inter-arrival times
- Overlay candidate distribution curves
- Check for general shape match

**Step 2: Calculate Coefficient of Variation**
```
CV = Standard Deviation / Mean

CV ≈ 1.0  → Try Exponential first
CV < 1.0  → Try Erlang or Normal
CV > 1.0  → Try Gamma or Weibull
```

**Step 3: Goodness-of-Fit Tests**
- **Chi-Square Test:** Tests if observed frequencies match expected
- **Kolmogorov-Smirnov Test:** Tests if cumulative distributions match
- **Anderson-Darling Test:** More sensitive to tail behavior

**Step 4: Select Best Fit**
- Choose distribution with lowest Chi-Square statistic (or highest p-value)
- Verify visually that fit looks reasonable
- Consider simplicity (Exponential preferred if adequate)

**Software Tools for Fitting:**
- **R:** `fitdistrplus` package
- **Python:** `scipy.stats` module
- **Minitab:** Stat > Quality Tools > Individual Distribution Identification
- **Excel:** Manual fitting with CHITEST function
- **Simul8:** Built-in "Fit Distribution" tool (if available in your version)

#### 9.2.2 Service Time Distributions (Pedestrians)

**Candidate Distributions:**

1. **Normal Distribution**
   - **When to use:** Symmetric, bell-shaped service times
   - **Parameters:** μ (mean), σ (standard deviation)
   - **Simul8 Entry:** "Normal" distribution
   - **Note:** Truncate at reasonable minimum (e.g., 2 seconds)

2. **Lognormal Distribution**
   - **When to use:** Right-skewed, some very long service times
   - **Parameters:** μ (log-mean), σ (log-standard deviation)
   - **Simul8 Entry:** "Lognormal" distribution
   - **Advantage:** Cannot produce negative values

3. **Triangular Distribution**
   - **When to use:** Simple approximation, known minimum/mode/maximum
   - **Parameters:** min, mode, max
   - **Simul8 Entry:** "Triangular" distribution
   - **Advantage:** Easy to explain and justify

4. **Uniform Distribution**
   - **When to use:** All service times equally likely within range
   - **Parameters:** min, max
   - **Simul8 Entry:** "Uniform" distribution
   - **Advantage:** Simplest possible distribution

**Separate Distributions for Crossers vs Posers:**
- **Important:** Fit distributions separately for Crossers and Posers
- Crossers typically Normal or Lognormal (shorter, less variable)
- Posers typically Lognormal or Gamma (longer, more variable)

---

## 10. Reporting Data Collection for Academic Submission

### 10.1 Report Structure (for MAT021 Coursework)

**Section 1: Data Collection and Analysis (20% of marks, max 3 pages)**

**Recommended Structure:**

**1.1 Research Objectives (0.5 pages)**
- State the purpose of your simulation model
- List the specific data required (entity types, arrival patterns, service times)
- Explain how data will inform Simul8 parameters

**1.2 Data Collection Methodology (1 page)**
- **Brief description of Abbey Road crossing system**
  - Location, layout, traffic patterns
  - Why this system was chosen (accessibility, interesting behavior, etc.)
- **Data collection tool**
  - Custom web-based video annotator (brief feature list)
  - Multi-user keyboard interface for efficient real-time annotation
  - Automatic calculation of inter-arrival and service times
  - Built-in quality control features (edit, delete, undo)
- **Procedure**
  - Video source (YouTube, duration, date/time of footage)
  - Observer setup (solo or dual-user)
  - Real-time annotation protocol
  - Quality assurance steps

**1.3 Data Presentation (1 page)**
- **Summary statistics table** (counts, means, standard deviations for each entity type)
- **Entity distribution chart** (bar chart showing proportion of each type)
- **Inter-arrival time histograms** (for EB vehicles, WB vehicles)
- **Service time histograms** (for Crossers and Posers separately)

**1.4 Distribution Fitting and Simul8 Parameters (0.5 pages)**
- **Distributions selected** (e.g., Exponential for arrivals, Normal for service times)
- **Goodness-of-fit statistics** (Chi-Square test results, p-values)
- **Justification** for distribution choices
- **Parameters used in Simul8** (table of distribution types and parameter values)

**Example Table:**
```
Entity Type     Simul8 Input             Distribution   Parameters
EB Vehicles     Inter-Arrival Time       Exponential    Mean = 8.2s
WB Vehicles     Inter-Arrival Time       Exponential    Mean = 8.7s
Crossers        Service Time             Normal         Mean = 4.2s, SD = 1.1s, Min = 2.0s
Posers          Service Time             Lognormal      Mean = 14.7s, SD = 5.3s
```

### 10.2 What to Include

**DO Include:**
✅ Clear statement of what data was collected and why
✅ Description of collection method (tool features, procedure)
✅ Summary statistics and visualizations
✅ Distribution fitting process and results
✅ Direct connection to Simul8 model parameters
✅ Any limitations or assumptions made

**DO NOT Include:**
❌ Full HTML code of the annotation tool (too technical, not relevant)
❌ Raw data tables (put in appendix if needed, cite in text)
❌ Excessive detail on tool implementation (focus on functionality, not code)
❌ Repetitive histograms (show representative examples only)

### 10.3 Emphasizing Originality

**What Makes Your Approach Original (Marks Available):**

1. **Custom tool development** - Most students use stopwatches or manual tallying; you built a specialized software tool
2. **Automated calculations** - Inter-arrival and service times calculated automatically, reducing human error
3. **Multi-user design** - Dual-keyboard layout enables collaborative annotation, increasing throughput
4. **Real-time annotation** - Recording events as they happen (rather than pausing/rewinding) better captures flow dynamics
5. **Integrated quality control** - Built-in edit/delete/undo functions ensure data quality
6. **Comprehensive data export** - Five filtered views enable focused analysis of each entity type

**How to Present This:**
- Dedicate 1-2 paragraphs in the Methodology subsection to explaining why you built the tool
- Emphasize the advantages over traditional methods (accuracy, efficiency, reproducibility)
- Include a screenshot of the tool interface (with annotations labeling key features)
- Mention it briefly again in the Simulation Model section when explaining how data informed parameters

### 10.4 Connecting Data to Simulation Model

**Critical:** The report must show a clear link from collected data → distribution fitting → Simul8 parameters.

**Example Flow:**
1. "We collected 45 EB vehicle arrivals over 380 seconds of video footage"
2. "The mean inter-arrival time was 8.2 seconds with a standard deviation of 4.1 seconds"
3. "The coefficient of variation (CV = 0.50) suggested a less-than-purely-random process, but we fit an Exponential distribution for simplicity (CV = 1.0 for Exponential)"
4. "Chi-Square goodness-of-fit test yielded p = 0.12, indicating adequate fit"
5. "In Simul8, we set the EB Vehicle entry point to use an Exponential distribution with mean = 8.2 seconds"

**Visual Aid:** Consider a flowchart showing:
```
[Video Footage] → [Annotation Tool] → [Raw Timestamps] → 
[Statistical Analysis] → [Distribution Fitting] → [Simul8 Parameters]
```

---

## 11. Future Enhancements (Optional)

### 11.1 Machine Learning Integration

**If time permits and interest exists**, the data collection methodology could be enhanced with automated detection using computer vision and machine learning.

**Approach:**
- **YOLOv8** for object detection (vehicles and pedestrians)
- **DeepSORT** for object tracking (assign unique IDs)
- **Direction classification** based on position and movement
- **Behavior analysis** to distinguish Crossers from Posers

**Advantages:**
- Fully automated data collection (no manual key pressing)
- Consistent accuracy (no observer fatigue)
- Can process hours of footage quickly
- Live dashboard for real-time monitoring

**Software Required (All Free):**
- Python 3.8+
- YOLOv8 (Ultralytics)
- OpenCV
- DeepSORT
- Streamlit (for dashboard)

**Note:** This is **optional** and **not required** for the coursework. The manual annotation tool is sufficient and appropriate for academic purposes. ML integration is mentioned here as a potential future direction for interested students or for professional-scale deployments.

**Reference:** See `ML_INTEGRATION_GUIDE.md` for detailed implementation instructions (100% free, open-source tools).

### 11.2 Extended Data Collection

**For more comprehensive analysis:**
- **Weather conditions:** Compare sunny vs rainy day traffic
- **Time of day:** Morning rush vs midday vs evening
- **Day of week:** Weekday vs weekend tourist traffic
- **Seasonal variations:** Summer tourist season vs winter

**Each condition would require:**
- Separate video footage
- Separate annotation session
- Separate distribution fitting
- Multiple Simul8 scenarios

---

## 12. Summary and Key Takeaways

### 12.1 Core Principles

**Remember the Three Pillars:**
1. **Record Arrivals, Not Passages** - Count when entities arrive, even if they must wait
2. **Consistency is Critical** - Use the same criteria throughout data collection
3. **Quality Over Quantity** - 30 minutes of careful annotation beats 2 hours of careless work

### 12.2 Methodology Strengths

**What Makes This Approach Effective:**
- ✅ **Systematic:** Standardized tool and procedure ensure reproducibility
- ✅ **Accurate:** Real-time timestamping with 0.1s precision
- ✅ **Efficient:** Multi-user design and keyboard shortcuts speed collection
- ✅ **Validated:** Built-in quality controls and post-collection checks
- ✅ **Compatible:** Direct export to formats usable by statistical software and Simul8

### 12.3 From Data to Simulation

**The Complete Pipeline:**
1. **Video Source** → Choose representative footage
2. **Annotation** → Use custom tool to record arrivals and service times
3. **Export** → Generate CSV/Excel files
4. **Analysis** → Calculate summary statistics, fit distributions
5. **Validation** → Goodness-of-fit tests, visual inspection
6. **Implementation** → Enter distribution parameters into Simul8
7. **Verification** → Compare simulation outputs to observed data

### 12.4 Success Criteria

**Your data collection is successful when:**
- ✅ Sample sizes adequate (30+ for each main entity type)
- ✅ Distributions fit reasonably well (p > 0.05 on goodness-of-fit tests)
- ✅ Parameters make intuitive sense (e.g., mean vehicle inter-arrival 5-15 seconds)
- ✅ Simul8 model produces outputs similar to observed behavior
- ✅ Documentation is clear and methodology is reproducible

---

## 13. Quick Start Checklist (1 Page Summary)

For students who need to get started quickly, here's the absolute minimum you need to know:

### Setup (15 minutes)
- [ ] Open `mkv-annotation-tool.html` in browser
- [ ] Load your video (local file, YouTube, or URL)
- [ ] Test keyboard shortcuts (Q, W, A, S, O, P, K, L)

### Recording (30-60 minutes)
- [ ] Press keys AS events happen in real-time:
  - Q or O = EB Vehicle arrives
  - W or P = WB Vehicle arrives
  - A or K = Pedestrian starts crossing
  - S = Crosser finishes
  - L = Poser finishes
- [ ] Count ALL vehicles, even when they must wait for pedestrians
- [ ] Use Undo (↩️) for immediate errors

### Export (5 minutes)
- [ ] Click 📄 CSV buttons to export all 5 tables
- [ ] Save files to project folder
- [ ] Create backup copies

### Analysis (30 minutes)
- [ ] Calculate mean and standard deviation for inter-arrival times
- [ ] Calculate mean and standard deviation for service times
- [ ] Fit distributions (usually Exponential for arrivals, Normal for service)
- [ ] Run goodness-of-fit tests

### Simul8 (30 minutes)
- [ ] Enter distribution types and parameters into Simul8
- [ ] Run simulation
- [ ] Compare outputs to observed data

**Total Time:** 2-3 hours for complete data collection and analysis

**Key Principle:** Record ARRIVALS (when entities show up), not passages (when they leave). Let the simulation calculate waiting times and queues.

---

## Document Control

**Document Title:** Abbey Road Crossing - Data Collection Methodology (Version 3.0 - Academic Coursework Edition)

**Version History:**

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | Sept 2024 | Initial methodology document | Research Team |
| 2.0 | Oct 2024 | Updated with arrival recording emphasis, clarified vehicle-pedestrian rules | Research Team |
| 3.0 | Oct 2024 | Comprehensive rewrite for academic coursework, added distribution fitting section, integrated tool documentation, ML positioned as future enhancement | Research Team |

**Related Documents:**
- `USAGE_INSTRUCTIONS.md` - Quick reference guide for the annotation tool
- `mkv-annotation-tool.html` - The video annotation software
- `ML_INTEGRATION_GUIDE.md` - Optional machine learning enhancement guide (future work)
- `Simulation_Coursework_Instructions.pdf` - MAT021 coursework requirements

**Contact Information:**
- **Course Instructor:** Dr. Mark Tuson (TusonM@cardiff.ac.uk), Abacws 2.55

---

**END OF DOCUMENT**

**Document prepared for MAT021 Simulation Coursework**
**Cardiff University - School of Mathematics**
**October 2024**
