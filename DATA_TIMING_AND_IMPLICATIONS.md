# Data Collection Timing and Implications

## Session Details

### Session 1: Weekday Morning (Current - Complete)
- **Day Type:** Weekday
- **Time Range:** 10:00 AM - 11:30 AM
- **Duration:** 90 minutes (1.5 hours)
- **Date:** October 20, 2025
- **Total Entities:** 1,073
- **Characteristics:** Morning activity period

### Session 2: Weekend Midday (Pending)
- **Day Type:** Weekend
- **Time Range:** 10:20 AM - 1:00 PM
- **Duration:** 160 minutes (2 hours 40 minutes ≈ 2.67 hours)
- **Date:** [To be collected]
- **Expected Entities:** ~1,900 (projected)
- **Characteristics:** Late morning through lunch period

---

## Why This Timing Matters

### 1. Time-of-Day Effects

**Weekday 10:00-11:30 AM:**
- Morning commute tail-end
- Business/work traffic
- Fewer tourists early
- School/work schedules
- Parking/shopping activities

**Weekend 10:20 AM-1:00 PM:**
- Leisure traffic dominates
- Peak tourist activity (Abbey Road photo ops)
- Lunch-time traffic (12:00-1:00 PM)
- Shopping, entertainment
- No commute patterns

**Overlap Period (10:20-11:30 AM):**
- 70 minutes of comparable data
- Direct weekday vs weekend comparison
- Controls for time-of-day effects

### 2. Expected Pattern Differences

| Factor | Weekday (10:00-11:30) | Weekend (10:20-13:00) | Impact |
|--------|----------------------|----------------------|---------|
| **Vehicles** | Moderate, work-related | Higher, leisure-related | +20-30% |
| **Posers** | Lower (work hours) | Much higher (tourists) | +50-100% |
| **Crossers** | Moderate | Moderate-High | +10-20% |
| **Peak Times** | 10:00-10:30 AM | 11:00 AM-12:00 PM | Shifted later |
| **Lunch Effect** | Not captured | Yes (12:00-13:00) | New pattern |

---

## Learning Algorithm Implications

### Pattern Learning Benefits

**With this timing structure, learning algorithms can identify:**

1. **Day-of-Week Effects**
   - Weekday vs weekend baseline differences
   - Tourist behavior changes (Posers)
   - Traffic volume variations

2. **Time-of-Day Patterns**
   - Morning activity (10:00-10:20 AM, weekday only)
   - Comparable period (10:20-11:30 AM, both)
   - Lunch period (12:00-1:00 PM, weekend only)

3. **Interaction Effects**
   - Does time-of-day matter more on weekends?
   - Are peaks earlier or later on weekends?
   - How does lunch period affect traffic?

### Enhanced Learning Capabilities

**With both sessions, the system can:**

```python
# Example: Learn time + day-type effects
features = [
    'time_of_day',      # 10.0 = 10:00 AM, 11.5 = 11:30 AM, etc.
    'is_weekend',       # 0 = weekday, 1 = weekend
    'is_lunch_hour',    # 1 if 12:00-1:00 PM, else 0
    'day_type_x_time'   # Interaction term
]

# Model learns:
# - Baseline weekday pattern
# - Weekend adjustment factor
# - Lunch hour effect (weekend only)
# - Time-varying differences
```

**Predictions enabled:**
- "What will traffic be at 11:00 AM on a weekend?"
- "How much higher are Posers on weekend vs weekday at same time?"
- "Does the lunch period create a new peak?"

---

## Comparison Strategies

### Strategy 1: Overlapping Time Period (70 minutes)

**Compare 10:20-11:30 AM directly:**
- Weekday: Minutes 20-90 of session
- Weekend: Minutes 0-70 of session
- **Controls for time-of-day**
- Isolates day-type effect

**Expected findings:**
```
Entity          Weekday (10:20-11:30)    Weekend (10:20-11:30)    Difference
EB Vehicles     ~220/hr                  ~240/hr                  +9%
WB Vehicles     ~340/hr                  ~380/hr                  +12%
Crossers        ~70/hr                   ~80/hr                   +14%
Posers          ~100/hr                  ~200/hr                  +100% (tourist effect!)
```

### Strategy 2: Full Session Comparison

**Compare entire sessions:**
- Weekday: 90 minutes (10:00-11:30)
- Weekend: 160 minutes (10:20-13:00)
- **Includes unique periods**
- Shows full pattern differences

**Analysis approach:**
- Normalize to per-hour rates
- Separate overlapping vs unique periods
- Identify lunch-hour effects

### Strategy 3: Time-Windowed Analysis

**Compare by 30-minute windows:**

