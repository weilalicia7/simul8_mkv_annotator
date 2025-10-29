"""
Traffic Time & Cost Analysis System
Complete implementation for analyzing SIMUL8 traffic simulation data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime

# Set plotting style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

@dataclass
class CostParameters:
    """Cost structure for traffic system analysis"""
    # Infrastructure costs (£)
    traffic_light_cost: float = 5000.0
    signage_cost: float = 500.0
    road_marking_cost: float = 2000.0
    pedestrian_barrier_cost: float = 1500.0

    # Annual operational costs (£)
    maintenance_cost_per_year: float = 36500.0
    electricity_cost_per_year: float = 9125.0

    # Time value costs (£/hour)
    vehicle_time_value: float = 15.0
    pedestrian_time_value: float = 8.0

    # Externality costs (£)
    congestion_cost_per_minute: float = 0.5
    emission_cost_per_vehicle_minute: float = 0.1
    safety_incident_cost: float = 5000.0

@dataclass
class TimeMetrics:
    """Comprehensive time-related performance metrics"""
    # Wait times (seconds)
    avg_vehicle_wait_time: float
    avg_pedestrian_wait_time: float
    max_queue_time: float
    min_inter_arrival: float
    max_inter_arrival: float

    # Throughput metrics
    total_arrivals: int
    simulation_duration: float  # seconds
    throughput_per_hour: float

    # Utilization metrics
    system_utilization: float
    peak_period_utilization: float

    # Service time metrics
    avg_service_time: float
    max_service_time: float

@dataclass
class CostMetrics:
    """Comprehensive cost breakdown"""
    infrastructure_cost_per_day: float
    operational_cost_per_day: float
    time_value_cost_per_day: float
    congestion_cost_per_day: float
    environmental_cost_per_day: float
    total_cost_per_day: float

    # Annual projections
    annual_infrastructure: float
    annual_operational: float
    annual_time_value: float
    annual_congestion: float
    annual_environmental: float
    annual_total: float

class TrafficDataLoader:
    """Load and preprocess traffic simulation data"""

    @staticmethod
    def load_data(filepath: str) -> pd.DataFrame:
        """Load CSV data with preprocessing"""
        df = pd.read_csv(filepath)

        # Convert Service Time to numeric (handle '-' values)
        if 'Service Time (s)' in df.columns:
            df['Service Time (s)'] = pd.to_numeric(
                df['Service Time (s)'].replace('-', np.nan),
                errors='coerce'
            )

        # Convert Inter-Arrival to numeric
        if 'Inter-Arrival (s)' in df.columns:
            df['Inter-Arrival (s)'] = pd.to_numeric(
                df['Inter-Arrival (s)'],
                errors='coerce'
            )

        # Sort by time
        if 'Time (s)' in df.columns:
            df = df.sort_values('Time (s)').reset_index(drop=True)

        return df

    @staticmethod
    def separate_entity_types(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Separate data by entity type"""
        entity_data = {}

        if 'Entity' in df.columns:
            for entity in df['Entity'].unique():
                entity_data[entity] = df[df['Entity'] == entity].copy()

        return entity_data

