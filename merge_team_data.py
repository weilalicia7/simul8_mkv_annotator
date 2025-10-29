"""
Team Data Merger for Collaborative Data Collection
Merges 4 CSV files (WB Vehicles, EB Vehicles, Crossers, Posers) into one combined file for SIMUL8
"""

import pandas as pd
import sys
import os

def validate_csv(df, filename, expected_entity):
    """Validate CSV file format and content"""
    required_columns = ['ID', 'Time (s)', 'Entity', 'Type/Dir', 'Inter-Arrival (s)', 'Service Time (s)']

    # Check columns
    if not all(col in df.columns for col in required_columns):
        print(f"ERROR: {filename} missing required columns")
        print(f"Expected: {required_columns}")
        print(f"Found: {list(df.columns)}")
        return False

    # Check not empty
    if len(df) == 0:
        print(f"WARNING: {filename} is empty")
        return True  # Allow empty files

    # Check entity types
    entities = df['Entity'].unique()
    print(f"  {filename}: {len(df)} entries, Entity types: {list(entities)}")

    return True

def recalculate_inter_arrival(df):
    """Recalculate inter-arrival times for each entity type"""
    df = df.sort_values('Time (s)').reset_index(drop=True)

    # Track last arrival time for each entity type
    last_time = {}
    inter_arrivals = []

    for idx, row in df.iterrows():
        entity = row['Entity']
        time = row['Time (s)']

        if entity not in last_time:
            # First arrival of this entity type
            inter_arrivals.append(0.0)
            last_time[entity] = time
        else:
            # Calculate inter-arrival time
            inter_arrival = time - last_time[entity]
            inter_arrivals.append(round(inter_arrival, 1))
            last_time[entity] = time

    df['Inter-Arrival (s)'] = inter_arrivals
    return df

def merge_team_data(wb_file, eb_file, crossers_file, posers_file, output_file='combined_results.csv'):
    """
    Merge 4 CSV files from team data collection

    Parameters:
    - wb_file: Westbound vehicles CSV
    - eb_file: Eastbound vehicles CSV
    - crossers_file: Crossers (pedestrians who just cross) CSV
    - posers_file: Posers (pedestrians who stop for photos) CSV
    - output_file: Combined output CSV
    """

    print("="*70)
    print("Team Data Merger - Collaborative Data Collection")
    print("="*70)

    # Check files exist
    for filename in [wb_file, eb_file, crossers_file, posers_file]:
        if not os.path.exists(filename):
            print(f"ERROR: File not found: {filename}")
            return False

    print("\n[Step 1/5] Loading CSV files...")

    try:
        df_wb = pd.read_csv(wb_file)
        df_eb = pd.read_csv(eb_file)
        df_crossers = pd.read_csv(crossers_file)
        df_posers = pd.read_csv(posers_file)
    except Exception as e:
        print(f"ERROR: Failed to load CSV files: {e}")
        return False

    print("\n[Step 2/5] Validating data...")

    if not validate_csv(df_wb, wb_file, "WB Vehicles"):
        return False
    if not validate_csv(df_eb, eb_file, "EB Vehicles"):
        return False
    if not validate_csv(df_crossers, crossers_file, "Crossers"):
        return False
    if not validate_csv(df_posers, posers_file, "Posers"):
        return False

    print("\n[Step 3/5] Combining data...")

    # Combine all dataframes
    combined = pd.concat([df_wb, df_eb, df_crossers, df_posers], ignore_index=True)

    # Sort by time
    combined = combined.sort_values('Time (s)').reset_index(drop=True)

    print(f"  Total entries: {len(combined)}")

    if len(combined) == 0:
        print("ERROR: No data to merge (all files empty)")
        return False

    print("\n[Step 4/5] Recalculating inter-arrival times...")

    # Recalculate inter-arrival times (since we combined from multiple sources)
    combined = recalculate_inter_arrival(combined)

    # Renumber IDs sequentially
    combined['ID'] = range(1, len(combined) + 1)

    print("\n[Step 5/5] Saving combined file...")

    try:
        combined.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file}")
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")
        return False

    print("\n" + "="*70)
    print("SUCCESS: Files merged successfully!")
    print("="*70)

    # Summary statistics
    print("\nSummary Statistics:")
    print(f"  Total arrivals: {len(combined)}")

    for entity in combined['Entity'].unique():
        count = len(combined[combined['Entity'] == entity])
        print(f"  {entity}: {count}")

    print(f"\nTime range:")
    print(f"  Earliest: {combined['Time (s)'].min():.1f}s")
    print(f"  Latest: {combined['Time (s)'].max():.1f}s")
    print(f"  Duration: {combined['Time (s)'].max() - combined['Time (s)'].min():.1f}s")

    print(f"\nOutput file: {output_file}")
    print("Ready for SIMUL8 import!")

    return True

def main():
    """Main function"""

    if len(sys.argv) != 5:
        print("Usage: python merge_team_data.py <wb_file> <eb_file> <crossers_file> <posers_file>")
        print("\nExample:")
        print("  python merge_team_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv")
        print("\nThis will create: combined_results.csv")
        sys.exit(1)

    wb_file = sys.argv[1]
    eb_file = sys.argv[2]
    crossers_file = sys.argv[3]
    posers_file = sys.argv[4]

    success = merge_team_data(wb_file, eb_file, crossers_file, posers_file)

    if not success:
        print("\n[FAILED] Merge process encountered errors")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
