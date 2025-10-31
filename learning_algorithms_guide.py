"""
Learning Algorithms for Traffic Pattern Analysis
=================================================
Uses machine learning to learn from historical data and predict/optimize traffic behavior.

Applications for Abbey Road Traffic Analysis:
1. Arrival pattern prediction (time-based forecasting)
2. Peak period detection (anomaly detection)
3. Optimal resource allocation (optimization)
4. Traffic state classification (pattern recognition)
5. Adaptive capacity planning (reinforcement learning concepts)

Dataset: October 20 data (90 minutes, 1,073 entities)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
import sys
import io

warnings.filterwarnings('ignore')

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ===========================
# 1. TIME-BASED PATTERN LEARNING
# ===========================

def learn_arrival_patterns(df, entity_type, time_window_minutes=5):
    """
    Learn arrival rate patterns over time.
    Useful for: Predicting future arrival rates, identifying peak periods.
    """
    print(f"\n{'='*70}")
    print(f"Learning Arrival Patterns: {entity_type}")
    print('='*70)

    # Filter by entity type
    entity_df = df[df['Entity_Type'] == entity_type].copy()

    # Create time windows
    max_time = entity_df['Arrival_Time'].max()
    time_windows = np.arange(0, max_time + time_window_minutes*60, time_window_minutes*60)

    # Count arrivals in each window
    arrival_counts = []
    window_centers = []

    for i in range(len(time_windows) - 1):
        start = time_windows[i]
        end = time_windows[i + 1]
        count = len(entity_df[(entity_df['Arrival_Time'] >= start) &
                              (entity_df['Arrival_Time'] < end)])
        arrival_counts.append(count)
        window_centers.append((start + end) / 2)

    # Create features for learning
    features_df = pd.DataFrame({
        'time_minutes': np.array(window_centers) / 60,
        'arrival_count': arrival_counts
    })

    # Add derived features
    features_df['time_squared'] = features_df['time_minutes'] ** 2
    features_df['time_cubed'] = features_df['time_minutes'] ** 3
    features_df['sin_time'] = np.sin(2 * np.pi * features_df['time_minutes'] / 90)  # 90-min cycle
    features_df['cos_time'] = np.cos(2 * np.pi * features_df['time_minutes'] / 90)

    # Train predictive model
    X = features_df[['time_minutes', 'time_squared', 'time_cubed', 'sin_time', 'cos_time']]
    y = features_df['arrival_count']

    model = GradientBoostingRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    # Predictions
    predictions = model.predict(X)

    # Calculate metrics
    mse = mean_squared_error(y, predictions)
    r2 = r2_score(y, predictions)

    print(f"\nModel Performance:")
    print(f"  MSE: {mse:.2f}")
    print(f"  R² Score: {r2:.3f}")
    print(f"  Average arrivals per {time_window_minutes} min: {np.mean(arrival_counts):.1f}")

    # Identify peak periods
    peak_threshold = np.mean(arrival_counts) + np.std(arrival_counts)
    peak_windows = features_df[features_df['arrival_count'] > peak_threshold]

    print(f"\nPeak Periods Detected:")
    print(f"  Threshold: >{peak_threshold:.1f} arrivals per {time_window_minutes} min")
    print(f"  Number of peak windows: {len(peak_windows)}")
    if len(peak_windows) > 0:
        for idx, row in peak_windows.iterrows():
            print(f"    {row['time_minutes']:.1f} min: {row['arrival_count']:.0f} arrivals")

    return {
        'model': model,
        'features': features_df,
        'predictions': predictions,
        'metrics': {'mse': mse, 'r2': r2},
        'peak_threshold': peak_threshold
    }


# ===========================
# 2. TRAFFIC STATE CLASSIFICATION
# ===========================

def classify_traffic_states(df, n_states=3):
    """
    Use clustering to identify distinct traffic states (e.g., light, moderate, heavy).
    Useful for: Adaptive resource allocation, understanding traffic patterns.
    """
    print(f"\n{'='*70}")
    print(f"Traffic State Classification (K-Means Clustering)")
    print('='*70)

    # Create time windows (1-minute intervals)
    max_time = df['Arrival_Time'].max()
    time_windows = np.arange(0, max_time + 60, 60)

    # Calculate features for each time window
    features_list = []
    for i in range(len(time_windows) - 1):
        start = time_windows[i]
        end = time_windows[i + 1]
        window_df = df[(df['Arrival_Time'] >= start) & (df['Arrival_Time'] < end)]

        # Count by entity type
        eb_count = len(window_df[window_df['Entity_Type'] == 'EB Vehicles'])
        wb_count = len(window_df[window_df['Entity_Type'] == 'WB Vehicles'])
        crosser_count = len(window_df[window_df['Entity_Type'] == 'Crossers'])
        poser_count = len(window_df[window_df['Entity_Type'] == 'Posers'])

        total_count = len(window_df)

        features_list.append({
            'time_minutes': start / 60,
            'eb_count': eb_count,
            'wb_count': wb_count,
            'crosser_count': crosser_count,
            'poser_count': poser_count,
            'total_count': total_count
        })

    features_df = pd.DataFrame(features_list)

    # Perform clustering
    X = features_df[['eb_count', 'wb_count', 'crosser_count', 'poser_count']].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=n_states, random_state=42, n_init=10)
    features_df['state'] = kmeans.fit_predict(X_scaled)

    # Analyze states
    print(f"\nIdentified {n_states} Traffic States:")
    for state in range(n_states):
        state_df = features_df[features_df['state'] == state]
        print(f"\nState {state} ({len(state_df)} minutes, {len(state_df)/len(features_df)*100:.1f}%):")
        print(f"  Average arrivals per minute:")
        print(f"    EB Vehicles: {state_df['eb_count'].mean():.2f}")
        print(f"    WB Vehicles: {state_df['wb_count'].mean():.2f}")
        print(f"    Crossers: {state_df['crosser_count'].mean():.2f}")
        print(f"    Posers: {state_df['poser_count'].mean():.2f}")
        print(f"    Total: {state_df['total_count'].mean():.2f}")

        # Characterize state
        total_avg = state_df['total_count'].mean()
        if total_avg < 8:
            label = "LIGHT Traffic"
        elif total_avg < 15:
            label = "MODERATE Traffic"
        else:
            label = "HEAVY Traffic"
        print(f"  Classification: {label}")

    return {
        'model': kmeans,
        'scaler': scaler,
        'features': features_df,
        'cluster_centers': kmeans.cluster_centers_
    }


# ===========================
# 3. OPTIMAL CAPACITY LEARNING
# ===========================

def learn_optimal_capacity(df, entity_type, target_wait_time=5.0):
    """
    Learn optimal server capacity based on arrival patterns.
    Uses queueing theory + learning to find best capacity for different traffic states.
    """
    print(f"\n{'='*70}")
    print(f"Learning Optimal Capacity: {entity_type}")
    print('='*70)

    entity_df = df[df['Entity_Type'] == entity_type].copy()

    # Calculate arrival rate (λ)
    duration_hours = entity_df['Arrival_Time'].max() / 3600
    arrival_rate = len(entity_df) / duration_hours

    # Estimate service rate (μ)
    if 'Service_Time' in entity_df.columns:
        service_times = pd.to_numeric(entity_df['Service_Time'], errors='coerce')
        service_times = service_times[service_times > 0]
        if len(service_times) > 0:
            mean_service_time = service_times.mean() / 3600  # Convert to hours
            service_rate = 1 / mean_service_time
        else:
            service_rate = arrival_rate * 2  # Default assumption
    else:
        service_rate = arrival_rate * 2

    # Calculate traffic intensity and CV
    if 'Inter_Arrival_Time' in entity_df.columns:
        iat = pd.to_numeric(entity_df['Inter_Arrival_Time'], errors='coerce')
        iat = iat[iat > 0]
        cv_a = iat.std() / iat.mean() if len(iat) > 0 else 1.0
    else:
        cv_a = 1.0

    cv_s = 0.5  # Assume moderate service time variability

    print(f"\nTraffic Parameters:")
    print(f"  Arrival rate (λ): {arrival_rate:.2f} per hour")
    print(f"  Service rate (μ): {service_rate:.2f} per hour")
    print(f"  CV of arrivals: {cv_a:.2f}")
    print(f"  Target wait time: {target_wait_time:.1f} seconds")

    # Test different capacities
    capacity_options = range(1, 20)
    results = []

    for c in capacity_options:
        rho = arrival_rate / (c * service_rate)

        if rho >= 1:
            wait_time = float('inf')
            utilization = 100
        else:
            # Kingman's VUT approximation
            wait_time = (rho / (1 - rho)) * ((cv_a**2 + cv_s**2) / 2) * (1 / service_rate) * 3600
            utilization = rho * 100

        results.append({
            'capacity': c,
            'utilization': utilization,
            'wait_time': wait_time,
            'feasible': wait_time <= target_wait_time
        })

    results_df = pd.DataFrame(results)

    # Find optimal capacity
    feasible = results_df[results_df['feasible']]
    if len(feasible) > 0:
        optimal = feasible.iloc[0]
        print(f"\nOptimal Capacity Found:")
        print(f"  Servers: {optimal['capacity']:.0f}")
        print(f"  Utilization: {optimal['utilization']:.1f}%")
        print(f"  Wait time: {optimal['wait_time']:.1f} seconds")
    else:
        print(f"\nNo feasible capacity found within tested range!")
        print(f"  Minimum wait time achieved: {results_df['wait_time'].min():.1f} seconds")
        print(f"  Required capacity: >{capacity_options[-1]}")

    # Show capacity options
    print(f"\nCapacity Options (first 10):")
    print(results_df.head(10).to_string(index=False))

    return {
        'results': results_df,
        'optimal': optimal if len(feasible) > 0 else None,
        'arrival_rate': arrival_rate,
        'service_rate': service_rate
    }


# ===========================
# 4. INTER-ARRIVAL TIME PREDICTION
# ===========================

def predict_next_arrival(df, entity_type, lookback=5):
    """
    Learn to predict next inter-arrival time based on recent history.
    Useful for: Real-time traffic prediction, adaptive signal control.
    """
    print(f"\n{'='*70}")
    print(f"Next Arrival Prediction: {entity_type}")
    print('='*70)

    entity_df = df[df['Entity_Type'] == entity_type].copy()
    entity_df = entity_df.sort_values('Arrival_Time').reset_index(drop=True)

    # Get inter-arrival times
    if 'Inter_Arrival_Time' not in entity_df.columns:
        entity_df['Inter_Arrival_Time'] = entity_df['Arrival_Time'].diff()

    iat = pd.to_numeric(entity_df['Inter_Arrival_Time'], errors='coerce')
    iat = iat.dropna()

    if len(iat) < lookback + 10:
        print(f"Not enough data for prediction (need >{lookback + 10} arrivals)")
        return None

    # Create sequences
    X = []
    y = []

    for i in range(lookback, len(iat)):
        X.append(iat.iloc[i-lookback:i].values)
        y.append(iat.iloc[i])

    X = np.array(X)
    y = np.array(y)

    # Split data
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    # Train model
    model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
    model.fit(X_train, y_train)

    # Evaluate
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    train_mse = mean_squared_error(y_train, train_pred)
    test_mse = mean_squared_error(y_test, test_pred)
    train_r2 = r2_score(y_train, train_pred)
    test_r2 = r2_score(y_test, test_pred)

    print(f"\nModel Performance (predicting next inter-arrival time):")
    print(f"  Training MSE: {train_mse:.2f}, R²: {train_r2:.3f}")
    print(f"  Testing MSE: {test_mse:.2f}, R²: {test_r2:.3f}")
    print(f"  Baseline (mean): {y.mean():.2f} seconds")

    # Feature importance
    print(f"\nFeature Importance (most recent = higher index):")
    importance = model.feature_importances_
    for i, imp in enumerate(importance):
        print(f"  Position t-{lookback-i}: {imp:.3f}")

    return {
        'model': model,
        'train_mse': train_mse,
        'test_mse': test_mse,
        'train_r2': train_r2,
        'test_r2': test_r2,
        'feature_importance': importance
    }


# ===========================
# 5. ADAPTIVE RESOURCE ALLOCATION
# ===========================

def adaptive_resource_learning(df):
    """
    Learn adaptive resource allocation rules based on current traffic state.
    Uses decision tree logic to determine: Given current conditions, how many servers needed?
    """
    print(f"\n{'='*70}")
    print(f"Adaptive Resource Allocation Learning")
    print('='*70)

    # Create time windows (5-minute intervals)
    max_time = df['Arrival_Time'].max()
    time_windows = np.arange(0, max_time + 300, 300)

    training_data = []

    for i in range(len(time_windows) - 1):
        start = time_windows[i]
        end = time_windows[i + 1]
        window_df = df[(df['Arrival_Time'] >= start) & (df['Arrival_Time'] < end)]

        # Features: arrival counts by entity type
        eb_count = len(window_df[window_df['Entity_Type'] == 'EB Vehicles'])
        wb_count = len(window_df[window_df['Entity_Type'] == 'WB Vehicles'])
        crosser_count = len(window_df[window_df['Entity_Type'] == 'Crossers'])
        poser_count = len(window_df[window_df['Entity_Type'] == 'Posers'])

        # Calculate required capacity (simplified queueing logic)
        # Target: 80% utilization
        eb_required = max(1, int(np.ceil(eb_count / (5 * 0.8))))
        wb_required = max(1, int(np.ceil(wb_count / (5 * 0.8))))
        crosser_required = max(1, int(np.ceil(crosser_count / (5 * 0.8))))
        poser_required = max(1, int(np.ceil(poser_count / (5 * 0.8))))

        training_data.append({
            'eb_arrivals': eb_count,
            'wb_arrivals': wb_count,
            'crosser_arrivals': crosser_count,
            'poser_arrivals': poser_count,
            'total_arrivals': len(window_df),
            'eb_capacity': eb_required,
            'wb_capacity': wb_required,
            'crosser_capacity': crosser_required,
            'poser_capacity': poser_required
        })

    training_df = pd.DataFrame(training_data)

    print(f"\nLearned Allocation Rules:")
    print(f"  Training samples: {len(training_df)}")

    # Train models for each entity type
    entity_types = ['eb', 'wb', 'crosser', 'poser']
    models = {}

    for entity in entity_types:
        X = training_df[['eb_arrivals', 'wb_arrivals', 'crosser_arrivals', 'poser_arrivals']]
        y = training_df[f'{entity}_capacity']

        model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=5)
        model.fit(X, y)

        models[entity] = model

        # Show example rules
        avg_arrivals = training_df[f'{entity}_arrivals'].mean()
        avg_capacity = training_df[f'{entity}_capacity'].mean()

        print(f"\n  {entity.upper()}:")
        print(f"    Average arrivals (5 min): {avg_arrivals:.1f}")
        print(f"    Average capacity needed: {avg_capacity:.1f} servers")

    # Test adaptive allocation
    print(f"\n{'='*70}")
    print("Example Adaptive Allocation:")
    print('='*70)

    test_scenarios = [
        {'name': 'Light Traffic', 'eb': 15, 'wb': 20, 'crosser': 5, 'poser': 8},
        {'name': 'Moderate Traffic', 'eb': 30, 'wb': 40, 'crosser': 10, 'poser': 15},
        {'name': 'Heavy Traffic', 'eb': 50, 'wb': 70, 'crosser': 15, 'poser': 25}
    ]

    for scenario in test_scenarios:
        X_test = np.array([[scenario['eb'], scenario['wb'], scenario['crosser'], scenario['poser']]])

        print(f"\n{scenario['name']}:")
        print(f"  Arrivals (5 min): EB={scenario['eb']}, WB={scenario['wb']}, "
              f"Crosser={scenario['crosser']}, Poser={scenario['poser']}")
        print(f"  Recommended capacity:")

        for entity in entity_types:
            capacity = int(np.round(models[entity].predict(X_test)[0]))
            print(f"    {entity.upper()}: {capacity} servers")

    return {
        'models': models,
        'training_data': training_df
    }


# ===========================
# MAIN EXECUTION
# ===========================

def main():
    print("="*70)
    print("LEARNING ALGORITHMS FOR TRAFFIC ANALYSIS")
    print("="*70)
    print("\nUsing machine learning to learn from October 20 dataset")
    print("and make predictions/optimizations for future traffic patterns.\n")

    # Load data
    try:
        df = pd.read_csv('combined_results.csv')
    except FileNotFoundError:
        df = pd.read_csv('all_sessions_combined.csv')

    # Standardize column names
    column_mapping = {
        'Time (s)': 'Arrival_Time',
        'Entity': 'Entity_Type',
        'Inter-Arrival (s)': 'Inter_Arrival_Time',
        'Service Time (s)': 'Service_Time'
    }

    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})

    print(f"Dataset loaded: {len(df)} entities")
    print(f"Entity types: {df['Entity_Type'].unique()}")
    print(f"Duration: {df['Arrival_Time'].max()/60:.1f} minutes")

    # 1. Learn arrival patterns
    results = {}
    for entity in df['Entity_Type'].unique():
        results[f'{entity}_patterns'] = learn_arrival_patterns(df, entity, time_window_minutes=5)

    # 2. Classify traffic states
    results['traffic_states'] = classify_traffic_states(df, n_states=3)

    # 3. Learn optimal capacity
    for entity in df['Entity_Type'].unique():
        results[f'{entity}_capacity'] = learn_optimal_capacity(df, entity, target_wait_time=5.0)

    # 4. Predict next arrivals
    for entity in df['Entity_Type'].unique():
        results[f'{entity}_prediction'] = predict_next_arrival(df, entity, lookback=5)

    # 5. Adaptive resource allocation
    results['adaptive_allocation'] = adaptive_resource_learning(df)

    # Summary
    print(f"\n{'='*70}")
    print("LEARNING ALGORITHM SUMMARY")
    print('='*70)
    print("\n✓ Completed 5 learning algorithm analyses:")
    print("  1. Time-based arrival pattern learning")
    print("  2. Traffic state classification (clustering)")
    print("  3. Optimal capacity learning")
    print("  4. Next arrival prediction")
    print("  5. Adaptive resource allocation")

    print("\n📊 Results saved in memory (use Python to access)")
    print("📈 Ready for integration with SIMUL8 simulation")

    print(f"\n{'='*70}")
    print("NEXT STEPS FOR SIMUL8 INTEGRATION:")
    print('='*70)
    print("\n1. Use learned patterns to set arrival distributions")
    print("2. Implement adaptive capacity based on traffic states")
    print("3. Use predictions for proactive resource allocation")
    print("4. Test different scenarios using learned rules")
    print("5. Validate with weekend data when available")

    return results

if __name__ == "__main__":
    results = main()
