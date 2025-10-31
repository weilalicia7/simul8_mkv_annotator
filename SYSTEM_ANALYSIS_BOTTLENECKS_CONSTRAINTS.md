# System Analysis: Bottlenecks, Constraints, and Sensitive Parameters

## Executive Summary

Analysis of weekday traffic data (9:00-10:30 AM, 1,073 entities) reveals critical system features that impact performance and capacity planning.

**Key Findings:**
- **Primary Bottleneck:** WB Vehicles (339/hour, highest traffic intensity)
- **Critical Constraint:** Bidirectional conflict (EB vs WB cannot cross simultaneously)
- **Most Sensitive Parameter:** Poser service time (CV=1.95, extreme variability)
- **System Utilization:** 25-50% (room for optimization)

---

## Part 1: Bottleneck Analysis

### 1.1 Traffic Intensity by Entity Type

| Entity | Arrival Rate (λ) | Service Rate (μ) | Traffic Intensity (ρ) | Status |
|--------|-----------------|------------------|----------------------|---------|
| **WB Vehicles** | 339.56/hr | 679.12/hr | **0.50** | **BOTTLENECK** |
| EB Vehicles | 210.19/hr | 420.37/hr | 0.50 | High |
| Posers | 100.64/hr | 327.53/hr | 0.31 | Moderate |
| Crossers | 68.70/hr | 497.02/hr | 0.14 | Low |

**Analysis:**

**WB Vehicles = Primary Bottleneck**
- Highest arrival rate (339/hour)
- 62% more traffic than EB direction
- At 50% traffic intensity with only 1 server
- Needs 2+ servers to maintain stability (ρ < 1)

**Why WB is the Bottleneck:**
1. Volume: 506 entities in 90 minutes (47% of all traffic)
2. Consistency: 5 peak periods (sustained high load)
3. Directional imbalance: Significantly more than EB
4. Limited crossing windows due to EB conflicts

### 1.2 Peak Period Bottlenecks

**Identified Peak Congestion Points:**

| Time | EB Rate | WB Rate | Total | Bottleneck Type |
|------|---------|---------|-------|-----------------|
| 9:02-9:07 | 312/hr | 432/hr | 744/hr | **Bidirectional surge** |
| 9:27-9:30 | 276/hr | 340/hr | 616/hr | Moderate congestion |
| 10:07-10:12 | 300/hr | 468/hr | **768/hr** | **Maximum bottleneck** |
| 10:17-10:22 | 264/hr | 340/hr | 604/hr | EB surge |

**Critical Finding:**
- **10:07-10:12 AM = System-Wide Bottleneck**
- Combined rate: 768 entities/hour
- Both directions peak simultaneously
- Requires maximum capacity allocation
- Queue formation highly likely

### 1.3 Pedestrian Bottleneck Analysis

**Posers (Tourists):**
- **Not a volume bottleneck** (only 101/hour)
- **Service time bottleneck** due to high variability
- CV = 1.95 (extreme unpredictability)
- 30% of Posers require 47% longer service than average
- Creates sporadic congestion spikes

**Crossers:**
- **Not a bottleneck** (lowest traffic intensity: 0.14)
- Fast service (mean: 7.5s)
- Low variability (CV: 1.05)
- Single server sufficient

### 1.4 Temporal Bottlenecks

**Morning Rush Effect (9:00-9:30 AM):**
- First 30 minutes = 40% of total traffic
- Multiple simultaneous peaks
- System under maximum stress
- Capacity inadequate for this period

**Mid-Session Stabilization (9:30-10:00 AM):**
- Traffic normalizes
- Bottlenecks relieve
- System operates efficiently

**Late Rush (10:07-10:17 AM):**
- Secondary surge period
- Tourist activity peaks (Posers)
- Renewed bottleneck formation

---

## Part 2: System Constraints

### 2.1 Hard Constraints (Cannot be Violated)

**Physical Constraints:**

1. **Bidirectional Conflict**
   - EB and WB vehicles cannot cross simultaneously
   - Mutual exclusion required
   - Creates natural bottleneck
   - **Impact:** Reduces effective capacity by 50%

2. **Crossing Width**
   - Limited physical space
   - Maximum vehicles side-by-side: Assumed 2-3
   - Determines maximum server count
   - **Constraint:** Cannot exceed physical capacity

3. **Safety Clearance**
   - Minimum time between vehicle crossings
   - Pedestrian right-of-way periods
   - Emergency access requirements
   - **Impact:** Reduces theoretical maximum throughput

