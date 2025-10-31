# Weekend Data Processing Guide

## Current Data Status (as of Oct 31, 2025)

### Session 1: Weekday Morning Commute (Already Processed)
- **Day Type**: Weekday
- **Time Range**: 9:00 AM - 10:30 AM
- **Duration**: 90 minutes (1.5 hours)
- **Total Entities**: 1,073
  - EB Vehicles: 315
  - WB Vehicles: 506
  - Crossers: 102
  - Posers: 150
- **Throughput**: 717 entities/hour
- **Characteristics**: Morning commute/rush hour period
- **Video Source**: First 90 minutes of "2025-10-20 08-50-33.mkv"

### Session 2: Weekend Midday (Pending)
- **Day Type**: Weekend
- **Time Range**: 10:20 AM - 1:00 PM
- **Duration**: 160 minutes (2 hours 40 minutes)
- **Expected Entities**: 2,150-2,370 (projected)
  - EB Vehicles: ~600-650
  - WB Vehicles: ~950-1,000
  - Crossers: ~200-220
  - Posers: ~400-500 (peak tourist time!)
- **Characteristics**: Late morning through lunch period, leisure/tourist traffic
- **Overlap with Session 1**: Only 10 minutes (10:20-10:30 AM) - minimal overlap
- **Comparison Type**: Different time periods (commute vs leisure patterns)

### Available Video
- **File**: "2025-10-20 08-50-33.mkv"
- **Duration**: 6.94 hours
- **Annotated**: Session 1 only (first 90 minutes)
- **Remaining**: 6 hours available for additional annotation

---

## When You Have 2.5-Hour Weekend Data

Once you've manually annotated the 2.5-hour weekend segment and exported it to CSV files, follow these steps:

### Step 1: Organize Your Files

Place your 4 weekend CSV/Excel files in the "data set" folder or main directory:
- Weekend EB Vehicles file
- Weekend WB Vehicles file
- Weekend Crossers file
- Weekend Posers file

### Step 2: Prepare and Combine Weekend Data

Run the weekend data preparation script:

```bash
python weekend_data_prep.py "weekend_eb.csv" "weekend_wb.csv" "weekend_crossers.csv" "weekend_posers.csv"
```

**Replace the filenames** with your actual weekend data files.

This will:
- ✓ Load and standardize all 4 entity types
- ✓ Combine into single weekend dataset
- ✓ Analyze weekend session statistics
- ✓ Compare with existing 90-minute session
- ✓ Create multi-session combined dataset

**Output files:**
- `weekend_combined.csv` - Weekend session only (2.5 hours)
- `multi_session_combined.csv` - Both sessions combined

### Step 3: Run Complete Analysis on Weekend Data

```bash
# Traffic analysis
python traffic_analyzer.py weekend_combined.csv

# Variability analysis
python variability_analyzer.py weekend_combined.csv

# Queueing analysis
python queueing_calculator.py weekend_combined.csv

# Resource planning
python resource_planner.py weekend_combined.csv
```

This will generate all analysis reports for the weekend session:
- `traffic_analysis_report.txt`
- `variability_report.txt`
- `queueing_analysis_report.txt`
- `resource_planning_report.txt`
- Charts and visualizations

### Step 4: Multi-Session Comparison

To analyze both sessions together (90-min + 2.5-hour weekend):

```bash
# Analyze combined dataset
python traffic_analyzer.py multi_session_combined.csv
python variability_analyzer.py multi_session_combined.csv
python queueing_calculator.py multi_session_combined.csv
```

---

## Expected Results

### What to Expect from 2.5-Hour Weekend Data

**If weekend patterns are similar to 90-minute session:**
- EB Vehicles: ~525 entities (315 × 2.5/1.5)
- WB Vehicles: ~843 entities (506 × 2.5/1.5)
- Crossers: ~170 entities (102 × 2.5/1.5)
- Posers: ~250 entities (150 × 2.5/1.5)
- **Total**: ~1,788 entities
- **Throughput**: ~715 entities/hour

**Weekend patterns may differ due to:**
- Tourist activity (more Posers?)
- Different traffic patterns
- Time of day effects
- Weather conditions

### Key Comparisons to Look For

1. **Throughput Difference**
   - Is weekend busier or quieter?
   - By how much (%)?

2. **Entity Mix Changes**
   - More/fewer tourists (Posers)?
   - Traffic volume shifts?

3. **Variability Patterns**
   - Are arrival patterns more/less variable?
   - CV changes by entity type?

4. **Peak Hours**
   - Different peak times on weekends?
   - Duration of peaks?

5. **Resource Requirements**
   - Do weekend patterns need more/fewer servers?
   - Different capacity recommendations?

---

## Analysis Workflow Options

### Option A: Separate Sessions (Recommended for Comparison)

Analyze each session independently to identify differences:

```bash
# 90-minute weekday session (already done)
python traffic_analyzer.py combined_results.csv

# 2.5-hour weekend session (when ready)
python traffic_analyzer.py weekend_combined.csv

# Compare results manually
```

**Advantages:**
- Clear comparison between weekday vs weekend
- Identify time-of-day patterns
- Separate capacity requirements
- Better for dissertation analysis

### Option B: Combined Analysis (For Overall Patterns)

