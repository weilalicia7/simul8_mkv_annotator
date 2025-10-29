# Hybrid Modeling & Optimization Framework
## SIMUL8 Traffic System with Time & Cost Analysis

---

## Overview

This guide explains how to implement hybrid modeling with optimization approaches for the Abbey Road crossing traffic system, plus build analysis software for time and cost evaluation.

---

## Part 1: Hybrid Modeling Approaches

### 1.1 Hybrid Model Architecture

**Combine Three Modeling Paradigms:**

```
┌─────────────────────────────────────────────────────────┐
│           HYBRID TRAFFIC SIMULATION MODEL               │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────┐  ┌──────────────────┐             │
│  │   Discrete      │  │   Agent-Based    │             │
│  │   Event         │◄─┤   (Pedestrian    │             │
│  │   Simulation    │  │    Behavior)     │             │
│  │   (Vehicles)    │  └──────────────────┘             │
│  └─────────────────┘                                     │
│         ▲                                                │
│         │                                                │
│         ▼                                                │
│  ┌─────────────────────────────────────┐               │
│  │  System Dynamics                    │               │
│  │  (Traffic Flow Patterns)            │               │
│  └─────────────────────────────────────┘               │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

**Component 1: Discrete Event Simulation (SIMUL8 Core)**
- Vehicle arrivals and departures
- Queue formation and service
- Traffic light cycles
- Based on your collected data

**Component 2: Agent-Based Model (Pedestrian Behavior)**
- Individual pedestrian decision-making
- Crosser vs Poser behavior logic
- Photo-taking duration variability
- Group dynamics

**Component 3: System Dynamics (Flow Patterns)**
- Traffic volume trends over time
- Peak hour dynamics
- Seasonal/temporal variations
- Feedback loops (congestion affects arrivals)

---

### 1.2 SIMUL8 Hybrid Implementation Strategy

**Step 1: Core SIMUL8 Model Setup**

Use your collected data for:
```
Entities:
- EB Vehicles (Inter-arrival from data)
- WB Vehicles (Inter-arrival from data)
- Crossers (Service time from data)
- Posers (Service time from data)

Resources:
- Road crossing capacity
- Pedestrian crossing time
- Traffic light phases
```

**Step 2: Add Agent-Based Layer**

Create Visual Logic code in SIMUL8 for pedestrian agents:
```vb
' Pedestrian decision logic
If PedestrianType = "Tourist" Then
    If TimeOfDay = "Peak" Then
        PoserProbability = 0.7
    Else
        PoserProbability = 0.3
    End If
Else ' Commuter
    PoserProbability = 0.05
End If

' Dynamic service time based on agent type
If Poser = True Then
    ServiceTime = NormalDistribution(12.8, 3.5)
Else
    ServiceTime = NormalDistribution(4.2, 1.2)
End If
```

**Step 3: Add System Dynamics Layer**

External Excel/Python model feeding SIMUL8:
```python
# System dynamics model
def calculate_arrival_rate(time_of_day, congestion_level):
    """
    Adjust arrival rates based on system state
    """
    base_rate = get_base_rate_from_data(time_of_day)

    # Feedback loop: congestion reduces arrivals
    congestion_factor = 1 - (congestion_level * 0.3)

    # Seasonal factor
    seasonal_factor = get_seasonal_multiplier()

    adjusted_rate = base_rate * congestion_factor * seasonal_factor
    return adjusted_rate
```

---

## Part 2: Optimization Approaches

### 2.1 Multi-Objective Optimization Framework

**Optimization Goals:**

1. **Minimize Average Wait Time** (vehicles and pedestrians)
2. **Maximize Throughput** (total entities processed)
3. **Minimize Cost** (infrastructure, operations)
4. **Maximize Safety** (reduce conflicts)

**Decision Variables:**

- Traffic light cycle duration
- Pedestrian crossing phase length
- Road capacity allocation
- Signage placement
- Crowd control measures

### 2.2 Optimization Methods

**Method 1: Simulation-Based Optimization (SIMUL8 Built-in)**

```
SIMUL8 → Experiments → Optimization
- Use OptQuest engine
- Define objective functions
- Set decision variable ranges
- Run optimization experiments
```

**Method 2: External Genetic Algorithm**

Python implementation:
```python
import numpy as np
from deap import base, creator, tools, algorithms