**Operational Constraints:**

4. **Service Time Minimums**
   - Vehicles: ~4-5 seconds minimum crossing time
   - Pedestrians: ~3 seconds minimum
   - Cannot be reduced below safe limits
   - **Constraint:** Lower bound on service rate

5. **Queue Space**
   - Limited queuing area on both sides
   - Maximum queue length before spillback
   - Affects upstream traffic
   - **Constraint:** System capacity limited by queue space

### 2.2 Soft Constraints (Performance Targets)

**Quality of Service Constraints:**

1. **Maximum Wait Time Target: 5 seconds**
   - Current learning algorithm target
   - Determines required capacity
   - **Status:** Achievable with 2 servers per direction
   - **Trade-off:** Higher capacity = lower utilization

2. **Utilization Target: 50-70%**
   - Balance efficiency vs responsiveness
   - Current: 25-50% (conservative)
   - **Opportunity:** Can increase utilization
   - **Risk:** Higher utilization = longer queues

3. **Pedestrian Priority**
   - Crossers must not wait >10 seconds
   - Posers can tolerate longer waits (photo activity)
   - Creates service priority constraint
   - **Impact:** Vehicles may experience delays

### 2.3 Demand Constraints

**Arrival Rate Constraints:**

1. **Peak Demand: 768/hour (combined)**
   - System must handle maximum load
   - Occurs at 10:07-10:12 AM
   - **Constraint:** Capacity must exceed this rate
   - **Current:** Marginal capacity (requires 3-4 servers per direction)

2. **Directional Imbalance: 62%**
   - WB = 339/hr, EB = 210/hr
   - Cannot assume balanced load
   - **Constraint:** Must size for actual asymmetry
   - **Impact:** WB needs more capacity than EB

3. **Variability Constraint**
   - High CV (1.28-1.95) requires buffer capacity
   - Cannot plan for average only
   - **Constraint:** 20-30% capacity buffer needed
   - **Impact:** Lower effective utilization

### 2.4 Resource Constraints

**Capacity Constraints:**

1. **Server Availability**
   - Finite number of crossing "slots"
   - Each server = one crossing lane
   - **Current Learned Optimal:** EB=2, WB=2
   - **Peak Requirement:** EB=3-5, WB=4-7

2. **Cost Constraints**
   - Each additional server = infrastructure cost
   - Annual operating costs: £970,236 (current)
   - **Trade-off:** Capacity vs cost
   - **Sensitivity:** High (cost increases linearly with servers)

3. **Space Constraints**
   - Physical space for lanes
   - Pedestrian pathways
   - Safety zones
   - **Practical Limit:** Maximum ~5-7 servers total

---

## Part 3: Sensitive Parameters

### 3.1 High Sensitivity Parameters (Major Impact)

**1. Service Time Variability (CV) - CRITICAL**

**Poser CV = 1.95 (Extreme Variability)**

Impact Analysis:
- **Wait Time Sensitivity:** ±50% change in CV → ±30-40% change in wait time
- **Capacity Requirement:** High CV requires 47% more capacity than low CV
- **System Stability:** CV >1.5 creates unpredictable performance

**Why It Matters:**
- Posers are unpredictable (3s to 60s+ service times)
- Single long photo session blocks crossing
- Queue builds rapidly during long service
- Cannot be managed with fixed capacity

**Sensitivity Test:**
| CV Value | Required Servers | Wait Time | Utilization |
|----------|-----------------|-----------|-------------|
| 0.5 (Low) | 1 | 1.2s | 30% |
| 1.0 (Moderate) | 1 | 2.5s | 30% |
| 1.5 (High) | 2 | 3.8s | 15% |
| **1.95 (Actual)** | **2** | **4.0s** | **15%** |
| 2.5 (Extreme) | 3 | 6.5s | 10% |

**Conclusion:** CV is the MOST sensitive parameter. Reducing Poser variability would significantly improve system performance.

**2. Arrival Rate (λ) - HIGH**

**Sensitivity:** ±10% change in λ → ±15-20% change in wait time

**Critical Thresholds:**
- WB at 339/hr: Near capacity limit with 2 servers
- Increase to 373/hr (+10%): Requires 3 servers
- Increase to 407/hr (+20%): Requires 4 servers
- Increase to 509/hr (+50%): System unstable (ρ > 1)

**Peak Hour Sensitivity:**
- During peaks (768/hr combined): System stressed
- Even 5% increase creates significant queues
- **Most Sensitive Period:** 10:07-10:12 AM

