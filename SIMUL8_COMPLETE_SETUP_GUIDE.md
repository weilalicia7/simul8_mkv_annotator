# SIMUL8 Complete Setup Guide - Bidirectional Traffic Model

**Status**: Complete Dataset - All 4 Entity Types Collected
**Total Entities**: 1,073 (EB: 315, WB: 506, Crossers: 102, Posers: 150)
**Duration**: 90 minutes (5,390 seconds)
**Purpose**: Build complete bidirectional traffic simulation model

---

## Executive Summary

Your data collection is now COMPLETE. This guide shows you how to build a full bidirectional traffic model in SIMUL8 using all four entity types with scientifically-determined capacities based on queueing theory analysis.

### Key Metrics from Analysis:

**Traffic Volume:**
- Total throughput: 717 entities/hour
- EB Vehicles: 210 entities/hour (high frequency)
- WB Vehicles: 340 entities/hour (highest frequency)
- Crossers: 70 entities/hour
- Posers: 104 entities/hour

**Variability (Critical Finding):**
- EB Vehicles: CV = 1.28 (High variability)
- WB Vehicles: CV = 1.29 (High variability)
- Crossers: CV = 1.05 (Medium variability)
- **Posers: CV = 1.95 (Extremely high variability)**

**Recommended Capacities (from Queueing Theory):**
- EB Vehicle lanes: **5 servers** (optimal)
- WB Vehicle lanes: **7 servers** (optimal)
- Pedestrian crossing capacity: **2 servers** (Posers), **1 server** (Crossers)

---

## Part 1: Understanding Your Complete Dataset

### File Locations:

```
data set/
├── wb_vehicles.csv      506 entries  [WB traffic →]
├── eb_vehicles.csv      315 entries  [← EB traffic]
├── crossers.csv         102 entries  [Quick pedestrians]
├── posers.csv           150 entries  [Photo-taking tourists]
└── Combined:
    ├── combined_results.csv        1,073 entities (ready for SIMUL8)
    └── all_sessions_combined.csv   (same data, different name)
```

### Data Format (All Files):

| Column | Description | Example |
|--------|-------------|---------|
| ID | Entity number | 1, 2, 3... |
| Time (s) | Timestamp in seconds | 5.5, 34.6, 67.9 |
| Entity | Entity type | "EB Vehicles", "WB Vehicles", "Crossers", "Posers" |
| Type/Dir | Direction/type detail | "EB", "WB", "Crosser", "Poser" |
| Inter-Arrival (s) | Time since last entity | 0, 29.0, 33.4 |
| Service Time (s) | Processing time | "-" for vehicles, 7.2 for pedestrians |

---

## Part 2: Open SIMUL8 and Initial Configuration

### Step 1: Create New Simulation

1. **Launch SIMUL8**
2. **File → New Simulation**
3. **Save immediately**: `abbey_road_complete_model.s8`

### Step 2: Configure Time Settings

1. **Simulation → Simulation Settings**
2. Set parameters:
   ```
   Time Units: Seconds
   Run Length: 5400 seconds (90 minutes)
   Warm-up Period: 600 seconds (10 minutes)
   Number of Replications: 10
   Random Seed: Fixed (for reproducibility)
   ```

3. **Click Clock Display** → Set format to "hh:mm:ss"

### Step 3: Set Global Parameters

1. **Simulation → Objects → Global Data**
2. Add parameters:
   ```
   EB_ARRIVAL_RATE = 210.39 (entities/hour)
   WB_ARRIVAL_RATE = 339.91 (entities/hour)
   CROSSER_RATE = 69.59 (entities/hour)
   POSER_RATE = 103.54 (entities/hour)

   EB_CAPACITY = 5 (lanes/servers)
   WB_CAPACITY = 7 (lanes/servers)
   CROSSING_CAPACITY = 2 (parallel crossings)
   ```

---

## Part 3: Build the Model Structure

### Conceptual Layout:

