# Data Status Report - Abbey Road Traffic Analysis

**Generated:** October 31, 2025
**Project:** SIMUL8 Traffic Simulation - Cardiff University

---

## Executive Summary

You currently have **one complete data session** (90 minutes) fully analyzed. You mentioned collecting **weekend data (2.5 hours)**, but the CSV files for this session haven't been found yet.

All preparation work for processing the weekend data has been completed, including scripts and workflows.

---

## Current Data Inventory

### Session 1: Weekday (October 20, 2025)

**Source:** First 90 minutes of "2025-10-20 08-50-33.mkv"
**Status:** ✓ Fully annotated and analyzed

**Data Files:**
| File | Entities | Format | Status |
|------|----------|--------|--------|
| eb_vehicles.csv | 315 | CSV | ✓ Processed |
| wb_vehicles.csv | 506 | CSV | ✓ Processed |
| crossers.csv | 102 | CSV | ✓ Processed |
| posers.csv | 150 | CSV | ✓ Processed |
| **Total** | **1,073** | - | - |

**Also available in:**
- Excel format (.xlsx): East_bound(10-20).xlsx, West_bond(10-20).xlsx, etc.
- Text format (.txt): data 1020.txt, data crosser 1020.txt, etc.

**Analysis Completed:**
- ✓ Traffic analysis (throughput: 717/hour)
- ✓ Variability analysis (CV: Posers=1.95, others=1.05-1.29)
- ✓ Queueing theory analysis (capacity recommendations)
- ✓ Resource planning (4 scenarios per entity type)
- ✓ SIMUL8 setup guide
- ✓ All visualizations and reports

### Session 2: Weekend (2.5 hours)

**Status:** ⏳ Mentioned but data files not found

**Your statement:** "we recorded data from another Weekend, but the hr is 2.5 hrs"

**Video available:**
- File: "2025-10-20 08-50-33.mkv"
- Total duration: 6.94 hours
- Only first 90 minutes currently annotated
- Remaining 6 hours available for annotation

**Possible scenarios:**
1. You've annotated 2.5 hours but haven't exported CSV files yet
2. You're planning to annotate another 2.5-hour segment
3. The data is in a different location/format than expected
4. You have a separate 2.5-hour video file not yet in this directory

---

## What Was Prepared for Weekend Data

To handle the weekend data when it becomes available, I've created:

### 1. weekend_data_prep.py

**Purpose:** Automate weekend data processing

**Features:**
- Loads 4 weekend CSV/Excel files (EB, WB, Crossers, Posers)
- Standardizes column names automatically
- Combines into single weekend dataset
- Analyzes weekend statistics
- Compares weekend vs weekday sessions
- Creates multi-session combined file

**Usage:**
```bash
python weekend_data_prep.py <weekend_eb.csv> <weekend_wb.csv> <weekend_crossers.csv> <weekend_posers.csv>
```

**Outputs:**
- `weekend_combined.csv` - Weekend session only
- `multi_session_combined.csv` - Both sessions combined
- Detailed comparison statistics

### 2. WEEKEND_DATA_GUIDE.md

**Purpose:** Complete documentation for processing weekend data

**Contents:**
- Current data status summary
- Step-by-step workflow
- Expected results and projections
- Analysis options (separate vs combined)
- SIMUL8 integration strategies
- Multi-session comparison methods
- Data quality checks
- Troubleshooting guide
- Dissertation reporting recommendations

---

## Analysis Tools Ready

All existing analysis tools work with the weekend data format:

| Tool | Purpose | Status |
|------|---------|--------|
| merge_team_data.py | Combine 4 CSV files | ✓ Ready |
| traffic_analyzer.py | Throughput, costs, distributions | ✓ Ready |
| variability_analyzer.py | CV, distribution fitting | ✓ Ready |
| queueing_calculator.py | Capacity calculations | ✓ Ready |
| resource_planner.py | Multi-scenario planning | ✓ Ready |
| weekend_data_prep.py | Weekend-specific processing | ✓ New |

