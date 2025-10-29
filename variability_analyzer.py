#!/usr/bin/env python3
"""
Variability Analyzer for Traffic Data
Analyzes arrival patterns and calculates coefficient of variation
to inform queueing theory-based resource planning.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

@dataclass
class VariabilityMetrics:
    """Metrics describing arrival pattern variability"""
    entity_type: str
    period_type: str

    # Arrival metrics
    total_arrivals: int
    mean_arrival_rate: float  # entities per hour

    # Inter-arrival time metrics
    mean_inter_arrival: float  # seconds
    std_inter_arrival: float   # seconds
    cv_inter_arrival: float    # coefficient of variation

    # Service time metrics (wait time as proxy)
    mean_service_time: float   # seconds
    std_service_time: float    # seconds
    cv_service_time: float     # coefficient of variation

    # Variability classification
    variability_class: str     # Low/Medium/High

    # Distribution fit
    best_fit_distribution: str
    distribution_params: Dict


class VariabilityAnalyzer:
    """Analyzes variability in traffic arrival and service patterns"""

    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.results = {}

    def analyze_all(self) -> Dict[str, List[VariabilityMetrics]]:
        """Analyze variability for all entity types and periods"""
        results = {}

        # Group by period type and entity type
        if 'Period_Type' in self.data.columns:
            groups = self.data.groupby(['Period_Type', 'Entity_Type'])
        else:
            groups = self.data.groupby('Entity_Type')

        for group_key, group_data in groups:
            if isinstance(group_key, tuple):
                period_type, entity_type = group_key
            else:
                period_type = 'All'
                entity_type = group_key

            metrics = self._analyze_group(group_data, entity_type, period_type)

            key = f"{period_type}_{entity_type}"
            results[key] = metrics

        self.results = results
        return results

    def _analyze_group(self, data: pd.DataFrame, entity_type: str,
                       period_type: str) -> VariabilityMetrics:
        """Analyze a single group of data"""

        # Calculate inter-arrival times
        data_sorted = data.sort_values('Arrival_Time')
        inter_arrivals = data_sorted['Arrival_Time'].diff().dropna()

        # Basic metrics
        total_arrivals = len(data)
        duration_hours = (data['Arrival_Time'].max() - data['Arrival_Time'].min()) / 3600
        mean_arrival_rate = total_arrivals / duration_hours if duration_hours > 0 else 0

        # Inter-arrival statistics
        mean_ia = inter_arrivals.mean()
        std_ia = inter_arrivals.std()
        cv_ia = std_ia / mean_ia if mean_ia > 0 else 0

        # Service time statistics (using wait time as proxy)
        if 'Wait_Time' in data.columns:
            mean_service = data['Wait_Time'].mean()
            std_service = data['Wait_Time'].std()
            cv_service = std_service / mean_service if mean_service > 0 else 0
        else:
            mean_service = std_service = cv_service = 0

        # Classify variability
        variability_class = self._classify_variability(cv_ia)

        # Fit distribution
        best_fit, params = self._fit_distribution(inter_arrivals.values)

        return VariabilityMetrics(
            entity_type=entity_type,
            period_type=period_type,
            total_arrivals=total_arrivals,
            mean_arrival_rate=mean_arrival_rate,
            mean_inter_arrival=mean_ia,
            std_inter_arrival=std_ia,
            cv_inter_arrival=cv_ia,
            mean_service_time=mean_service,
            std_service_time=std_service,
            cv_service_time=cv_service,
            variability_class=variability_class,
            best_fit_distribution=best_fit,
            distribution_params=params
        )

    def _classify_variability(self, cv: float) -> str:
        """Classify variability level based on CV"""
        if cv < 0.75:
            return "Low (Regular arrivals)"
        elif cv < 1.25:
            return "Medium (Random arrivals)"
        else:
            return "High (Bursty arrivals)"

    def _fit_distribution(self, data: np.ndarray) -> Tuple[str, Dict]:
        """Fit common distributions and return best fit"""
        if len(data) < 10:
            return "Insufficient data", {}

        distributions = {
            'Exponential': stats.expon,
            'Gamma': stats.gamma,
            'Lognormal': stats.lognorm,
            'Weibull': stats.weibull_min
        }

        best_fit = None
        best_ks_stat = np.inf
        best_params = {}

        for name, dist in distributions.items():
            try:
                params = dist.fit(data)
                ks_stat, _ = stats.kstest(data, lambda x: dist.cdf(x, *params))

                if ks_stat < best_ks_stat:
                    best_ks_stat = ks_stat
                    best_fit = name
                    best_params = {'params': params, 'ks_stat': ks_stat}
            except:
                continue

        return best_fit or "Unknown", best_params

    def generate_text_report(self) -> str:
        """Generate detailed text report"""
        report = []
        report.append("=" * 80)
        report.append("TRAFFIC VARIABILITY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")

        for key, metrics in self.results.items():
            report.append(f"\n{'=' * 80}")
            report.append(f"GROUP: {metrics.period_type} - {metrics.entity_type}")
            report.append(f"{'=' * 80}\n")

            report.append(f"ARRIVAL PATTERN:")
            report.append(f"  Total Arrivals: {metrics.total_arrivals}")
            report.append(f"  Mean Arrival Rate: {metrics.mean_arrival_rate:.2f} entities/hour")
            report.append(f"  Mean Inter-Arrival Time: {metrics.mean_inter_arrival:.2f} seconds")
            report.append(f"  Std Dev Inter-Arrival: {metrics.std_inter_arrival:.2f} seconds")
            report.append(f"  Coefficient of Variation (CV): {metrics.cv_inter_arrival:.3f}")
            report.append(f"  Variability Classification: {metrics.variability_class}")
            report.append(f"  Best Fit Distribution: {metrics.best_fit_distribution}")

            if metrics.mean_service_time > 0:
                report.append(f"\nSERVICE PATTERN:")
                report.append(f"  Mean Service Time: {metrics.mean_service_time:.2f} seconds")
                report.append(f"  Std Dev Service Time: {metrics.std_service_time:.2f} seconds")
                report.append(f"  CV Service: {metrics.cv_service_time:.3f}")

            # Queueing implications
            report.append(f"\nQUEUEING THEORY IMPLICATIONS:")
            if metrics.cv_inter_arrival < 0.75:
                report.append(f"  - Low variability: System can operate at higher utilization")
                report.append(f"  - Recommended max utilization: 85%")
            elif metrics.cv_inter_arrival < 1.25:
                report.append(f"  - Moderate variability: Use standard queueing formulas")
                report.append(f"  - Recommended max utilization: 75%")
            else:
                report.append(f"  - High variability: Requires significant capacity buffer")
                report.append(f"  - Recommended max utilization: 65%")
                report.append(f"  - Consider: Capacity increase of {(metrics.cv_inter_arrival - 1) * 50:.0f}%")

            report.append("")

        report.append("\n" + "=" * 80)
        report.append("SUMMARY RECOMMENDATIONS")
        report.append("=" * 80)
        report.append("")

        # Overall recommendations
        high_var_groups = [k for k, m in self.results.items() if m.cv_inter_arrival > 1.25]
        if high_var_groups:
            report.append("HIGH VARIABILITY PERIODS DETECTED:")
            for group in high_var_groups:
                metrics = self.results[group]
                report.append(f"  - {metrics.period_type} / {metrics.entity_type}: CV = {metrics.cv_inter_arrival:.3f}")
            report.append("\nACTIONS:")
            report.append("  1. Size resources for peak + variability buffer")
            report.append("  2. Use empirical distributions in SIMUL8 (not theoretical)")
            report.append("  3. Run longer simulation replications to capture variability")
            report.append("  4. Consider adaptive/dynamic resource allocation")

        return "\n".join(report)

    def export_to_json(self, filename: str = 'variability_metrics.json'):
        """Export metrics to JSON"""
        export_data = {}
        for key, metrics in self.results.items():
            export_data[key] = {
                'entity_type': metrics.entity_type,
                'period_type': metrics.period_type,
                'total_arrivals': metrics.total_arrivals,
                'mean_arrival_rate': metrics.mean_arrival_rate,
                'mean_inter_arrival': metrics.mean_inter_arrival,
                'std_inter_arrival': metrics.std_inter_arrival,
                'cv_inter_arrival': metrics.cv_inter_arrival,
                'mean_service_time': metrics.mean_service_time,
                'std_service_time': metrics.std_service_time,
                'cv_service_time': metrics.cv_service_time,
                'variability_class': metrics.variability_class,
                'best_fit_distribution': metrics.best_fit_distribution
            }

        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)

        print(f"Metrics exported to {filename}")

    def create_visualizations(self, output_dir: str = '.'):
        """Create variability visualization charts"""

        # Prepare data for plotting
        plot_data = []
        for key, metrics in self.results.items():
            plot_data.append({
                'Group': f"{metrics.period_type}\n{metrics.entity_type}",
                'Period': metrics.period_type,
                'Entity': metrics.entity_type,
                'CV_Arrival': metrics.cv_inter_arrival,
                'CV_Service': metrics.cv_service_time,
                'Arrival_Rate': metrics.mean_arrival_rate
            })

        df_plot = pd.DataFrame(plot_data)

        # Create figure with subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Traffic Variability Analysis', fontsize=16, fontweight='bold')

        # 1. CV by group
        ax = axes[0, 0]
        x = np.arange(len(df_plot))
        width = 0.35
        ax.bar(x - width/2, df_plot['CV_Arrival'], width, label='CV Arrivals', alpha=0.8)
        ax.bar(x + width/2, df_plot['CV_Service'], width, label='CV Service', alpha=0.8)
        ax.set_xlabel('Group')
        ax.set_ylabel('Coefficient of Variation')
        ax.set_title('Variability by Group')
        ax.set_xticks(x)
        ax.set_xticklabels(df_plot['Group'], rotation=45, ha='right', fontsize=8)
        ax.axhline(y=1.0, color='r', linestyle='--', label='CV=1 (Exponential)')
        ax.legend()
        ax.grid(True, alpha=0.3)

        # 2. Arrival rate by period
        ax = axes[0, 1]
        period_rates = df_plot.groupby('Period')['Arrival_Rate'].mean().sort_values()
        period_rates.plot(kind='barh', ax=ax, color='steelblue', alpha=0.8)
        ax.set_xlabel('Mean Arrival Rate (entities/hour)')
        ax.set_title('Average Arrival Rate by Period')
        ax.grid(True, alpha=0.3, axis='x')

        # 3. Variability classification
        ax = axes[1, 0]
        var_classes = [m.variability_class.split()[0] for m in self.results.values()]
        var_counts = pd.Series(var_classes).value_counts()
        colors = {'Low': 'green', 'Medium': 'orange', 'High': 'red'}
        var_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%',
                       colors=[colors.get(x, 'gray') for x in var_counts.index])
        ax.set_ylabel('')
        ax.set_title('Variability Classification Distribution')

        # 4. CV vs Arrival Rate scatter
        ax = axes[1, 1]
        scatter = ax.scatter(df_plot['Arrival_Rate'], df_plot['CV_Arrival'],
                           s=100, alpha=0.6, c=range(len(df_plot)), cmap='viridis')
        ax.set_xlabel('Arrival Rate (entities/hour)')
        ax.set_ylabel('CV of Inter-Arrival Times')
        ax.set_title('Variability vs Arrival Rate')
        ax.axhline(y=1.0, color='r', linestyle='--', alpha=0.5, label='CV=1')
        ax.grid(True, alpha=0.3)
        ax.legend()

        # Add labels for each point
        for idx, row in df_plot.iterrows():
            ax.annotate(row['Entity'],
                       (row['Arrival_Rate'], row['CV_Arrival']),
                       fontsize=7, alpha=0.7)

        plt.tight_layout()
        output_file = f'{output_dir}/variability_analysis.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Visualization saved to {output_file}")
        plt.close()


class DataLoader:
    """Load and preprocess traffic data"""

    @staticmethod
    def load_data(filename: str) -> pd.DataFrame:
        """Load CSV data and preprocess"""
        print(f"Loading data from {filename}...")
        df = pd.read_csv(filename)

        print(f"Loaded {len(df)} records")
        print(f"Columns: {', '.join(df.columns)}")

        # Ensure required columns exist
        required_cols = ['Arrival_Time', 'Entity_Type']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        return df


def main():
    """Main execution"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python variability_analyzer.py <data_file.csv>")
        print("\nExample:")
        print("  python variability_analyzer.py all_sessions_combined.csv")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        # Load data
        data = DataLoader.load_data(input_file)

        # Analyze variability
        print("\nAnalyzing variability patterns...")
        analyzer = VariabilityAnalyzer(data)
        results = analyzer.analyze_all()

        print(f"\nAnalyzed {len(results)} groups")

        # Generate outputs
        print("\nGenerating report...")
        report = analyzer.generate_text_report()

        # Save text report
        with open('variability_report.txt', 'w') as f:
            f.write(report)
        print("Report saved to variability_report.txt")

        # Export JSON
        analyzer.export_to_json('variability_metrics.json')

        # Create visualizations
        print("\nCreating visualizations...")
        analyzer.create_visualizations()

        # Print summary to console
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print("\nOutputs generated:")
        print("  - variability_report.txt (detailed text report)")
        print("  - variability_metrics.json (machine-readable metrics)")
        print("  - variability_analysis.png (visualization charts)")
        print("\nNext steps:")
        print("  1. Review variability classifications")
        print("  2. Run queueing_calculator.py for capacity requirements")
        print("  3. Use metrics in SIMUL8 model configuration")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