```
                    [Crossing Zone]
                          |
[EB Entry] ← ← ← [EB Processing] ← ← ← [Conflict Point] → → → [WB Processing] → → → [WB Exit]
    ↓                                         ↑
[EB Exit]                                     |
                                    [Pedestrian Processing]
                                        ↗           ↖
                            [Crosser Entry]    [Poser Entry]
                                   ↓               ↓
                            [Crosser Exit]     [Poser Exit]
```

### Step 3.1: Create Entry Points (4 Total)

**EB Vehicle Entry:**
1. Drag "Entry Point" onto canvas (top-left area)
2. Label: "EB Vehicle Entry"
3. Double-click → **Inter-Arrival Times** tab
4. **Import Distribution**:
   - File: `data set/eb_vehicles.csv`
   - Column: Column 5 (Inter-Arrival (s))
   - Skip header: Yes
5. Verify: Mean ≈ 17.1 seconds, 315 data points

**WB Vehicle Entry:**
1. Create entry point (top-right area)
2. Label: "WB Vehicle Entry"
3. Import distribution from `wb_vehicles.csv`, Column 5
4. Verify: Mean ≈ 10.6 seconds, 506 data points

**Crosser Entry:**
1. Create entry point (bottom-left area)
2. Label: "Crosser Entry"
3. Import from `crossers.csv`, Column 5
4. Verify: Mean ≈ 51.7 seconds, 102 data points

**Poser Entry:**
1. Create entry point (bottom-right area)
2. Label: "Poser Entry"
3. Import from `posers.csv`, Column 5
4. Verify: Mean ≈ 34.8 seconds, 150 data points

### Step 3.2: Create Processing Activities

**EB Vehicle Processing:**
1. Drag "Activity" onto canvas
2. Label: "EB Lanes"
3. Double-click → **Resources** tab
4. Set capacity: **5** (from queueing analysis)
5. **Timing** tab:
   - Distribution: Fixed
   - Value: 60 seconds (average crossing time)
6. Connect: EB Entry → EB Lanes

**WB Vehicle Processing:**
1. Create activity
2. Label: "WB Lanes"
3. Capacity: **7** (from queueing analysis)
4. Timing: Fixed, 60 seconds
5. Connect: WB Entry → WB Lanes

**Crosser Processing:**
1. Create activity
2. Label: "Crosser Crossing"
3. Capacity: **1** (single file crossing)
4. **Import Service Time Distribution**:
   - File: `crossers.csv`
   - Column: Column 6 (Service Time (s))
   - Skip header: Yes
5. Verify: Mean ≈ 7.2 seconds
6. Connect: Crosser Entry → Crosser Crossing

**Poser Processing:**
1. Create activity
2. Label: "Poser Crossing"
3. Capacity: **2** (need buffer due to high variability)
4. Import from `posers.csv`, Column 6
5. Verify: Mean ≈ 11.0 seconds
6. Connect: Poser Entry → Poser Crossing

### Step 3.3: Create Conflict/Crossing Zone

This represents the shared crossing space where conflicts occur.

1. **Create Queue**: Place in center of canvas
2. Label: "Crossing Zone"
3. **Visual Queue**: Set to display entities waiting
4. Set capacity: **10** (physical space constraint)

**Connect entities to crossing zone:**
- EB Lanes → Crossing Zone
- WB Lanes → Crossing Zone
- Crosser Crossing → Crossing Zone
- Poser Crossing → Crossing Zone

### Step 3.4: Add Priority Logic (Critical!)

Since vehicles and pedestrians conflict, add priority rules:

1. Right-click "Crossing Zone"
2. **Routing In** → Set Priority:
   ```
   Priority 1: Pedestrians (Crossers + Posers)
   Priority 2: EB Vehicles
   Priority 3: WB Vehicles
   ```

   **Reasoning**: Give pedestrians right-of-way (safety), then vehicles by arrival order.

