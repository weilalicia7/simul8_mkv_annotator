# Queueing Theory & Variability Analysis for Traffic Resource Planning

## Overview

This guide explains how to use queueing theory and variability analysis to scientifically determine resource needs for the Abbey Road crossing, rather than making arbitrary capacity decisions.

**Why This Matters:**
- Traditional approaches guess at capacity (e.g., "let's use 2 lanes")
- Queueing theory calculates optimal capacity based on arrival patterns
- Variability analysis accounts for real-world fluctuations
- Results in data-driven resource planning with quantified performance metrics

---

## Core Queueing Theory Concepts

### 1. Traffic Intensity (Utilization)

**Formula:** ρ = λ / μ

Where:
- λ (lambda) = Arrival rate (entities per hour)
- μ (mu) = Service rate (entities per hour the system can handle)
- ρ (rho) = Utilization (0 to 1, where 1 = 100% utilized)

**Critical Insight:**
- ρ < 0.7: System is underutilized, possibly over-resourced
- ρ = 0.7-0.85: Optimal range (efficient but not overloaded)
- ρ > 0.85: System approaching saturation, queues grow rapidly
- ρ ≥ 1.0: System unstable, queues grow infinitely

### 2. Coefficient of Variation (CV)

**Formula:** CV = σ / μ

Where:
- σ (sigma) = Standard deviation of inter-arrival or service times
- μ (mu) = Mean of inter-arrival or service times

**What It Means:**
- CV = 0: No variability (perfectly regular, like a clock)
- CV = 1: Exponential distribution (typical random arrivals)
- CV > 1: High variability (bursty, irregular traffic)

**Why It Matters:**
- Higher variability = longer queues even with same average arrival rate
- Must account for variability when sizing resources

### 3. Kingman's Formula (VUT Equation)

**Most important formula for resource planning:**

**Average Wait Time in Queue:**

W_q = (ρ / (1 - ρ)) × ((CV_a² + CV_s²) / 2) × (1 / μ)

Where:
- ρ = Utilization (λ/μ)
- CV_a = Coefficient of variation of arrival process
- CV_s = Coefficient of variation of service process
- μ = Service rate

**Key Insights:**
1. Wait time increases exponentially as ρ approaches 1.0
2. Higher variability (CV) directly increases wait times
3. Even small increases in capacity can dramatically reduce waits when ρ is high

### 4. Little's Law

**Formula:** L = λ × W

Where:
- L = Average number in system
- λ = Arrival rate
- W = Average time in system

**Applications:**
- Calculate required queue space (how many waiting areas needed)
- Determine pedestrian crowding at crossing points
- Estimate vehicle queue lengths on road

---

## Applying Queueing Theory to Abbey Road

### Traffic System Classification

**Your system is an M/G/c queue:**
- M = Markovian (random) arrivals
- G = General service time distribution (varies by period)
- c = Multiple servers (crossing capacity, traffic light phases)

### Key Metrics to Calculate

1. **Arrival Rate (λ)** - From your 8 observation sessions
2. **Service Rate (μ)** - How fast the system processes entities
3. **Variability (CV)** - Fluctuation in arrivals and service
4. **Optimal Capacity (c)** - How many "servers" (crossing capacity) needed
5. **Performance Metrics** - Wait times, queue lengths, utilization

---

## Resource Planning Methodology

### Step 1: Analyze Variability in Your Data

Use the `variability_analyzer.py` script (provided below) to calculate:

```bash
python variability_analyzer.py all_sessions_combined.csv
```

**Outputs:**
- Mean arrival rate by period
- Standard deviation of inter-arrival times
- Coefficient of Variation (CV) for each entity type
- Variability classification (Low/Medium/High)

### Step 2: Calculate Theoretical Performance

For each observation period, calculate:

**Arrival Rate:**
```
λ = Total entities / Observation duration (hours)
```

**Service Rate:**
```
μ = Capacity / Average service time
```

**Required Capacity for Target Utilization:**
```
c_required = λ / (μ × ρ_target)
```

Where ρ_target = 0.75 (recommended safe utilization)

### Step 3: Account for Variability

**Adjust capacity using Kingman's approximation:**