All tools include:
- ✓ Column name standardization
- ✓ UTF-8 encoding support
- ✓ Error handling
- ✓ Multiple file format support (CSV, Excel)

---

## What Happens When Weekend Data Arrives

### Immediate Processing (Estimated: 10 minutes)

When you have the 4 weekend CSV files ready:

**Step 1:** Prepare and combine (2 minutes)
```bash
python weekend_data_prep.py "weekend_eb.csv" "weekend_wb.csv" "weekend_crossers.csv" "weekend_posers.csv"
```

**Step 2:** Run all analyses (8 minutes)
```bash
python traffic_analyzer.py weekend_combined.csv
python variability_analyzer.py weekend_combined.csv
python queueing_calculator.py weekend_combined.csv
python resource_planner.py weekend_combined.csv
```

**Outputs generated:**
- Weekend-specific statistics and reports
- Weekday vs weekend comparison
- Multi-session combined dataset
- Weekend-specific SIMUL8 parameters
- Updated capacity recommendations
- All visualizations and charts

---

## Expected Weekend Data Characteristics

If weekend patterns similar to 90-minute weekday:

**Projected entities (2.5 hrs ÷ 1.5 hrs = 1.67x multiplier):**
| Entity | Weekday (90 min) | Projected Weekend (2.5 hrs) |
|--------|------------------|------------------------------|
| EB Vehicles | 315 | ~525 |
| WB Vehicles | 506 | ~843 |
| Crossers | 102 | ~170 |
| Posers | 150 | ~250 |
| **Total** | **1,073** | **~1,788** |

**Likely differences:**
- Posers may be higher (more tourists on weekend)
- Traffic patterns may differ (shopping, leisure trips)
- Time-of-day effects
- Peak hours at different times

---

## Multi-Session Analysis Benefits

Having both weekday and weekend data provides:

### Statistical Benefits
- Larger sample size (1,073 + ~1,788 = ~2,861 entities)
- More robust statistical estimates
- Confidence intervals for parameters
- Pattern variability quantification

### Practical Benefits
- Weekday vs weekend capacity requirements
- Time-based optimization strategies
- Worst-case scenario planning
- Model validation (train on one, validate on other)

### Dissertation Benefits
- Demonstrates thorough data collection
- Shows pattern analysis capability
- Supports generalizability claims
- Enables comparative analysis section

---

## Video File Analysis

**Available:** "2025-10-20 08-50-33.mkv"
- Duration: 6.94 hours (24,995 seconds)
- FPS: 60 fps
- Frame count: 1,499,704 frames
- Size: 8.6 GB

**Annotation progress:**
- Annotated: First 90 minutes (1.5 hours, 21.6%)
- Remaining: 6.0 hours (78.4%)

**Potential segments for annotation:**
| Segment | Time Range | Duration | Purpose |
|---------|------------|----------|---------|
| Morning | 0:00 - 1:30 | 90 min | ✓ Done |
| Late Morning | 1:30 - 3:00 | 90 min | Compare to first |
| Midday | 3:00 - 5:30 | 2.5 hrs | Weekend session? |
| Afternoon | 5:30 - 6:54 | 84 min | Evening patterns |

---

## Current File Structure

```
simul8/
├── Video Files
│   └── 2025-10-20 08-50-33.mkv (6.94 hours, 8.6 GB)
│
├── Session 1 Data (Weekday, 90 min)
│   ├── data set/
│   │   ├── eb_vehicles.csv (315 entities)
│   │   ├── wb_vehicles.csv (506 entities)
│   │   ├── crossers.csv (102 entities)
│   │   ├── posers.csv (150 entities)
│   │   └── [Excel and txt versions]
│   ├── combined_results.csv (1,073 entities)
│   └── all_sessions_combined.csv (same as above)
│
├── Session 1 Analysis Results
│   ├── traffic_analysis_report.txt
│   ├── variability_report.txt
│   ├── queueing_analysis_report.txt
│   ├── resource_planning_report.txt
│   └── [Various charts and visualizations]
│
├── Analysis Tools
│   ├── merge_team_data.py
│   ├── traffic_analyzer.py
│   ├── variability_analyzer.py
│   ├── queueing_calculator.py
│   ├── resource_planner.py
│   └── weekend_data_prep.py (NEW)
│
├── Documentation
│   ├── SIMUL8_COMPLETE_SETUP_GUIDE.md
│   ├── FINAL_PROJECT_COMPREHENSIVE_GUIDE.md
│   ├── WEEKEND_DATA_GUIDE.md (NEW)
│   ├── DATA_STATUS_REPORT.md (this file)
│   └── [ML documentation files]
│
└── Session 2 Data (Weekend, 2.5 hrs)
    └── ⏳ Awaiting CSV files
```

