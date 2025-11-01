# Stochastic vs Deterministic Modeling - Why Your System REQUIRES Stochastic Methods

## Critical Understanding

**Your traffic system is STOCHASTIC, not deterministic.**

This is not a choice - it's proven by your data. This guide explains why stochastic modeling is mandatory and how to implement it properly.

---

## Part 1: Evidence from Your Data

### Proof 1: High Variability (CV > 1.0)

**Your results:**

| Entity | Mean (s) | Std Dev (s) | CV | Interpretation |
|--------|----------|-------------|-----|----------------|
| EB Vehicles | 17.1 | 21.9 | **1.28** | High variability |
| WB Vehicles | 10.6 | 13.7 | **1.29** | High variability |
| Crossers | 35.3 | 37.3 | **1.06** | Moderate variability |
| Posers | 34.8 | 68.2 | **1.96** | EXTREME variability |

**What CV > 1.0 means:**
- CV = σ/μ = standard deviation / mean
- CV > 1.0 → Standard deviation EXCEEDS the mean
- **This is textbook stochastic behavior**

**Example (Posers):**
```
Mean = 34.8s
Std Dev = 68.2s (almost 2× the mean!)

This means:
- Some posers take 5 seconds
- Some take 180+ seconds
- Massive unpredictability
```

**Deterministic model would assume:** Everyone takes exactly 34.8s (WRONG!)
**Stochastic model recognizes:** Huge variability around 34.8s (CORRECT!)

### Proof 2: Non-Exponential Distributions

**Your enhanced variability analysis found:**

```
WB Vehicles Inter-Arrivals:
  Best Fit: Lognormal (NOT Exponential)
  CV = 1.11
  AIC = 3234 (beats Exponential by 164 points)
  K-S test: Rejected exponential assumption (p<0.001)
```

**Why this matters:**
- Exponential = memoryless (completely random)
- Lognormal = right-skewed (bunching + occasional long gaps)
- **Your data shows clustering behavior** (not uniform randomness)

**This proves:** Arrivals are stochastic BUT not simple Poisson!

### Proof 3: Time-Varying Behavior

**Your time-varying analysis showed:**

```
WB Vehicles CV over time:
  Window 9 (45-50 min): CV = 0.66 (relatively regular)
  Window 13 (65-70 min): CV = 2.06 (very chaotic)

3× difference in variability!
```

**What this means:**
- System behavior changes over time
- No single "average" captures reality
- **Inherent unpredictability**

### Proof 4: Peak Period Variability

**Your peak analysis:**

```
Peak Period (10:07-10:12 AM):
  Combined rate: 768 entities/hour
  But individual 1-minute windows varied:
    - Min: 580/hour
    - Max: 920/hour
  Within same 5-minute peak!
```

**Even during "peak":**
- 59% variation minute-to-minute
- Cannot predict exact arrivals
- **Stochastic fluctuations dominate**

---

## Part 2: The "Sneaky Average" Trap

### What Happens If You Use Deterministic Model

**Naive deterministic approach:**

```
"Average EB arrival = 17.1s apart
 → Create 1 vehicle every 17.1s exactly
 → Capacity = 1 lane handles this fine"
```

**DISASTER! Here's why:**

**Reality from your data:**
```
EB Inter-Arrival Times (actual):
  Min: 1.5s (vehicles very close!)
  Mean: 17.1s
  Max: 112.8s (long gap)
  CV = 1.28 (huge variability)
```

**What deterministic model misses:**

1. **Bunching:** Sometimes 5 vehicles arrive within 10 seconds
   - Deterministic: Never happens
   - Reality: Happens frequently

2. **Bursts:** Peak arrival rate can be 10× average
   - Deterministic: Constant rate
   - Reality: Highly variable

3. **Idle Periods:** Sometimes no arrivals for 100+ seconds
   - Deterministic: Never happens
   - Reality: Waste capacity during these times

4. **Queues:** With bunching, queues form even when average < capacity
   - Deterministic: No queues (capacity always exceeds average)
   - Reality: Queues inevitable with variability

