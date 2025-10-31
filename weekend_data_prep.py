"""
Weekend Data Preparation Script
================================
Prepares and analyzes 2.5-hour weekend session data when available.

This script will:
1. Load weekend session data (2.5 hours)
2. Combine all 4 entity types
3. Calculate statistics
4. Compare with the existing 90-minute session
5. Generate combined multi-session analysis

Usage:
    python weekend_data_prep.py <eb_file> <wb_file> <crossers_file> <posers_file>

Example:
    python weekend_data_prep.py "weekend_eb.csv" "weekend_wb.csv" "weekend_crossers.csv" "weekend_posers.csv"
"""

import pandas as pd
import sys
import os

def load_and_standardize(filepath, entity_type):
    """Load a CSV/Excel file and standardize column names"""
    print(f"\nLoading {os.path.basename(filepath)}...")

    # Try reading as CSV first, then Excel if that fails
    try:
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith('.xlsx') or filepath.endswith('.xls'):
            df = pd.read_excel(filepath)
        else:
            df = pd.read_csv(filepath)  # Try CSV as default
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None

    # Standardize column names
    column_mapping = {
        'Time (s)': 'Arrival_Time',
        'Entity': 'Entity_Type',
        'Type/Dir': 'Direction',
        'Inter-Arrival (s)': 'Inter_Arrival_Time',
        'Service Time (s)': 'Service_Time'
    }

    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            df = df.rename(columns={old_col: new_col})

    # Ensure Entity_Type is set
    if 'Entity_Type' not in df.columns:
        df['Entity_Type'] = entity_type

    print(f"  ✓ Loaded {len(df)} entities")
    print(f"  Duration: {df['Arrival_Time'].max():.1f}s ({df['Arrival_Time'].max()/60:.1f} min)")

    return df

def analyze_session(df, session_name):
    """Analyze a single session"""
    print(f"\n{'='*70}")
    print(f"Analysis: {session_name}")
    print('='*70)

    # Duration
    duration_sec = df['Arrival_Time'].max()
    duration_hours = duration_sec / 3600
    print(f"\nDuration: {duration_sec:.1f}s ({duration_sec/60:.1f} min = {duration_hours:.2f} hours)")

    # Entity counts
    print("\nEntity Breakdown:")
    entity_counts = df.groupby('Entity_Type').size().sort_values(ascending=False)
    for entity, count in entity_counts.items():
        pct = (count / len(df)) * 100
        print(f"  {entity}: {count} ({pct:.1f}%)")
    print(f"  Total: {len(df)}")

    # Throughput
    throughput_per_hour = len(df) / duration_hours
    print(f"\nThroughput: {throughput_per_hour:.1f} entities/hour")

    # Inter-arrival statistics by entity
    print("\nMean Inter-Arrival Times:")
    for entity in df['Entity_Type'].unique():
        entity_df = df[df['Entity_Type'] == entity]
        if 'Inter_Arrival_Time' in entity_df.columns:
            mean_iat = entity_df['Inter_Arrival_Time'].replace('-', 0).astype(float).mean()
            print(f"  {entity}: {mean_iat:.2f}s")

    return {
        'duration_hours': duration_hours,
        'total_entities': len(df),
        'throughput': throughput_per_hour,
        'entity_counts': entity_counts.to_dict()
    }

def compare_sessions(session1_stats, session2_stats, name1, name2):
    """Compare two sessions"""
    print(f"\n{'='*70}")
    print(f"Comparison: {name1} vs {name2}")
    print('='*70)

    print(f"\nDuration:")
    print(f"  {name1}: {session1_stats['duration_hours']:.2f} hours")
    print(f"  {name2}: {session2_stats['duration_hours']:.2f} hours")
    print(f"  Difference: {abs(session1_stats['duration_hours'] - session2_stats['duration_hours']):.2f} hours")

    print(f"\nThroughput:")
    print(f"  {name1}: {session1_stats['throughput']:.1f} entities/hour")
    print(f"  {name2}: {session2_stats['throughput']:.1f} entities/hour")
    throughput_diff = ((session2_stats['throughput'] - session1_stats['throughput']) / session1_stats['throughput']) * 100
    print(f"  Difference: {throughput_diff:+.1f}%")

    print(f"\nEntity Counts:")
    all_entities = set(list(session1_stats['entity_counts'].keys()) + list(session2_stats['entity_counts'].keys()))
    for entity in sorted(all_entities):
        count1 = session1_stats['entity_counts'].get(entity, 0)
        count2 = session2_stats['entity_counts'].get(entity, 0)
        rate1 = count1 / session1_stats['duration_hours']
        rate2 = count2 / session2_stats['duration_hours']
        print(f"  {entity}:")
        print(f"    {name1}: {count1} ({rate1:.1f}/hour)")
        print(f"    {name2}: {count2} ({rate2:.1f}/hour)")
        if rate1 > 0:
            rate_diff = ((rate2 - rate1) / rate1) * 100
            print(f"    Difference: {rate_diff:+.1f}%")