3. **Or use Traffic Light Logic** (Advanced):
   - Add Visual Logic → Traffic Light
   - Cycle: 60s green (vehicles), 30s green (pedestrians)
   - This is more realistic

### Step 3.5: Create Exit Points

1. Create 4 exit points:
   - EB Exit (vehicles leaving eastbound)
   - WB Exit (vehicles leaving westbound)
   - Crosser Exit (pedestrians finished)
   - Poser Exit (tourists finished)

2. Connect Crossing Zone to all 4 exits with routing logic

---

## Part 4: Configure Visual Appearance

### Entity Types and Colors:

1. **Simulation → Work Items**
2. Configure each type:

| Entity Type | Color | Icon | Size | Purpose |
|-------------|-------|------|------|---------|
| EB Vehicles | Blue | Car | Large | Eastbound traffic |
| WB Vehicles | Red | Car | Large | Westbound traffic |
| Crossers | Green | Person | Medium | Quick pedestrians |
| Posers | Yellow | Camera | Medium | Photo-taking tourists |

3. **Set animation speed**: Vehicles faster than pedestrians
   - Right-click each entry → Travel Time
   - Vehicles: 2 seconds
   - Pedestrians: 5 seconds (slower walking)

---

## Part 5: Add Results Collection

### Key Metrics to Track:

**For Each Activity:**
1. Right-click activity → **Results → Collect Results**
2. Enable:
   - Average Time in Activity
   - Queue Length (time series)
   - Utilization
   - Maximum Queue Length
   - Number Completed

**Specific Metrics:**

| Object | Metric | Why Important |
|--------|--------|---------------|
| EB Lanes | Utilization | Should be ~70% (matches queueing analysis) |
| WB Lanes | Utilization | Should be ~48% (matches queueing analysis) |
| Crosser Crossing | Queue Length | Should be low (< 1 avg) |
| Poser Crossing | Queue Length | May be higher due to variability |
| Crossing Zone | Queue Time | Critical bottleneck indicator |
| All Exits | Number Completed | Validate throughput matches real data |

### Create Result Dashboard:

1. **Results → Dashboard**
2. Add charts:
   - **Line Chart**: Queue lengths over time (all activities)
   - **Bar Chart**: Utilization by entity type
   - **Pie Chart**: Throughput distribution
   - **Time Series**: Total entities in system

---

## Part 6: Validation Run

### Step 1: Quick Test (10 minutes)

1. Set Run Length: 600 seconds
2. **Run → Start** (F5)
3. Watch animation:
   - EB vehicles appearing frequently (every ~17s)
   - WB vehicles very frequent (every ~11s)
   - Crossers occasional (every ~52s)
   - Posers moderate (every ~35s)

**Expected Behavior:**
- Vehicles queue at crossing zone
- Pedestrians cross in batches
- Some conflicts/waiting occurs
- No deadlocks or infinite queues

**If problems:**
- Entities not appearing → Check entry point distributions
- Infinite queues → Check capacity settings
- No conflicts → Check routing logic

### Step 2: Full Validation Run (90 minutes)

1. Set Run Length: 5400 seconds
2. Set Replications: 1 (for first test)
3. Run simulation
4. **Speed up**: Simulation → Speed → Fast

**Validate Results:**

| Metric | Expected (Real Data) | SIMUL8 Should Show | Acceptable Range |
|--------|----------------------|--------------------|------------------|
| EB Vehicles throughput | 315 in 90 min | 300-330 | ±5% |
| WB Vehicles throughput | 506 in 90 min | 480-530 | ±5% |
| Crossers throughput | 102 in 90 min | 97-107 | ±5% |
| Posers throughput | 150 in 90 min | 143-158 | ±5% |
| EB utilization | 70.1% | 65-75% | ±7% |
| WB utilization | 48.0% | 43-53% | ±10% |
| Avg crossing queue time | Low | < 30 seconds | - |

**If throughput doesn't match:**
- Too low → Check for bottlenecks (capacity too small)
- Too high → Check inter-arrival distributions
- Uneven → Check routing logic