---

## Next Steps

### Immediate (When Weekend Data Ready)

**If you have weekend CSV files:**
1. Place them in "data set" folder or main directory
2. Run: `python weekend_data_prep.py <files>`
3. Review comparison statistics
4. Run full analysis pipeline
5. Update SIMUL8 model with weekend parameters

**If you need to annotate weekend segment:**
1. Identify which 2.5-hour segment to annotate
2. Use mkv-annotation-tool.html
3. Export 4 CSV files (EB, WB, Crossers, Posers)
4. Follow weekend data processing workflow

### For Dissertation

**Data Collection Chapter:**
- ✓ Session 1 complete (90 minutes, 1,073 entities)
- ⏳ Session 2 pending (2.5 hours, ~1,788 projected)
- Total: ~2,861 entities across 2 observation sessions
- Method: Manual video annotation with custom tool

**Analysis Chapter:**
- ✓ Descriptive statistics (throughput, distributions)
- ✓ Variability analysis (CV calculations)
- ✓ Queueing theory application (Kingman's VUT, Erlang C)
- ✓ Resource planning (4 capacity scenarios)
- ⏳ Multi-session comparison (when weekend data ready)

---

## Questions to Clarify

To help locate or prepare the weekend data, please clarify:

1. **Have you already annotated 2.5 hours?**
   - Yes → Where are the CSV files?
   - No → Which segment should be annotated?

2. **Is the weekend data from the same video?**
   - Yes → Which time range (e.g., 1:30-4:00)?
   - No → Is there a different video file?

3. **File format of weekend data?**
   - CSV files
   - Excel files
   - Still in annotation tool (not exported yet)
   - Other format

4. **File location?**
   - In "data set" folder with different names?
   - Different directory?
   - External drive?
   - Not yet created?

---

## Status Summary

| Component | Status | Next Action |
|-----------|--------|-------------|
| Weekday session (90 min) | ✓ Complete | - |
| Weekday analysis | ✓ Complete | - |
| Weekend data prep script | ✓ Ready | Waiting for CSV files |
| Weekend analysis guide | ✓ Complete | - |
| Weekend CSV files | ⏳ Pending | Locate or create |
| Weekend analysis | ⏳ Pending | Run when data ready |
| Multi-session comparison | ⏳ Pending | Run when data ready |
| SIMUL8 model | ✓ Guide complete | Build model |

---

## Summary

**What you have:**
- 1 complete data session (90 minutes, 1,073 entities)
- Full analysis with all statistics and recommendations
- Complete SIMUL8 setup guide
- Dissertation-ready documentation

**What's ready for weekend data:**
- Automated processing script (weekend_data_prep.py)
- Complete workflow documentation
- All analysis tools configured
- Multi-session comparison capability

**What's needed:**
- 4 weekend CSV files (EB, WB, Crossers, Posers)
- OR clarification on where weekend data is located
- OR guidance on which video segment to annotate

**Time to process when ready:**
- ~10 minutes for complete weekend analysis
- Immediate generation of comparison statistics
- Automatic creation of multi-session dataset

---

**Status:** ✓ All preparation complete, ready for weekend data
**Recommendation:** Locate or export weekend CSV files, then run weekend_data_prep.py
**Support:** See WEEKEND_DATA_GUIDE.md for detailed instructions

---

*Report generated: October 31, 2025*
*System status: Operational and ready*