If CV_a > 1 (high variability), increase capacity by:
```
Capacity adjustment = 1 + (CV_a - 1) × 0.5
```

**Example:**
- Base capacity needed: 2 lanes
- CV_a = 1.8 (high variability)
- Adjusted capacity: 2 × (1 + (1.8-1) × 0.5) = 2 × 1.4 = 2.8 ≈ 3 lanes

### Step 4: Validate in SIMUL8

1. Configure SIMUL8 with calculated capacity
2. Use empirical distributions from your data (not theoretical)
3. Run multiple replications (30+) to capture variability
4. Verify performance metrics match queueing theory predictions

---

## SIMUL8 Implementation

### Method 1: Direct Capacity Calculation

**In SIMUL8:**

1. **Set Arrival Distributions** (from your data):
   - Go to Entry Point → Distribution
   - Import inter-arrival times from CSV
   - SIMUL8 will fit best distribution

2. **Set Service Time Distributions**:
   - Go to Work Center → Timing
   - Import service times from CSV
   - Use empirical distribution if high variability

3. **Set Capacity** (from queueing calculations):
   - Work Center → Capacity
   - Enter calculated optimal capacity

4. **Configure Queue Policies**:
   - Queue → Discipline: FIFO (First In First Out)
   - Queue → Capacity: Set to L_q + 20% buffer

### Method 2: What-If Analysis with Different Capacities

**Create scenarios:**

| Scenario | Capacity | Expected ρ | Expected W_q |
|----------|----------|------------|--------------|
| Minimum  | c_min    | 0.90       | Very High    |
| Conservative | c_opt × 0.8 | 0.85 | High    |
| Optimal  | c_opt    | 0.75       | Moderate     |
| Safe     | c_opt × 1.2 | 0.60   | Low          |

Run each scenario and compare:
- Average wait times
- Maximum queue lengths
- 95th percentile wait times
- Cost implications

---

## Variability Impact Examples

### Example 1: Low Variability (CV = 0.5)

**Scenario:**
- Arrival rate: λ = 100 vehicles/hour
- Service rate: μ = 120 vehicles/hour per lane
- Capacity: c = 1 lane
- Utilization: ρ = 100/120 = 0.83

**Kingman's Formula:**
```
W_q = (0.83/(1-0.83)) × ((0.5² + 0.5²)/2) × (1/120)
W_q = 4.88 × 0.25 × 0.0083
W_q = 0.0101 hours = 36 seconds
```

### Example 2: High Variability (CV = 1.5)

**Same scenario, but CV = 1.5:**

```
W_q = (0.83/(1-0.83)) × ((1.5² + 1.5²)/2) × (1/120)
W_q = 4.88 × 2.25 × 0.0083
W_q = 0.0912 hours = 328 seconds (5.5 minutes!)
```

**Impact of Variability:**
- Same utilization (83%)
- 9× longer wait times due to variability alone!

**Solution:** Increase capacity to reduce ρ and compensate for variability

---

## Multi-Server Queue Formulas

### Erlang C Formula (for c servers)

**Probability of waiting:**

P(Wait) = (Erlang_C) = C(c, λ/μ) / [C(c, λ/μ) + (1 - λ/(cμ)) × (cμ/λ)^c × c!]

**Where:**
- c = Number of servers (lanes, crossing capacity)
- λ/μ = Offered load

**This is complex - use the Python calculator provided below**

### Average Wait Time (M/M/c):

W_q = P(Wait) × (1/(cμ - λ))

---

## Resource Planning Decision Framework

### Traffic Light Cycle Optimization

**Current State Analysis:**
1. Measure green time for each direction
2. Calculate effective service rate: μ = (Green time / Cycle time) × Flow capacity
3. Calculate ρ for each direction

**Optimization Goal:**
Balance utilization across all directions

**Formula:**
```
Green_time_optimal = (λ_direction / Σλ_all) × Available_green_time
```

**Constraints:**
- Minimum pedestrian crossing time (safety)
- Minimum vehicle green time (efficiency)
- All-red clearance interval (safety)

### Pedestrian Crossing Capacity

**Factors:**
1. Crossing width (meters)
2. Pedestrian flow rate (ped/meter/second)
3. Crossing time requirement

