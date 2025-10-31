# Quick Weekend Data Processing Checklist

## When You Have Weekend CSV Files Ready

### Step 1: Locate Your Files ☐
- [ ] Find your 4 weekend data CSV files:
  - [ ] Weekend EB Vehicles CSV
  - [ ] Weekend WB Vehicles CSV
  - [ ] Weekend Crossers CSV
  - [ ] Weekend Posers CSV

### Step 2: Run Preparation Script ☐
```bash
python weekend_data_prep.py "weekend_eb.csv" "weekend_wb.csv" "weekend_crossers.csv" "weekend_posers.csv"
```
Replace filenames with your actual file names.

**Expected output:**
- ✓ weekend_combined.csv created
- ✓ multi_session_combined.csv created
- ✓ Comparison statistics displayed

### Step 3: Run All Analyses ☐
```bash
python traffic_analyzer.py weekend_combined.csv
python variability_analyzer.py weekend_combined.csv
python queueing_calculator.py weekend_combined.csv
python resource_planner.py weekend_combined.csv
```

**Expected output:**
- ✓ traffic_analysis_report.txt
- ✓ variability_report.txt
- ✓ queueing_analysis_report.txt
- ✓ resource_planning_report.txt
- ✓ All visualizations (PNG files)

### Step 4: Review Results ☐
- [ ] Check weekend session statistics
- [ ] Compare with weekday session (90 min)
- [ ] Review capacity recommendations
- [ ] Note any significant differences

### Step 5: Update SIMUL8 (Optional) ☐
- [ ] Open your SIMUL8 model
- [ ] Import weekend_combined.csv
- [ ] Update arrival distributions
- [ ] Update capacity parameters
- [ ] Run experiments

---

## If You Need to Annotate Weekend Segment First

### Annotation Checklist ☐
- [ ] Open "2025-10-20 08-50-33.mkv" in video player
- [ ] Identify which 2.5-hour segment to annotate (e.g., 1:30-4:00)
- [ ] Open mkv-annotation-tool.html
- [ ] Load video file
- [ ] Annotate all 4 entity types:
  - [ ] EB Vehicles
  - [ ] WB Vehicles
  - [ ] Crossers
  - [ ] Posers
- [ ] Export each entity type as CSV
- [ ] Save files with clear names (e.g., "weekend_eb.csv")
- [ ] Proceed to Step 1 above

---

## Troubleshooting

**Can't find weekend_data_prep.py?**
- It should be in your main project folder (simul8/)
- Check: `ls -la weekend_data_prep.py`

**Script says "file not found"?**
- Use full paths: `"data set/weekend_eb.csv"`
- Check spelling of filenames
- Make sure files are CSV format

**Wrong duration in results?**
- Check max timestamp in your CSV: Should be ~9000 seconds (2.5 hours)
- Verify you annotated the correct time range

**Column name errors?**
- The script handles different column formats automatically
- If error persists, check your CSV has: ID, Time (s), Entity, Inter-Arrival (s)

---

## Quick Reference

**Current status:** 90-minute weekday session complete (1,073 entities)
**What's needed:** 2.5-hour weekend session data files
**Processing time:** ~10 minutes once files are ready

**See detailed guides:**
- WEEKEND_DATA_GUIDE.md - Complete instructions
- DATA_STATUS_REPORT.md - Current project status
- SIMUL8_COMPLETE_SETUP_GUIDE.md - Model building

---

**Last updated:** October 31, 2025
