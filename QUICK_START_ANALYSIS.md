# Quick Start: Hybrid Optimization & Time/Cost Analysis

## Summary

You now have a complete system for:
1. **Hybrid Modeling** - Combining discrete-event, agent-based, and system dynamics
2. **Optimization** - Using genetic algorithms and response surface methodology
3. **Time & Cost Analysis** - Automated software to analyze your SIMUL8 data

---

## Immediate Next Steps

### Step 1: Install Required Packages

```bash
pip install -r requirements_analyzer.txt
```

This installs:
- pandas, numpy (data processing)
- matplotlib, seaborn (visualization)
- scipy, scikit-learn (optimization algorithms)
- deap (genetic algorithms)
- plotly (interactive plots)

### Step 2: Run Time & Cost Analysis

After you have `all_sessions_combined.csv` from your 8 observation windows:

```bash
python traffic_analyzer.py
```

**This will generate:**
- `traffic_analysis_report.txt` - Complete text report
- `traffic_metrics.json` - Metrics in JSON format
- `time_analysis.png` - Wait times, throughput, utilization charts
- `cost_analysis.png` - Cost breakdown (daily & annual)
- `period_comparison.png` - Comparison across 8 sessions

### Step 3: Review Results

**Key Metrics to Check:**
- Average wait times (should be < 60s for good performance)
- System utilization (target 70-80%)
- Daily cost breakdown (identify largest cost drivers)
- Period variations (compare peak vs off-peak)

---

## Three-Layer Approach Explained

### Layer 1: Discrete Event Simulation (SIMUL8)
**What it does:** Models vehicle and pedestrian arrivals/departures as discrete events
**Your data feeds:** Inter-arrival times, service times from CSV
**SIMUL8 handles:** Queue management, resource allocation, traffic light cycles

### Layer 2: Agent-Based Model (Embedded Logic)
**What it does:** Models individual pedestrian decision-making
**Implementation:** Add Visual Logic code in SIMUL8:
```vb
' Example: Poser vs Crosser behavior
If TimeOfDay = "Tourist_Peak" Then
    PoserProbability = 0.7
Else
    PoserProbability = 0.3
End If
```

### Layer 3: System Dynamics (Python Integration)
**What it does:** Captures feedback loops (e.g., congestion reduces arrivals)
**Implementation:** Python script adjusts SIMUL8 parameters based on system state

---

## Optimization Workflow

### Option 1: Use SIMUL8's Built-in OptQuest

**Steps:**
1. Open your SIMUL8 model
2. Go to **Experiments** → **Optimization**
3. Define decision variables:
   - Traffic light cycle (30-90 seconds)
   - Pedestrian phase length (10-30 seconds)
4. Set objectives:
   - Minimize: Average wait time
   - Maximize: Throughput
5. Run optimization (50-100 iterations)

### Option 2: External Genetic Algorithm (Python)

**Use Case:** More complex multi-objective optimization

```python
# Example: Run optimization
from optimization_engine import GeneticOptimizer

optimizer = GeneticOptimizer(
    simul8_model="abbey_road_model.s8",
    objectives=["wait_time", "throughput", "cost"],
    population_size=50,
    generations=40
)

best_solution = optimizer.run()
print(f"Optimal configuration: {best_solution}")
```

---

## Cost Analysis Components

### Infrastructure Costs (One-time, Amortized)
- Traffic lights: £5,000 × 2 = £10,000
- Signage: £500 × 4 = £2,000
- Road markings: £2,000 × 2 = £4,000
- Barriers: £1,500 × 2 = £3,000
- **Total: £19,000** (amortized over 10 years = £1,900/year)

### Operational Costs (Annual)
- Maintenance: £36,500/year
- Electricity: £9,125/year
- **Total: £45,625/year**

### Time Value Costs (Calculated from Data)
- Vehicle waiting time: £15/hour per vehicle
- Pedestrian waiting time: £8/hour per person
- Calculated based on your simulation results

### Externality Costs
- Congestion: £0.50/minute per occurrence
- Emissions: £0.10/vehicle-minute
- Safety incidents: £5,000 per incident (if applicable)

**You can adjust these in `CostParameters` class!**

---

## Customizing Cost Parameters

Edit `traffic_analyzer.py` to match your specific costs:

```python
cost_params = CostParameters(
    # Infrastructure (£)
    traffic_light_cost=5000.0,      # Your actual cost
    signage_cost=500.0,
    road_marking_cost=2000.0,

    # Operational (£/year)
    maintenance_cost_per_year=36500.0,
    electricity_cost_per_year=9125.0,

    # Time value (£/hour)
    vehicle_time_value=15.0,        # UK average
    pedestrian_time_value=8.0,

    # Externalities (£)
    congestion_cost_per_minute=0.5,
    emission_cost_per_vehicle_minute=0.1
)
```

---

## Understanding Outputs

### Time Analysis Visualization
**File:** `time_analysis.png`

**Four Charts:**
1. **Wait Time Comparison** - Vehicles vs Pedestrians
2. **Throughput** - Entities per hour
3. **Utilization** - Overall vs Peak (target: 70-80%)
4. **Inter-Arrival Distribution** - Pattern of arrivals

### Cost Analysis Visualization
**File:** `cost_analysis.png`

**Two Charts:**
1. **Daily Cost Pie Chart** - Proportions of each cost type
2. **Annual Cost Bar Chart** - Total annual costs by category

### Period Comparison
**File:** `period_comparison.png` (if you have 8 sessions)