# Define optimization problem
creator.create("FitnessMulti", base.Fitness, weights=(-1.0, 1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)

def evaluate_traffic_config(individual):
    """
    Evaluate traffic configuration

    Parameters:
    - individual: [light_cycle, ped_phase, capacity]

    Returns:
    - (wait_time, throughput, cost)
    """
    # Run SIMUL8 simulation with these parameters
    results = run_simul8_experiment(individual)

    wait_time = results['avg_wait_time']
    throughput = results['total_throughput']
    cost = calculate_cost(individual)

    return wait_time, throughput, cost

# Genetic algorithm setup
toolbox = base.Toolbox()
toolbox.register("attr_light", np.random.uniform, 30, 90)  # seconds
toolbox.register("attr_ped", np.random.uniform, 10, 30)    # seconds
toolbox.register("attr_capacity", np.random.randint, 1, 5)  # lanes

toolbox.register("individual", tools.initCycle, creator.Individual,
                (toolbox.attr_light, toolbox.attr_ped, toolbox.attr_capacity))
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate_traffic_config)
toolbox.register("mate", tools.cxBlend, alpha=0.5)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
toolbox.register("select", tools.selNSGA2)

# Run optimization
population = toolbox.population(n=50)
algorithms.eaMuPlusLambda(population, toolbox, mu=50, lambda_=100,
                         cxpb=0.7, mutpb=0.3, ngen=40)
```

**Method 3: Response Surface Methodology**

Use statistical design of experiments:
```python
from sklearn.gaussian_process import GaussianProcessRegressor
from scipy.optimize import minimize

# Build surrogate model from SIMUL8 runs
def build_surrogate_model(simul8_results):
    """
    Build metamodel from simulation results
    """
    X = simul8_results[['light_cycle', 'ped_phase', 'capacity']]
    y = simul8_results['objective_value']

    gp = GaussianProcessRegressor()
    gp.fit(X, y)
    return gp

# Optimize using surrogate
def optimize_via_surrogate(surrogate_model):
    result = minimize(
        lambda x: surrogate_model.predict([x])[0],
        x0=[60, 20, 3],
        bounds=[(30, 90), (10, 30), (1, 5)],
        method='L-BFGS-B'
    )
    return result.x
```

---

## Part 3: Time & Cost Analysis Software

### 3.1 Software Architecture

```
┌─────────────────────────────────────────────────────────┐
│         Traffic Analysis & Optimization Suite           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Data Import     │  │  SIMUL8          │            │
│  │  Module          │─►│  Integration     │            │
│  │  (CSV files)     │  │  API             │            │
│  └──────────────────┘  └──────────────────┘            │
│           │                      │                       │
│           ▼                      ▼                       │
│  ┌─────────────────────────────────────┐               │
│  │     Hybrid Simulation Engine         │               │
│  │  (Orchestrates SIMUL8 + Python)     │               │
│  └─────────────────────────────────────┘               │
│           │                                               │
│           ▼                                               │
│  ┌──────────────────┐  ┌──────────────────┐            │
│  │  Optimization    │  │  Time & Cost     │            │
│  │  Engine          │  │  Analyzer        │            │
│  │  (GA/RSM)        │  │                  │            │
│  └──────────────────┘  └──────────────────┘            │
│           │                      │                       │
│           └──────────┬───────────┘                       │
│                      ▼                                   │
│           ┌──────────────────┐                          │
│           │  Dashboard &     │                          │
│           │  Reporting       │                          │
│           └──────────────────┘                          │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Implementation: Time & Cost Analysis Module

**File: `traffic_time_cost_analyzer.py`**