**Capacity Calculation:**
```
Capacity = (Width × Flow_rate) / (Crossing_time / Green_phase)
```

**Typical Values:**
- Flow rate: 1.3 ped/meter/second
- Crossing time: Width × 1.2 m/s (walking speed)
- Minimum green: 7 seconds + (Width / 1.2)

### Multi-Period Resource Allocation

**Challenge:** Different periods have different λ (arrivals)

**Solution:** Size resources for peak period, optimize control for off-peak

| Period | λ | Optimal c | Strategy |
|--------|---|-----------|----------|
| Morning Peak | 180/hr | 3 | Full capacity |
| Midday Tourist | 120/hr | 2 | Adaptive signals |
| Evening Peak | 200/hr | 3 | Full capacity |
| Off-Peak | 60/hr | 1 | Timed signals |

---

## Practical Steps for Your Project

### Phase 1: Data Analysis (Week 1)

1. Run `variability_analyzer.py` on your combined data
2. Calculate CV for each entity type and period
3. Identify high-variability periods (CV > 1.2)
4. Calculate mean arrival and service rates

### Phase 2: Theoretical Calculations (Week 1)

1. Use `queueing_calculator.py` to compute:
   - Optimal capacity for each period
   - Expected wait times
   - Queue lengths
   - Utilization targets

2. Create resource planning table:
   - Period → Arrivals → Variability → Capacity needed

### Phase 3: SIMUL8 Validation (Week 2-3)

1. Build model with calculated capacities
2. Import empirical distributions from data
3. Run 30+ replications
4. Compare simulation results to theoretical predictions
5. Adjust for discrepancies

### Phase 4: Optimization (Week 3-4)

1. Use queueing insights to guide optimization:
   - Don't optimize beyond ρ = 0.65 (diminishing returns)
   - Focus on high-variability periods
   - Balance multiple objectives

2. Test scenarios:
   - Baseline (current state)
   - Optimized signals (from queueing theory)
   - Adaptive capacity (dynamic allocation)

---

## Common Queueing Models for Traffic

### Model Selection Guide

| Model | Description | When to Use |
|-------|-------------|-------------|
| M/M/1 | Single server, exponential service | Simple intersection, one lane |
| M/M/c | Multiple servers, exponential service | Multi-lane road, parallel crossings |
| M/G/1 | Single server, general service | Variable service times |
| M/G/c | Multiple servers, general service | **Use for Abbey Road** |
| G/G/1 | General arrivals, general service | Highly variable both arrival & service |

**For Your Project:** M/G/c or G/G/c

- Arrivals: Somewhat random (M) or clustered (G)
- Service: Variable by pedestrian type (G)
- Servers: Multiple crossing points/directions (c)

---

## Performance Metrics from Queueing Theory

### Metrics You Should Calculate

1. **W_q** - Average wait time in queue
   - Target: < 60 seconds for good service
   - Critical: > 120 seconds indicates severe congestion

2. **W** - Average time in system (W_q + service time)
   - Used for total delay cost calculations

3. **L_q** - Average queue length
   - Determines space requirements
   - Safety consideration for pedestrians

4. **L** - Average number in system
   - Indicates overall congestion level

5. **P(W > t)** - Probability wait exceeds threshold
   - E.g., P(W > 90 sec) - what % wait more than 90 seconds?

### 95th Percentile Wait Time

**More important than average:**

W_95 ≈ W_q × 3 (rule of thumb for M/M/c)

**Why it matters:**
- Captures worst-case scenarios most users experience
- Better metric for customer satisfaction
- Used in service level agreements

---

## Integration with Cost Analysis

### Time Value Cost Refinement

**From queueing theory:**
```python
# Instead of average wait time
time_cost_simple = λ × W_q × Value_of_time

# Use distribution of wait times
time_cost_accurate = Σ[P(W = t) × t × Value_of_time]
```

### Resource Cost vs Service Cost Tradeoff

**Total Cost Function:**
```
TC = (Resource_cost × c) + (Delay_cost × W_q)
```

**Optimal capacity:**
```
c* = argmin(TC)
```

This is the capacity that minimizes total cost (not just resource cost)

---

## Advanced Topics

### Non-Stationary Arrivals (Time-Varying λ)