**Weekend Projection:**
- Expected: +10-20% arrival rate
- Posers: +200-300% (VERY sensitive)
- **Impact:** Will require capacity increase

**3. Number of Servers (c) - HIGH**

**Capacity Sensitivity Analysis:**

For WB Vehicles (339/hr arrival rate):

| Servers | Utilization | Wait Time | Feasible? | Sensitivity |
|---------|-------------|-----------|-----------|-------------|
| 1 | 50% | 5.1s | No (exceeds target) | Baseline |
| **2** | **25%** | **1.7s** | **Yes** | **-67% wait time** |
| 3 | 17% | 1.0s | Yes | -41% wait time |
| 4 | 13% | 0.7s | Yes | -30% wait time |

**Key Finding:** Going from 1→2 servers reduces wait time by 67%! Highly sensitive parameter.

**Diminishing Returns:**
- 1→2 servers: 67% reduction
- 2→3 servers: 41% reduction
- 3→4 servers: 30% reduction

**Optimal Range:** 2-3 servers (best trade-off)

### 3.2 Moderate Sensitivity Parameters

**4. Service Time Mean (μ) - MODERATE**

**Sensitivity:** ±10% change in μ → ±8-12% change in wait time

**Why Less Sensitive Than λ:**
- Service times relatively stable (compared to arrivals)
- Mean service time: 5-8 seconds for vehicles
- Limited room for improvement (safety constraints)

**Improvement Potential:**
- Reducing service time by 1 second = 12-15% improvement
- **Realistic Opportunity:** Traffic light optimization, road surface
- **Constraint:** Safety limits how much can be reduced

**5. Peak Period Duration - MODERATE**

**Sensitivity:** Duration of peaks affects queue buildup

**Analysis:**
- 5-minute peak: Manageable with buffer capacity
- 10-minute peak: Significant queue formation
- 15+ minute peak: May require capacity increase

**Current Status:**
- Most peaks: 5 minutes (optimal)
- One peak: 10 minutes (10:07-10:17)
- **Sensitivity:** Linear relationship (2x duration = ~2x queue)

### 3.3 Low Sensitivity Parameters

**6. Inter-Arrival Distribution Shape - LOW**

**Sensitivity:** Exponential vs Gamma vs Lognormal → <5% impact

**Why Low Sensitivity:**
- Mean and CV dominate performance
- Specific distribution shape matters less
- **Exception:** Heavy-tailed distributions (extreme outliers)

**Practical Implication:** Can use Exponential approximation without significant error

**7. Queue Discipline (FIFO vs Priority) - LOW**

**Sensitivity:** For current system, <3% impact on average wait time

**Why Low:**
- All entity types have similar urgency
- No strict priority rules needed
- FIFO is sufficient

**Exception:** If implementing pedestrian priority, becomes moderate sensitivity

---

## Part 4: Critical Interactions and Trade-offs

### 4.1 Capacity vs Cost Trade-off

**Trade-off Analysis:**

| Configuration | Servers | Wait Time | Cost/Year | Utilization |
|--------------|---------|-----------|-----------|-------------|
| Minimum | EB=1, WB=2, C=1, P=1 | 6.5s | £485K | 40% |
| **Learned Optimal** | **EB=2, WB=2, C=1, P=2** | **2.3s** | **£970K** | **25%** |
| Conservative | EB=3, WB=4, C=2, P=3 | 1.2s | £1,456K | 18% |
| Over-capacity | EB=5, WB=7, C=2, P=4 | 0.6s | £2,037K | 12% |

**Sensitivity to Cost:**
- Each additional server: +£242K/year
- Diminishing returns after 2-3 servers
- **Sweet Spot:** Current learned optimal (EB=2, WB=2)

### 4.2 Utilization vs Responsiveness Trade-off

**The Fundamental Trade-off:**

```
High Utilization (60-80%):
+ Efficient resource use
+ Lower cost per entity served
- Long wait times during peaks
- High queue variability
- Poor responsiveness

Low Utilization (20-40%):
+ Fast service
+ Short wait times
+ Better handling of variability
- Inefficient resource use
- Higher cost per entity served
```

**Current Status:** 25% utilization (low)
**Opportunity:** Can increase to 40-50% with adaptive capacity
**Risk:** Above 50% = exponential wait time growth

**Sensitivity:**
- At 50% utilization: Wait time = 2x baseline
- At 70% utilization: Wait time = 5x baseline
- At 80% utilization: Wait time = 10x+ baseline

