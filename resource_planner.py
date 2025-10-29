#!/usr/bin/env python3
"""
Resource Planning Tool for Traffic Systems
Combines variability analysis and queueing theory to generate
comprehensive resource allocation recommendations.
"""

import pandas as pd
import numpy as np
import json
from dataclasses import dataclass
from typing import Dict, List
import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class ResourceScenario:
    """A resource allocation scenario"""
    name: str
    description: str
    capacity: int
    utilization: float
    avg_wait: float
    queue_length: float
    daily_cost: float
    annual_cost: float
    performance_score: float  # 0-100


class ResourcePlanner:
    """Generate resource planning scenarios and recommendations"""

    def __init__(self, variability_data: Dict, queueing_data: Dict,
                 cost_per_server: float = 10000):
        self.var_data = variability_data
        self.queue_data = queueing_data
        self.cost_per_server = cost_per_server
        self.scenarios = {}

    def generate_scenarios(self) -> Dict[str, List[ResourceScenario]]:
        """Generate multiple scenarios for each period/entity combination"""
        scenarios = {}

        for key in self.queue_data.keys():
            queue_result = self.queue_data[key]
            optimal_servers = queue_result.get('optimal_servers', 2)
            min_servers = queue_result.get('min_servers', 1)

            period_entity_scenarios = []

            # Scenario 1: Minimum capacity (cost-focused)
            period_entity_scenarios.append(self._create_scenario(
                name="Minimum Cost",
                description="Absolute minimum capacity (high risk)",
                capacity=min_servers,
                key=key
            ))

            # Scenario 2: Conservative (85% target utilization)
            conservative_capacity = max(min_servers, int(optimal_servers * 0.85))
            period_entity_scenarios.append(self._create_scenario(
                name="Conservative",
                description="85% target utilization (moderate risk)",
                capacity=conservative_capacity,
                key=key
            ))

            # Scenario 3: Optimal (75% target utilization)
            period_entity_scenarios.append(self._create_scenario(
                name="Optimal",
                description="75% target utilization (balanced)",
                capacity=optimal_servers,
                key=key
            ))

            # Scenario 4: Safe (65% target utilization)
            safe_capacity = int(optimal_servers * 1.15)
            period_entity_scenarios.append(self._create_scenario(
                name="Safe",
                description="65% target utilization (low risk)",
                capacity=safe_capacity,
                key=key
            ))

            scenarios[key] = period_entity_scenarios

        self.scenarios = scenarios
        return scenarios

    def _create_scenario(self, name: str, description: str,
                        capacity: int, key: str) -> ResourceScenario:
        """Create a single resource scenario"""
        queue_result = self.queue_data[key]
        arrival_rate = queue_result.get('arrival_rate', 0)
        service_rate = 60  # Default service rate

        # Recalculate utilization with this capacity
        utilization = arrival_rate / (capacity * service_rate)

        # Estimate wait time (simplified)
        if utilization >= 1.0:
            avg_wait = float('inf')
            queue_length = float('inf')
            performance_score = 0
        else:
            # Simple approximation
            base_wait = queue_result.get('avg_wait_queue', 60)
            optimal_cap = queue_result.get('optimal_servers', capacity)
            # Adjust wait based on capacity difference
            capacity_ratio = optimal_cap / capacity if capacity > 0 else 1
            avg_wait = base_wait * (capacity_ratio ** 2)
            queue_length = (arrival_rate / 3600) * avg_wait

            # Performance score (0-100)
            wait_score = max(0, 100 - avg_wait)
            util_score = 100 * (1 - abs(utilization - 0.70) / 0.70)
            performance_score = (wait_score + util_score) / 2

        # Cost calculations
        # Infrastructure cost (amortized daily)
        infra_cost_daily = (self.cost_per_server * capacity) / (10 * 365)

        # Operational cost (daily)
        operational_daily = capacity * 5  # £5 per server per day

        # Time value cost (estimate)
        time_value_hourly = (avg_wait / 3600) * arrival_rate * 15  # £15/hour
        time_value_daily = time_value_hourly * 8  # 8-hour day

        daily_cost = infra_cost_daily + operational_daily + time_value_daily
        annual_cost = daily_cost * 365

        return ResourceScenario(
            name=name,
            description=description,
            capacity=capacity,
            utilization=utilization,
            avg_wait=avg_wait if avg_wait != float('inf') else 999,
            queue_length=queue_length if queue_length != float('inf') else 99,
            daily_cost=daily_cost,
            annual_cost=annual_cost,
            performance_score=performance_score
        )

    def generate_report(self) -> str:
        """Generate comprehensive resource planning report"""
        report = []
        report.append("=" * 80)
        report.append("RESOURCE PLANNING REPORT")
        report.append("=" * 80)
        report.append("")

        for key, scenario_list in self.scenarios.items():
            # Extract period and entity from key
            parts = key.split('_')
            period = ' '.join(parts[:-1])
            entity = parts[-1]

            report.append(f"\n{'=' * 80}")
            report.append(f"RESOURCE SCENARIOS: {period} - {entity}")
            report.append(f"{'=' * 80}\n")

            # Create comparison table
            report.append(f"{'Scenario':<20} {'Cap':<5} {'Util':<8} {'Wait(s)':<10} "
                        f"{'Queue':<8} {'Daily £':<12} {'Annual £':<14} {'Score':<6}")
            report.append("-" * 80)

            for scenario in scenario_list:
                wait_str = f"{scenario.avg_wait:.0f}" if scenario.avg_wait < 900 else "999+"
                util_str = f"{scenario.utilization:.1%}" if scenario.utilization < 1 else ">100%"
                queue_str = f"{scenario.queue_length:.1f}" if scenario.queue_length < 90 else "99+"

                report.append(
                    f"{scenario.name:<20} "
                    f"{scenario.capacity:<5} "
                    f"{util_str:<8} "
                    f"{wait_str:<10} "
                    f"{queue_str:<8} "
                    f"{scenario.daily_cost:<12,.2f} "
                    f"{scenario.annual_cost:<14,.2f} "
                    f"{scenario.performance_score:<6.0f}"
                )

            # Recommendation
            report.append("")
            best_scenario = max(scenario_list, key=lambda s: s.performance_score)
            report.append(f"RECOMMENDED: {best_scenario.name}")
            report.append(f"  Capacity: {best_scenario.capacity} servers")
            report.append(f"  Utilization: {best_scenario.utilization:.1%}")
            report.append(f"  Expected Wait: {best_scenario.avg_wait:.0f} seconds")
            report.append(f"  Annual Cost: £{best_scenario.annual_cost:,.2f}")
            report.append(f"  {best_scenario.description}")
            report.append("")

        # Overall summary
        report.append("\n" + "=" * 80)
        report.append("IMPLEMENTATION ROADMAP")
        report.append("=" * 80)
        report.append("")

        report.append("PHASE 1: IMMEDIATE (Week 1-2)")
        report.append("  1. Configure SIMUL8 with recommended capacities")
        report.append("  2. Import empirical distributions from variability analysis")
        report.append("  3. Run baseline simulation (30+ replications)")
        report.append("  4. Validate against queueing theory predictions")
        report.append("")

        report.append("PHASE 2: OPTIMIZATION (Week 3-4)")
        report.append("  1. Test alternative scenarios in SIMUL8")
        report.append("  2. Run sensitivity analysis (±20% arrival rates)")
        report.append("  3. Calculate cost-benefit for each scenario")
        report.append("  4. Generate Pareto front (cost vs performance)")
        report.append("")

        report.append("PHASE 3: VALIDATION (Week 5-6)")
        report.append("  1. Compare simulation results to queueing predictions")
        report.append("  2. Refine capacity recommendations")
        report.append("  3. Document assumptions and limitations")
        report.append("  4. Prepare final recommendations")
        report.append("")

        report.append("CONFIGURATION FOR SIMUL8:")
        report.append("-" * 80)
        for key, scenario_list in self.scenarios.items():
            parts = key.split('_')
            period = ' '.join(parts[:-1])
            entity = parts[-1]
            best = max(scenario_list, key=lambda s: s.performance_score)

            report.append(f"{period} - {entity}:")
            report.append(f"  Work Center Capacity: {best.capacity}")
            report.append(f"  Queue Capacity: {int(best.queue_length) + 10}")
            report.append("")

        return "\n".join(report)

    def create_comparison_charts(self, output_dir: str = '.'):
        """Create visual comparison of scenarios"""

        # Collect all scenarios for plotting
        all_scenarios = []
        for key, scenario_list in self.scenarios.items():
            for scenario in scenario_list:
                parts = key.split('_')
                period = ' '.join(parts[:-1])
                entity = parts[-1]
                all_scenarios.append({
                    'Period': period,
                    'Entity': entity,
                    'Scenario': scenario.name,
                    'Capacity': scenario.capacity,
                    'Utilization': scenario.utilization,
                    'Wait': scenario.avg_wait if scenario.avg_wait < 900 else 900,
                    'Annual_Cost': scenario.annual_cost,
                    'Score': scenario.performance_score
                })

        df = pd.DataFrame(all_scenarios)

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Resource Planning Scenario Comparison', fontsize=16, fontweight='bold')

        # 1. Cost vs Performance scatter
        ax = axes[0, 0]
        scenarios_unique = df['Scenario'].unique()
        colors = {'Minimum Cost': 'red', 'Conservative': 'orange',
                 'Optimal': 'green', 'Safe': 'blue'}

        for scenario_name in scenarios_unique:
            subset = df[df['Scenario'] == scenario_name]
            ax.scatter(subset['Annual_Cost'], subset['Score'],
                      label=scenario_name, alpha=0.7, s=100,
                      color=colors.get(scenario_name, 'gray'))

        ax.set_xlabel('Annual Cost (£)')
        ax.set_ylabel('Performance Score (0-100)')
        ax.set_title('Cost vs Performance Tradeoff')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Wait time by scenario
        ax = axes[0, 1]
        scenario_order = ['Minimum Cost', 'Conservative', 'Optimal', 'Safe']
        df_grouped = df.groupby('Scenario')['Wait'].mean().reindex(scenario_order)
        bars = df_grouped.plot(kind='bar', ax=ax, color='steelblue', alpha=0.8)
        ax.set_xlabel('Scenario')
        ax.set_ylabel('Average Wait Time (seconds)')
        ax.set_title('Average Wait Time by Scenario')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=60, color='r', linestyle='--', label='60s target', alpha=0.7)
        ax.legend()

        # 3. Utilization by scenario
        ax = axes[1, 0]
        df_util = df.groupby('Scenario')['Utilization'].mean().reindex(scenario_order)
        bars = df_util.plot(kind='bar', ax=ax, color='coral', alpha=0.8)
        ax.set_xlabel('Scenario')
        ax.set_ylabel('Average Utilization')
        ax.set_title('System Utilization by Scenario')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0.75, color='g', linestyle='--', label='75% target', alpha=0.7)
        ax.axhline(y=0.85, color='orange', linestyle='--', label='85% warning', alpha=0.7)
        ax.legend()

        # 4. Capacity requirements by period
        ax = axes[1, 1]
        optimal_data = df[df['Scenario'] == 'Optimal']
        pivot = optimal_data.pivot_table(values='Capacity', index='Period',
                                        columns='Entity', aggfunc='mean')
        pivot.plot(kind='bar', ax=ax, alpha=0.8)
        ax.set_xlabel('Period')
        ax.set_ylabel('Recommended Capacity (servers)')
        ax.set_title('Optimal Capacity by Period (Optimal Scenario)')
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        ax.legend(title='Entity Type')
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        output_file = f'{output_dir}/resource_planning_scenarios.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Scenario comparison chart saved to {output_file}")
        plt.close()

    def export_scenarios_to_json(self, filename: str = 'resource_scenarios.json'):
        """Export all scenarios to JSON"""
        export_data = {}

        for key, scenario_list in self.scenarios.items():
            export_data[key] = []
            for scenario in scenario_list:
                export_data[key].append({
                    'name': scenario.name,
                    'description': scenario.description,
                    'capacity': scenario.capacity,
                    'utilization': scenario.utilization,
                    'avg_wait': scenario.avg_wait,
                    'queue_length': scenario.queue_length,
                    'daily_cost': scenario.daily_cost,
                    'annual_cost': scenario.annual_cost,
                    'performance_score': scenario.performance_score
                })

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"Scenarios exported to {filename}")


