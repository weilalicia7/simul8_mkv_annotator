# Quick Start: Queueing Theory Resource Planning

## Overview

This quick start guide walks you through using queueing theory and variability analysis to scientifically determine optimal resource requirements for your traffic system.

**Why Queueing Theory?**
- Replaces guesswork with mathematical optimization
- Accounts for variability in arrival patterns
- Calculates exact capacity needed for target performance
- Validates simulation results with analytical models

---

## Installation

```bash
pip install -r requirements_queueing.txt
```

---

## Three-Step Workflow

### Step 1: Analyze Variability

**Purpose:** Understand arrival patterns and fluctuations

**Command:**
```bash
python variability_analyzer.py all_sessions_combined.csv
```

**What It Does:**
- Calculates arrival rates for each period/entity type
- Computes Coefficient of Variation (CV) - measure of variability
- Classifies variability as Low/Medium/High
- Fits probability distributions to your data

**Outputs:**
- `variability_report.txt` - Detailed text report
- `variability_metrics.json` - Machine-readable metrics
- `variability_analysis.png` - Visualization charts

**Key Metrics to Review:**
- **CV < 0.75:** Low variability (regular arrivals)
- **CV 0.75-1.25:** Medium variability (random arrivals)
- **CV > 1.25:** High variability (bursty arrivals)

**Example Output:**
```
GROUP: Morning Peak - WB_Vehicle
==================================
ARRIVAL PATTERN:
  Total Arrivals: 245
  Mean Arrival Rate: 122.50 entities/hour
  Mean Inter-Arrival Time: 29.39 seconds
  Coefficient of Variation (CV): 1.45
  Variability Classification: High (Bursty arrivals)

QUEUEING THEORY IMPLICATIONS:
  - High variability: Requires significant capacity buffer
  - Recommended max utilization: 65%
  - Consider: Capacity increase of 22%
```

---

### Step 2: Calculate Queueing Metrics

**Purpose:** Apply queueing formulas to determine capacity requirements

**Command:**
```bash
python queueing_calculator.py all_sessions_combined.csv 60
```

Where `60` = service rate (entities per hour per server)

**Typical Service Rates:**
- Vehicles per lane: 50-80 per hour
- Pedestrians per crossing: 100-150 per hour
- Mixed traffic: 60 per hour (conservative)

**What It Does:**
- Implements Kingman's VUT formula (accounts for variability)
- Calculates Erlang C (for multi-server systems)
- Uses Little's Law (queue lengths)
- Determines optimal capacity for each period

**Outputs:**
- `queueing_analysis_report.txt` - Detailed calculations
- `queueing_results.json` - Machine-readable results

**Key Metrics Calculated:**
- **W_q:** Average wait time in queue (seconds)
- **L_q:** Average number in queue
- **ρ (rho):** Utilization (should be 0.65-0.85)
- **P(Wait):** Probability of having to wait
- **Optimal servers:** Recommended capacity

**Example Output:**
```
ANALYSIS: Morning Peak - WB_Vehicle
====================================
INPUT PARAMETERS:
  Arrival Rate (λ): 122.50 entities/hour
  Service Rate (μ): 60.00 entities/hour/server
  Number of Servers (c): 2
  Utilization (ρ): 102% - UNSTABLE!

PERFORMANCE METRICS:
  Average Wait in Queue: INFINITE
  Performance Classification: CRITICAL - System near capacity

RECOMMENDATIONS:
  Minimum Servers Required: 3
  Optimal Servers: 3
  Target Utilization: 75%
```

**Critical Indicators:**
- ρ ≥ 1.0 → System unstable, increase capacity immediately
- ρ > 0.85 → High congestion, consider increasing capacity
- W_q > 120s → Unacceptable wait times

---

### Step 3: Generate Resource Plan

**Purpose:** Create implementation scenarios with cost-benefit analysis

**Command:**
```bash
python resource_planner.py 10000
```

Where `10000` = cost per server/lane (£)

**What It Does:**
- Combines variability and queueing results
- Generates 4 scenarios per period/entity:
  1. Minimum Cost (highest utilization)
  2. Conservative (85% target utilization)
  3. Optimal (75% target utilization)
  4. Safe (65% target utilization)
- Calculates costs for each scenario
- Recommends best option balancing cost and performance

**Outputs:**
- `resource_planning_report.txt` - Scenario comparison
- `resource_scenarios.json` - All scenarios with metrics
- `resource_planning_scenarios.png` - Visual comparison

**Example Output:**
```
RESOURCE SCENARIOS: Morning Peak - WB_Vehicle
==============================================
Scenario            Cap   Util     Wait(s)    Queue    Daily £      Annual £       Score
------------------------------------------------------------------------------------
Minimum Cost        2     102%     999+       99+      458.50       167,352.50     0
Conservative        2     88%      187        4.2      512.30       187,989.50     42
Optimal             3     68%      45         2.1      687.90       251,083.50     89
Safe                4     51%      18         0.8      863.50       315,177.50     76

RECOMMENDED: Optimal
  Capacity: 3 servers
  Utilization: 68%
  Expected Wait: 45 seconds
  Annual Cost: £251,083.50
```