---

## Part 7: Advanced Configuration

### Option A: Add Time-of-Day Variation

Your data is from a single 90-minute period. To model different times:

1. **Create Arrival Schedule**:
   - Simulation → Arrival Control
   - Define periods:
     ```
     08:00-09:00: Morning Peak (1.3x normal rate)
     12:00-13:00: Midday Tourist (1.5x pedestrian rate)
     17:00-18:00: Evening Peak (1.4x vehicle rate)
     11:00-12:00: Weekend (balanced)
     ```

2. **Apply to Entry Points**:
   - Right-click each entry → Arrivals → Schedule
   - Link to time periods

### Option B: Add Traffic Light Control

More realistic than priority rules:

1. **Add Visual Logic → Traffic Signal**
2. Configure cycles:
   ```
   Cycle Length: 90 seconds

   Phase 1: Vehicles (60s)
     - EB Green: 30s
     - WB Green: 30s
     - Pedestrian Red: 60s

   Phase 2: Pedestrians (30s)
     - Vehicle Red: 30s
     - Pedestrian Green: 30s
   ```

3. **Link to Activities**:
   - Traffic light controls entry to Crossing Zone
   - Entities wait at signal

### Option C: Add Costs

Use your cost analysis results:

1. **Simulation → Costs**
2. Add cost types:
   ```
   Infrastructure Cost: £5.21/day
   Operational Cost: £125/day
   Time Value Cost: £1,134/day
   Congestion Cost: £1,131/day
   Environmental Cost: £263/day
   TOTAL: £2,658/day
   ```

3. **Assign to Objects**:
   - Queue time → Time Value Cost (£20/hour per entity)
   - Long waits → Congestion Cost
   - Processing → Operational Cost

---

## Part 8: Optimization Experiments

Now that the model is validated, run "What-If" scenarios:

### Experiment 1: Increase EB Capacity

**Question**: Would adding an EB lane reduce congestion?

1. **Duplicate model**: Save as `abbey_road_exp1_eb_lanes.s8`
2. Change EB Lanes capacity: 5 → 6
3. Run 10 replications
4. **Compare results**:
   - Queue times (should decrease)
   - Utilization (should drop from 70% to ~59%)
   - Cost vs benefit

### Experiment 2: Pedestrian-Only Phases

**Question**: Would dedicated pedestrian crossing times help?

1. Implement traffic light (Option B above)
2. Try different cycle times:
   - Scenario A: 60s vehicle / 30s pedestrian
   - Scenario B: 45s vehicle / 45s pedestrian
   - Scenario C: 90s vehicle / 30s pedestrian

3. Measure:
   - Pedestrian wait times
   - Vehicle delays
   - Total system throughput

### Experiment 3: Separate Poser Lane

**Question**: Should photo-takers have a separate area?

**Rationale**: Posers are 52% slower than Crossers and have CV=1.95 (extremely variable)

1. Split pedestrian processing:
   - Crosser Crossing: Capacity 1, fast lane
   - Poser Area: Capacity 2, designated photo zone (off to side)

2. **Routing Logic**:
   - Crossers → Direct crossing
   - Posers → Separate area, then crossing

3. Compare:
   - Crosser wait times (should improve)
   - Overall pedestrian throughput
   - Safety (fewer conflicts)

---

## Part 9: Using Queueing Theory Results in SIMUL8

Your queueing analysis provides scientific capacity recommendations:

### From queueing_analysis_report.txt:

**EB Vehicles:**
- Recommended capacity: **5 servers** (optimal)
- Expected utilization: 70.1%
- Average wait: 4.6 seconds
- Performance: EXCELLENT

**WB Vehicles:**
- Recommended capacity: **7 servers** (optimal)
- Expected utilization: 48.2%
- Average wait: Very low
- Performance: EXCELLENT