def main():
    if len(sys.argv) < 5:
        print("Usage: python weekend_data_prep.py <eb_file> <wb_file> <crossers_file> <posers_file>")
        print("\nExample:")
        print('  python weekend_data_prep.py "weekend_eb.csv" "weekend_wb.csv" "weekend_crossers.csv" "weekend_posers.csv"')
        return

    eb_file = sys.argv[1]
    wb_file = sys.argv[2]
    crossers_file = sys.argv[3]
    posers_file = sys.argv[4]

    print("Weekend Data Preparation")
    print("="*70)

    # Load weekend data
    print("\nLoading weekend session data...")
    df_eb = load_and_standardize(eb_file, "EB Vehicles")
    df_wb = load_and_standardize(wb_file, "WB Vehicles")
    df_crossers = load_and_standardize(crossers_file, "Crossers")
    df_posers = load_and_standardize(posers_file, "Posers")

    if any(df is None for df in [df_eb, df_wb, df_crossers, df_posers]):
        print("\n❌ Error: Could not load all files")
        return

    # Combine weekend data
    print("\nCombining weekend session data...")
    weekend_df = pd.concat([df_eb, df_wb, df_crossers, df_posers], ignore_index=True)
    weekend_df = weekend_df.sort_values('Arrival_Time').reset_index(drop=True)
    weekend_df['ID'] = range(1, len(weekend_df) + 1)

    # Save combined weekend data
    output_file = 'weekend_combined.csv'
    weekend_df.to_csv(output_file, index=False, encoding='utf-8')
    print(f"✓ Saved combined weekend data to {output_file}")

    # Analyze weekend session
    weekend_stats = analyze_session(weekend_df, "Weekend Session (2.5 hours)")

    # Load and analyze existing 90-minute session
    print("\n" + "="*70)
    print("Loading existing 90-minute session for comparison...")
    print("="*70)

    try:
        existing_df = pd.read_csv('combined_results.csv')
        # Standardize column names
        column_mapping = {
            'Time (s)': 'Arrival_Time',
            'Entity': 'Entity_Type',
            'Inter-Arrival (s)': 'Inter_Arrival_Time',
            'Service Time (s)': 'Service_Time'
        }
        for old_col, new_col in column_mapping.items():
            if old_col in existing_df.columns:
                existing_df = existing_df.rename(columns={old_col: new_col})

        existing_stats = analyze_session(existing_df, "Existing Session (90 minutes)")

        # Compare sessions
        compare_sessions(existing_stats, weekend_stats, "90-min Session", "Weekend Session")

        # Create multi-session combined file
        print(f"\n{'='*70}")
        print("Creating multi-session combined dataset...")
        print('='*70)

        # Add session identifier
        existing_df['Session'] = 'Session 1 (90 min)'
        weekend_df['Session'] = 'Session 2 (Weekend 2.5hr)'

        # Combine both sessions
        multi_session_df = pd.concat([existing_df, weekend_df], ignore_index=True)
        multi_session_df.to_csv('multi_session_combined.csv', index=False, encoding='utf-8')
        print(f"✓ Saved multi-session data to multi_session_combined.csv")
        print(f"  Total entities: {len(multi_session_df)}")
        print(f"  Sessions: 2")

    except FileNotFoundError:
        print("\nNote: Could not find existing 90-minute session data for comparison")
        print("      (File 'combined_results.csv' not found)")

    print(f"\n{'='*70}")
    print("✓ Weekend data preparation complete!")
    print('='*70)
    print(f"\nOutput files created:")
    print(f"  1. {output_file} - Weekend session only")
    print(f"  2. multi_session_combined.csv - Both sessions combined")
    print(f"\nNext steps:")
    print(f"  1. Run traffic analysis: python traffic_analyzer.py {output_file}")
    print(f"  2. Run variability analysis: python variability_analyzer.py {output_file}")
    print(f"  3. Run queueing analysis: python queueing_calculator.py {output_file}")
    print(f"  4. Run resource planner: python resource_planner.py {output_file}")
    print(f"\nFor multi-session analysis, use: multi_session_combined.csv")

if __name__ == "__main__":
    main()