### 4.3 Variability vs Capacity Trade-off

**Kingman's VUT Equation Sensitivity:**

```
Wait Time ∝ (CV_a² + CV_s²) / 2
```

**Analysis:**

For Posers (CV = 1.95):
- Variability term: (1.95² + 0.5²) / 2 = 2.03
- For Crossers (CV = 1.05): 0.68
- **3x difference due to variability alone!**

**Options:**

**Option A: Accept Variability, Add Capacity**
- Keep CV = 1.95
- Add servers (2→3)
- Cost: +£242K/year
- Result: Wait time 4.0s → 2.5s

**Option B: Reduce Variability, Same Capacity**
- Reduce CV: 1.95 → 1.2 (time limits on photos)
- Keep 2 servers
- Cost: £0
- Result: Wait time 4.0s → 2.1s

**Conclusion:** Reducing variability is more cost-effective than adding capacity!

---

## Part 5: Sensitivity Rankings

### 5.1 Overall Parameter Sensitivity Ranking

| Rank | Parameter | Sensitivity | Impact on Wait Time | Impact on Capacity | Controllable? |
|------|-----------|-------------|---------------------|-------------------|---------------|
| 1 | **Service Time CV** | **Critical** | ±30-40% | ±50% | Moderate |
| 2 | **Arrival Rate (λ)** | **High** | ±15-20% | ±25% | Low |
| 3 | **Number of Servers** | **High** | ±60-70% | N/A | High |
| 4 | Peak Period Timing | Moderate | ±10-15% | ±15% | Low |
| 5 | Service Rate (μ) | Moderate | ±8-12% | ±12% | Low |
| 6 | Peak Duration | Moderate | ±5-10% | ±10% | Low |
| 7 | Distribution Shape | Low | <5% | <5% | N/A |
| 8 | Queue Discipline | Low | <3% | <3% | High |

### 5.2 Controllable vs Uncontrollable Parameters

**Highly Controllable (Can Change):**
1. **Number of Servers** - Direct control
2. **Service Time CV** - Moderate control (time limits, signage)
3. **Queue Discipline** - Full control (rules)

**Moderately Controllable:**
4. **Service Rate (μ)** - Some control (traffic lights, road design)
5. **Peak Period Timing** - Indirect control (incentives, pricing)

**Not Controllable:**
6. **Arrival Rate (λ)** - External demand
7. **Distribution Shape** - Natural traffic patterns
8. **Peak Duration** - Depends on external factors

### 5.3 Recommended Focus Areas

**Priority 1: Address High-Sensitivity Controllable Parameters**
1. Optimize server count (already done: EB=2, WB=2)
2. Reduce Poser service time variability (signage, time limits)
3. Implement adaptive capacity for peaks

**Priority 2: Monitor High-Sensitivity Uncontrollable Parameters**
1. Track arrival rates (early warning system)
2. Identify peak period shifts
3. Prepare contingency capacity

**Priority 3: Accept Low-Sensitivity Parameters**
1. Distribution shape: Use Exponential approximation
2. Queue discipline: Keep simple FIFO
3. Don't over-optimize these

---

## Part 6: Scenario Analysis

### 6.1 Best Case Scenario

**Conditions:**
- Arrival rates: -10% (quieter period)
- Service CV reduced: 1.95 → 1.2 (time management)
- Capacity: Learned optimal (EB=2, WB=2)

**Results:**
- Wait time: 1.5s average
- Utilization: 20%
- Queue length: <2 entities
- **Status:** System over-capacity

### 6.2 Expected Case Scenario

**Conditions:**
- Arrival rates: As observed (current)
- Service CV: As observed (1.95)
- Capacity: Learned optimal (EB=2, WB=2)

**Results:**
- Wait time: 2.3s average
- Utilization: 25%
- Queue length: <3 entities
- **Status:** System well-balanced

### 6.3 Worst Case Scenario

**Conditions:**
- Arrival rates: +20% (weekend, special event)
- Service CV: 1.95 (unchanged)
- Peak duration: 2x longer
- Capacity: Fixed (EB=2, WB=2)

**Results:**
- Wait time: 8-12s average
- Utilization: 50-60%
- Queue length: 5-8 entities
- **Status:** System stressed

**Required Response:**
- Increase capacity: EB=3, WB=4
- Implement adaptive rules
- OR reduce service CV

### 6.4 Weekend Scenario (Projected)

