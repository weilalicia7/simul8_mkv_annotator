#!/usr/bin/env python3
"""
Queueing Theory Calculator for Traffic Systems
Implements key formulas: Kingman's VUT, Erlang C, Little's Law
Calculates optimal capacity and performance metrics.
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple
import json
import math
from scipy.special import factorial
from scipy.optimize import fsolve

@dataclass
class QueueingParameters:
    """Input parameters for queueing calculations"""
    arrival_rate: float  # λ (entities per hour)
    service_rate: float  # μ (entities per hour per server)
    num_servers: int     # c (number of parallel servers)
    cv_arrival: float    # CV_a (coefficient of variation of arrivals)
    cv_service: float    # CV_s (coefficient of variation of service)

    @property
    def utilization(self) -> float:
        """Calculate traffic intensity (rho)"""
        return self.arrival_rate / (self.num_servers * self.service_rate)

    @property
    def is_stable(self) -> bool:
        """Check if system is stable (rho < 1)"""
        return self.utilization < 1.0


@dataclass
class QueueingResults:
    """Results from queueing calculations"""
    # Input parameters
    arrival_rate: float
    service_rate: float
    num_servers: int
    utilization: float

    # Performance metrics
    avg_wait_in_queue: float      # W_q (seconds)
    avg_time_in_system: float     # W (seconds)
    avg_num_in_queue: float       # L_q
    avg_num_in_system: float      # L
    prob_wait: float              # P(Wait > 0)
    prob_wait_exceed_t: Dict[int, float]  # P(Wait > t) for various t

    # Capacity recommendations
    min_required_servers: int
    optimal_servers: int
    recommended_utilization: float

    # Classification
    performance_class: str  # Excellent/Good/Acceptable/Poor/Critical


class QueueingCalculator:
    """Implements queueing theory calculations"""

    @staticmethod
    def kingman_formula(params: QueueingParameters) -> float:
        """
        Calculate average wait time using Kingman's VUT equation

        W_q = (rho / (1-rho)) * ((CV_a^2 + CV_s^2)/2) * (1/mu)

        Applicable to: M/G/1, G/G/1 queues (single server)
        """
        rho = params.utilization
        mu = params.service_rate
        cv_a = params.cv_arrival
        cv_s = params.cv_service

        if rho >= 1.0:
            return float('inf')

        variability_factor = (cv_a**2 + cv_s**2) / 2
        congestion_factor = rho / (1 - rho)

        # W_q in hours
        w_q_hours = congestion_factor * variability_factor * (1 / mu)

        # Convert to seconds
        return w_q_hours * 3600

    @staticmethod
    def erlang_c(c: int, a: float) -> float:
        """
        Calculate Erlang C formula: Probability of waiting in M/M/c queue

        c: number of servers
        a: offered load (lambda / mu)
        """
        if a >= c:
            return 1.0  # Unstable system

        # Calculate sum term
        sum_term = sum([(a**n) / factorial(n) for n in range(c)])

        # Calculate Erlang C
        numerator = (a**c) / factorial(c)
        denominator = sum_term + numerator * (c / (c - a))

        return numerator / denominator

    @staticmethod
    def mm_c_wait_time(params: QueueingParameters) -> float:
        """
        Calculate average wait time for M/M/c queue
        (Exponential arrivals and service, c servers)
        """
        lambda_rate = params.arrival_rate
        mu = params.service_rate
        c = params.num_servers
        a = lambda_rate / mu

        if a >= c:
            return float('inf')

        prob_wait = QueueingCalculator.erlang_c(c, a)

        # Average wait time (hours)
        w_q = prob_wait / (c * mu - lambda_rate)

        # Convert to seconds
        return w_q * 3600

    @staticmethod
    def littles_law_queue(lambda_rate: float, w_q: float) -> float:
        """
        Calculate average number in queue using Little's Law
        L_q = lambda * W_q
        """
        # w_q is in seconds, lambda is per hour
        w_q_hours = w_q / 3600
        return lambda_rate * w_q_hours

    @staticmethod
    def littles_law_system(lambda_rate: float, w: float) -> float:
        """
        Calculate average number in system using Little's Law
        L = lambda * W
        """
        w_hours = w / 3600
        return lambda_rate * w_hours

    @staticmethod
    def calculate_min_servers(lambda_rate: float, mu: float,
                             target_util: float = 0.85) -> int:
        """
        Calculate minimum servers needed for target utilization
        c = ceil(lambda / (mu * target_util))
        """
        min_servers = math.ceil(lambda_rate / (mu * target_util))
        return max(1, min_servers)

    @staticmethod
    def calculate_optimal_servers(lambda_rate: float, mu: float,
                                 cv_a: float = 1.0,
                                 target_wait: float = 60) -> int:
        """
        Calculate optimal servers to achieve target wait time
        Iteratively tests server counts
        """
        c = QueueingCalculator.calculate_min_servers(lambda_rate, mu, 0.85)

        # Test increasing server counts
        for test_c in range(c, c + 20):
            params = QueueingParameters(
                arrival_rate=lambda_rate,
                service_rate=mu,
                num_servers=test_c,
                cv_arrival=cv_a,
                cv_service=1.0
            )

            try:
                wait = QueueingCalculator.mm_c_wait_time(params)
                if wait <= target_wait:
                    return test_c
            except:
                continue

        return c  # Return minimum if target can't be achieved

    @staticmethod
    def prob_wait_exceeds_t(w_q_avg: float, t: float,
                           distribution: str = 'exponential') -> float:
        """
        Calculate probability that wait time exceeds t

        For exponential: P(W > t) = exp(-t / w_q_avg)
        """
        if distribution == 'exponential':
            if w_q_avg <= 0:
                return 0.0
            return math.exp(-t / w_q_avg)
        else:
            # Approximation for general case
            return max(0, 1 - (t / (w_q_avg * 2)))

    def calculate_comprehensive(self, params: QueueingParameters) -> QueueingResults:
        """Calculate comprehensive queueing metrics"""

        if not params.is_stable:
            # Unstable system
            return QueueingResults(
                arrival_rate=params.arrival_rate,
                service_rate=params.service_rate,
                num_servers=params.num_servers,
                utilization=params.utilization,
                avg_wait_in_queue=float('inf'),
                avg_time_in_system=float('inf'),
                avg_num_in_queue=float('inf'),
                avg_num_in_system=float('inf'),
                prob_wait=1.0,
                prob_wait_exceed_t={},
                min_required_servers=self.calculate_min_servers(
                    params.arrival_rate, params.service_rate, 0.95),
                optimal_servers=self.calculate_optimal_servers(
                    params.arrival_rate, params.service_rate),
                recommended_utilization=0.75,
                performance_class="UNSTABLE - System cannot handle load"
            )

        # Calculate wait time (use M/M/c for multi-server)
        if params.num_servers == 1:
            w_q = self.kingman_formula(params)
        else:
            w_q = self.mm_c_wait_time(params)

        # Service time (average)
        service_time = 3600 / params.service_rate  # in seconds

        # Total time in system
        w = w_q + service_time

        # Queue lengths (Little's Law)
        l_q = self.littles_law_queue(params.arrival_rate, w_q)
        l = self.littles_law_system(params.arrival_rate, w)

        # Probability of waiting
        if params.num_servers == 1:
            prob_wait = params.utilization
        else:
            prob_wait = self.erlang_c(
                params.num_servers,
                params.arrival_rate / params.service_rate
            )

        # Probability wait exceeds various thresholds
        prob_exceed = {
            30: self.prob_wait_exceeds_t(w_q, 30),
            60: self.prob_wait_exceeds_t(w_q, 60),
            90: self.prob_wait_exceeds_t(w_q, 90),
            120: self.prob_wait_exceeds_t(w_q, 120)
        }

        # Calculate recommendations
        min_servers = self.calculate_min_servers(
            params.arrival_rate, params.service_rate, 0.95)
        optimal_servers = self.calculate_optimal_servers(
            params.arrival_rate, params.service_rate, params.cv_arrival)

        # Performance classification
        performance_class = self._classify_performance(
            params.utilization, w_q, l_q)

        return QueueingResults(
            arrival_rate=params.arrival_rate,
            service_rate=params.service_rate,
            num_servers=params.num_servers,
            utilization=params.utilization,
            avg_wait_in_queue=w_q,
            avg_time_in_system=w,
            avg_num_in_queue=l_q,
            avg_num_in_system=l,
            prob_wait=prob_wait,
            prob_wait_exceed_t=prob_exceed,
            min_required_servers=min_servers,
            optimal_servers=optimal_servers,
            recommended_utilization=0.75,
            performance_class=performance_class
        )

    def _classify_performance(self, rho: float, w_q: float, l_q: float) -> str:
        """Classify system performance"""
        if rho >= 0.95:
            return "CRITICAL - System near capacity"
        elif rho >= 0.85:
            return "POOR - High congestion"
        elif rho >= 0.75:
            return "ACCEPTABLE - Moderate congestion"
        elif w_q <= 30 and l_q <= 2:
            return "EXCELLENT - Low congestion"
        else:
            return "GOOD - Reasonable performance"


class TrafficQueueingAnalyzer:
    """Analyze traffic data using queueing theory"""

    def __init__(self, data: pd.DataFrame, variability_metrics: Dict = None):
        self.data = data
        self.variability_metrics = variability_metrics or {}
        self.calculator = QueueingCalculator()
        self.results = {}

    def analyze_all_periods(self, service_rate: float = 60) -> Dict:
        """
        Analyze all periods in the dataset

        service_rate: entities per hour the system can handle per server
        """
        results = {}

        # Default service rate if not specified
        # For traffic: assume 60 vehicles/hour per lane or 120 peds/hour per crossing

        # Group by period and entity type
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

            # Calculate arrival rate
            duration_hours = (group_data['Arrival_Time'].max() -
                            group_data['Arrival_Time'].min()) / 3600
            arrival_rate = len(group_data) / duration_hours if duration_hours > 0 else 0

            # Get CV from variability metrics if available
            key = f"{period_type}_{entity_type}"
            if key in self.variability_metrics:
                cv_a = self.variability_metrics[key].get('cv_inter_arrival', 1.0)
                cv_s = self.variability_metrics[key].get('cv_service_time', 1.0)
            else:
                cv_a = cv_s = 1.0

            # Adjust service rate by entity type
            if 'Vehicle' in entity_type:
                mu = service_rate  # vehicles per hour per lane
            else:
                mu = service_rate * 2  # pedestrians cross faster

            # Calculate optimal servers
            optimal_c = self.calculator.calculate_optimal_servers(
                arrival_rate, mu, cv_a)

            # Create parameters
            params = QueueingParameters(
                arrival_rate=arrival_rate,
                service_rate=mu,
                num_servers=optimal_c,
                cv_arrival=cv_a,
                cv_service=cv_s
            )

            # Calculate results
            result = self.calculator.calculate_comprehensive(params)
            results[key] = {
                'period': period_type,
                'entity': entity_type,
                'params': params,
                'results': result
            }

        self.results = results
        return results

    def generate_report(self) -> str:
        """Generate detailed queueing analysis report"""
        report = []
        report.append("=" * 80)
        report.append("QUEUEING THEORY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")

        for key, analysis in self.results.items():
            params = analysis['params']
            results = analysis['results']

            report.append(f"\n{'=' * 80}")
            report.append(f"ANALYSIS: {analysis['period']} - {analysis['entity']}")
            report.append(f"{'=' * 80}\n")

            report.append("INPUT PARAMETERS:")
            report.append(f"  Arrival Rate (λ): {params.arrival_rate:.2f} entities/hour")
            report.append(f"  Service Rate (μ): {params.service_rate:.2f} entities/hour/server")
            report.append(f"  Number of Servers (c): {params.num_servers}")
            report.append(f"  CV Arrivals: {params.cv_arrival:.3f}")
            report.append(f"  CV Service: {params.cv_service:.3f}")
            report.append(f"  Utilization (ρ): {results.utilization:.2%}")

            report.append("\nPERFORMANCE METRICS:")
            report.append(f"  Average Wait in Queue: {results.avg_wait_in_queue:.1f} seconds")
            report.append(f"  Average Time in System: {results.avg_time_in_system:.1f} seconds")
            report.append(f"  Average Number in Queue: {results.avg_num_in_queue:.2f}")
            report.append(f"  Average Number in System: {results.avg_num_in_system:.2f}")
            report.append(f"  Probability of Waiting: {results.prob_wait:.1%}")

            report.append("\nSERVICE LEVEL:")
            for threshold, prob in results.prob_wait_exceed_t.items():
                report.append(f"  P(Wait > {threshold}s): {prob:.1%}")

            report.append(f"\nPERFORMANCE CLASSIFICATION: {results.performance_class}")

            report.append("\nRECOMMENDATIONS:")
            report.append(f"  Minimum Servers Required: {results.min_required_servers}")
            report.append(f"  Optimal Servers: {results.optimal_servers}")
            report.append(f"  Target Utilization: {results.recommended_utilization:.0%}")

            if results.utilization > 0.85:
                report.append("\n  WARNING: System highly utilized!")
                report.append(f"  Consider increasing capacity from {params.num_servers} to {results.optimal_servers}")
                savings = results.avg_wait_in_queue - (results.avg_wait_in_queue / 2)
                report.append(f"  Potential wait time reduction: ~{savings:.0f} seconds")

            report.append("")

        # Overall summary
        report.append("\n" + "=" * 80)
        report.append("SUMMARY AND RECOMMENDATIONS")
        report.append("=" * 80)
        report.append("")

        critical_periods = [k for k, v in self.results.items()
                          if v['results'].utilization > 0.85]
        if critical_periods:
            report.append("CRITICAL PERIODS (ρ > 85%):")
            for key in critical_periods:
                analysis = self.results[key]
                report.append(f"  - {analysis['period']} / {analysis['entity']}")
                report.append(f"    Current: {analysis['params'].num_servers} servers, "
                            f"ρ = {analysis['results'].utilization:.1%}")
                report.append(f"    Recommended: {analysis['results'].optimal_servers} servers")
            report.append("")

        report.append("NEXT STEPS:")
        report.append("  1. Implement recommended server capacities in SIMUL8")
        report.append("  2. Run simulation to validate queueing predictions")
        report.append("  3. Compare theoretical vs simulated performance")
        report.append("  4. Adjust for any real-world constraints")

        return "\n".join(report)

    def export_to_json(self, filename: str = 'queueing_results.json'):
        """Export results to JSON"""
        export_data = {}
        for key, analysis in self.results.items():
            results = analysis['results']
            export_data[key] = {
                'period': analysis['period'],
                'entity': analysis['entity'],
                'arrival_rate': results.arrival_rate,
                'utilization': results.utilization,
                'avg_wait_queue': results.avg_wait_in_queue,
                'avg_time_system': results.avg_time_in_system,
                'avg_num_queue': results.avg_num_in_queue,
                'min_servers': results.min_required_servers,
                'optimal_servers': results.optimal_servers,
                'performance_class': results.performance_class
            }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)

        print(f"Results exported to {filename}")


def main():
    """Main execution"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python queueing_calculator.py <data_file.csv> [service_rate]")
        print("\nExample:")
        print("  python queueing_calculator.py all_sessions_combined.csv 60")
        print("\nservice_rate: entities per hour per server (default: 60)")
        sys.exit(1)

    input_file = sys.argv[1]
    service_rate = float(sys.argv[2]) if len(sys.argv) > 2 else 60

    try:
        # Load data
        print(f"Loading data from {input_file}...")
        data = pd.read_csv(input_file)
        print(f"Loaded {len(data)} records")

        # Map column names to standard format
        column_mapping = {
            'Time (s)': 'Arrival_Time',
            'Entity': 'Entity_Type',
            'Inter-Arrival (s)': 'Inter_Arrival_Time',
            'Service Time (s)': 'Service_Time'
        }
        for old_col, new_col in column_mapping.items():
            if old_col in data.columns:
                data = data.rename(columns={old_col: new_col})

        # Load variability metrics if available
        try:
            with open('variability_metrics.json', 'r') as f:
                var_metrics = json.load(f)
            print("Loaded variability metrics from variability_metrics.json")
        except:
            var_metrics = {}
            print("No variability metrics found, using defaults")

        # Analyze
        print(f"\nCalculating queueing metrics (service rate: {service_rate}/hour)...")
        analyzer = TrafficQueueingAnalyzer(data, var_metrics)
        results = analyzer.analyze_all_periods(service_rate)

        print(f"Analyzed {len(results)} period/entity combinations")

        # Generate report
        print("\nGenerating report...")
        report = analyzer.generate_report()

        # Save report
        with open('queueing_analysis_report.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        print("Report saved to queueing_analysis_report.txt")

        # Export JSON
        analyzer.export_to_json('queueing_results.json')

        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print("\nOutputs generated:")
        print("  - queueing_analysis_report.txt (detailed analysis)")
        print("  - queueing_results.json (machine-readable results)")
        print("\nNext steps:")
        print("  1. Review capacity recommendations")
        print("  2. Run resource_planner.py for implementation scenarios")
        print("  3. Configure SIMUL8 with recommended capacities")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