Merge all sessions for overall traffic characteristics:

```bash
python traffic_analyzer.py multi_session_combined.csv
```

**Advantages:**
- Larger sample size
- More robust statistics
- Overall system behavior
- Combined capacity planning

### Option C: Hybrid Approach (Best for Dissertation)

1. Analyze sessions separately (Option A)
2. Compare results to identify patterns
3. Combine for overall statistics (Option B)
4. Use separate analyses for time-based recommendations
5. Use combined analysis for general system design

---

## SIMUL8 Integration

### Single Session Models

**90-Minute Weekday Model:**
- Use `combined_results.csv`
- Current capacity recommendations (EB=5, WB=7, Crossers=1, Posers=2)

**2.5-Hour Weekend Model:**
- Use `weekend_combined.csv`
- Run queueing analysis to get weekend-specific capacities

### Multi-Session Model

For a comprehensive SIMUL8 model that represents both weekday and weekend:

1. **Create separate arrival distributions** for each session
2. **Use SIMUL8's schedule feature** to switch between patterns:
   - Weekday: Use 90-minute session distributions
   - Weekend: Use 2.5-hour session distributions
3. **Size resources** for worst-case (higher of the two)
4. **Run experiments** for different scenarios:
   - Weekday only
   - Weekend only
   - Mixed (5 weekdays + 2 weekend days)

---

## Data Quality Checks

When you have the weekend data, verify:

### Duration Check
```python
import pandas as pd
df = pd.read_csv('weekend_combined.csv')
max_time = df['Time (s)'].max()
print(f"Duration: {max_time/3600:.2f} hours")
# Should be close to 2.5 hours (9000 seconds)
```

### Entity Count Check
```python
print(f"Total entities: {len(df)}")
print(df.groupby('Entity').size())
# Should have reasonable counts for all 4 entity types
```

### Timestamp Check
```python
print(f"Min time: {df['Time (s)'].min()}")
print(f"Max time: {df['Time (s)'].max()}")
# Should start near 0 and end near 9000 (2.5 hours)
```

---

## Quick Reference Commands

```bash
# When you have weekend data files ready:

# Step 1: Prepare weekend data
python weekend_data_prep.py <eb> <wb> <crossers> <posers>

# Step 2: Run all analyses
python traffic_analyzer.py weekend_combined.csv
python variability_analyzer.py weekend_combined.csv
python queueing_calculator.py weekend_combined.csv
python resource_planner.py weekend_combined.csv

# Step 3: Multi-session analysis (optional)
python traffic_analyzer.py multi_session_combined.csv
python variability_analyzer.py multi_session_combined.csv
python queueing_calculator.py multi_session_combined.csv
```

---

## Troubleshooting

### Issue: "Could not find weekend data files"
**Solution:** Check file paths and names. Use full paths if needed:
```bash
python weekend_data_prep.py "data set/weekend_eb.csv" "data set/weekend_wb.csv" ...
```

### Issue: "Column name not found"
**Solution:** The script automatically handles column name mapping. If error persists, check that your CSV has these columns:
- ID
- Time (s)
- Entity
- Type/Dir (for vehicles)
- Inter-Arrival (s)
- Service Time (s)

### Issue: "Duration doesn't match expected 2.5 hours"
**Solution:**
- Check max timestamp in CSV
- Verify you annotated 2.5 hours (9000 seconds)
- Confirm you're using the correct segment of the video

---

## For Your Dissertation

### Multi-Session Benefits

Having multiple observation sessions strengthens your dissertation:

1. **Statistical Validity**
   - Larger sample size
   - More robust estimates
   - Confidence intervals

2. **Pattern Identification**
   - Weekday vs weekend differences
   - Time-of-day effects
   - Variability across conditions

3. **Model Validation**
   - Use Session 1 for model building
   - Use Session 2 for validation
   - Demonstrate generalizability

4. **Capacity Planning**
   - Peak vs off-peak requirements
   - Worst-case scenario planning
   - Time-based recommendations

### Reporting Results

**For each session, report:**
- Duration and entity counts
- Throughput (entities/hour)
- Inter-arrival time distributions
- Service time distributions
- CV values
- Capacity recommendations

**For comparison:**
- Throughput difference (%)
- Entity mix changes
- Variability differences
- Capacity requirement differences

**Example structure:**
```
Chapter: Data Collection
- Session 1 (Weekday, 90 min): 1,073 entities
- Session 2 (Weekend, 2.5 hrs): [TBD] entities
- Combined: [TBD] total entities
- Observation method: Manual video annotation
```

---

## Status Summary

**✓ Completed:**
- 90-minute weekday session (1,073 entities)
- Complete analysis (traffic, variability, queueing, resources)
- SIMUL8 setup guide
- Analysis tools tested and working

**⏳ Pending:**
- 2.5-hour weekend session data collection/export
- Weekend data analysis
- Multi-session comparison
- Weekend-specific SIMUL8 parameters

**📋 Ready for Next Steps:**
- weekend_data_prep.py script created
- All analysis tools configured
- Multi-session workflow prepared
- Documentation complete

---

**Last Updated:** October 31, 2025
**Status:** Ready for weekend data when available
**Next Action:** Export weekend CSV files and run weekend_data_prep.py
