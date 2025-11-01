"""
Enhanced Variability Analysis for Queueing Theory and Simulation
Incorporates distribution fitting, advanced queueing models, and variability propagation
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize
import sys
import io

# UTF-8 encoding for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


# ============================================================================
# PART 1: DISTRIBUTION FITTING WITH GOODNESS-OF-FIT TESTS
# ============================================================================

def fit_distributions(data, data_name="Data"):
    """
    Fit multiple distributions to data and select best based on goodness-of-fit

    Tests:
    - Exponential (M)
    - Gamma (Erlang-k as special case)
    - Lognormal
    - Weibull

    Returns best fit with parameters and goodness-of-fit statistics
    """
    print(f"\n{'='*70}")
    print(f"DISTRIBUTION FITTING: {data_name}")
    print('='*70)

    # Remove zeros and invalid data
    data = data[data > 0]
    n = len(data)

    print(f"\nSample size: {n}")
    print(f"Mean: {np.mean(data):.4f}")
    print(f"Std: {np.std(data):.4f}")
    print(f"CV: {np.std(data)/np.mean(data):.4f}")
    print(f"Min: {np.min(data):.4f}, Max: {np.max(data):.4f}")

    results = {}

    # 1. EXPONENTIAL (M) - CV = 1
    print(f"\n1. EXPONENTIAL DISTRIBUTION (Memoryless, CV=1)")
    try:
        # MLE: lambda = 1/mean
        loc_exp, scale_exp = 0, np.mean(data)

        # K-S test
        ks_stat, ks_pvalue = stats.kstest(data, 'expon', args=(loc_exp, scale_exp))

        # Log-likelihood
        log_likelihood = np.sum(stats.expon.logpdf(data, loc=loc_exp, scale=scale_exp))

        # AIC
        k_params = 1  # Only scale parameter
        aic = 2 * k_params - 2 * log_likelihood

        results['Exponential'] = {
            'distribution': 'Exponential',
            'params': {'loc': loc_exp, 'scale': scale_exp},
            'mean': scale_exp,
            'cv': 1.0,
            'ks_stat': ks_stat,
            'ks_pvalue': ks_pvalue,
            'log_likelihood': log_likelihood,
            'aic': aic,
            'scipy_name': 'expon',
            'scipy_params': (loc_exp, scale_exp)
        }

        print(f"   Scale (1/λ): {scale_exp:.4f}")
        print(f"   Theoretical CV: 1.0")
        print(f"   K-S statistic: {ks_stat:.4f}, p-value: {ks_pvalue:.4f}")
        print(f"   AIC: {aic:.2f}")

        if ks_pvalue < 0.05:
            print(f"   ⚠ Rejected at 5% significance (not exponential)")
        else:
            print(f"   ✓ Cannot reject (may be exponential)")

    except Exception as e:
        print(f"   Error fitting Exponential: {e}")

    # 2. GAMMA (Erlang-k) - CV = 1/sqrt(k)
    print(f"\n2. GAMMA DISTRIBUTION (Erlang-k, flexible CV)")
    try:
        # Fit using MLE
        shape_gamma, loc_gamma, scale_gamma = stats.gamma.fit(data, floc=0)

        # K-S test
        ks_stat, ks_pvalue = stats.kstest(data, 'gamma', args=(shape_gamma, loc_gamma, scale_gamma))

        # Log-likelihood
        log_likelihood = np.sum(stats.gamma.logpdf(data, shape_gamma, loc=loc_gamma, scale=scale_gamma))

        # AIC
        k_params = 2  # shape and scale
        aic = 2 * k_params - 2 * log_likelihood

        # Calculate CV
        cv_gamma = 1 / np.sqrt(shape_gamma)

        results['Gamma'] = {
            'distribution': 'Gamma',
            'params': {'shape': shape_gamma, 'loc': loc_gamma, 'scale': scale_gamma},
            'mean': shape_gamma * scale_gamma,
            'cv': cv_gamma,
            'ks_stat': ks_stat,
            'ks_pvalue': ks_pvalue,
            'log_likelihood': log_likelihood,
            'aic': aic,
            'scipy_name': 'gamma',
            'scipy_params': (shape_gamma, loc_gamma, scale_gamma)
        }

        print(f"   Shape (k): {shape_gamma:.4f}")
        print(f"   Scale (θ): {scale_gamma:.4f}")
        print(f"   Mean: {shape_gamma * scale_gamma:.4f}")
        print(f"   CV: {cv_gamma:.4f}")
        print(f"   K-S statistic: {ks_stat:.4f}, p-value: {ks_pvalue:.4f}")
        print(f"   AIC: {aic:.2f}")

        if ks_pvalue < 0.05:
            print(f"   ⚠ Rejected at 5% significance")
        else:
            print(f"   ✓ Cannot reject (good fit)")

    except Exception as e:
        print(f"   Error fitting Gamma: {e}")

    # 3. LOGNORMAL - Right-skewed, CV > 1 typical
    print(f"\n3. LOGNORMAL DISTRIBUTION (Right-skewed, high variability)")
    try:
        # Fit using MLE
        shape_lognorm, loc_lognorm, scale_lognorm = stats.lognorm.fit(data, floc=0)

        # K-S test
        ks_stat, ks_pvalue = stats.kstest(data, 'lognorm', args=(shape_lognorm, loc_lognorm, scale_lognorm))

        # Log-likelihood
        log_likelihood = np.sum(stats.lognorm.logpdf(data, shape_lognorm, loc=loc_lognorm, scale=scale_lognorm))

        # AIC
        k_params = 2  # shape (sigma) and scale (exp(mu))
        aic = 2 * k_params - 2 * log_likelihood

        # Calculate CV
        cv_lognorm = np.sqrt(np.exp(shape_lognorm**2) - 1)

        results['Lognormal'] = {
            'distribution': 'Lognormal',
            'params': {'shape': shape_lognorm, 'loc': loc_lognorm, 'scale': scale_lognorm},
            'mean': scale_lognorm * np.exp(shape_lognorm**2 / 2),
            'cv': cv_lognorm,
            'ks_stat': ks_stat,
            'ks_pvalue': ks_pvalue,
            'log_likelihood': log_likelihood,
            'aic': aic,
            'scipy_name': 'lognorm',
            'scipy_params': (shape_lognorm, loc_lognorm, scale_lognorm)
        }

        print(f"   Shape (σ): {shape_lognorm:.4f}")
        print(f"   Scale (exp(μ)): {scale_lognorm:.4f}")
        print(f"   Mean: {results['Lognormal']['mean']:.4f}")
        print(f"   CV: {cv_lognorm:.4f}")
        print(f"   K-S statistic: {ks_stat:.4f}, p-value: {ks_pvalue:.4f}")
        print(f"   AIC: {aic:.2f}")

        if ks_pvalue < 0.05:
            print(f"   ⚠ Rejected at 5% significance")
        else:
            print(f"   ✓ Cannot reject (good fit)")

    except Exception as e:
        print(f"   Error fitting Lognormal: {e}")

    # 4. WEIBULL - Flexible shape (increasing/decreasing hazard)
    print(f"\n4. WEIBULL DISTRIBUTION (Flexible failure rate)")
    try:
        # Fit using MLE
        shape_weibull, loc_weibull, scale_weibull = stats.weibull_min.fit(data, floc=0)

        # K-S test
        ks_stat, ks_pvalue = stats.kstest(data, 'weibull_min', args=(shape_weibull, loc_weibull, scale_weibull))

        # Log-likelihood
        log_likelihood = np.sum(stats.weibull_min.logpdf(data, shape_weibull, loc=loc_weibull, scale=scale_weibull))

        # AIC
        k_params = 2  # shape and scale
        aic = 2 * k_params - 2 * log_likelihood

        # Calculate CV
        mean_weibull = scale_weibull * stats.gamma(1 + 1/shape_weibull)
        variance_weibull = scale_weibull**2 * (stats.gamma(1 + 2/shape_weibull) - stats.gamma(1 + 1/shape_weibull)**2)
        cv_weibull = np.sqrt(variance_weibull) / mean_weibull

        results['Weibull'] = {
            'distribution': 'Weibull',
            'params': {'shape': shape_weibull, 'loc': loc_weibull, 'scale': scale_weibull},
            'mean': mean_weibull,
            'cv': cv_weibull,
            'ks_stat': ks_stat,
            'ks_pvalue': ks_pvalue,
            'log_likelihood': log_likelihood,
            'aic': aic,
            'scipy_name': 'weibull_min',
            'scipy_params': (shape_weibull, loc_weibull, scale_weibull)
        }

        print(f"   Shape (k): {shape_weibull:.4f}")
        print(f"   Scale (λ): {scale_weibull:.4f}")
        print(f"   Mean: {mean_weibull:.4f}")
        print(f"   CV: {cv_weibull:.4f}")
        print(f"   K-S statistic: {ks_stat:.4f}, p-value: {ks_pvalue:.4f}")
        print(f"   AIC: {aic:.2f}")

        if ks_pvalue < 0.05:
            print(f"   ⚠ Rejected at 5% significance")
        else:
            print(f"   ✓ Cannot reject (good fit)")

    except Exception as e:
        print(f"   Error fitting Weibull: {e}")

    # SELECT BEST DISTRIBUTION
    print(f"\n{'='*70}")
    print("BEST DISTRIBUTION SELECTION")
    print('='*70)

    # Rank by AIC (lower is better)
    ranked = sorted(results.items(), key=lambda x: x[1]['aic'])

    print(f"\nRanking by AIC (Akaike Information Criterion):")
    for i, (name, result) in enumerate(ranked, 1):
        print(f"  {i}. {name:15} AIC={result['aic']:.2f}, K-S p={result['ks_pvalue']:.4f}, CV={result['cv']:.4f}")

    best_dist = ranked[0][1]
    print(f"\n✓ BEST FIT: {best_dist['distribution']}")
    print(f"  Mean: {best_dist['mean']:.4f}")
    print(f"  CV: {best_dist['cv']:.4f}")
    print(f"  AIC: {best_dist['aic']:.2f}")

    return results, best_dist, data


def plot_distribution_fit(data, fit_results, data_name="Data", filename=None):
    """Create comprehensive visualization of distribution fits"""

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Distribution Fitting: {data_name}', fontsize=14, fontweight='bold')

    # Plot 1: Histogram with fitted PDFs
    ax = axes[0, 0]
    ax.hist(data, bins=30, density=True, alpha=0.6, color='gray', edgecolor='black', label='Observed Data')

    x_range = np.linspace(data.min(), data.max(), 200)

    colors = {'Exponential': 'blue', 'Gamma': 'green', 'Lognormal': 'red', 'Weibull': 'purple'}

    for dist_name, result in fit_results.items():
        if dist_name in colors:
            dist_obj = getattr(stats, result['scipy_name'])
            pdf = dist_obj.pdf(x_range, *result['scipy_params'])
            ax.plot(x_range, pdf, label=f"{dist_name} (AIC={result['aic']:.0f})",
                   color=colors[dist_name], linewidth=2)

    ax.set_xlabel('Value')
    ax.set_ylabel('Probability Density')
    ax.set_title('Probability Density Functions')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 2: CDF Comparison
    ax = axes[0, 1]

    # Empirical CDF
    sorted_data = np.sort(data)
    empirical_cdf = np.arange(1, len(sorted_data) + 1) / len(sorted_data)
    ax.plot(sorted_data, empirical_cdf, 'o', markersize=2, alpha=0.5, color='gray', label='Empirical CDF')

    for dist_name, result in fit_results.items():
        if dist_name in colors:
            dist_obj = getattr(stats, result['scipy_name'])
            theoretical_cdf = dist_obj.cdf(sorted_data, *result['scipy_params'])
            ax.plot(sorted_data, theoretical_cdf, label=dist_name,
                   color=colors[dist_name], linewidth=2)

    ax.set_xlabel('Value')
    ax.set_ylabel('Cumulative Probability')
    ax.set_title('Cumulative Distribution Functions')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 3: Q-Q Plot for best distribution
    ax = axes[1, 0]

    best_dist_name = min(fit_results.items(), key=lambda x: x[1]['aic'])[0]
    best_result = fit_results[best_dist_name]

    dist_obj = getattr(stats, best_result['scipy_name'])
    theoretical_quantiles = dist_obj.ppf(empirical_cdf, *best_result['scipy_params'])

    ax.scatter(theoretical_quantiles, sorted_data, alpha=0.5, s=10)

    # Reference line
    min_val = min(theoretical_quantiles.min(), sorted_data.min())
    max_val = max(theoretical_quantiles.max(), sorted_data.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Fit')

    ax.set_xlabel(f'Theoretical Quantiles ({best_dist_name})')
    ax.set_ylabel('Sample Quantiles')
    ax.set_title(f'Q-Q Plot: {best_dist_name} (Best Fit)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Plot 4: AIC Comparison
    ax = axes[1, 1]

    dist_names = list(fit_results.keys())
    aics = [fit_results[name]['aic'] for name in dist_names]
    colors_list = [colors.get(name, 'gray') for name in dist_names]

    bars = ax.bar(dist_names, aics, color=colors_list, alpha=0.7, edgecolor='black')

    # Highlight best (lowest AIC)
    best_idx = np.argmin(aics)
    bars[best_idx].set_edgecolor('red')
    bars[best_idx].set_linewidth(3)

    ax.set_ylabel('AIC (lower is better)')
    ax.set_title('Model Comparison (AIC)')
    ax.grid(True, alpha=0.3, axis='y')

    # Add values on bars
    for i, (name, aic) in enumerate(zip(dist_names, aics)):
        ax.text(i, aic + max(aics)*0.02, f'{aic:.0f}', ha='center', fontsize=9)

    plt.tight_layout()

    if filename:
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\n✓ Plot saved to '{filename}'")

    plt.close()


# ============================================================================
# PART 2: ADVANCED QUEUEING MODELS WITH SPECIFIC DISTRIBUTIONS
# ============================================================================

def advanced_queueing_analysis(arrival_dist, service_dist, num_servers, name="System"):
    """
    Advanced queueing analysis using specific distributions

    Models:
    - M/M/c (Exponential arrivals and service)
    - M/G/c (Exponential arrivals, General service)
    - GI/G/c (General arrivals and service - approximations)
    """
    print(f"\n{'='*70}")
    print(f"ADVANCED QUEUEING ANALYSIS: {name}")
    print('='*70)

    lambda_rate = 1 / arrival_dist['mean']  # Arrival rate
    mu_rate = 1 / service_dist['mean']  # Service rate
    c = num_servers

    rho = lambda_rate / (c * mu_rate)  # Traffic intensity

    print(f"\nSystem Parameters:")
    print(f"  Arrival rate (λ): {lambda_rate*3600:.1f}/hour")
    print(f"  Service rate (μ): {mu_rate*3600:.1f}/hour per server")
    print(f"  Number of servers (c): {c}")
    print(f"  Traffic intensity (ρ): {rho:.4f}")

    if rho >= 1.0:
        print(f"\n⚠ WARNING: System is unstable (ρ ≥ 1). Queue will grow indefinitely!")
        return None

    cv_a = arrival_dist['cv']
    cv_s = service_dist['cv']

    print(f"  CV of arrivals: {cv_a:.4f}")
    print(f"  CV of service: {cv_s:.4f}")

    results = {}

    # Model 1: M/M/c (if both exponential)
    if abs(cv_a - 1.0) < 0.1 and abs(cv_s - 1.0) < 0.1:
        print(f"\n1. M/M/{c} MODEL (Exponential/Exponential)")
        print("   Exact Erlang-C formula available")

        # Erlang-C probability (probability of queueing)
        def erlang_c(c, rho_total):
            """Probability that arrival has to wait (all servers busy)"""
            rho_total = lambda_rate / mu_rate

            # Calculate P(0) - probability system is empty
            sum_term = sum([(rho_total**n) / np.math.factorial(n) for n in range(c)])
            last_term = (rho_total**c) / (np.math.factorial(c) * (1 - rho))
            p0 = 1 / (sum_term + last_term)

            # Erlang-C
            pc = ((rho_total**c) / np.math.factorial(c)) * (1 / (1 - rho)) * p0

            return pc

        try:
            rho_total = lambda_rate / mu_rate
            prob_wait = erlang_c(c, rho_total)

            # Average wait time in queue
            wait_queue = prob_wait / (c * mu_rate - lambda_rate)

            # Average time in system
            wait_system = wait_queue + 1/mu_rate

            # Average queue length
            queue_length = lambda_rate * wait_queue

            # Average number in system
            num_in_system = lambda_rate * wait_system

            results['MM c'] = {
                'model': f'M/M/{c}',
                'prob_wait': prob_wait,
                'wait_queue': wait_queue,
                'wait_system': wait_system,
                'queue_length': queue_length,
                'num_in_system': num_in_system
            }

            print(f"   P(Wait): {prob_wait:.4f}")
            print(f"   Average wait in queue: {wait_queue:.4f}s")
            print(f"   Average time in system: {wait_system:.4f}s")
            print(f"   Average queue length: {queue_length:.4f}")
            print(f"   Average in system: {num_in_system:.4f}")

        except Exception as e:
            print(f"   Error in M/M/c calculation: {e}")

    # Model 2: M/G/c approximation (Exponential arrivals, General service)
    if abs(cv_a - 1.0) < 0.1:
        print(f"\n2. M/G/{c} APPROXIMATION (Exponential arrivals, General service)")

        # Use Kingman's approximation modified for multiple servers
        wait_queue_mmc = erlang_c(c, lambda_rate/mu_rate) / (c * mu_rate - lambda_rate) if 'erlang_c' in dir() else \
                         (rho / (1 - rho)) * ((1 + cv_s**2) / 2) / mu_rate

        wait_system = wait_queue_mmc + 1/mu_rate
        queue_length = lambda_rate * wait_queue_mmc

        results['MG c'] = {
            'model': f'M/G/{c}',
            'wait_queue': wait_queue_mmc,
            'wait_system': wait_system,
            'queue_length': queue_length,
            'service_cv_impact': cv_s
        }

        print(f"   Average wait in queue: {wait_queue_mmc:.4f}s")
        print(f"   Impact of service CV={cv_s:.2f}: ")
        print(f"     If CV=1.0: wait ≈ {wait_queue_mmc * (1.0**2)/cv_s**2:.4f}s")
        print(f"     If CV=0.5: wait ≈ {wait_queue_mmc * (0.5**2)/cv_s**2:.4f}s ({100*(1-0.25/cv_s**2):.0f}% reduction)")

    # Model 3: GI/G/c approximation (General/General)
    print(f"\n3. GI/G/{c} APPROXIMATION (General/General - Kingman)")

    # Kingman's VUT equation
    wait_queue_gig = (rho / (1 - rho)) * ((cv_a**2 + cv_s**2) / 2) / mu_rate
    wait_system = wait_queue_gig + 1/mu_rate
    queue_length = lambda_rate * wait_queue_gig

    results['GIG c'] = {
        'model': f'GI/G/{c}',
        'wait_queue': wait_queue_gig,
        'wait_system': wait_system,
        'queue_length': queue_length,
        'variability_index': (cv_a**2 + cv_s**2) / 2
    }

    print(f"   Variability index: (CV_a² + CV_s²)/2 = {(cv_a**2 + cv_s**2)/2:.4f}")
    print(f"   Average wait in queue: {wait_queue_gig:.4f}s")
    print(f"   Average time in system: {wait_system:.4f}s")

    # Variability decomposition
    print(f"\n   VARIABILITY DECOMPOSITION:")
    total_var_contribution = cv_a**2 + cv_s**2
    arrival_contribution = cv_a**2 / total_var_contribution * 100
    service_contribution = cv_s**2 / total_var_contribution * 100

    print(f"   Arrival variability contributes: {arrival_contribution:.1f}%")
    print(f"   Service variability contributes: {service_contribution:.1f}%")

    if service_contribution > 60:
        print(f"   → Service variability is DOMINANT - focus on standardization!")
    elif arrival_contribution > 60:
        print(f"   → Arrival variability is DOMINANT - focus on demand smoothing!")
    else:
        print(f"   → Both sources contribute significantly")

    return results


# ============================================================================
# PART 3: TIME-VARYING VARIABILITY ANALYSIS
# ============================================================================

def time_varying_variability(df, entity_type, window_minutes=5):
    """
    Analyze how variability changes over time
    Shows periods of high/low variability
    """
    print(f"\n{'='*70}")
    print(f"TIME-VARYING VARIABILITY ANALYSIS: {entity_type}")
    print('='*70)

    entity_df = df[df['Entity_Type'] == entity_type].copy()
    entity_df = entity_df.sort_values('Arrival_Time')

    # Calculate inter-arrival times
    entity_df['Inter_Arrival'] = entity_df['Arrival_Time'].diff()
    entity_df = entity_df.dropna()

    # Window analysis
    window_seconds = window_minutes * 60
    max_time = entity_df['Arrival_Time'].max()
    num_windows = int(np.ceil(max_time / window_seconds))

    print(f"\nWindow size: {window_minutes} minutes")
    print(f"Number of windows: {num_windows}")

    window_stats = []

    for i in range(num_windows):
        start_time = i * window_seconds
        end_time = (i + 1) * window_seconds

        window_data = entity_df[(entity_df['Arrival_Time'] >= start_time) &
                                (entity_df['Arrival_Time'] < end_time)]

        if len(window_data) < 2:
            continue

        inter_arrivals = window_data['Inter_Arrival'].values

        mean_ia = np.mean(inter_arrivals)
        std_ia = np.std(inter_arrivals)
        cv_ia = std_ia / mean_ia if mean_ia > 0 else 0

        # Service time variability (if available)
        if 'Service_Time' in window_data.columns:
            service_times = window_data['Service_Time'].values
            mean_st = np.mean(service_times)
            std_st = np.std(service_times)
            cv_st = std_st / mean_st if mean_st > 0 else 0
        else:
            mean_st, std_st, cv_st = 0, 0, 0

        window_stats.append({
            'window': i,
            'start_min': start_time / 60,
            'end_min': end_time / 60,
            'count': len(window_data),
            'mean_ia': mean_ia,
            'cv_ia': cv_ia,
            'mean_st': mean_st,
            'cv_st': cv_st
        })

    stats_df = pd.DataFrame(window_stats)

    print(f"\nOverall Statistics Across Time:")
    print(f"  Mean CV (inter-arrival): {stats_df['cv_ia'].mean():.4f}")
    print(f"  Std CV (inter-arrival): {stats_df['cv_ia'].std():.4f}")
    print(f"  Min CV: {stats_df['cv_ia'].min():.4f} (window {stats_df.loc[stats_df['cv_ia'].idxmin(), 'window']:.0f})")
    print(f"  Max CV: {stats_df['cv_ia'].max():.4f} (window {stats_df.loc[stats_df['cv_ia'].idxmax(), 'window']:.0f})")

    # Identify high/low variability periods
    median_cv = stats_df['cv_ia'].median()
    high_var_windows = stats_df[stats_df['cv_ia'] > median_cv * 1.5]
    low_var_windows = stats_df[stats_df['cv_ia'] < median_cv * 0.5]

    print(f"\nHigh Variability Periods (CV > {median_cv*1.5:.2f}):")
    if len(high_var_windows) > 0:
        for _, row in high_var_windows.iterrows():
            print(f"  {row['start_min']:.1f}-{row['end_min']:.1f} min: CV={row['cv_ia']:.2f}")
    else:
        print("  None")

    print(f"\nLow Variability Periods (CV < {median_cv*0.5:.2f}):")
    if len(low_var_windows) > 0:
        for _, row in low_var_windows.iterrows():
            print(f"  {row['start_min']:.1f}-{row['end_min']:.1f} min: CV={row['cv_ia']:.2f}")
    else:
        print("  None")

    # Plot
    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(stats_df['start_min'], stats_df['cv_ia'], 'bo-', label='CV (Inter-Arrival)')
    plt.axhline(median_cv, color='r', linestyle='--', label=f'Median CV = {median_cv:.2f}')
    plt.axhline(median_cv * 1.5, color='orange', linestyle=':', label='High Variability Threshold')
    plt.axhline(median_cv * 0.5, color='green', linestyle=':', label='Low Variability Threshold')
    plt.xlabel('Time (minutes)')
    plt.ylabel('CV')
    plt.title(f'Inter-Arrival Time Variability Over Time - {entity_type}')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(2, 1, 2)
    plt.bar(stats_df['start_min'], stats_df['count'], width=window_minutes*0.8,
           alpha=0.6, edgecolor='black')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Arrivals per Window')
    plt.title('Arrival Counts by Time Window')
    plt.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    filename = f'time_varying_variability_{entity_type.replace(" ", "_")}.png'
    plt.savefig(filename, dpi=150)
    print(f"\n✓ Plot saved to '{filename}'")
    plt.close()

    return stats_df


# ============================================================================
# MAIN ANALYSIS RUNNER
# ============================================================================

def load_data(filepath='combined_results.csv'):
    """Load traffic data"""
    try:
        df = pd.read_csv(filepath)
    except:
        df = pd.read_excel(filepath)

    if 'Time (s)' in df.columns:
        df = df.rename(columns={'Time (s)': 'Arrival_Time', 'Entity': 'Entity_Type'})

    return df


def main():
    """Run comprehensive variability analysis"""
    print("="*70)
    print("ENHANCED VARIABILITY ANALYSIS")
    print("Queueing Theory + Simulation with Distribution Fitting")
    print("="*70)

    # Load data
    print("\nLoading data...")
    df = load_data('combined_results.csv')
    print(f"✓ Loaded {len(df)} entities")

    # Analyze each entity type
    for entity_type in ['WB Vehicles', 'EB Vehicles', 'Crossers', 'Posers']:
        entity_df = df[df['Entity_Type'] == entity_type]

        if len(entity_df) < 10:
            print(f"\n⚠ Skipping {entity_type} - insufficient data")
            continue

        print(f"\n{'#'*70}")
        print(f"# ENTITY: {entity_type}")
        print(f"{'#'*70}")

        # Calculate inter-arrival times
        entity_df = entity_df.sort_values('Arrival_Time')
        inter_arrivals = entity_df['Arrival_Time'].diff().dropna().values

        # Fit distributions to inter-arrival times
        ia_results, ia_best, ia_data = fit_distributions(inter_arrivals,
                                                          f"{entity_type} - Inter-Arrival Times")

        # Plot fits
        plot_distribution_fit(ia_data, ia_results,
                            f"{entity_type} - Inter-Arrival Times",
                            f"distribution_fit_{entity_type.replace(' ', '_')}_arrivals.png")

        # Fit distributions to service times (if available)
        if 'Service_Time' in entity_df.columns:
            service_times = entity_df['Service_Time'].dropna().values
            if len(service_times) > 10:
                st_results, st_best, st_data = fit_distributions(service_times,
                                                                 f"{entity_type} - Service Times")

                plot_distribution_fit(st_data, st_results,
                                    f"{entity_type} - Service Times",
                                    f"distribution_fit_{entity_type.replace(' ', '_')}_service.png")
            else:
                st_best = {'distribution': 'Exponential', 'mean': 1.0, 'cv': 1.0}
        else:
            st_best = {'distribution': 'Exponential', 'mean': 1.0, 'cv': 1.0}

        # Advanced queueing analysis with fitted distributions
        num_servers = 2 if 'Vehicles' in entity_type else 1
        queue_results = advanced_queueing_analysis(ia_best, st_best, num_servers, entity_type)

        # Time-varying variability
        time_var_stats = time_varying_variability(df, entity_type, window_minutes=5)

    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print('='*70)
    print("\n✓ Distribution fits completed")
    print("✓ Advanced queueing models evaluated")
    print("✓ Time-varying variability analyzed")
    print("\nGenerated files:")
    print("  - distribution_fit_*_arrivals.png")
    print("  - distribution_fit_*_service.png")
    print("  - time_varying_variability_*.png")


if __name__ == '__main__':
    main()