def main():
    """Main execution"""
    import sys

    print("=" * 80)
    print("RESOURCE PLANNER - Queueing Theory-Based Capacity Planning")
    print("=" * 80)
    print()

    # Load variability metrics
    try:
        with open('variability_metrics.json', 'r') as f:
            var_data = json.load(f)
        print(f"Loaded variability metrics: {len(var_data)} groups")
    except FileNotFoundError:
        print("ERROR: variability_metrics.json not found")
        print("Please run: python variability_analyzer.py <data.csv>")
        sys.exit(1)

    # Load queueing results
    try:
        with open('queueing_results.json', 'r') as f:
            queue_data = json.load(f)
        print(f"Loaded queueing results: {len(queue_data)} groups")
    except FileNotFoundError:
        print("ERROR: queueing_results.json not found")
        print("Please run: python queueing_calculator.py <data.csv>")
        sys.exit(1)

    # Get cost per server from command line or use default
    cost_per_server = float(sys.argv[1]) if len(sys.argv) > 1 else 10000
    print(f"Using cost per server: £{cost_per_server:,.2f}")
    print()

    try:
        # Create planner
        planner = ResourcePlanner(var_data, queue_data, cost_per_server)

        # Generate scenarios
        print("Generating resource allocation scenarios...")
        scenarios = planner.generate_scenarios()
        print(f"Generated {sum(len(s) for s in scenarios.values())} scenarios")

        # Generate report
        print("\nGenerating comprehensive report...")
        report = planner.generate_report()

        # Save report
        with open('resource_planning_report.txt', 'w') as f:
            f.write(report)
        print("Report saved to resource_planning_report.txt")

        # Export scenarios
        planner.export_scenarios_to_json('resource_scenarios.json')

        # Create visualizations
        print("\nCreating comparison charts...")
        planner.create_comparison_charts()

        print("\n" + "=" * 80)
        print("RESOURCE PLANNING COMPLETE")
        print("=" * 80)
        print("\nOutputs generated:")
        print("  - resource_planning_report.txt (comprehensive report)")
        print("  - resource_scenarios.json (all scenarios)")
        print("  - resource_planning_scenarios.png (comparison charts)")
        print("\nNext steps:")
        print("  1. Review recommended scenarios")
        print("  2. Configure SIMUL8 with optimal capacities")
        print("  3. Run simulation validation")
        print("  4. Perform sensitivity analysis")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