```python
"""
Traffic Time & Cost Analysis System
Analyzes simulation results for time and cost metrics
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class CostParameters:
    """Cost structure for traffic system"""
    # Infrastructure costs
    traffic_light_cost: float = 5000.0  # per unit
    signage_cost: float = 500.0
    road_marking_cost: float = 2000.0

    # Operational costs
    maintenance_cost_per_day: float = 100.0
    electricity_cost_per_hour: float = 2.5

    # Time value costs
    vehicle_time_value: float = 15.0  # per hour per vehicle
    pedestrian_time_value: float = 8.0  # per hour per person

    # Congestion externality costs
    congestion_cost_per_minute: float = 0.5
    emission_cost_per_vehicle_minute: float = 0.1

@dataclass
class TimeMetrics:
    """Time-related performance metrics"""
    avg_vehicle_wait_time: float
    avg_pedestrian_wait_time: float
    max_queue_time: float
    total_system_time: float
    throughput_per_hour: float
    utilization_rate: float

class TrafficTimeAnalyzer:
    """Analyze time-related metrics from simulation"""

    def __init__(self, simul8_data: pd.DataFrame):
        self.data = simul8_data
        self.metrics = None

    def calculate_time_metrics(self) -> TimeMetrics:
        """Calculate all time-related metrics"""

        # Separate by entity type
        vehicles = self.data[self.data['Entity'].isin(['EB Vehicles', 'WB Vehicles'])]
        pedestrians = self.data[self.data['Entity'].isin(['Crossers', 'Posers'])]

        # Calculate metrics
        avg_vehicle_wait = self._calculate_avg_wait_time(vehicles)
        avg_ped_wait = self._calculate_avg_wait_time(pedestrians)
        max_queue = self._calculate_max_queue_time()
        total_time = self.data['Time (s)'].max() - self.data['Time (s)'].min()
        throughput = len(self.data) / (total_time / 3600)  # per hour
        utilization = self._calculate_utilization()

        self.metrics = TimeMetrics(
            avg_vehicle_wait_time=avg_vehicle_wait,
            avg_pedestrian_wait_time=avg_ped_wait,
            max_queue_time=max_queue,
            total_system_time=total_time,
            throughput_per_hour=throughput,
            utilization_rate=utilization
        )

        return self.metrics

    def _calculate_avg_wait_time(self, df: pd.DataFrame) -> float:
        """Calculate average waiting time for entities"""
        # Assuming wait time can be derived from inter-arrival patterns
        if 'Inter-Arrival (s)' in df.columns:
            return df['Inter-Arrival (s)'].mean()
        return 0.0

    def _calculate_max_queue_time(self) -> float:
        """Calculate maximum queue waiting time"""
        # Simplified - would need queue data from SIMUL8
        return self.data['Inter-Arrival (s)'].max()

    def _calculate_utilization(self) -> float:
        """Calculate system utilization rate"""
        # Service time / Total time
        total_service = self.data['Service Time (s)'].replace('-', 0).astype(float).sum()
        total_time = self.data['Time (s)'].max()
        return total_service / total_time if total_time > 0 else 0.0

    def analyze_by_period(self) -> pd.DataFrame:
        """Analyze time metrics by period type"""
        if 'Period_Type' not in self.data.columns:
            return None

        results = []
        for period in self.data['Period_Type'].unique():
            period_data = self.data[self.data['Period_Type'] == period]
            analyzer = TrafficTimeAnalyzer(period_data)
            metrics = analyzer.calculate_time_metrics()

            results.append({
                'Period': period,
                'Avg_Vehicle_Wait': metrics.avg_vehicle_wait_time,
                'Avg_Pedestrian_Wait': metrics.avg_pedestrian_wait_time,
                'Throughput': metrics.throughput_per_hour,
                'Utilization': metrics.utilization_rate
            })

        return pd.DataFrame(results)

class TrafficCostAnalyzer:
    """Analyze cost metrics from simulation"""

    def __init__(self, time_metrics: TimeMetrics, cost_params: CostParameters):
        self.time_metrics = time_metrics
        self.cost_params = cost_params

    def calculate_total_cost(self) -> Dict[str, float]:
        """Calculate comprehensive cost breakdown"""

        costs = {
            'infrastructure': self._calculate_infrastructure_cost(),
            'operational': self._calculate_operational_cost(),
            'time_value': self._calculate_time_value_cost(),
            'congestion': self._calculate_congestion_cost(),
            'environmental': self._calculate_environmental_cost()
        }

        costs['total'] = sum(costs.values())

        return costs

    def _calculate_infrastructure_cost(self) -> float:
        """Calculate infrastructure investment cost"""
        # Amortize over expected lifetime
        annual_cost = (
            self.cost_params.traffic_light_cost * 2 +  # 2 traffic lights
            self.cost_params.signage_cost * 4 +        # 4 signs
            self.cost_params.road_marking_cost * 2      # 2 crossings
        ) / 10  # 10-year amortization

        # Daily cost
        return annual_cost / 365

    def _calculate_operational_cost(self) -> float:
        """Calculate daily operational costs"""
        hours = self.time_metrics.total_system_time / 3600

        return (
            self.cost_params.maintenance_cost_per_day +
            self.cost_params.electricity_cost_per_hour * hours
        )

    def _calculate_time_value_cost(self) -> float:
        """Calculate value of time lost"""
        # Assuming we can estimate vehicle and pedestrian counts
        vehicle_time_cost = (
            self.time_metrics.avg_vehicle_wait_time / 3600 *
            self.cost_params.vehicle_time_value *
            self.time_metrics.throughput_per_hour * 0.7  # 70% vehicles
        )

        ped_time_cost = (
            self.time_metrics.avg_pedestrian_wait_time / 3600 *
            self.cost_params.pedestrian_time_value *
            self.time_metrics.throughput_per_hour * 0.3  # 30% pedestrians
        )

        return vehicle_time_cost + ped_time_cost

    def _calculate_congestion_cost(self) -> float:
        """Calculate congestion externality cost"""
        # Higher wait times = higher congestion cost
        congestion_minutes = self.time_metrics.max_queue_time / 60
        return congestion_minutes * self.cost_params.congestion_cost_per_minute

    def _calculate_environmental_cost(self) -> float:
        """Calculate environmental impact cost"""
        vehicle_minutes = self.time_metrics.avg_vehicle_wait_time / 60
        vehicle_count = self.time_metrics.throughput_per_hour * 0.7

        return (vehicle_minutes * vehicle_count *
                self.cost_params.emission_cost_per_vehicle_minute)

    def calculate_cost_benefit_ratio(self, improvement_cost: float,
                                     baseline_cost: float) -> float:
        """Calculate benefit-cost ratio for improvements"""
        cost_savings = baseline_cost - self.calculate_total_cost()['total']
        return cost_savings / improvement_cost if improvement_cost > 0 else 0.0

class OptimizationEvaluator:
    """Evaluate optimization scenarios"""

    def __init__(self, base_data: pd.DataFrame):
        self.base_data = base_data
        self.scenarios = []

    def add_scenario(self, name: str, data: pd.DataFrame,
                    implementation_cost: float):
        """Add optimization scenario for evaluation"""
        self.scenarios.append({
            'name': name,
            'data': data,
            'cost': implementation_cost
        })

    def compare_scenarios(self) -> pd.DataFrame:
        """Compare all scenarios on time and cost"""
        results = []

        # Baseline
        base_analyzer = TrafficTimeAnalyzer(self.base_data)
        base_metrics = base_analyzer.calculate_time_metrics()
        base_cost_analyzer = TrafficCostAnalyzer(base_metrics, CostParameters())
        base_costs = base_cost_analyzer.calculate_total_cost()

        results.append({
            'Scenario': 'Baseline',
            'Avg_Wait_Time': base_metrics.avg_vehicle_wait_time,
            'Throughput': base_metrics.throughput_per_hour,
            'Total_Cost': base_costs['total'],
            'Implementation_Cost': 0,
            'ROI': 0
        })

        # Each scenario
        for scenario in self.scenarios:
            analyzer = TrafficTimeAnalyzer(scenario['data'])
            metrics = analyzer.calculate_time_metrics()
            cost_analyzer = TrafficCostAnalyzer(metrics, CostParameters())
            costs = cost_analyzer.calculate_total_cost()

            # Calculate ROI
            cost_savings = base_costs['total'] - costs['total']
            roi = (cost_savings / scenario['cost'] * 100) if scenario['cost'] > 0 else 0

            results.append({
                'Scenario': scenario['name'],
                'Avg_Wait_Time': metrics.avg_vehicle_wait_time,
                'Throughput': metrics.throughput_per_hour,
                'Total_Cost': costs['total'],
                'Implementation_Cost': scenario['cost'],
                'ROI': roi
            })

        return pd.DataFrame(results)

    def visualize_comparison(self, results_df: pd.DataFrame):
        """Create visualization of scenario comparison"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Wait time comparison
        axes[0, 0].bar(results_df['Scenario'], results_df['Avg_Wait_Time'])
        axes[0, 0].set_title('Average Wait Time by Scenario')
        axes[0, 0].set_ylabel('Wait Time (seconds)')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # Throughput comparison
        axes[0, 1].bar(results_df['Scenario'], results_df['Throughput'])
        axes[0, 1].set_title('Throughput by Scenario')
        axes[0, 1].set_ylabel('Entities per Hour')
        axes[0, 1].tick_params(axis='x', rotation=45)

        # Cost comparison
        axes[1, 0].bar(results_df['Scenario'], results_df['Total_Cost'])
        axes[1, 0].set_title('Total Cost by Scenario')
        axes[1, 0].set_ylabel('Cost (£/day)')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # ROI comparison
        axes[1, 1].bar(results_df['Scenario'], results_df['ROI'])
        axes[1, 1].set_title('Return on Investment')
        axes[1, 1].set_ylabel('ROI (%)')
        axes[1, 1].axhline(y=0, color='r', linestyle='--')
        axes[1, 1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig('scenario_comparison.png', dpi=300, bbox_inches='tight')
        plt.show()

# Main execution example
if __name__ == "__main__":
    # Load simulation data
    data = pd.read_csv('all_sessions_combined.csv')

    # Time analysis
    print("=" * 60)
    print("TIME ANALYSIS")
    print("=" * 60)
    time_analyzer = TrafficTimeAnalyzer(data)
    metrics = time_analyzer.calculate_time_metrics()
    print(f"Average Vehicle Wait Time: {metrics.avg_vehicle_wait_time:.2f}s")
    print(f"Average Pedestrian Wait Time: {metrics.avg_pedestrian_wait_time:.2f}s")
    print(f"Throughput: {metrics.throughput_per_hour:.2f} entities/hour")
    print(f"Utilization: {metrics.utilization_rate:.2%}")

    # Cost analysis
    print("\n" + "=" * 60)
    print("COST ANALYSIS")
    print("=" * 60)
    cost_params = CostParameters()
    cost_analyzer = TrafficCostAnalyzer(metrics, cost_params)
    costs = cost_analyzer.calculate_total_cost()
    for category, cost in costs.items():
        print(f"{category.replace('_', ' ').title()}: £{cost:.2f}")

    # Period analysis
    print("\n" + "=" * 60)
    print("ANALYSIS BY PERIOD TYPE")
    print("=" * 60)
    period_results = time_analyzer.analyze_by_period()
    if period_results is not None:
        print(period_results.to_string(index=False))
```