class TrafficTimeAnalyzer:
    """Analyze time-related metrics from simulation data"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.entity_data = TrafficDataLoader.separate_entity_types(data)
        self.metrics = None

    def calculate_comprehensive_metrics(self) -> TimeMetrics:
        """Calculate all time-related metrics"""

        # Separate vehicles and pedestrians
        vehicles = pd.concat([
            self.entity_data.get('EB Vehicles', pd.DataFrame()),
            self.entity_data.get('WB Vehicles', pd.DataFrame())
        ]) if len(self.entity_data) > 0 else pd.DataFrame()

        pedestrians = pd.concat([
            self.entity_data.get('Crossers', pd.DataFrame()),
            self.entity_data.get('Posers', pd.DataFrame())
        ]) if len(self.entity_data) > 0 else pd.DataFrame()

        # Calculate wait times (using inter-arrival as proxy)
        avg_vehicle_wait = vehicles['Inter-Arrival (s)'].mean() if len(vehicles) > 0 else 0.0
        avg_ped_wait = pedestrians['Inter-Arrival (s)'].mean() if len(pedestrians) > 0 else 0.0

        # Calculate service times
        avg_service = self.data['Service Time (s)'].mean()
        max_service = self.data['Service Time (s)'].max()

        # Calculate throughput
        if 'Time (s)' in self.data.columns and len(self.data) > 0:
            duration = self.data['Time (s)'].max() - self.data['Time (s)'].min()
            throughput = len(self.data) / (duration / 3600) if duration > 0 else 0.0
        else:
            duration = 0.0
            throughput = 0.0

        # Calculate utilization
        total_service_time = self.data['Service Time (s)'].sum()
        utilization = (total_service_time / duration) if duration > 0 else 0.0

        # Peak period analysis (if Session_ID or Period_Type available)
        peak_utilization = self._calculate_peak_utilization()

        # Inter-arrival statistics
        min_inter = self.data['Inter-Arrival (s)'].min()
        max_inter = self.data['Inter-Arrival (s)'].max()
        max_queue = max_inter  # Simplified

        self.metrics = TimeMetrics(
            avg_vehicle_wait_time=avg_vehicle_wait,
            avg_pedestrian_wait_time=avg_ped_wait,
            max_queue_time=max_queue,
            min_inter_arrival=min_inter,
            max_inter_arrival=max_inter,
            total_arrivals=len(self.data),
            simulation_duration=duration,
            throughput_per_hour=throughput,
            system_utilization=min(utilization, 1.0),
            peak_period_utilization=peak_utilization,
            avg_service_time=avg_service,
            max_service_time=max_service
        )

        return self.metrics

    def _calculate_peak_utilization(self) -> float:
        """Calculate utilization during peak periods"""
        if 'Period_Type' in self.data.columns:
            peak_data = self.data[self.data['Period_Type'].str.contains('Peak', na=False)]
            if len(peak_data) > 0:
                duration = peak_data['Time (s)'].max() - peak_data['Time (s)'].min()
                service_time = peak_data['Service Time (s)'].sum()
                return service_time / duration if duration > 0 else 0.0
        return self.metrics.system_utilization if self.metrics else 0.0

    def analyze_by_period(self) -> Optional[pd.DataFrame]:
        """Analyze metrics by period type"""
        if 'Period_Type' not in self.data.columns:
            return None

        results = []
        for period in self.data['Period_Type'].unique():
            period_data = self.data[self.data['Period_Type'] == period]
            analyzer = TrafficTimeAnalyzer(period_data)
            metrics = analyzer.calculate_comprehensive_metrics()

            results.append({
                'Period': period,
                'Arrivals': metrics.total_arrivals,
                'Avg_Vehicle_Wait': metrics.avg_vehicle_wait_time,
                'Avg_Pedestrian_Wait': metrics.avg_pedestrian_wait_time,
                'Throughput': metrics.throughput_per_hour,
                'Utilization': metrics.system_utilization * 100
            })

        return pd.DataFrame(results)

    def analyze_by_entity(self) -> pd.DataFrame:
        """Analyze metrics by entity type"""
        results = []

        for entity_name, entity_df in self.entity_data.items():
            if len(entity_df) == 0:
                continue

            results.append({
                'Entity': entity_name,
                'Count': len(entity_df),
                'Avg_Inter_Arrival': entity_df['Inter-Arrival (s)'].mean(),
                'Std_Inter_Arrival': entity_df['Inter-Arrival (s)'].std(),
                'Avg_Service_Time': entity_df['Service Time (s)'].mean(),
                'Max_Service_Time': entity_df['Service Time (s)'].max()
            })

        return pd.DataFrame(results)

class TrafficCostAnalyzer:
    """Analyze cost metrics from time data"""

    def __init__(self, time_metrics: TimeMetrics, cost_params: CostParameters):
        self.time_metrics = time_metrics
        self.cost_params = cost_params

    def calculate_comprehensive_costs(self) -> CostMetrics:
        """Calculate complete cost breakdown"""

        # Infrastructure (amortized daily)
        infra_per_day = self._calculate_infrastructure_cost()

        # Operational
        ops_per_day = self._calculate_operational_cost()

        # Time value
        time_value_per_day = self._calculate_time_value_cost()

        # Congestion
        congestion_per_day = self._calculate_congestion_cost()

        # Environmental
        env_per_day = self._calculate_environmental_cost()

        # Total
        total_per_day = (infra_per_day + ops_per_day + time_value_per_day +
                        congestion_per_day + env_per_day)

        # Annual projections
        return CostMetrics(
            infrastructure_cost_per_day=infra_per_day,
            operational_cost_per_day=ops_per_day,
            time_value_cost_per_day=time_value_per_day,
            congestion_cost_per_day=congestion_per_day,
            environmental_cost_per_day=env_per_day,
            total_cost_per_day=total_per_day,
            annual_infrastructure=infra_per_day * 365,
            annual_operational=ops_per_day * 365,
            annual_time_value=time_value_per_day * 365,
            annual_congestion=congestion_per_day * 365,
            annual_environmental=env_per_day * 365,
            annual_total=total_per_day * 365
        )

    def _calculate_infrastructure_cost(self) -> float:
        """Calculate amortized infrastructure cost per day"""
        total_infrastructure = (
            self.cost_params.traffic_light_cost * 2 +
            self.cost_params.signage_cost * 4 +
            self.cost_params.road_marking_cost * 2 +
            self.cost_params.pedestrian_barrier_cost * 2
        )

        # Amortize over 10 years
        annual_cost = total_infrastructure / 10
        return annual_cost / 365

    def _calculate_operational_cost(self) -> float:
        """Calculate daily operational costs"""
        return (self.cost_params.maintenance_cost_per_year +
                self.cost_params.electricity_cost_per_year) / 365

    def _calculate_time_value_cost(self) -> float:
        """Calculate value of time lost"""
        hours_simulated = self.time_metrics.simulation_duration / 3600

        # Estimate vehicle and pedestrian proportions
        vehicles_per_hour = self.time_metrics.throughput_per_hour * 0.7
        pedestrians_per_hour = self.time_metrics.throughput_per_hour * 0.3

        # Calculate time value costs
        vehicle_time_cost = (
            vehicles_per_hour *
            (self.time_metrics.avg_vehicle_wait_time / 3600) *
            self.cost_params.vehicle_time_value *
            hours_simulated
        )

        ped_time_cost = (
            pedestrians_per_hour *
            (self.time_metrics.avg_pedestrian_wait_time / 3600) *
            self.cost_params.pedestrian_time_value *
            hours_simulated
        )

        # Convert to daily cost (scale to 24 hours)
        daily_factor = 24 / hours_simulated if hours_simulated > 0 else 1
        return (vehicle_time_cost + ped_time_cost) * daily_factor

    def _calculate_congestion_cost(self) -> float:
        """Calculate congestion externality cost"""
        congestion_minutes = self.time_metrics.max_queue_time / 60
        arrivals_per_day = self.time_metrics.throughput_per_hour * 24

        return (congestion_minutes *
                self.cost_params.congestion_cost_per_minute *
                arrivals_per_day / 100)  # Per 100 arrivals

    def _calculate_environmental_cost(self) -> float:
        """Calculate environmental impact cost"""
        vehicle_wait_minutes = self.time_metrics.avg_vehicle_wait_time / 60
        vehicles_per_day = self.time_metrics.throughput_per_hour * 24 * 0.7

        return (vehicle_wait_minutes *
                vehicles_per_day *
                self.cost_params.emission_cost_per_vehicle_minute)

class TrafficReportGenerator:
    """Generate comprehensive analysis reports"""

    def __init__(self, data: pd.DataFrame, cost_params: CostParameters):
        self.data = data
        self.cost_params = cost_params

        # Run analyses
        self.time_analyzer = TrafficTimeAnalyzer(data)
        self.time_metrics = self.time_analyzer.calculate_comprehensive_metrics()

        self.cost_analyzer = TrafficCostAnalyzer(self.time_metrics, cost_params)
        self.cost_metrics = self.cost_analyzer.calculate_comprehensive_costs()

    def generate_text_report(self) -> str:
        """Generate formatted text report"""
        report = []
        report.append("=" * 80)
        report.append("TRAFFIC ANALYSIS REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 80)

        # Time metrics
        report.append("\n" + "TIME ANALYSIS")
        report.append("-" * 80)
        report.append(f"Total Arrivals: {self.time_metrics.total_arrivals}")
        report.append(f"Simulation Duration: {self.time_metrics.simulation_duration:.1f} seconds")
        report.append(f"Throughput: {self.time_metrics.throughput_per_hour:.2f} entities/hour")
        report.append(f"\nAverage Wait Times:")
        report.append(f"  Vehicles: {self.time_metrics.avg_vehicle_wait_time:.2f} seconds")
        report.append(f"  Pedestrians: {self.time_metrics.avg_pedestrian_wait_time:.2f} seconds")
        report.append(f"\nSystem Utilization: {self.time_metrics.system_utilization:.2%}")
        report.append(f"Peak Period Utilization: {self.time_metrics.peak_period_utilization:.2%}")

        # Cost metrics
        report.append("\n" + "COST ANALYSIS (Daily)")
        report.append("-" * 80)
        report.append(f"Infrastructure: £{self.cost_metrics.infrastructure_cost_per_day:.2f}")
        report.append(f"Operational: £{self.cost_metrics.operational_cost_per_day:.2f}")
        report.append(f"Time Value: £{self.cost_metrics.time_value_cost_per_day:.2f}")
        report.append(f"Congestion: £{self.cost_metrics.congestion_cost_per_day:.2f}")
        report.append(f"Environmental: £{self.cost_metrics.environmental_cost_per_day:.2f}")
        report.append(f"{'=' * 80}")
        report.append(f"TOTAL DAILY COST: £{self.cost_metrics.total_cost_per_day:.2f}")
        report.append(f"TOTAL ANNUAL COST: £{self.cost_metrics.annual_total:,.2f}")

        # Period analysis
        if 'Period_Type' in self.data.columns:
            period_df = self.time_analyzer.analyze_by_period()
            if period_df is not None:
                report.append("\n" + "ANALYSIS BY PERIOD TYPE")
                report.append("-" * 80)
                report.append(period_df.to_string(index=False))

        # Entity analysis
        entity_df = self.time_analyzer.analyze_by_entity()
        if len(entity_df) > 0:
            report.append("\n" + "ANALYSIS BY ENTITY TYPE")
            report.append("-" * 80)
            report.append(entity_df.to_string(index=False))

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def save_report(self, filename: str = "traffic_analysis_report.txt"):
        """Save report to file"""
        report = self.generate_text_report()
        with open(filename, 'w') as f:
            f.write(report)
        print(f"Report saved to: {filename}")

    def export_metrics_json(self, filename: str = "traffic_metrics.json"):
        """Export metrics as JSON"""
        metrics_dict = {
            'time_metrics': asdict(self.time_metrics),
            'cost_metrics': asdict(self.cost_metrics),
            'analysis_date': datetime.now().isoformat()
        }

        with open(filename, 'w') as f:
            json.dump(metrics_dict, f, indent=2)
        print(f"Metrics exported to: {filename}")

    def create_visualizations(self, output_dir: str = "."):
        """Create comprehensive visualizations"""

        # Figure 1: Time metrics
        fig1, axes = plt.subplots(2, 2, figsize=(15, 12))

        # Wait time comparison
        wait_data = {
            'Vehicles': self.time_metrics.avg_vehicle_wait_time,
            'Pedestrians': self.time_metrics.avg_pedestrian_wait_time
        }
        axes[0, 0].bar(wait_data.keys(), wait_data.values(), color=['#1f77b4', '#ff7f0e'])
        axes[0, 0].set_title('Average Wait Time by Type', fontsize=14, fontweight='bold')
        axes[0, 0].set_ylabel('Wait Time (seconds)')
        axes[0, 0].grid(axis='y', alpha=0.3)

        # Throughput
        axes[0, 1].bar(['Throughput'], [self.time_metrics.throughput_per_hour],
                      color='#2ca02c', width=0.5)
        axes[0, 1].set_title('System Throughput', fontsize=14, fontweight='bold')
        axes[0, 1].set_ylabel('Entities per Hour')
        axes[0, 1].grid(axis='y', alpha=0.3)

        # Utilization
        util_data = {
            'Overall': self.time_metrics.system_utilization * 100,
            'Peak Period': self.time_metrics.peak_period_utilization * 100
        }
        axes[1, 0].bar(util_data.keys(), util_data.values(), color=['#d62728', '#9467bd'])
        axes[1, 0].set_title('System Utilization', fontsize=14, fontweight='bold')
        axes[1, 0].set_ylabel('Utilization (%)')
        axes[1, 0].set_ylim([0, 100])
        axes[1, 0].axhline(y=80, color='r', linestyle='--', label='Target (80%)')
        axes[1, 0].legend()
        axes[1, 0].grid(axis='y', alpha=0.3)

        # Inter-arrival distribution
        if len(self.data) > 0:
            axes[1, 1].hist(self.data['Inter-Arrival (s)'].dropna(), bins=30,
                           color='#8c564b', edgecolor='black', alpha=0.7)
            axes[1, 1].set_title('Inter-Arrival Time Distribution', fontsize=14, fontweight='bold')
            axes[1, 1].set_xlabel('Inter-Arrival Time (seconds)')
            axes[1, 1].set_ylabel('Frequency')
            axes[1, 1].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        plt.savefig(f'{output_dir}/time_analysis.png', dpi=300, bbox_inches='tight')
        print(f"Time analysis visualization saved to: {output_dir}/time_analysis.png")
        plt.close()

        # Figure 2: Cost breakdown
        fig2, axes = plt.subplots(1, 2, figsize=(15, 6))

        # Daily costs
        cost_categories = ['Infrastructure', 'Operational', 'Time Value', 'Congestion', 'Environmental']
        daily_costs = [
            self.cost_metrics.infrastructure_cost_per_day,
            self.cost_metrics.operational_cost_per_day,
            self.cost_metrics.time_value_cost_per_day,
            self.cost_metrics.congestion_cost_per_day,
            self.cost_metrics.environmental_cost_per_day
        ]

        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        axes[0].pie(daily_costs, labels=cost_categories, autopct='%1.1f%%',
                   colors=colors, startangle=90)
        axes[0].set_title('Daily Cost Breakdown', fontsize=14, fontweight='bold')

        # Annual costs bar chart
        annual_costs = [
            self.cost_metrics.annual_infrastructure,
            self.cost_metrics.annual_operational,
            self.cost_metrics.annual_time_value,
            self.cost_metrics.annual_congestion,
            self.cost_metrics.annual_environmental
        ]

        axes[1].barh(cost_categories, annual_costs, color=colors)
        axes[1].set_title('Annual Cost Breakdown', fontsize=14, fontweight='bold')
        axes[1].set_xlabel('Annual Cost (£)')
        axes[1].grid(axis='x', alpha=0.3)

        # Add value labels
        for i, v in enumerate(annual_costs):
            axes[1].text(v, i, f' £{v:,.0f}', va='center')

        plt.tight_layout()
        plt.savefig(f'{output_dir}/cost_analysis.png', dpi=300, bbox_inches='tight')
        print(f"Cost analysis visualization saved to: {output_dir}/cost_analysis.png")
        plt.close()

        # Figure 3: Period comparison (if available)
        if 'Period_Type' in self.data.columns:
            period_df = self.time_analyzer.analyze_by_period()
            if period_df is not None and len(period_df) > 0:
                fig3, axes = plt.subplots(2, 2, figsize=(15, 12))

                # Arrivals by period
                axes[0, 0].bar(period_df['Period'], period_df['Arrivals'])
                axes[0, 0].set_title('Arrivals by Period', fontsize=14, fontweight='bold')
                axes[0, 0].set_ylabel('Total Arrivals')
                axes[0, 0].tick_params(axis='x', rotation=45)
                axes[0, 0].grid(axis='y', alpha=0.3)

                # Throughput by period
                axes[0, 1].bar(period_df['Period'], period_df['Throughput'], color='#2ca02c')
                axes[0, 1].set_title('Throughput by Period', fontsize=14, fontweight='bold')
                axes[0, 1].set_ylabel('Entities per Hour')
                axes[0, 1].tick_params(axis='x', rotation=45)
                axes[0, 1].grid(axis='y', alpha=0.3)

                # Wait times by period
                x = np.arange(len(period_df))
                width = 0.35
                axes[1, 0].bar(x - width/2, period_df['Avg_Vehicle_Wait'], width,
                             label='Vehicles', color='#1f77b4')
                axes[1, 0].bar(x + width/2, period_df['Avg_Pedestrian_Wait'], width,
                             label='Pedestrians', color='#ff7f0e')
                axes[1, 0].set_title('Wait Times by Period', fontsize=14, fontweight='bold')
                axes[1, 0].set_ylabel('Wait Time (seconds)')
                axes[1, 0].set_xticks(x)
                axes[1, 0].set_xticklabels(period_df['Period'], rotation=45)
                axes[1, 0].legend()
                axes[1, 0].grid(axis='y', alpha=0.3)

                # Utilization by period
                axes[1, 1].bar(period_df['Period'], period_df['Utilization'], color='#d62728')
                axes[1, 1].set_title('Utilization by Period', fontsize=14, fontweight='bold')
                axes[1, 1].set_ylabel('Utilization (%)')
                axes[1, 1].tick_params(axis='x', rotation=45)
                axes[1, 1].axhline(y=80, color='black', linestyle='--', label='Target (80%)')
                axes[1, 1].legend()
                axes[1, 1].grid(axis='y', alpha=0.3)

                plt.tight_layout()
                plt.savefig(f'{output_dir}/period_comparison.png', dpi=300, bbox_inches='tight')
                print(f"Period comparison saved to: {output_dir}/period_comparison.png")
                plt.close()

def main():
    """Main execution function"""
    print("=" * 80)
    print("TRAFFIC TIME & COST ANALYSIS SYSTEM")
    print("=" * 80)

    # Load data
    print("\nLoading data...")
    try:
        data = TrafficDataLoader.load_data('all_sessions_combined.csv')
        print(f"Loaded {len(data)} records")
    except FileNotFoundError:
        print("Error: all_sessions_combined.csv not found")
        print("Please ensure your simulation data is in the current directory")
        return

    # Initialize cost parameters
    cost_params = CostParameters()

    # Generate report
    print("\nGenerating analysis report...")
    reporter = TrafficReportGenerator(data, cost_params)

    # Print report to console
    print("\n" + reporter.generate_text_report())

    # Save reports
    print("\nSaving outputs...")
    reporter.save_report("traffic_analysis_report.txt")
    reporter.export_metrics_json("traffic_metrics.json")

    # Create visualizations
    print("\nGenerating visualizations...")
    reporter.create_visualizations()

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE!")
    print("=" * 80)
    print("\nGenerated files:")
    print("  - traffic_analysis_report.txt")
    print("  - traffic_metrics.json")
    print("  - time_analysis.png")
    print("  - cost_analysis.png")
    if 'Period_Type' in data.columns:
        print("  - period_comparison.png")

if __name__ == "__main__":
    main()