**Crossers:**
- Recommended capacity: **1 server** (sufficient)
- Utilization: 58.0%
- Average wait: 22.7 seconds
- Performance: EXCELLENT

**Posers:**
- Recommended capacity: **2 servers** (buffer for variability)
- Utilization: 43.1%
- Average wait: 3.9 seconds
- Performance: EXCELLENT

### Apply These Settings:

1. **Set these as initial capacities** in your SIMUL8 model
2. **Validate** that simulation results match queueing predictions
3. **If they match** → Your model is correctly calibrated
4. **If they don't match** → Check:
   - Routing logic errors
   - Distribution imports
   - Priority rules interfering

---

## Part 10: Report Generation for Dissertation

### Results to Extract from SIMUL8:

1. **Run → Trial Results Manager**
2. Export to Excel:
   - Activity utilization statistics
   - Queue time statistics
   - Throughput by entity type
   - Confidence intervals (from 10 replications)

### Create Comparison Table:

| Metric | Real Data | Queueing Theory | SIMUL8 | Match? |
|--------|-----------|-----------------|--------|--------|
| EB throughput | 315/90min | - | [Your result] | ✓/✗ |
| WB throughput | 506/90min | - | [Your result] | ✓/✗ |
| EB utilization | - | 70.1% | [Your result] | ✓/✗ |
| WB utilization | - | 48.2% | [Your result] | ✓/✗ |
| EB wait time | - | 4.6s | [Your result] | ✓/✗ |
| Crosser wait | - | 22.7s | [Your result] | ✓/✗ |

**This validates your model!**

### Key Visualizations to Create:

1. **Utilization Chart**: Bar chart showing all 4 entity types
2. **Queue Length Time Series**: Line chart showing congestion over time
3. **Throughput Comparison**: Clustered bar (Real vs SIMUL8)
4. **Cost Analysis**: Stacked area chart showing cost breakdown
5. **Sensitivity Analysis**: Line charts showing impact of capacity changes

---

## Part 11: Common Issues and Solutions

### Issue 1: "Distributions don't import properly"

**Solution**:
- Use **Method A**: Import empirical distribution from CSV
- If fails, use **Method B**: Manual entry of mean/std
  - EB Inter-arrival: Mean=17.1s, Std=22.0s → Lognormal distribution
  - WB Inter-arrival: Mean=10.6s, Std=13.7s → Lognormal distribution

### Issue 2: "Simulation runs too slowly"

**Solution**:
- Disable animation: View → Animation Off
- Reduce visual complexity
- Increase time step: Simulation → Settings → Time Step = 1 second

### Issue 3: "Results don't match real data"

**Checklist**:
- [ ] Imported all 4 CSV files correctly?
- [ ] Used Column 5 for inter-arrivals?
- [ ] Used Column 6 for service times (pedestrians only)?
- [ ] Set correct capacities (5, 7, 1, 2)?
- [ ] Warm-up period enabled (600s)?
- [ ] Multiple replications run (min 10)?

### Issue 4: "Entities getting stuck/deadlock"

**Solution**:
- Check routing logic: Every activity must connect to an exit
- Check capacity > 0 for all activities
- Ensure Crossing Zone has multiple exits

### Issue 5: "High variability not captured"

**Your data has high CV (1.28-1.95)**

**Solution**:
- Use empirical distributions (import from CSV), NOT theoretical
- Increase buffer capacity in high-variability areas (Posers)
- Run longer simulations (multiple 90-min periods)
- Increase replications to 20-30 to capture variability

---

## Part 12: Checklist - Is Your Model Complete?

Before finalizing, verify:

### Data Import:
- [ ] All 4 CSV files imported successfully
- [ ] Entry point distributions show correct means
- [ ] Service time distributions imported for pedestrians
- [ ] Total entities in simulation ≈ 1,073 in 90 minutes

### Model Structure:
- [ ] 4 entry points (EB, WB, Crossers, Posers)
- [ ] 4 processing activities with correct capacities
- [ ] 1 central Crossing Zone (conflict point)
- [ ] 4 exit points
- [ ] Routing logic connects all paths