---

## Part 4: Complete Implementation Workflow

### 4.1 Step-by-Step Implementation

**Phase 1: Data Collection (Completed)**
- 8 observation windows
- 4-person team collection
- Merged with metadata

**Phase 2: Build Base SIMUL8 Model**
```
1. Import your collected data
2. Create entities (WB/EB Vehicles, Crossers, Posers)
3. Define queues and resources
4. Add arrival distributions from data
5. Add service time distributions from data
6. Run baseline simulation
```

**Phase 3: Add Hybrid Components**
```
1. Add agent-based pedestrian logic (Visual Logic)
2. Add system dynamics feedback (Excel/Python link)
3. Validate hybrid model against real data
```

**Phase 4: Implement Optimization**
```
1. Define decision variables
2. Set up optimization objectives
3. Run simulation-based optimization
4. Or use external GA with Python
```

**Phase 5: Build Analysis Software**
```
1. Implement TrafficTimeAnalyzer
2. Implement TrafficCostAnalyzer
3. Implement OptimizationEvaluator
4. Create dashboard/reporting
```

### 4.2 Integration Architecture

```python
# Main integration script
class HybridTrafficOptimizationSystem:
    """
    Complete system integrating:
    - SIMUL8 simulation
    - Hybrid modeling
    - Optimization
    - Time & cost analysis
    """

    def __init__(self, data_file: str):
        self.data = pd.read_csv(data_file)
        self.simul8_connector = SIMUL8Connector()  # COM interface
        self.optimizer = GeneticAlgorithmOptimizer()
        self.analyzer = TrafficTimeAnalyzer(self.data)

    def run_optimization_cycle(self, n_iterations: int = 50):
        """
        Complete optimization cycle
        """
        best_solution = None
        best_fitness = float('inf')

        for i in range(n_iterations):
            # Generate candidate solution
            solution = self.optimizer.generate_candidate()

            # Run SIMUL8 with this configuration
            results = self.simul8_connector.run_simulation(solution)

            # Analyze time & cost
            metrics = self.analyze_results(results)
            fitness = self.calculate_fitness(metrics)

            # Update best
            if fitness < best_fitness:
                best_solution = solution
                best_fitness = fitness

            # Update optimizer
            self.optimizer.update(solution, fitness)

        return best_solution, best_fitness
```