**Four Charts:**
1. **Arrivals by Period** - Traffic volume comparison
2. **Throughput by Period** - Efficiency comparison
3. **Wait Times by Period** - Service quality comparison
4. **Utilization by Period** - Resource usage comparison

---

## Sample Results Interpretation

### Example Output:

```
TIME ANALYSIS
Total Arrivals: 2,450
Throughput: 306.25 entities/hour
Avg Wait Times:
  Vehicles: 23.5 seconds
  Pedestrians: 18.2 seconds
System Utilization: 68.3%

COST ANALYSIS (Daily)
Infrastructure: £5.21
Operational: £125.00
Time Value: £892.50
Congestion: £45.30
Environmental: £67.80
==========================
TOTAL DAILY COST: £1,135.81
TOTAL ANNUAL COST: £414,571.65
```

**Interpretation:**
- **Good:** Utilization at 68% (near target)
- **Good:** Wait times under 30 seconds
- **Concern:** Time value is largest cost component (78% of daily cost)
- **Action:** Optimization should focus on reducing wait times

---

## Optimization Scenarios to Test

### Scenario 1: Longer Pedestrian Phase
**Change:** Increase ped crossing time from 15s to 25s
**Expected:** Lower pedestrian wait, higher vehicle wait
**Cost Impact:** Reduced time value for pedestrians, increased for vehicles

### Scenario 2: Adaptive Traffic Lights
**Change:** Adjust cycle based on real-time traffic
**Expected:** Better overall utilization
**Cost Impact:** Higher implementation cost, lower operational costs

### Scenario 3: Additional Crossing
**Change:** Add second pedestrian crossing 50m away
**Expected:** Distribute pedestrian load
**Cost Impact:** High infrastructure cost, significantly lower time value costs

### Scenario 4: Peak Hour Management
**Change:** Different light cycles for peak vs off-peak
**Expected:** Optimized for traffic patterns
**Cost Impact:** Minimal infrastructure, large time value savings

---

## Integration with SIMUL8

### Method 1: Manual Parameter Updates
1. Run analysis → Get optimal parameters
2. Manually update SIMUL8 model
3. Re-run simulation
4. Verify improvement

### Method 2: COM Automation (Advanced)
```python
import win32com.client

# Connect to SIMUL8
simul8 = win32com.client.Dispatch("Simul8.Simul8Object")
simul8.Load Model("abbey_road_model.s8")

# Update parameters
simul8.SetParameter("TrafficLightCycle", optimal_cycle)
simul8.SetParameter("PedPhase", optimal_ped_phase)

# Run simulation
simul8.RunSimulation()

# Get results
results = simul8.GetResults()
```

---

## Next Steps for Your Project

### Phase 1: Data Collection (In Progress)
- [ ] Complete all 8 observation sessions
- [ ] Merge session data
- [ ] Validate data quality

### Phase 2: Base Analysis (Next)
- [ ] Run `traffic_analyzer.py` on your data
- [ ] Review time metrics
- [ ] Review cost breakdown
- [ ] Identify optimization opportunities

### Phase 3: SIMUL8 Modeling (2-3 weeks)
- [ ] Build base discrete-event model
- [ ] Validate against real data
- [ ] Add agent-based pedestrian logic
- [ ] Add system dynamics feedback

### Phase 4: Optimization (2-3 weeks)
- [ ] Define decision variables
- [ ] Run optimization experiments
- [ ] Test top 3-5 scenarios
- [ ] Select optimal configuration

### Phase 5: Cost-Benefit Analysis (1 week)
- [ ] Calculate implementation costs for scenarios
- [ ] Project cost savings over 1, 5, 10 years
- [ ] Calculate ROI for each scenario
- [ ] Present recommendations

---

## Troubleshooting

### Error: "all_sessions_combined.csv not found"
**Solution:** Ensure you've completed data collection and merging:
```bash
python combine_all_sessions.py
```

### Error: "Module not found"
**Solution:** Install required packages:
```bash
pip install -r requirements_analyzer.txt
```

### Warning: "Cost metrics seem unrealistic"
**Solution:** Adjust `CostParameters` to match your specific context

### Low Utilization (<50%)
**Possible causes:**
- Long inter-arrival times (low traffic)
- Oversized capacity
- Inefficient traffic light cycles

### High Wait Times (>60s)
**Possible causes:**
- Undersized capacity
- Poor traffic light synchronization
- High pedestrian congestion

---

## Academic Context

### For Your Report/Dissertation

**Hybrid Modeling Section:**
- Explain why hybrid approach is superior to single-paradigm
- Show how DES + ABM + SD captures different aspects
- Reference: Siebers et al. (2010) "Discrete-event simulation is dead, long live agent-based simulation!"

**Optimization Section:**
- Justify choice of GA vs other methods
- Present Pareto front for multi-objective optimization
- Compare baseline vs optimized scenarios

**Cost Analysis Section:**
- Break down cost components with literature references
- Show sensitivity analysis (how costs change with parameters)
- Present ROI calculations for implementation scenarios

---

## Key Deliverables for Academic Project

1. **SIMUL8 Model** - Working simulation with your data
2. **Analysis Report** - Generated by `traffic_analyzer.py`
3. **Optimization Results** - Best configurations found
4. **Cost-Benefit Analysis** - ROI for recommended scenarios
5. **Visualizations** - Charts and graphs for presentation
6. **Documentation** - This guide + your methodology

---

**Total Development Timeline: 7-11 weeks**
**Current Status: Data collection phase**
**Next Immediate Action: Complete 8 observation sessions**