**Problem:** Arrival rate changes within observation period

**Solution:** Piecewise-stationary approximation
- Divide period into smaller intervals (15-min windows)
- Calculate λ for each interval
- Size resources for peak interval
- Use adaptive control for off-peak

### Priority Queuing

**If emergency vehicles or special pedestrians:**

Use M/M/c with priority classes:
- Class 1: Emergency vehicles (highest priority)
- Class 2: Regular vehicles
- Class 3: Pedestrians

**Average wait for class i:**
```
W_q,i = W_q,baseline × (1 / (1 - ρ_higher_priority))
```

### Network Effects

**Abbey Road is part of larger network:**

Consider:
1. Upstream congestion affects arrival patterns
2. Downstream congestion affects service times
3. Jackson Network theory for connected queues

---

## Validation Checklist

Use these checks to ensure your queueing analysis is correct:

1. **Stability Check:** ρ < 1 for all periods
   - [ ] All calculated ρ values < 1.0

2. **Little's Law Validation:**
   - [ ] L_calculated ≈ λ × W_measured
   - [ ] Discrepancy < 10%

3. **CV Reasonableness:**
   - [ ] CV_arrivals between 0.5 and 2.0
   - [ ] CV_service between 0.3 and 1.5

4. **Wait Time Sanity:**
   - [ ] W_q increases as ρ increases
   - [ ] W_q → ∞ as ρ → 1

5. **Simulation Match:**
   - [ ] SIMUL8 results within 20% of queueing predictions
   - [ ] If not, check distribution assumptions

---

## Key References

### Essential Formulas Summary

**Traffic Intensity:**
```
ρ = λ / (c × μ)
```

**Coefficient of Variation:**
```
CV = σ / μ
```

**Kingman's VUT:**
```
W_q ≈ (ρ/(1-ρ)) × ((CV_a² + CV_s²)/2) × (1/μ)
```

**Little's Law:**
```
L = λ × W
```

**Required Capacity:**
```
c = λ / (μ × ρ_target)
```

**Adjusted for Variability:**
```
c_adjusted = c × [1 + (CV - 1) × k]
```
Where k ≈ 0.5 for moderate variability adjustment

---

## Tools Provided

### 1. variability_analyzer.py
Analyzes your CSV data to extract:
- Arrival rates by period
- Coefficient of variation
- Variability classification
- Distribution fitting

### 2. queueing_calculator.py
Calculates theoretical performance:
- Wait times (Kingman's formula)
- Queue lengths (Little's Law)
- Required capacity
- Multi-server probabilities (Erlang C)

### 3. resource_planner.py
Generates resource planning recommendations:
- Optimal capacity by period
- Cost-performance tradeoffs
- Scenario comparisons
- SIMUL8 configuration suggestions

---

## Expected Outcomes

By applying queueing theory, you will:

1. **Quantify Performance:**
   - Replace "seems busy" with "ρ = 0.87, critical threshold"
   - Replace "long waits" with "W_q = 127 seconds, 95th percentile = 285 seconds"

2. **Optimize Resources:**
   - Calculate exact capacity needed (not guess)
   - Balance cost vs service level mathematically
   - Justify resource allocation with formulas

3. **Predict Impact:**
   - Before building changes, predict performance
   - Test "what-if" scenarios with equations
   - Understand variability impact quantitatively

4. **Academic Rigor:**
   - Apply established OR theory
   - Validate simulation with analytical methods
   - Demonstrate advanced analytical capability

---

## Next Steps

1. **Install tools:**
   ```bash
   pip install -r requirements_queueing.txt
   ```

2. **Analyze your data:**
   ```bash
   python variability_analyzer.py all_sessions_combined.csv
   ```

3. **Calculate requirements:**
   ```bash
   python queueing_calculator.py all_sessions_combined.csv
   ```

4. **Generate resource plan:**
   ```bash
   python resource_planner.py all_sessions_combined.csv
   ```

5. **Implement in SIMUL8:**
   - Follow configuration guide
   - Run validation experiments
   - Compare theoretical vs simulation results

---

**Remember:** Queueing theory provides the "what should be" (theoretical optimum), while simulation provides "what will be" (realistic performance with all constraints). Use both together for best results.