---

## Understanding the Results

### Utilization (ρ)

**Formula:** ρ = λ / (c × μ)

**Interpretation:**
- **ρ < 0.65:** Over-resourced, wasting capacity
- **ρ = 0.65-0.75:** Optimal range (recommended)
- **ρ = 0.75-0.85:** Acceptable but monitor closely
- **ρ > 0.85:** Critical - waits increase exponentially
- **ρ ≥ 1.0:** Unstable - system cannot handle load

**Why Not Target 100% Utilization?**
Because wait times explode as ρ → 1.0:
- At ρ = 0.70: W_q = 30 seconds
- At ρ = 0.85: W_q = 90 seconds
- At ρ = 0.95: W_q = 400 seconds
- At ρ = 1.00: W_q = ∞

### Coefficient of Variation (CV)

**Formula:** CV = σ / μ

**Impact on Capacity:**
- CV = 0.5 → Can operate at 85% utilization safely
- CV = 1.0 → Target 75% utilization
- CV = 1.5 → Target 65% utilization (need 15% extra capacity)

**Example:**
If CV = 1.5 (high variability), add capacity buffer:
```
Base capacity needed: 2 lanes
Variability adjustment: +23%
Final capacity: 3 lanes
```

### Service Level Probabilities

**P(Wait > 60s):** Probability wait exceeds 60 seconds

**Target Service Levels:**
- Excellent: P(Wait > 60s) < 10%
- Good: P(Wait > 60s) < 25%
- Acceptable: P(Wait > 60s) < 40%
- Poor: P(Wait > 60s) > 40%

---

## Applying Results in SIMUL8

### Configuration Workflow

1. **For Each Period/Entity Type:**

   a. Note recommended capacity from resource planner

   b. In SIMUL8:
   - Work Center → Capacity = [recommended value]
   - Queue → Capacity = [L_q from queueing analysis] + 20% buffer

   c. Set arrival distribution:
   - Import inter-arrival times from CSV
   - Or use best-fit distribution from variability analyzer

2. **Run Validation Simulation:**

   - Warm-up period: 1 hour
   - Run length: 8 hours minimum
   - Replications: 30+
   - Collect: Wait times, utilization, queue lengths

3. **Compare to Queueing Predictions:**

   | Metric | Queueing Theory | SIMUL8 | Difference |
   |--------|-----------------|---------|------------|
   | ρ      | 68%            | 71%     | +3%        |
   | W_q    | 45s            | 52s     | +7s        |
   | L_q    | 2.1            | 2.4     | +0.3       |

   If differences > 20%, investigate:
   - Arrival distribution fit
   - Service time assumptions
   - Queue discipline
   - System constraints not modeled

---

## Real Example Walkthrough

### Scenario: Morning Peak, Westbound Vehicles

**Step 1: Variability Analysis**
```
Mean arrival rate: 180 vehicles/hour
CV inter-arrival: 1.35 (High variability - bursty traffic)
Classification: High (Bursty arrivals)
Recommended max utilization: 65%
```

**Step 2: Queueing Calculations**

Assume service rate = 70 vehicles/hour/lane

**Test with 2 lanes:**
```
ρ = 180 / (2 × 70) = 1.29 → UNSTABLE!
```

**Test with 3 lanes:**
```
ρ = 180 / (3 × 70) = 0.86 → Too high for CV=1.35
Using Kingman's formula:
W_q = 142 seconds → Unacceptable
```

**Test with 4 lanes:**
```
ρ = 180 / (4 × 70) = 0.64 → Within target!
Using Kingman's formula:
W_q = 38 seconds → Acceptable
L_q = 1.9 vehicles
P(Wait > 60s) = 12%
```

**Conclusion:** Need 4 lanes for morning peak westbound traffic

**Step 3: Cost-Benefit**

| Scenario | Lanes | Wait | Annual Cost | Notes |
|----------|-------|------|-------------|-------|
| Current  | 2     | ∞    | £125,000    | Unstable |
| Minimum  | 3     | 142s | £187,500    | Poor service |
| Optimal  | 4     | 38s  | £250,000    | Recommended |
| Safe     | 5     | 15s  | £312,500    | Over-capacity |

**Recommendation:** 4 lanes
- Utilization: 64%
- Wait time: 38 seconds
- Additional cost vs 3 lanes: £62,500/year
- Benefit: Reduces wait time by 104 seconds
- Time value savings: £89,000/year
- **Net benefit: £26,500/year**

---

## Key Formulas Reference

### Kingman's VUT Equation
```
W_q = (ρ/(1-ρ)) × ((CV_a² + CV_s²)/2) × (1/μ)
```
Accounts for variability impact on wait times

### Required Capacity
```
c = ceil(λ / (μ × ρ_target))
```
Where ρ_target = 0.75 for CV ≈ 1.0

### Variability-Adjusted Capacity
```
c_adjusted = c_base × [1 + (CV - 1) × 0.5]
```
Add buffer for high variability

### Little's Law
```
L = λ × W
```
Converts wait time to queue length