---

## Part 5: Dashboard & Reporting

### 5.1 Create Interactive Dashboard

Use Streamlit for real-time analysis:

```python
import streamlit as st

def main():
    st.title("Traffic Optimization Dashboard")

    # Load data
    data = load_simulation_data()

    # Sidebar controls
    st.sidebar.header("Analysis Options")
    analysis_type = st.sidebar.selectbox(
        "Select Analysis",
        ["Time Analysis", "Cost Analysis", "Optimization Results"]
    )

    if analysis_type == "Time Analysis":
        show_time_analysis(data)
    elif analysis_type == "Cost Analysis":
        show_cost_analysis(data)
    else:
        show_optimization_results(data)

def show_time_analysis(data):
    analyzer = TrafficTimeAnalyzer(data)
    metrics = analyzer.calculate_time_metrics()

    col1, col2, col3 = st.columns(3)
    col1.metric("Avg Wait Time", f"{metrics.avg_vehicle_wait_time:.1f}s")
    col2.metric("Throughput", f"{metrics.throughput_per_hour:.1f}/hr")
    col3.metric("Utilization", f"{metrics.utilization_rate:.1%}")

    # Period analysis
    period_df = analyzer.analyze_by_period()
    if period_df is not None:
        st.subheader("Performance by Period")
        st.dataframe(period_df)

        # Visualization
        fig = px.bar(period_df, x='Period', y='Throughput')
        st.plotly_chart(fig)
```

---

## Summary: Implementation Checklist

### Hybrid Modeling:
- [ ] Build base SIMUL8 discrete event model
- [ ] Add agent-based pedestrian behavior
- [ ] Integrate system dynamics feedback
- [ ] Validate against real data

### Optimization:
- [ ] Define optimization objectives
- [ ] Implement decision variables
- [ ] Choose optimization algorithm (GA/RSM)
- [ ] Run optimization experiments
- [ ] Validate optimal solutions

### Time & Cost Software:
- [ ] Implement TrafficTimeAnalyzer class
- [ ] Implement TrafficCostAnalyzer class
- [ ] Create cost parameter database
- [ ] Build OptimizationEvaluator
- [ ] Create visualization module
- [ ] Build interactive dashboard

### Integration:
- [ ] Connect SIMUL8 to Python (COM/API)
- [ ] Build orchestration layer
- [ ] Implement data pipeline
- [ ] Create reporting system

---

**Estimated Development Time:**
- Hybrid Model: 2-3 weeks
- Optimization System: 2-3 weeks
- Time & Cost Software: 2-3 weeks
- Integration & Testing: 1-2 weeks
- **Total: 7-11 weeks**