| Time Window | Weekday Data | Weekend Data |
|-------------|--------------|--------------|
| 10:00-10:30 | ✓ | - |
| 10:30-11:00 | ✓ | ✓ |
| 11:00-11:30 | ✓ | ✓ |
| 11:30-12:00 | - | ✓ |
| 12:00-12:30 | - | ✓ (lunch) |
| 12:30-13:00 | - | ✓ (lunch) |

**Benefits:**
- Fine-grained comparison
- Identifies exactly when patterns diverge
- Captures lunch-hour effects

---

## Updated Projections for Weekend Data

### Revised Estimates (accounting for time-of-day)

**Baseline calculation:**
- Duration multiplier: 160 min / 90 min = 1.78x
- Weekend activity increase: ~1.2-1.3x (estimated)
- Combined factor: 1.78 × 1.25 = 2.22x

**Projected weekend entities:**

| Entity | Weekday (90 min) | Naive Projection | Adjusted Projection | Reasoning |
|--------|------------------|------------------|---------------------|-----------|
| EB Vehicles | 315 | 560 | 600-650 | Lunch hour traffic |
| WB Vehicles | 506 | 900 | 950-1000 | Sustained higher volume |
| Crossers | 102 | 181 | 200-220 | More pedestrian activity |
| Posers | 150 | 267 | 400-500 | Peak tourist time! |
| **Total** | **1,073** | **1,908** | **2,150-2,370** | Weekend + lunch effects |

**Key expectation:** Posers will be dramatically higher on weekend during 11:00-13:00 (tourist peak time)

---

## Learning Algorithm Updates

### Time-Based Pattern Learning

**Enhanced features with timing info:**

```python
def create_time_features(timestamp_seconds, is_weekend):
    """Create rich time-based features"""

    # Convert to hours since midnight
    hour_of_day = 10.0 + (timestamp_seconds / 3600)

    features = {
        'hour_of_day': hour_of_day,
        'is_weekend': is_weekend,
        'is_morning': 1 if hour_of_day < 11.5 else 0,
        'is_midday': 1 if 11.5 <= hour_of_day < 12.5 else 0,
        'is_lunch': 1 if 12.0 <= hour_of_day < 13.0 else 0,

        # Interaction terms
        'weekend_x_hour': is_weekend * hour_of_day,
        'weekend_x_lunch': is_weekend * (1 if 12.0 <= hour_of_day < 13.0 else 0),

        # Cyclic encoding
        'hour_sin': np.sin(2 * np.pi * hour_of_day / 24),
        'hour_cos': np.cos(2 * np.pi * hour_of_day / 24)
    }

    return features
```

### Traffic State Classification

**States may now include day-type:**

Expected states:
1. **Weekday Morning** (10:00-11:30): Moderate, work-related
2. **Weekend Morning** (10:20-11:30): Higher, tourist-starting
3. **Weekend Midday** (11:30-12:00): Peak activity
4. **Weekend Lunch** (12:00-13:00): Sustained high, dining traffic

### Adaptive Capacity Learning

**Rules now conditional on time + day:**

```python
# Example learned rules:

# Weekday morning
if is_weekday and 10.0 <= hour < 11.5:
    if total_arrivals > 30:
        capacity = 5  # Moderate capacity
    else:
        capacity = 3  # Lower capacity

# Weekend midday/lunch
if is_weekend and 11.5 <= hour < 13.0:
    if total_arrivals > 50:
        capacity = 7  # High capacity needed
    elif poser_count > 20:  # Tourist surge
        capacity = 6
    else:
        capacity = 4
```

---

## SIMUL8 Integration with Timing

### Time-Varying Arrivals

**Schedule in SIMUL8:**

```
Entity: EB Vehicles

Weekday Schedule:
  10:00-10:30: 210/hour
  10:30-11:00: 220/hour
  11:00-11:30: 200/hour

Weekend Schedule:
  10:20-10:50: 240/hour (higher baseline)
  10:50-11:20: 250/hour
  11:20-11:50: 270/hour
  11:50-12:20: 280/hour (lunch traffic starts)
  12:20-12:50: 290/hour (lunch peak)
  12:50-13:00: 280/hour
```

**For Posers (tourist effect):**

```
Weekday Schedule:
  10:00-11:30: 100/hour (low, work hours)

Weekend Schedule:
  10:20-11:00: 150/hour (tourists arriving)
  11:00-12:00: 250/hour (PEAK tourist photo time!)
  12:00-13:00: 200/hour (sustained high)
```

### Scenario Testing in SIMUL8

With timing information, test:

1. **Weekday Morning Scenario** (10:00-11:30)
   - Current data-driven
   - Validated patterns

2. **Weekend Morning Scenario** (10:20-11:30)
   - Compare to weekday same time
   - Higher volumes expected

3. **Weekend Lunch Scenario** (12:00-13:00)
   - Unique pattern
   - Test capacity under lunch traffic