---

## Common Issues & Solutions

### Issue 1: All Scenarios Show ρ > 1.0

**Problem:** Arrival rate exceeds system capacity

**Solutions:**
- Increase service rate (faster processing)
- Add more servers/lanes
- Reduce arrival rate (demand management)
- Extend operating hours (spread demand)

### Issue 2: High CV (>1.5) Everywhere

**Problem:** Very bursty/irregular arrivals

**Solutions:**
- Size for peak + significant buffer (ρ target = 0.60-0.65)
- Use empirical distributions in SIMUL8 (not theoretical)
- Consider adaptive/dynamic resource allocation
- Investigate arrival patterns (are there clustering causes?)

### Issue 3: SIMUL8 Results Don't Match Queueing Theory

**Common Causes:**
- Wrong distribution used (use empirical, not exponential)
- Warm-up period too short
- Not enough replications (need 30+)
- System has constraints not modeled in queueing formulas

**Validation Checks:**
- Verify λ (arrival rate) matches in both
- Check μ (service rate) is correct
- Ensure ρ calculation matches
- Use Little's Law to cross-check: L should equal λ × W

---

## Integration with Other Tools

### With Traffic Analyzer (Time & Cost)

1. Run queueing analysis to get optimal capacity
2. Configure SIMUL8 with recommended capacity
3. Run SIMUL8 simulation
4. Export results to CSV
5. Run traffic_analyzer.py on simulation output
6. Compare costs across different capacity scenarios

### With Optimization Engine

1. Use queueing results to set capacity bounds
   - Lower bound: Minimum stable capacity (ρ < 1)
   - Upper bound: Optimal capacity + 50%

2. Queueing theory guides optimization search space
   - Don't search below ρ = 0.95 (unstable)
   - Don't search below ρ = 0.60 (waste)

3. Multi-objective optimization:
   - Minimize: Cost (from resource planner)
   - Minimize: Wait time (from queueing calculator)
   - Constraint: ρ < 0.85

---

## Academic Deliverables

### For Your Report/Dissertation

**Section 1: Variability Analysis**
- Present CV for each entity type and period
- Show distribution fits
- Explain impact on capacity requirements
- Include variability_analysis.png

**Section 2: Queueing Theory Application**
- Derive capacity requirements using formulas
- Show calculations for key periods
- Present utilization vs wait time tradeoffs
- Reference: Kingman (1961), Erlang (1917)

**Section 3: Resource Planning**
- Compare scenarios (minimum/optimal/safe)
- Present cost-benefit analysis
- Justify recommended configuration
- Include resource_planning_scenarios.png

**Section 4: Simulation Validation**
- Compare queueing predictions to SIMUL8 results
- Explain any discrepancies
- Demonstrate consistency with analytical models
- Shows rigor and validation

---

## Complete Workflow Example

```bash
# Step 1: Collect data (you do this manually with annotation tool)
# Result: all_sessions_combined.csv

# Step 2: Analyze variability
python variability_analyzer.py all_sessions_combined.csv
# Review: variability_report.txt
# Note CV values for high-variability periods

# Step 3: Calculate queueing metrics
python queueing_calculator.py all_sessions_combined.csv 60
# Review: queueing_analysis_report.txt
# Note optimal capacities

# Step 4: Generate resource plan
python resource_planner.py 10000
# Review: resource_planning_report.txt
# Select scenario (usually "Optimal")

# Step 5: Configure SIMUL8
# Use recommended capacities from resource planner
# Import empirical distributions
# Set queue capacities from L_q values

# Step 6: Run SIMUL8 validation
# 30+ replications, 8+ hour runs
# Compare results to queueing predictions

# Step 7: Iterate if needed
# If results differ significantly, refine service rate or distributions
# Re-run queueing calculator with adjusted parameters
```

---

## Troubleshooting

**Q: Variability analyzer shows "Insufficient data"**
A: Need at least 30 data points per group. Combine periods or extend observation time.

**Q: All recommended capacities seem very high**
A: Check service rate - may be too low. Verify μ is entities per hour per server, not total.

**Q: Queueing results show ρ > 1 for everything**
A: Either arrival rate too high or service rate too low. Verify:
- λ calculation (total arrivals / duration in hours)
- μ is per server, not total system

**Q: Resource planner shows negative performance scores**
A: Indicates unstable system. Must increase capacity or reduce arrivals.

---

## Next Steps

After completing queueing analysis:

1. **Document findings** in your report/dissertation
2. **Configure SIMUL8** with recommended capacities
3. **Run validation** simulations (30+ reps)
4. **Compare** queueing predictions vs simulation
5. **Optimize** using genetic algorithm (HYBRID_OPTIMIZATION_GUIDE.md)
6. **Cost-benefit** analysis for final recommendations
7. **Sensitivity analysis** (±20% arrival rates)

---

**You now have a complete queueing theory-based resource planning system that:**
- Scientifically determines capacity requirements
- Accounts for variability in arrival patterns
- Provides cost-benefit analysis for scenarios
- Validates simulation results with analytical models
- Demonstrates advanced OR/analytics skills
