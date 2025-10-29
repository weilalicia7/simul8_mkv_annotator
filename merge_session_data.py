"""
Enhanced Session Data Merger
Merges 4 CSV files AND adds session metadata for multi-session studies
"""

import pandas as pd
import sys
import os

def merge_session_data(wb_file, eb_file, crossers_file, posers_file,
                       session_id, period_type, day_of_week,
                       output_file='session_combined.csv'):
    """
    Merge 4 CSV files with session metadata

    Parameters:
    - wb_file: Westbound vehicles CSV
    - eb_file: Eastbound vehicles CSV
    - crossers_file: Crossers CSV
    - posers_file: Posers CSV
    - session_id: Session number (e.g., "01", "02")
    - period_type: "Morning Peak", "Midday Tourist", "Evening Peak", "Weekend"
    - day_of_week: Day name (e.g., "Monday", "Saturday")
    - output_file: Combined output CSV
    """

    print("="*70)
    print(f"Session Data Merger - Session {session_id}")
    print(f"Period: {period_type} | Day: {day_of_week}")
    print("="*70)

    # Check files exist
    for filename in [wb_file, eb_file, crossers_file, posers_file]:
        if not os.path.exists(filename):
            print(f"ERROR: File not found: {filename}")
            return False

    print("\n[Step 1/6] Loading CSV files...")

    try:
        df_wb = pd.read_csv(wb_file)
        df_eb = pd.read_csv(eb_file)
        df_crossers = pd.read_csv(crossers_file)
        df_posers = pd.read_csv(posers_file)
    except Exception as e:
        print(f"ERROR: Failed to load CSV files: {e}")
        return False

    print("\n[Step 2/6] Validating data...")
    print(f"  {wb_file}: {len(df_wb)} entries")
    print(f"  {eb_file}: {len(df_eb)} entries")
    print(f"  {crossers_file}: {len(df_crossers)} entries")
    print(f"  {posers_file}: {len(df_posers)} entries")

    print("\n[Step 3/6] Combining data...")

    # Combine all dataframes
    combined = pd.concat([df_wb, df_eb, df_crossers, df_posers], ignore_index=True)

    # Sort by time
    combined = combined.sort_values('Time (s)').reset_index(drop=True)

    print(f"  Total entries: {len(combined)}")

    if len(combined) == 0:
        print("ERROR: No data to merge (all files empty)")
        return False

    print("\n[Step 4/6] Recalculating inter-arrival times...")

    # Recalculate inter-arrival times for each entity type
    combined = recalculate_inter_arrival(combined)

    # Renumber IDs sequentially
    combined['ID'] = range(1, len(combined) + 1)

    print("\n[Step 5/6] Adding session metadata...")

    # Add session metadata columns
    combined.insert(1, 'Session_ID', session_id)
    combined.insert(2, 'Period_Type', period_type)
    combined.insert(3, 'Day_of_Week', day_of_week)

    print(f"  Session ID: {session_id}")
    print(f"  Period Type: {period_type}")
    print(f"  Day of Week: {day_of_week}")

    print("\n[Step 6/6] Saving combined file...")

    try:
        combined.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file}")
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")
        return False

    print("\n" + "="*70)
    print(f"SUCCESS: Session {session_id} merged successfully!")
    print("="*70)

    # Summary statistics
    print("\nSummary Statistics:")
    print(f"  Session: {session_id} ({period_type} - {day_of_week})")
    print(f"  Total arrivals: {len(combined)}")

    for entity in combined['Entity'].unique():
        count = len(combined[combined['Entity'] == entity])
        print(f"  {entity}: {count}")

    print(f"\nTime range:")
    print(f"  Earliest: {combined['Time (s)'].min():.1f}s")
    print(f"  Latest: {combined['Time (s)'].max():.1f}s")
    print(f"  Duration: {combined['Time (s)'].max() - combined['Time (s)'].min():.1f}s")

    print(f"\nOutput file: {output_file}")

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

def main():
    """Main function"""

    if len(sys.argv) != 8:
        print("Usage: python merge_session_data.py <wb_file> <eb_file> <crossers_file> <posers_file> <session_id> <period_type> <day_of_week>")
        print("\nExample:")
        print("  python merge_session_data.py wb_vehicles.csv eb_vehicles.csv crossers.csv posers.csv 01 \"Morning Peak\" Monday")
        print("\nPeriod Types:")
        print("  - Morning Peak")
        print("  - Midday Tourist")
        print("  - Evening Peak")
        print("  - Weekend")
        sys.exit(1)

    wb_file = sys.argv[1]
    eb_file = sys.argv[2]
    crossers_file = sys.argv[3]
    posers_file = sys.argv[4]
    session_id = sys.argv[5]
    period_type = sys.argv[6]
    day_of_week = sys.argv[7]

    # Create output filename
    output_file = f"session_{session_id}_combined.csv"

    success = merge_session_data(wb_file, eb_file, crossers_file, posers_file,
                                  session_id, period_type, day_of_week, output_file)

    if not success:
        print("\n[FAILED] Merge process encountered errors")
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
