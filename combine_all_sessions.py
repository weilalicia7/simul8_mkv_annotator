"""
Final Session Combiner
Combines all 8 session files into one master file for SIMUL8
"""

import pandas as pd
import os

def combine_all_sessions(session_files, output_file='all_sessions_combined.csv'):
    """
    Combine all session CSV files into one master file

    Parameters:
    - session_files: List of session CSV file paths
    - output_file: Final combined output CSV
    """

    print("="*70)
    print("Final Session Combiner - All Observation Windows")
    print("="*70)

    all_sessions = []

    print("\n[Step 1/3] Loading all session files...")

    for session_file in session_files:
        if not os.path.exists(session_file):
            print(f"WARNING: File not found: {session_file}")
            continue

        df = pd.read_csv(session_file)
        all_sessions.append(df)
        session_id = df['Session_ID'].iloc[0] if 'Session_ID' in df.columns else 'Unknown'
        period = df['Period_Type'].iloc[0] if 'Period_Type' in df.columns else 'Unknown'
        day = df['Day_of_Week'].iloc[0] if 'Day_of_Week' in df.columns else 'Unknown'
        print(f"  ✓ Loaded: {session_file} (Session {session_id}: {period} - {day}, {len(df)} entries)")

    if not all_sessions:
        print("ERROR: No valid session files found")
        return False

    print(f"\n[Step 2/3] Combining {len(all_sessions)} sessions...")

    # Combine all sessions
    combined = pd.concat(all_sessions, ignore_index=True)

    # Sort by Session_ID and Time
    if 'Session_ID' in combined.columns:
        combined = combined.sort_values(['Session_ID', 'Time (s)']).reset_index(drop=True)
    else:
        combined = combined.sort_values('Time (s)').reset_index(drop=True)

    # Renumber global IDs
    combined['ID'] = range(1, len(combined) + 1)

    print(f"  Total entries across all sessions: {len(combined)}")

    print("\n[Step 3/3] Saving final combined file...")

    try:
        combined.to_csv(output_file, index=False)
        print(f"  Saved to: {output_file}")
    except Exception as e:
        print(f"ERROR: Failed to save file: {e}")
        return False

    print("\n" + "="*70)
    print("SUCCESS: All sessions combined successfully!")
    print("="*70)

    # Summary statistics
    print("\nFinal Statistics:")
    print(f"  Total sessions: {len(all_sessions)}")
    print(f"  Total arrivals: {len(combined)}")

    # Statistics by session
    if 'Session_ID' in combined.columns:
        print("\nBy Session:")
        for session_id in sorted(combined['Session_ID'].unique()):
            session_data = combined[combined['Session_ID'] == session_id]
            period = session_data['Period_Type'].iloc[0] if 'Period_Type' in session_data.columns else 'Unknown'
            day = session_data['Day_of_Week'].iloc[0] if 'Day_of_Week' in session_data.columns else 'Unknown'
            print(f"  Session {session_id} ({period} - {day}): {len(session_data)} arrivals")

    # Statistics by period type
    if 'Period_Type' in combined.columns:
        print("\nBy Period Type:")
        for period in combined['Period_Type'].unique():
            count = len(combined[combined['Period_Type'] == period])
            print(f"  {period}: {count} arrivals")

    # Statistics by entity type
    print("\nBy Entity Type (All Sessions):")
    for entity in combined['Entity'].unique():
        count = len(combined[combined['Entity'] == entity])
        print(f"  {entity}: {count}")

    print(f"\nOutput file: {output_file}")
    print("Ready for SIMUL8 import!")

    return True

def main():
    """Main function - finds all session files and combines them"""

    print("Searching for session files in current directory...")

    # Find all session_*_combined.csv files
    session_files = []
    for filename in os.listdir('.'):
        if filename.startswith('session_') and filename.endswith('_combined.csv'):
            session_files.append(filename)

    if not session_files:
        print("\nNo session files found. Looking in observation_windows/ subdirectory...")
        if os.path.exists('observation_windows'):
            for root, dirs, files in os.walk('observation_windows'):
                for filename in files:
                    if filename.startswith('session_') and filename.endswith('_combined.csv'):
                        session_files.append(os.path.join(root, filename))

    if not session_files:
        print("\nERROR: No session files found!")
        print("\nExpected file pattern: session_*_combined.csv")
        print("\nPlease ensure you have run merge_session_data.py for each observation window first.")
        return

    # Sort files naturally
    session_files.sort()

    print(f"\nFound {len(session_files)} session files:")
    for f in session_files:
        print(f"  - {f}")

    print("\nProceeding to combine all sessions...\n")

    success = combine_all_sessions(session_files)

    if not success:
        print("\n[FAILED] Combination process encountered errors")
        return

if __name__ == "__main__":
    main()