### Numerical Example: The Capacity Trap

**Scenario:** WB Vehicles

**Deterministic calculation:**
```
Average inter-arrival: 10.6s
Average service time: 1.0s
Capacity needed: 1.0/10.6 = 0.09 servers
Conclusion: 1 server is MORE than enough (900% capacity!)
```

**Stochastic calculation (Kingman's VUT):**
```
Arrival rate (λ): 1/10.6 = 0.094 /s
Service rate (μ): 1/1.0 = 1.0 /s
CV_arrivals: 1.29
CV_service: 1.00
Servers (c): 2

Traffic intensity (ρ): λ/(c×μ) = 0.094/2.0 = 0.047 (4.7%)

Wait time = (ρ/(1-ρ)) × ((CV_a² + CV_s²)/2) × (1/μ)
          = (0.047/0.953) × ((1.29² + 1.0²)/2) × 1.0
          = 0.049 × 1.828 × 1.0
          = 0.090 seconds

With only 1 server:
ρ = 0.094 (9.4%)
Wait = (0.094/0.906) × 1.828 × 1.0 = 0.19s (still okay)

BUT...
```

**The hidden problem:**
```
During bursts (95th percentile):
  Arrival rate temporarily: 1/3s = 0.33/s
  With 1 server: ρ = 0.33 (33% utilization)
  Wait time: (0.33/0.67) × 1.828 = 0.90s

  During extreme bursts (seen in data):
    Arrival rate: 1/1.5s = 0.67/s
    With 1 server: ρ = 0.67 (67%)
    Wait time: (0.67/0.33) × 1.828 = 3.7s

    With 2 servers: ρ = 0.33 (33%)
    Wait time: (0.33/0.67) × 1.828 = 0.90s
```

**Conclusion:**
- Deterministic: 1 server "sufficient" (based on average)
- Stochastic: 2 servers REQUIRED (to handle variability)
- **Your queueing analysis recommended 2 servers - CORRECT!**

---

## Part 3: Why Queueing Theory is ESSENTIAL

### Queueing Theory Explicitly Accounts for Variability

**Standard formula (Kingman's VUT):**

```
W = (ρ/(1-ρ)) × ((CV_a² + CV_s²)/2) × (1/μ)
     ^^^^         ^^^^^^^^^^^^^^^^
   Utilization   VARIABILITY TERM
```

**Key insight:** Wait time proportional to CV²!

**Your Posers example:**
```
CV = 1.96
CV² = 3.84

This means:
  If CV were 1.0: CV² = 1.0 (baseline)
  Actual CV = 1.96: CV² = 3.84 (3.8× worse!)

Variability causes 3.8× longer waits than if service times were constant!
```

### Queueing Theory Provides Capacity Buffers

**Why can't you run at 100% utilization?**

**Deterministic thinking:**
```
"Arrivals = 10/hour, Capacity = 10/hour
 → 100% utilization is fine"
```

**Stochastic reality:**
```
ρ = 1.0 → W = (1.0/0.0) × ... = ∞ (infinite wait!)

Even ρ = 0.9:
  W = (0.9/0.1) × ((1.29² + 1.0²)/2) × 1.0
    = 9 × 1.828 = 16.5 seconds wait time!

But ρ = 0.5:
  W = (0.5/0.5) × 1.828 = 1.8 seconds
```

**Your recommended utilizations:**
- EB: 25-50% (not 90%!)
- WB: 25-50%
- Posers: 25-50%

**This is the buffer for variability!**

---

## Part 4: Stochastic Simulation in SIMUL8

### Required Elements for Proper Stochastic Modeling

#### 1. Use Empirical or Fitted Distributions (NOT Fixed Values)

**WRONG (Deterministic):**
```
Entry Point: WB Vehicles
Inter-Arrival Time: 10.6 seconds (fixed)
```

**RIGHT (Stochastic):**
```
Entry Point: WB Vehicles
Distribution: Lognormal
  Sigma: 0.90
  Scale: 6.60

This generates:
  Mean ≈ 9.88s
  CV ≈ 1.11
  Matches your data!
```

#### 2. Import Actual Data Distributions

**Best practice:**
```
SIMUL8 → Import Data → Select your combined_results.csv

Use column: "Inter-Arrival Time (s)"
SIMUL8 will fit distribution automatically
OR
Use empirical distribution (replays actual pattern)
```

**Advantages:**
- Exact match to reality
- Captures all nuances
- No assumptions about distribution shape

#### 3. Multiple Replications (CRITICAL!)

**Single run is MEANINGLESS:**
```
Run 1: Average wait = 2.3s
Run 2: Average wait = 1.8s
Run 3: Average wait = 2.7s
...

Each run different due to randomness!
```

**Required approach:**
```
SIMUL8 → Trials → Set Number of Trials = 100

Output will show:
  Mean wait time: 2.25s
  95% CI: [1.95s, 2.55s]
  Std Dev: 0.42s
```

**Why 100 runs?**
- Statistical significance
- Confidence intervals
- Capture full variability
- Robust conclusions

**Rule of thumb:**
```
n = (Z × σ / E)²

Where:
  Z = 1.96 (for 95% confidence)
  σ = estimated std dev (from pilot runs)
  E = desired margin of error

Example:
  If σ = 0.4s, E = 0.1s:
  n = (1.96 × 0.4 / 0.1)² = 61.5 ≈ 100 runs
```

#### 4. Report with Confidence Intervals

**WRONG:**
```
"Average wait time is 2.25 seconds"
```

**RIGHT:**
```
"Average wait time is 2.25s (95% CI: [1.95s, 2.55s], n=100)"
```

**What this means:**
- We're 95% confident true mean is between 1.95s and 2.55s
- Based on 100 independent simulation runs
- Accounts for stochastic variability

#### 5. Design for 95th Percentile, Not Average

**Your data analysis should report:**

```python
import numpy as np

wait_times = [all simulation results]

mean_wait = np.mean(wait_times)
p50_wait = np.percentile(wait_times, 50)  # Median
p95_wait = np.percentile(wait_times, 95)  # 95th percentile
p99_wait = np.percentile(wait_times, 99)  # 99th percentile

print(f"Mean: {mean_wait:.2f}s")
print(f"50th percentile: {p50_wait:.2f}s")
print(f"95th percentile: {p95_wait:.2f}s")  # ← Design for this!
print(f"99th percentile: {p99_wait:.2f}s")
```

**Why 95th percentile?**
- Average hides worst-case scenarios
- 95% of entities experience ≤ this wait time
- Only 5% experience worse
- Balances service quality and capacity

**Example from your data:**
```
If simulation shows:
  Mean wait: 2.3s
  95th percentile wait: 5.8s

Design decision:
  "We will size capacity so that 95% of vehicles wait ≤ 6 seconds"

This is MORE rigorous than:
  "We will size capacity for average wait of 2.3s" (ignores variability!)
```

---

## Part 5: Your Required Stochastic Approach

### Step 1: Recognize Stochastic Nature (✓ DONE)

**Evidence compiled:**
- CV > 1.0 for all entities ✓
- Non-exponential distributions ✓
- Time-varying variability ✓
- Peak period fluctuations ✓

**Conclusion:** System is strongly stochastic ✓

### Step 2: Queueing Theory with Variability (✓ DONE)

**Your implementation:**
- Kingman's VUT equation ✓
- Includes CV terms ✓
- Capacity recommendations account for variability ✓

**Results:**
- EB: 2 servers (not 1)
- WB: 2 servers (not 1)
- Utilization targets: 25-50% (not 80-90%)

### Step 3: Distribution Fitting (✓ DONE)

**Your enhanced analysis:**
- Tested 4 distributions ✓
- AIC and K-S tests ✓
- Found Lognormal best fit (not Exponential) ✓

**Ready for SIMUL8:**
- Distribution parameters extracted ✓
- Can input directly into SIMUL8 ✓

### Step 4: Stochastic Simulation Setup (TODO)

**Required in SIMUL8:**

**Entry Points:**
```
For each entity type:
  1. Use fitted distribution (Lognormal for vehicles)
  2. OR import empirical data from CSV
  3. NOT fixed inter-arrival time!
```

**Activities (Work Centers):**
```
Service Times:
  1. Use fitted distribution or empirical
  2. For Posers: Lognormal with CV=1.95
  3. NOT fixed service time!
```

**Trials:**
```
Number of Trials: 100 minimum
Warmup Period: 10 minutes (to reach steady state)
Run Length: 90 minutes (match observation period)
```

### Step 5: Statistical Analysis (TODO)

**Required outputs:**

**For each performance metric:**
```
Wait Time Results:
  Mean: X.XX s
  Std Dev: X.XX s
  95% CI: [lower, upper]
  95th Percentile: X.XX s
  Max Observed: X.XX s

Based on: 100 replications
```

**Comparison to queueing theory:**
```
Queueing Theory Prediction: 2.1s
Simulation Mean: 2.25s (95% CI: [1.95s, 2.55s])
Difference: 0.15s (7% higher)
Conclusion: Good agreement (theory within CI)
```

### Step 6: Design Decisions (TODO)

**Capacity sizing:**
```
Target: 95% of entities wait ≤ 5 seconds

From simulation (100 runs):
  With EB=2, WB=2:
    95th percentile wait: 4.8s ✓ (meets target)

  With EB=1, WB=2:
    95th percentile wait: 7.2s ✗ (exceeds target)

Decision: Use EB=2, WB=2
Justification: Meets 95th percentile target
```

---

## Part 6: Stochastic vs Deterministic Comparison

### Your Traffic System Classification

**Stochastic Elements (Random, Unpredictable):**
✓ Arrival times (CV=1.11-1.29)
✓ Service times (CV=1.0-1.96)
✓ Human behavior (tourist photo duration)
✓ External factors (upstream traffic lights)
✓ Decision-making (to cross or wait)

**Deterministic Elements (Fixed, Predictable):**
✓ Crossing width (physical constraint)
✓ Speed limits (regulatory)
✓ Signal timing (if present, fixed cycle)
✓ Number of lanes (infrastructure)

**System Type: Mixed (Predominantly Stochastic)**

### When Deterministic Models Work

**Valid for:**
- Manufacturing with fixed cycle times
- Conveyor belts at constant speed
- Scheduled train/bus arrivals (ideal)
- Chemical processes with precise control

**NOT valid for:**
- Human-driven systems (your case!)
- Traffic with driver variability (your case!)
- Service systems with random arrivals (your case!)
- Tourist behavior (definitely your case!)

### Your Required Methods Matrix

| Aspect | Deterministic | Stochastic | Your Choice |
|--------|--------------|------------|-------------|
| **Arrivals** | Fixed interval | Random (fitted dist) | **Stochastic** |
| **Service** | Fixed time | Random (high CV) | **Stochastic** |
| **Capacity** | Average-based | Buffer for variability | **Stochastic** |
| **Analysis** | Single run | Multiple replications | **Stochastic** |
| **Reporting** | Point estimate | Mean + CI | **Stochastic** |
| **Design** | Average case | 95th percentile | **Stochastic** |

---

## Part 7: Implementation Checklist

### SIMUL8 Stochastic Setup

**✓ Entry Points:**
- [ ] Use Lognormal distribution for EB Vehicles (σ=0.88, scale=6.5)
- [ ] Use Lognormal distribution for WB Vehicles (σ=0.90, scale=6.6)
- [ ] Use fitted/empirical distributions for Crossers and Posers
- [ ] NOT fixed inter-arrival times

**✓ Work Centers:**
- [ ] Service times from fitted distributions
- [ ] Poser service: High variability (CV=1.95)
- [ ] NOT fixed service times

**✓ Simulation Settings:**
- [ ] Number of Trials: 100 minimum
- [ ] Warmup Period: 10-15 minutes
- [ ] Run Length: 90 minutes
- [ ] Random seed: Different for each trial

**✓ Output Collection:**
- [ ] Wait time: Mean, SD, 95% CI, 95th percentile
- [ ] Queue length: Mean, max, 95th percentile
- [ ] Utilization: Mean, 95% CI
- [ ] Throughput: Mean, 95% CI

**✓ Validation:**
- [ ] Compare simulation mean to queueing theory
- [ ] Check if theory within simulation 95% CI
- [ ] Validate arrival patterns match data
- [ ] Check service time distributions match

### Dissertation Documentation

**✓ Methods Section:**
- [ ] Justify stochastic approach (cite CV > 1.0)
- [ ] Describe fitted distributions
- [ ] Explain multiple replications methodology
- [ ] State confidence level (95%)

**✓ Results Section:**
- [ ] Report all metrics with 95% CI
- [ ] Show 95th percentile values
- [ ] Compare stochastic simulation to queueing theory
- [ ] Discuss variability impact

**✓ Discussion Section:**
- [ ] Explain why deterministic approach would fail
- [ ] Highlight "sneaky average" trap
- [ ] Emphasize capacity buffer necessity
- [ ] Justify design for 95th percentile

---

## Part 8: Key Formulas for Stochastic Analysis

### Confidence Interval for Mean

```
CI = X̄ ± (t_{α/2, n-1} × s/√n)

Where:
  X̄ = sample mean
  t = t-distribution critical value
  s = sample standard deviation
  n = number of replications
  α = significance level (0.05 for 95%)

Example (100 runs):
  X̄ = 2.25s
  s = 0.42s
  t_{0.025, 99} ≈ 1.984

  CI = 2.25 ± (1.984 × 0.42/√100)
     = 2.25 ± 0.083
     = [2.17s, 2.33s]
```

### Required Sample Size

```
n = (Z × σ / E)²

For 95% CI with margin of error E:
  Z = 1.96
  σ = standard deviation (from pilot)
  E = desired margin of error

Example:
  σ = 0.4s (from pilot 10 runs)
  E = 0.1s (want precision to ±0.1s)

  n = (1.96 × 0.4 / 0.1)² = 61.5 ≈ 62 runs minimum

  Use 100 for safety
```

### Percentile Calculation

```python
import numpy as np

# From 100 simulation runs
wait_times = [run1_mean, run2_mean, ..., run100_mean]

# Calculate percentiles
p50 = np.percentile(wait_times, 50)  # Median
p95 = np.percentile(wait_times, 95)  # 95th percentile
p99 = np.percentile(wait_times, 99)  # 99th percentile

print(f"50% of runs: wait ≤ {p50:.2f}s")
print(f"95% of runs: wait ≤ {p95:.2f}s")  # Design target
print(f"99% of runs: wait ≤ {p99:.2f}s")  # Worst-case bound
```

---

## Summary

### Why Your System is Stochastic (Proof)

1. **CV > 1.0** for all entities (high variability) ✓
2. **Non-exponential distributions** (Lognormal found) ✓
3. **Time-varying behavior** (3× CV range) ✓
4. **Bunching and bursts** (seen in data) ✓

### Why Deterministic Approach Fails

1. **Ignores variability** (designs for average only)
2. **No capacity buffer** (leads to infinite queues)
3. **Misses worst-case** (95% of scenarios underestimated)
4. **Single-run simulation** (no statistical significance)

### Your Required Stochastic Methods

✓ **Queueing Theory:** Accounts for CV in capacity planning
✓ **Distribution Fitting:** Uses actual data patterns
✓ **Multiple Replications:** 100+ runs for confidence intervals
✓ **95th Percentile Design:** Not average-case planning
✓ **Statistical Reporting:** Mean ± CI, not point estimates

### Impact on Capacity

**Deterministic approach:** 1 server per direction (WRONG!)
**Stochastic approach:** 2 servers per direction (CORRECT!)

**Difference:** 100% more capacity needed due to variability

---

**This is not optional - it's mandatory for accurate analysis!**

**Your data proves the stochastic nature of your system. Your methods MUST reflect this reality.**

---

**Last Updated:** October 31, 2025
**Key Message:** Variability is not noise - it's the signal! Design for it, don't ignore it.
