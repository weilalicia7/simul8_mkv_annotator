"""
Optimization Runner for Traffic System
Finds optimal server configuration using multiple methods
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize, differential_evolution
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import PolynomialFeatures
import sys
import io

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Constants
COST_PER_SERVER = 242000  # Annual cost per server
CROSSER_COST = 121000     # Annual cost for crosser server
MAX_WAIT_TIME = 5.0       # Maximum acceptable wait time (seconds)


def load_data(filepath='combined_results.csv'):
    """Load and prepare traffic data"""
    try:
        df = pd.read_csv(filepath)
    except:
        df = pd.read_excel(filepath)

    # Standardize column names
    if 'Time (s)' in df.columns:
        df = df.rename(columns={'Time (s)': 'Arrival_Time', 'Entity': 'Entity_Type'})

    return df


def calculate_wait_time_queueing(arrival_rate, service_rate, cv_service, num_servers):
    """
    Calculate wait time using Kingman's VUT equation

    Parameters:
    - arrival_rate: Lambda (arrivals per second)
    - service_rate: Mu (service per second per server)
    - cv_service: Coefficient of variation of service time
    - num_servers: Number of servers (c)

    Returns:
    - Wait time in seconds (or inf if unstable)
    """
    if num_servers < 1:
        return float('inf')

    # Traffic intensity
    rho = arrival_rate / (num_servers * service_rate)

    if rho >= 1.0:
        return float('inf')  # Unstable system

    # Kingman's VUT approximation
    # W_q = (rho / (1 - rho)) * (cv_a^2 + cv_s^2) / 2 * (1 / mu)
    # Assuming cv_arrival = 1 (Poisson-like)
    cv_arrival = 1.0

    wait_time = (rho / (1 - rho)) * (cv_arrival**2 + cv_service**2) / 2 / service_rate

    return wait_time


def evaluate_configuration(config, data_stats, weights={'wait': 0.5, 'cost': 0.3, 'queue': 0.2}):
    """
    Evaluate a server configuration

    Parameters:
    - config: [EB_servers, WB_servers, Crosser_servers, Poser_servers]
    - data_stats: Dictionary with arrival rates, service rates, CVs
    - weights: Objective function weights

    Returns:
    - objective_score: Lower is better
    - metrics: Dictionary with performance metrics
    """
    eb_servers, wb_servers, crosser_servers, poser_servers = config

    # Calculate wait times for each entity type
    wait_times = {}
    utilizations = {}

    for entity, servers in [('EB Vehicles', eb_servers),
                           ('WB Vehicles', wb_servers),
                           ('Crossers', crosser_servers),
                           ('Posers', poser_servers)]:

        if entity not in data_stats:
            wait_times[entity] = 0
            utilizations[entity] = 0
            continue

        arrival_rate = data_stats[entity]['arrival_rate']
        service_rate = data_stats[entity]['service_rate']
        cv_service = data_stats[entity]['cv_service']

        wait_time = calculate_wait_time_queueing(arrival_rate, service_rate, cv_service, servers)
        wait_times[entity] = wait_time

        if servers > 0 and service_rate > 0:
            utilizations[entity] = arrival_rate / (servers * service_rate)
        else:
            utilizations[entity] = 0

    # Calculate total cost
    total_cost = (eb_servers + wb_servers + poser_servers) * COST_PER_SERVER + \
                 crosser_servers * CROSSER_COST

    # Average wait time
    avg_wait_time = np.mean([w for w in wait_times.values() if w != float('inf')])

    # Max queue length (approximate from Little's Law)
    max_queue = 0
    for entity, servers in [('EB Vehicles', eb_servers),
                           ('WB Vehicles', wb_servers),
                           ('Crossers', crosser_servers),
                           ('Posers', poser_servers)]:
        if entity in data_stats and wait_times[entity] != float('inf'):
            arrival_rate = data_stats[entity]['arrival_rate']
            queue_length = arrival_rate * wait_times[entity]
            max_queue = max(max_queue, queue_length)

    # Penalty for infeasible solutions
    if any(w == float('inf') for w in wait_times.values()):
        objective_score = 1e9
    elif avg_wait_time > MAX_WAIT_TIME:
        # Soft penalty for exceeding max wait time
        objective_score = weights['wait'] * (avg_wait_time / MAX_WAIT_TIME) + \
                         weights['cost'] * (total_cost / 1e6) + \
                         weights['queue'] * max_queue + \
                         1000 * (avg_wait_time - MAX_WAIT_TIME)  # Penalty term
    else:
        # Normalize and combine objectives
        objective_score = weights['wait'] * (avg_wait_time / MAX_WAIT_TIME) + \
                         weights['cost'] * (total_cost / 1e6) + \
                         weights['queue'] * max_queue

    metrics = {
        'wait_times': wait_times,
        'avg_wait_time': avg_wait_time,
        'total_cost': total_cost,
        'max_queue': max_queue,
        'utilizations': utilizations,
        'objective_score': objective_score
    }

    return objective_score, metrics


def extract_data_stats(df):
    """Extract statistics from data for optimization"""
    stats = {}

    for entity in df['Entity_Type'].unique():
        entity_df = df[df['Entity_Type'] == entity]

        # Arrival rate (per second)
        duration = entity_df['Arrival_Time'].max()
        arrival_rate = len(entity_df) / duration

        # Service rate (per second)
        if 'Service_Time' in entity_df.columns:
            avg_service_time = entity_df['Service_Time'].mean()
            service_rate = 1 / avg_service_time if avg_service_time > 0 else 1

            # CV of service time
            std_service_time = entity_df['Service_Time'].std()
            cv_service = std_service_time / avg_service_time if avg_service_time > 0 else 1
        else:
            service_rate = 1  # Default
            cv_service = 1

        stats[entity] = {
            'arrival_rate': arrival_rate,
            'service_rate': service_rate,
            'cv_service': cv_service,
            'count': len(entity_df)
        }

    return stats


def grid_search_optimization(data_stats, weights):
    """
    Method 1: Exhaustive grid search
    Tests all combinations within reasonable ranges
    """
    print("\n" + "="*60)
    print("METHOD 1: GRID SEARCH OPTIMIZATION")
    print("="*60)

    best_score = float('inf')
    best_config = None
    best_metrics = None

    results = []

    # Define search ranges
    eb_range = range(1, 6)
    wb_range = range(1, 6)
    c_range = range(1, 3)
    p_range = range(1, 4)

    total_configs = len(eb_range) * len(wb_range) * len(c_range) * len(p_range)
    print(f"Testing {total_configs} configurations...")

    count = 0
    for eb in eb_range:
        for wb in wb_range:
            for c in c_range:
                for p in p_range:
                    config = [eb, wb, c, p]
                    score, metrics = evaluate_configuration(config, data_stats, weights)

                    results.append({
                        'EB': eb, 'WB': wb, 'C': c, 'P': p,
                        'Score': score,
                        'Wait_Time': metrics['avg_wait_time'],
                        'Cost': metrics['total_cost'],
                        'Queue': metrics['max_queue']
                    })

                    if score < best_score and metrics['avg_wait_time'] <= MAX_WAIT_TIME:
                        best_score = score
                        best_config = config
                        best_metrics = metrics

                    count += 1
                    if count % 30 == 0:
                        print(f"  Progress: {count}/{total_configs} ({100*count/total_configs:.0f}%)")

    print(f"\nBest Configuration Found:")
    print(f"  EB={best_config[0]}, WB={best_config[1]}, C={best_config[2]}, P={best_config[3]}")
    print(f"  Wait Time: {best_metrics['avg_wait_time']:.2f}s")
    print(f"  Cost: £{best_metrics['total_cost']:,.0f}/year")
    print(f"  Max Queue: {best_metrics['max_queue']:.2f}")
    print(f"  Objective Score: {best_score:.4f}")

    # Show top 5 configurations
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('Score')
    print("\nTop 5 Configurations:")
    print(results_df.head(5).to_string(index=False))

    return best_config, best_metrics, results_df


def gradient_optimization(data_stats, weights, initial_guess=[2, 2, 1, 2]):
    """
    Method 2: Gradient-based optimization
    Uses scipy.optimize.minimize with bounds
    """
    print("\n" + "="*60)
    print("METHOD 2: GRADIENT-BASED OPTIMIZATION")
    print("="*60)

    def objective(x):
        # Round to integers
        config = np.round(x).astype(int)
        score, _ = evaluate_configuration(config, data_stats, weights)
        return score

    # Bounds: [EB, WB, C, P]
    bounds = [(1, 5), (1, 5), (1, 2), (1, 3)]

    print(f"Starting from initial guess: EB={initial_guess[0]}, WB={initial_guess[1]}, "
          f"C={initial_guess[2]}, P={initial_guess[3]}")

    result = minimize(objective, x0=initial_guess, method='L-BFGS-B', bounds=bounds)

    optimal_config = np.round(result.x).astype(int)
    score, metrics = evaluate_configuration(optimal_config, data_stats, weights)

    print(f"\nOptimal Configuration Found:")
    print(f"  EB={optimal_config[0]}, WB={optimal_config[1]}, C={optimal_config[2]}, P={optimal_config[3]}")
    print(f"  Wait Time: {metrics['avg_wait_time']:.2f}s")
    print(f"  Cost: £{metrics['total_cost']:,.0f}/year")
    print(f"  Max Queue: {metrics['max_queue']:.2f}")
    print(f"  Objective Score: {score:.4f}")
    print(f"  Optimization Status: {result.message}")

    return optimal_config, metrics


def evolutionary_optimization(data_stats, weights):
    """
    Method 3: Differential Evolution (genetic algorithm variant)
    Global optimization algorithm
    """
    print("\n" + "="*60)
    print("METHOD 3: EVOLUTIONARY OPTIMIZATION")
    print("="*60)

    def objective(x):
        # Round to integers
        config = np.round(x).astype(int)
        score, _ = evaluate_configuration(config, data_stats, weights)
        return score

    # Bounds: [EB, WB, C, P]
    bounds = [(1, 5), (1, 5), (1, 2), (1, 3)]

    print("Running differential evolution (may take 1-2 minutes)...")

    result = differential_evolution(
        objective,
        bounds,
        seed=42,
        maxiter=100,
        popsize=15,
        integrality=[True, True, True, True],  # Integer constraints
        workers=1,
        updating='deferred',
        disp=True
    )

    optimal_config = np.round(result.x).astype(int)
    score, metrics = evaluate_configuration(optimal_config, data_stats, weights)

    print(f"\nOptimal Configuration Found:")
    print(f"  EB={optimal_config[0]}, WB={optimal_config[1]}, C={optimal_config[2]}, P={optimal_config[3]}")
    print(f"  Wait Time: {metrics['avg_wait_time']:.2f}s")
    print(f"  Cost: £{metrics['total_cost']:,.0f}/year")
    print(f"  Max Queue: {metrics['max_queue']:.2f}")
    print(f"  Objective Score: {score:.4f}")
    print(f"  Iterations: {result.nit}, Function Evals: {result.nfev}")

    return optimal_config, metrics


def sensitivity_analysis(config, data_stats, weights):
    """
    Perform sensitivity analysis around optimal configuration
    """
    print("\n" + "="*60)
    print("SENSITIVITY ANALYSIS")
    print("="*60)

    baseline_score, baseline_metrics = evaluate_configuration(config, data_stats, weights)

    print(f"\nBaseline Configuration: EB={config[0]}, WB={config[1]}, C={config[2]}, P={config[3]}")
    print(f"  Wait Time: {baseline_metrics['avg_wait_time']:.2f}s")
    print(f"  Cost: £{baseline_metrics['total_cost']:,.0f}/year")

    # Test ±1 server for each entity type
    sensitivities = []

    for i, name in enumerate(['EB', 'WB', 'C', 'P']):
        # Decrease by 1
        if config[i] > 1:
            test_config = config.copy()
            test_config[i] -= 1
            score, metrics = evaluate_configuration(test_config, data_stats, weights)

            wait_change = ((metrics['avg_wait_time'] - baseline_metrics['avg_wait_time']) /
                          baseline_metrics['avg_wait_time'] * 100)
            cost_change = metrics['total_cost'] - baseline_metrics['total_cost']

            sensitivities.append({
                'Parameter': f'{name} -1',
                'Config': str(test_config),
                'Wait_Change_%': wait_change,
                'Cost_Change': cost_change,
                'Wait_Time': metrics['avg_wait_time'],
                'Feasible': metrics['avg_wait_time'] <= MAX_WAIT_TIME
            })

        # Increase by 1
        test_config = config.copy()
        test_config[i] += 1
        score, metrics = evaluate_configuration(test_config, data_stats, weights)

        wait_change = ((metrics['avg_wait_time'] - baseline_metrics['avg_wait_time']) /
                      baseline_metrics['avg_wait_time'] * 100)
        cost_change = metrics['total_cost'] - baseline_metrics['total_cost']

        sensitivities.append({
            'Parameter': f'{name} +1',
            'Config': str(test_config),
            'Wait_Change_%': wait_change,
            'Cost_Change': cost_change,
            'Wait_Time': metrics['avg_wait_time'],
            'Feasible': metrics['avg_wait_time'] <= MAX_WAIT_TIME
        })

    sens_df = pd.DataFrame(sensitivities)
    print("\nSensitivity to ±1 Server:")
    print(sens_df.to_string(index=False))

    # Find most sensitive parameter
    sens_df['Abs_Wait_Change'] = abs(sens_df['Wait_Change_%'])
    most_sensitive = sens_df.loc[sens_df['Abs_Wait_Change'].idxmax()]
    print(f"\nMost Sensitive Parameter: {most_sensitive['Parameter']}")
    print(f"  Wait Time Change: {most_sensitive['Wait_Change_%']:+.1f}%")

    return sens_df


def generate_report(results_dict):
    """Generate optimization report"""
    print("\n" + "="*60)
    print("OPTIMIZATION SUMMARY REPORT")
    print("="*60)

    print("\nComparison of Methods:")
    print("-" * 60)

    for method_name, (config, metrics) in results_dict.items():
        print(f"\n{method_name}:")
        print(f"  Configuration: EB={config[0]}, WB={config[1]}, C={config[2]}, P={config[3]}")
        print(f"  Total Servers: {sum(config)}")
        print(f"  Wait Time: {metrics['avg_wait_time']:.2f}s")
        print(f"  Annual Cost: £{metrics['total_cost']:,.0f}")
        print(f"  Max Queue: {metrics['max_queue']:.2f}")

        # Show individual wait times
        print("  Wait Times by Entity:")
        for entity, wt in metrics['wait_times'].items():
            if wt != float('inf'):
                util = metrics['utilizations'].get(entity, 0)
                print(f"    {entity}: {wt:.2f}s (utilization: {util*100:.1f}%)")

    # Recommendation
    print("\n" + "="*60)
    print("RECOMMENDATION")
    print("="*60)

    # Check if all methods agree
    configs = [config for config, _ in results_dict.values()]

    if all(np.array_equal(configs[0], c) for c in configs):
        print("\n✓ All methods converged to the SAME configuration!")
        print(f"  RECOMMENDED: EB={configs[0][0]}, WB={configs[0][1]}, C={configs[0][2]}, P={configs[0][3]}")
    else:
        print("\nMethods found different configurations:")
        # Use most common configuration
        from collections import Counter
        config_tuples = [tuple(c) for c in configs]
        most_common = Counter(config_tuples).most_common(1)[0][0]
        print(f"  RECOMMENDED (most common): EB={most_common[0]}, WB={most_common[1]}, "
              f"C={most_common[2]}, P={most_common[3]}")


def main():
    """Main optimization workflow"""
    print("="*60)
    print("TRAFFIC SYSTEM OPTIMIZATION")
    print("Weekday Data (9:00-10:30 AM, October 20, 2025)")
    print("="*60)

    # Load data
    print("\nLoading data from combined_results.csv...")
    df = load_data('combined_results.csv')
    print(f"  Loaded {len(df)} entities")
    print(f"  Entity types: {df['Entity_Type'].unique()}")

    # Extract statistics
    print("\nExtracting traffic statistics...")
    data_stats = extract_data_stats(df)

    for entity, stats in data_stats.items():
        print(f"  {entity}:")
        print(f"    Arrival rate: {stats['arrival_rate']*3600:.1f}/hour")
        print(f"    Service rate: {stats['service_rate']*3600:.1f}/hour per server")
        print(f"    CV: {stats['cv_service']:.2f}")

    # Define objective weights
    weights = {
        'wait': 0.5,   # 50% weight on wait time
        'cost': 0.3,   # 30% weight on cost
        'queue': 0.2   # 20% weight on queue length
    }

    print(f"\nObjective Function Weights:")
    print(f"  Wait Time: {weights['wait']*100:.0f}%")
    print(f"  Cost: {weights['cost']*100:.0f}%")
    print(f"  Queue Length: {weights['queue']*100:.0f}%")
    print(f"\nConstraint: Max Wait Time = {MAX_WAIT_TIME}s")

    # Run optimization methods
    results = {}

    # Method 1: Grid Search
    best_config_grid, metrics_grid, all_results = grid_search_optimization(data_stats, weights)
    results['Grid Search'] = (best_config_grid, metrics_grid)

    # Method 2: Gradient-based
    best_config_gradient, metrics_gradient = gradient_optimization(data_stats, weights)
    results['Gradient-Based'] = (best_config_gradient, metrics_gradient)

    # Method 3: Evolutionary
    best_config_evo, metrics_evo = evolutionary_optimization(data_stats, weights)
    results['Evolutionary'] = (best_config_evo, metrics_evo)

    # Generate report
    generate_report(results)

    # Sensitivity analysis on best solution
    sensitivity_analysis(best_config_grid, data_stats, weights)

    # Save results
    all_results.to_csv('optimization_results_all.csv', index=False)
    print(f"\n✓ All results saved to 'optimization_results_all.csv'")

    print("\n" + "="*60)
    print("OPTIMIZATION COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()