### Configuration:
- [ ] Time units = seconds
- [ ] Run length = 5400 seconds
- [ ] Warm-up period = 600 seconds
- [ ] Replications ≥ 10
- [ ] Results collection enabled on all activities

### Validation:
- [ ] Throughput matches real data (±5%)
- [ ] Utilization matches queueing theory (±10%)
- [ ] Animation looks realistic (no weird behavior)
- [ ] No deadlocks or infinite queues

### Documentation:
- [ ] Model saved with clear name
- [ ] Screenshots of model layout taken
- [ ] Results exported to Excel
- [ ] Comparison table created (Real vs Theory vs SIMUL8)

---

## Part 13: Next Steps - Building on This Model

### Phase 1: Validation Complete
✓ You are here - model built and validated

### Phase 2: Optimization
- Run experiments (capacity changes, traffic lights, etc.)
- Use OptQuest (SIMUL8's built-in optimizer)
- Find minimum-cost configuration

### Phase 3: Scenario Analysis
- Model different times of day
- Model seasonal variations (more tourists in summer)
- Model special events (concerts at Abbey Road Studios)

### Phase 4: Hybrid Modeling
- Add agent-based behavior (pedestrians choose crossing time)
- Add system dynamics (long-term traffic growth trends)
- Combine with genetic algorithms for optimal scheduling

### Phase 5: Dissertation
- Write methodology section (data collection → queueing theory → SIMUL8)
- Present results (validation → optimization → recommendations)
- Discuss limitations and future work

---

## Summary of Key Numbers

**Your Complete Dataset:**
- **Total entities**: 1,073 over 90 minutes
- **Throughput**: 717 entities/hour
- **Cost**: £2,658/day, £970,236/year

**Recommended Capacities (from Queueing Theory):**
- EB Lanes: **5 servers** (utilization: 70%)
- WB Lanes: **7 servers** (utilization: 48%)
- Crosser Crossing: **1 server** (utilization: 58%)
- Poser Crossing: **2 servers** (utilization: 43%)

**Key Finding:**
- **High variability** in all arrival patterns (CV > 1.0)
- **Posers extremely variable** (CV = 1.95)
- Requires empirical distributions, NOT theoretical
- Need capacity buffers beyond simple average-based planning

---

## Files You'll Use:

**Input Data:**
```
data set/wb_vehicles.csv      → WB Entry Point
data set/eb_vehicles.csv      → EB Entry Point
data set/crossers.csv         → Crosser Entry + Service Time
data set/posers.csv           → Poser Entry + Service Time
```

**Analysis Results:**
```
traffic_analysis_report.txt        → Throughput and cost metrics
variability_report.txt             → CV and distribution fitting
queueing_analysis_report.txt       → Capacity recommendations
resource_planning_report.txt       → Scenario comparisons
```

**Visualizations:**
```
time_analysis.png                  → Wait times and utilization
cost_analysis.png                  → Cost breakdown
variability_analysis.png           → CV and patterns
resource_planning_scenarios.png    → Capacity options
```

---

## Final Advice

**Do:**
- Use empirical distributions (import from CSV) for maximum accuracy
- Validate against queueing theory before experimenting
- Run multiple replications (10+) to get confidence intervals
- Document everything with screenshots and notes

**Don't:**
- Use theoretical distributions (Exponential, Normal) - your data is too variable
- Skip warm-up period - first 10 minutes are transient
- Trust single-run results - need statistical significance
- Over-complicate initially - start simple, add complexity gradually

**Remember:**
Your queueing theory analysis gives you the **theoretical optimum**. SIMUL8 lets you test **practical implementation** with realistic constraints and behaviors. Together, they provide a scientifically rigorous yet practically useful solution.

---

**You now have everything you need to build a complete, validated SIMUL8 model!**

Good luck with your project! 🚦🚶‍♂️🚗