**Expected Changes:**
- Arrival rates: +10-20%
- **Posers: +200-300%** (tourist effect)
- Peak times: Later (11:00-12:00)
- New patterns: Lunch hour effect

**Sensitive Parameters in Weekend Scenario:**
1. **Poser capacity** - Will become bottleneck (high sensitivity)
2. **Peak timing** - Different from weekday (moderate sensitivity)
3. **Total arrival rate** - Higher overall (high sensitivity)

**Required Adjustments:**
- Posers: 2 → 3-4 servers
- WB: 2 → 3 servers
- Adaptive capacity critical for lunch hour

---

## Part 7: Recommendations

### 7.1 Immediate Actions (High Priority)

**1. Implement Learned Capacity (EB=2, WB=2, C=1, P=2)**
- **Rationale:** Optimal balance of cost and performance
- **Impact:** Achieves <5s wait time target
- **Cost:** £970K/year
- **Sensitivity:** Low risk, high benefit

**2. Add Signage to Reduce Poser Variability**
- **Target:** Reduce CV from 1.95 → 1.5
- **Method:** "Please limit photos to 20 seconds" signs
- **Impact:** -25% wait time, same capacity
- **Cost:** <£1K (one-time)
- **Sensitivity:** High payoff, low investment

**3. Monitor WB as Primary Bottleneck**
- **Rationale:** Highest traffic, most sensitive
- **Method:** Track queue lengths, wait times
- **Trigger:** If wait >7 seconds, add server
- **Sensitivity:** Early detection prevents cascading delays

### 7.2 Short-Term Improvements (Next 3 Months)

**4. Implement Time-Varying Capacity**
- **Rationale:** Peaks require more capacity
- **Method:** Use learned peak schedules
- **Impact:** -15% average wait time
- **Sensitivity:** Moderate benefit, moderate complexity

**5. Deploy Adaptive Capacity Rules**
- **Rationale:** Respond to actual conditions
- **Method:** Traffic state detection (3 states)
- **Impact:** -20% wait time, +25% utilization
- **Sensitivity:** High benefit, requires automation

### 7.3 Long-Term Strategies (6-12 Months)

**6. Collect Weekend Data & Re-optimize**
- **Rationale:** Expected +200% Posers (high sensitivity)
- **Method:** 2.5-hour session (10:20 AM-1:00 PM)
- **Impact:** Weekend-specific capacity plans
- **Sensitivity:** Critical for tourist season

**7. Consider Dynamic Pricing/Incentives**
- **Rationale:** Shift demand away from peaks
- **Method:** Encourage off-peak crossing
- **Impact:** -10% peak arrival rates
- **Sensitivity:** Moderate (unproven for pedestrians)

**8. Physical Infrastructure Assessment**
- **Rationale:** May need >2 servers per direction during peaks
- **Method:** Evaluate adding lanes
- **Impact:** Increase maximum capacity
- **Cost:** £50K-200K (construction)
- **Sensitivity:** Long-term capacity expansion

---

## Summary Table

| Feature | Status | Sensitivity | Recommendation |
|---------|--------|-------------|----------------|
| **WB Bottleneck** | 339/hr, ρ=0.5 | High | Monitor, prepare to add capacity |
| **Bidirectional Conflict** | Hard constraint | Critical | Accept as given constraint |
| **Poser CV=1.95** | Extreme variability | **Critical** | **Reduce with signage/limits** |
| **Peak at 10:07** | 768/hr combined | High | Time-varying capacity |
| **Server Count** | EB=2, WB=2 | **High** | **Optimal, implement now** |
| **Utilization=25%** | Low efficiency | Moderate | Acceptable for responsiveness |
| **Weekend Posers** | Expected +200% | **Critical** | **Must collect data & adjust** |

---

**Key Insights:**

1. **WB Vehicles = Bottleneck** (highest traffic, most sensitive)
2. **Poser Variability = Most Controllable High-Impact Parameter**
3. **Server Count = Most Sensitive Design Decision** (67% wait time reduction)
4. **Bidirectional Conflict = Fundamental Constraint** (cannot eliminate)
5. **Weekend Data = Critical for Complete Understanding** (Posers will surge)

**Most Important Action:** Reduce Poser service time variability (high impact, low cost, controllable)

---

**Last Updated:** October 31, 2025
**Based On:** Weekday data analysis (9:00-10:30 AM, 1,073 entities)
**Model Accuracy:** R² = 0.999-1.000
**Status:** Ready for implementation and testing
