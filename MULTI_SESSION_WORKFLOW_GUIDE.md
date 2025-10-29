# Multi-Session Data Collection Workflow Guide
## 8 Observation Windows - Complete Process

---

## Overview

This guide covers collecting data from **8 separate one-hour observation windows** across different times and days to capture traffic pattern variations.

### Your 8 Observation Windows:

| Session | Day | Time | Period Type | Focus |
|---------|-----|------|-------------|-------|
| 01 | Monday | 08:00-09:00 | Morning Peak | Commuter traffic |
| 02 | Wednesday | 08:00-09:00 | Morning Peak | Commuter traffic |
| 03 | Tuesday | 12:00-13:00 | Midday Tourist | Tourist traffic |
| 04 | Thursday | 12:00-13:00 | Midday Tourist | Tourist traffic |
| 05 | Monday | 17:00-18:00 | Evening Peak | Commuter traffic |
| 06 | Friday | 17:00-18:00 | Evening Peak | Commuter + weekend |
| 07 | Saturday | 11:00-12:00 | Weekend | Pure tourist |
| 08 | Sunday | 11:00-12:00 | Weekend | Pure tourist |

---

## Complete Workflow

### Phase 1: Setup (One Time)

**1. Create folder structure:**

```bash
cd "C:\Users\c25038355\OneDrive - Cardiff University\Desktop\simul8"

mkdir observation_windows
mkdir observation_windows\session_01_morning_peak
mkdir observation_windows\session_02_morning_peak
mkdir observation_windows\session_03_midday_tourist
mkdir observation_windows\session_04_midday_tourist
mkdir observation_windows\session_05_evening_peak
mkdir observation_windows\session_06_evening_peak
mkdir observation_windows\session_07_weekend
mkdir observation_windows\session_08_weekend
mkdir final_combined
```

**2. Prepare video segments:**
- Extract each 1-hour video segment from your recordings
- Name them clearly (e.g., `video_mon_0800.mkv`, `video_wed_0800.mkv`, etc.)

---

### Phase 2: Data Collection (Per Session)

**For EACH of the 8 sessions, repeat this process:**

#### Step 1: Prepare Session

Navigate to session folder:
```bash
cd observation_windows\session_01_morning_peak
```

Copy video segment to folder (or reference from central location)

#### Step 2: Team Data Collection

**4-person team collects data:**
- Person 1: WB Vehicles → exports `wb_vehicles.csv`
- Person 2: EB Vehicles → exports `eb_vehicles.csv`
- Person 3: Crossers → exports `crossers.csv`
- Person 4: Posers → exports `posers.csv`

**Important reminders:**
- All 4 people watch the same video at the same time
- Synchronize start with countdown: "3, 2, 1, Play!"
- Each person focuses ONLY on their assigned entity type
- Export files with clear, session-specific names

#### Step 3: Merge Session Data

Run the session merger with metadata:

```bash
python ..\..\merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv "01" "Morning Peak" "Monday"
```

**Output:** `session_01_combined.csv` with these columns:
```
ID, Session_ID, Period_Type, Day_of_Week, Time (s), Entity, Type/Dir, Inter-Arrival (s), Service Time (s)
```

#### Step 4: Verify Session Data

Check the output:
- Total entries looks reasonable
- All 4 entity types present
- No obvious errors in timestamps
- Session metadata correct

#### Step 5: Track Completion

Update your tracking spreadsheet:
- Mark session as "Complete"
- Note total arrivals
- Record any issues or observations

---

### Phase 3: Repeat for All 8 Sessions

**Session 01: Monday Morning Peak (08:00-09:00)**
```bash
cd observation_windows\session_01_morning_peak
python ..\..\merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv "01" "Morning Peak" "Monday"
```

**Session 02: Wednesday Morning Peak (08:00-09:00)**
```bash
cd observation_windows\session_02_morning_peak
python ..\..\merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv "02" "Morning Peak" "Wednesday"
```

**Session 03: Tuesday Midday Tourist (12:00-13:00)**
```bash
cd observation_windows\session_03_midday_tourist
python ..\..\merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv "03" "Midday Tourist" "Tuesday"
```

**Session 04: Thursday Midday Tourist (12:00-13:00)**
```bash
cd observation_windows\session_04_midday_tourist
python ..\..\merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv "04" "Midday Tourist" "Thursday"
```

**Session 05: Monday Evening Peak (17:00-18:00)**
```bash
cd observation_windows\session_05_evening_peak
python ..\..\merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv "05" "Evening Peak" "Monday"
```

**Session 06: Friday Evening Peak (17:00-18:00)**
```bash
cd observation_windows\session_06_evening_peak
python ..\..\merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv "06" "Evening Peak" "Friday"
```

**Session 07: Saturday Weekend (11:00-12:00)**
```bash
cd observation_windows\session_07_weekend
python ..\..\merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv "07" "Weekend" "Saturday"
```

**Session 08: Sunday Weekend (11:00-12:00)**
```bash
cd observation_windows\session_08_weekend
python ..\..\merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv "08" "Weekend" "Sunday"
```

---

### Phase 4: Final Combination

After ALL 8 sessions are complete:

**1. Copy all session files to one location:**

```bash
cd observation_windows
copy session_01_morning_peak\session_01_combined.csv .
copy session_02_morning_peak\session_02_combined.csv .
copy session_03_midday_tourist\session_03_combined.csv .
copy session_04_midday_tourist\session_04_combined.csv .
copy session_05_evening_peak\session_05_combined.csv .
copy session_06_evening_peak\session_06_combined.csv .
copy session_07_weekend\session_07_combined.csv .
copy session_08_weekend\session_08_combined.csv .
```

**2. Run final combiner:**