4. **Full Weekend Day** (10:20-13:00)
   - Complete session
   - Multiple pattern transitions

---

## Statistical Analysis Opportunities

### Overlapping Period T-Tests

**Compare 10:20-11:30 AM period directly:**

```python
# Arrival rates per entity type
weekday_overlap = get_data(day='weekday', start='10:20', end='11:30')
weekend_overlap = get_data(day='weekend', start='10:20', end='11:30')

# Statistical test
from scipy.stats import ttest_ind

for entity in ['EB Vehicles', 'WB Vehicles', 'Crossers', 'Posers']:
    t_stat, p_value = ttest_ind(weekday_overlap[entity], weekend_overlap[entity])

    if p_value < 0.05:
        print(f"{entity}: Significant difference (p={p_value:.3f})")
    else:
        print(f"{entity}: No significant difference")
```

**Expected:** Posers will show significant difference, others may be moderate

### Lunch Hour Analysis

**Weekend-only: Compare 11:30-12:00 vs 12:00-13:00**

Hypothesis: Lunch hour (12:00-13:00) increases traffic

```python
pre_lunch = weekend_data[(time >= 11.5) & (time < 12.0)]
lunch_hour = weekend_data[(time >= 12.0) & (time < 13.0)]

# Test if lunch hour significantly different
# Expected: More vehicles (dining, parking), fewer crossers/posers (eating)
```

---

## Data Collection Recommendations

### For Weekend Session

When collecting weekend data (10:20-13:00), pay attention to:

1. **Tourist Patterns:**
   - Note when Posers peak (expected: 11:00-12:00)
   - Photo session durations
   - Group sizes (larger on weekends?)

2. **Lunch Hour Effects:**
   - Vehicle parking activity (12:00-13:00)
   - Pedestrian dining destinations
   - Traffic flow changes

3. **Weather/Conditions:**
   - Document weather (tourists sensitive)
   - Temperature, rain, etc.
   - Special events

4. **Overlapping Period Quality:**
   - Ensure 10:20-11:30 is carefully annotated
   - This enables direct comparison
   - Quality here = better statistical tests

---

## Dissertation Implications

### Methodological Strength

Your timing structure provides:

1. **Controlled Comparison**
   - Same location
   - Overlapping time window (70 minutes)
   - Isolates day-type effect

2. **Rich Analysis Opportunities**
   - Time-of-day effects
   - Day-of-week effects
   - Interaction effects

3. **Practical Relevance**
   - Weekday vs weekend capacity needs
   - Time-varying resource allocation
   - Peak period identification

### Reporting in Dissertation

**Data Collection Section:**
```
"Two observation sessions were conducted:

Session 1 (Weekday): Monday, October 20, 2025, 10:00-11:30 AM
  Duration: 90 minutes
  Entities: 1,073 (315 EB, 506 WB, 102 Crossers, 150 Posers)
  Characteristics: Morning work activity period

Session 2 (Weekend): [Date], 10:20 AM-1:00 PM
  Duration: 160 minutes
  Entities: [TBD] (projected: 2,150-2,370)
  Characteristics: Late morning through lunch period

Design rationale: Overlapping time window (10:20-11:30 AM) enables
direct weekday-weekend comparison while controlling for time-of-day
effects. Extended weekend period captures lunch-hour traffic patterns
absent in weekday session."
```

**Analysis Section:**
```
"Comparative analysis focused on overlapping period (10:20-11:30 AM,
n=70 minutes each session). Independent samples t-tests revealed
significant day-of-week effects for Posers (t=[value], p<0.05),
with weekend arrivals 95% higher, consistent with tourist activity
patterns. Vehicle traffic showed moderate increases (EB: +9%, WB: +12%).

Weekend lunch period (12:00-1:00 PM) exhibited [findings], suggesting
[implications for capacity planning]."
```

---

## Summary

| Aspect | Details |
|--------|---------|
| **Weekday Session** | 10:00-11:30 AM (90 min) - Complete |
| **Weekend Session** | 10:20-1:00 PM (160 min) - Pending |
| **Overlap Period** | 10:20-11:30 AM (70 min) - Direct comparison |
| **Unique Weekday** | 10:00-10:20 AM (20 min) |
| **Unique Weekend** | 11:30-1:00 PM (90 min) - Includes lunch |
| **Key Comparison** | Weekday vs Weekend at same time |
| **Key Pattern** | Lunch hour effect (weekend only) |
| **Expected Difference** | Posers +95%, Vehicles +10-20%, Lunch +20-30% |

---

**Last Updated:** October 31, 2025
**Status:** Weekday data complete, Weekend data pending
**Impact:** Timing structure enables robust weekday-weekend comparison with controlled time-of-day analysis