```bash
cd ..
python combine_all_sessions.py
```

**Output:** `all_sessions_combined.csv` in the current directory

---

## Data Organization Checklist

### Before Each Session:
- [ ] Create session folder
- [ ] Prepare video segment
- [ ] Assign team roles (Person 1-4)
- [ ] Test annotation tool
- [ ] Verify everyone has correct video

### During Each Session:
- [ ] Synchronize start time
- [ ] Each person focuses on their entity type
- [ ] Record data systematically
- [ ] Communicate any issues immediately

### After Each Session:
- [ ] All 4 people export their CSV files
- [ ] Verify all 4 files exist
- [ ] Run merge_session_data.py
- [ ] Verify combined file has correct metadata
- [ ] Update tracking spreadsheet
- [ ] Backup individual CSVs

### After All 8 Sessions:
- [ ] Verify all 8 session_*_combined.csv files exist
- [ ] Run combine_all_sessions.py
- [ ] Verify final combined file
- [ ] Check statistics by period type
- [ ] Ready for SIMUL8 import

---

## Quality Checks

### Per-Session Quality Check:

**Verify each session file has:**
```python
# Expected columns:
ID, Session_ID, Period_Type, Day_of_Week, Time (s), Entity, Type/Dir, Inter-Arrival (s), Service Time (s)

# Expected metadata:
Session_ID: "01" through "08"
Period_Type: "Morning Peak", "Midday Tourist", "Evening Peak", or "Weekend"
Day_of_Week: Actual day name

# Expected entities:
- WB Vehicles
- EB Vehicles
- Crossers
- Posers
```

### Final Combined Quality Check:

**Verify final file has:**
- Total entries = sum of all 8 sessions
- All session IDs present (01-08)
- All 4 period types present
- All 4 entity types present
- Sequential IDs (no gaps)
- Realistic timestamps (0-3600s per session)

---

## Expected Output Format

### Session File (session_01_combined.csv):

```csv
ID,Session_ID,Period_Type,Day_of_Week,Time (s),Entity,Type/Dir,Inter-Arrival (s),Service Time (s)
1,01,Morning Peak,Monday,12.3,EB Vehicles,EB,0.0,-
2,01,Morning Peak,Monday,18.7,WB Vehicles,WB,0.0,-
3,01,Morning Peak,Monday,24.1,EB Vehicles,EB,11.8,-
4,01,Morning Peak,Monday,35.2,Crossers,Crosser,0.0,8.3
...
```

### Final Combined File (all_sessions_combined.csv):

```csv
ID,Session_ID,Period_Type,Day_of_Week,Time (s),Entity,Type/Dir,Inter-Arrival (s),Service Time (s)
1,01,Morning Peak,Monday,12.3,EB Vehicles,EB,0.0,-
2,01,Morning Peak,Monday,18.7,WB Vehicles,WB,0.0,-
...
523,02,Morning Peak,Wednesday,15.2,EB Vehicles,EB,0.0,-
...
1247,03,Midday Tourist,Tuesday,8.9,Posers,Poser,0.0,15.6
...
```

---

## SIMUL8 Analysis Options

### Option 1: Analyze by Period Type

Import `all_sessions_combined.csv` and use `Period_Type` column to filter:
- Compare "Morning Peak" vs "Evening Peak" vs "Midday Tourist" vs "Weekend"
- Analyze arrival patterns by time of day

### Option 2: Analyze by Day of Week

Use `Day_of_Week` column to compare:
- Weekdays (Mon-Fri) vs Weekends (Sat-Sun)
- Specific day patterns

### Option 3: Analyze Individual Sessions

Import individual `session_*_combined.csv` files separately:
- Deep dive into specific time periods
- Compare replicate sessions (e.g., two morning peaks)

### Option 4: Combined Analysis

Use full dataset to:
- Calculate overall arrival distributions
- Identify peak vs off-peak patterns
- Build comprehensive simulation model

---

## Time Estimates

### Per Session (1-hour video):
- **Data collection:** 1-1.5 hours (with 4-person team)
- **Export and merge:** 5 minutes
- **Verification:** 5 minutes
- **Total per session:** ~1.5-2 hours

### All 8 Sessions:
- **Total data collection:** 12-16 hours (spread across multiple days)
- **Final combination:** 10 minutes
- **Overall completion:** 2-3 weeks (if doing 2-3 sessions per week)

---

## Troubleshooting

### Problem: Session files won't combine
**Check:**
- All session files in same directory
- File names match pattern `session_*_combined.csv`
- All files have same column structure

### Problem: Missing metadata
**Fix:**
- Re-run merge_session_data.py with correct parameters
- Ensure session_id, period_type, and day_of_week are specified

### Problem: Duplicate IDs across sessions
**This is OK:**
- Each session has IDs 1, 2, 3...
- Final combiner will renumber globally
- Session_ID column distinguishes them

### Problem: Different entity counts across similar sessions
**This is expected:**
- Traffic varies day-to-day
- Replicate sessions show natural variation
- Document if difference is extreme (>50%)

---

## Success Criteria

You'll know you're successful when:

✅ All 8 session folders exist with complete data
✅ All 8 session_*_combined.csv files created
✅ Final all_sessions_combined.csv exists
✅ Total entries = sum of all sessions
✅ All metadata columns present and correct
✅ Statistics by period type show expected patterns
✅ Ready for SIMUL8 import and analysis

---

## Next Steps

1. **Start with Session 01** (Monday Morning Peak)
2. **Perfect your process** before moving to Session 02
3. **Do 2-3 sessions per week** to maintain quality
4. **Keep detailed notes** of any observations
5. **Compare replicate sessions** (e.g., two morning peaks) to validate consistency

Good luck with your multi-session data collection!
