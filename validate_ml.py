"""
ML Validation Tool
Compares ML detection results with manual annotations
Generates accuracy reports and visualizations
"""

import pandas as pd
import numpy as np
import argparse
import sys
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns


class MLValidator:
    """Validates ML detection results against manual annotations"""

    def __init__(self, manual_csv, ml_csv, time_tolerance=1.0):
        """
        Initialize validator

        Args:
            manual_csv: Path to manual annotation CSV
            ml_csv: Path to ML detection CSV
            time_tolerance: Time tolerance in seconds for matching (default: 1.0s)
        """
        self.time_tolerance = time_tolerance

        # Load data
        print("Loading data files...")
        self.manual = pd.read_csv(manual_csv)
        self.ml = pd.read_csv(ml_csv)

        print(f"  Manual annotations: {len(self.manual)} entries")
        print(f"  ML detections: {len(self.ml)} entries")
        print(f"  Time tolerance: ±{time_tolerance}s\n")

    def compare_counts(self):
        """Compare total counts by entity type"""
        print("="*70)
        print("COUNT COMPARISON")
        print("="*70)

        # Overall counts
        print(f"\nOverall:")
        print(f"  Manual:     {len(self.manual):4d}")
        print(f"  ML:         {len(self.ml):4d}")
        print(f"  Difference: {abs(len(self.manual) - len(self.ml)):4d}")

        # By entity type
        print(f"\nBy Entity Type:")
        print(f"{'Entity':<20s} {'Manual':<10s} {'ML':<10s} {'Diff':<10s} {'ML/Manual':<10s}")
        print("-" * 70)

        manual_counts = self.manual['Entity'].value_counts()
        ml_counts = self.ml['Entity'].value_counts()

        all_entities = set(manual_counts.index) | set(ml_counts.index)

        for entity in sorted(all_entities):
            manual_count = manual_counts.get(entity, 0)
            ml_count = ml_counts.get(entity, 0)
            diff = ml_count - manual_count

            if manual_count > 0:
                ratio = (ml_count / manual_count) * 100
                ratio_str = f"{ratio:.1f}%"
            else:
                ratio_str = "N/A"

            print(f"{entity:<20s} {manual_count:<10d} {ml_count:<10d} "
                  f"{diff:+10d} {ratio_str:<10s}")

        print("="*70)

    def calculate_precision_recall(self):
        """Calculate precision and recall for temporal matching"""
        print("\n" + "="*70)
        print("TEMPORAL PRECISION & RECALL")
        print("="*70)
        print(f"Matching criterion: Events within ±{self.time_tolerance}s of same entity type")
        print()

        results = {}

        for entity in self.manual['Entity'].unique():
            manual_entity = self.manual[self.manual['Entity'] == entity]
            ml_entity = self.ml[self.ml['Entity'] == entity]

            # Calculate matches
            matched_manual = 0
            matched_ml = 0
            matched_pairs = []

            # For each manual entry, find ML match
            for _, manual_row in manual_entity.iterrows():
                manual_time = manual_row['Time (s)']

                # Find ML detections within tolerance
                matches = ml_entity[
                    abs(ml_entity['Time (s)'] - manual_time) <= self.time_tolerance
                ]

                if len(matches) > 0:
                    matched_manual += 1
                    # Take closest match
                    closest_match = matches.iloc[
                        (matches['Time (s)'] - manual_time).abs().argmin()
                    ]
                    matched_pairs.append((manual_time, closest_match['Time (s)']))

            # For each ML entry, check if it has a manual match
            for _, ml_row in ml_entity.iterrows():
                ml_time = ml_row['Time (s)']

                matches = manual_entity[
                    abs(manual_entity['Time (s)'] - ml_time) <= self.time_tolerance
                ]

                if len(matches) > 0:
                    matched_ml += 1

            # Calculate metrics
            recall = (matched_manual / len(manual_entity) * 100) if len(manual_entity) > 0 else 0
            precision = (matched_ml / len(ml_entity) * 100) if len(ml_entity) > 0 else 0

            if precision + recall > 0:
                f1_score = 2 * (precision * recall) / (precision + recall)
            else:
                f1_score = 0

            results[entity] = {
                'manual_count': len(manual_entity),
                'ml_count': len(ml_entity),
                'matched_manual': matched_manual,
                'matched_ml': matched_ml,
                'recall': recall,
                'precision': precision,
                'f1_score': f1_score,
                'matched_pairs': matched_pairs
            }

        # Print results
        print(f"{'Entity':<20s} {'Recall':<12s} {'Precision':<12s} {'F1 Score':<12s}")
        print("-" * 70)

        for entity, metrics in results.items():
            print(f"{entity:<20s} {metrics['recall']:>10.1f}%  {metrics['precision']:>10.1f}%  "
                  f"{metrics['f1_score']:>10.1f}%")

        # Overall metrics
        total_manual = len(self.manual)
        total_ml = len(self.ml)
        total_matched_manual = sum(m['matched_manual'] for m in results.values())
        total_matched_ml = sum(m['matched_ml'] for m in results.values())

        overall_recall = (total_matched_manual / total_manual * 100) if total_manual > 0 else 0
        overall_precision = (total_matched_ml / total_ml * 100) if total_ml > 0 else 0

        if overall_precision + overall_recall > 0:
            overall_f1 = 2 * (overall_precision * overall_recall) / (overall_precision + overall_recall)
        else:
            overall_f1 = 0

        print("-" * 70)
        print(f"{'OVERALL':<20s} {overall_recall:>10.1f}%  {overall_precision:>10.1f}%  "
              f"{overall_f1:>10.1f}%")

        print("\nMetrics Explained:")
        print(f"  Recall:    {total_matched_manual}/{total_manual} manual events detected by ML")
        print(f"  Precision: {total_matched_ml}/{total_ml} ML detections match manual events")
        print(f"  F1 Score:  Harmonic mean of precision and recall")

        print("="*70)

        return results

    def analyze_timing_errors(self):
        """Analyze timing differences between matched events"""
        print("\n" + "="*70)
        print("TIMING ERROR ANALYSIS")
        print("="*70)

        all_errors = []

        for entity in self.manual['Entity'].unique():
            manual_entity = self.manual[self.manual['Entity'] == entity]
            ml_entity = self.ml[self.ml['Entity'] == entity]

            entity_errors = []

            for _, manual_row in manual_entity.iterrows():
                manual_time = manual_row['Time (s)']

                # Find closest ML match
                matches = ml_entity[
                    abs(ml_entity['Time (s)'] - manual_time) <= self.time_tolerance
                ]

                if len(matches) > 0:
                    closest_match = matches.iloc[
                        (matches['Time (s)'] - manual_time).abs().argmin()
                    ]
                    error = closest_match['Time (s)'] - manual_time
                    entity_errors.append(error)
                    all_errors.append(error)

            if entity_errors:
                mean_error = np.mean(entity_errors)
                std_error = np.std(entity_errors)
                abs_mean_error = np.mean(np.abs(entity_errors))

                print(f"\n{entity}:")
                print(f"  Mean error:          {mean_error:+.3f}s")
                print(f"  Std deviation:       {std_error:.3f}s")
                print(f"  Mean absolute error: {abs_mean_error:.3f}s")
                print(f"  Samples:             {len(entity_errors)}")

        if all_errors:
            print(f"\nOverall:")
            print(f"  Mean error:          {np.mean(all_errors):+.3f}s")
            print(f"  Std deviation:       {np.std(all_errors):.3f}s")
            print(f"  Mean absolute error: {np.mean(np.abs(all_errors)):.3f}s")
            print(f"  Samples:             {len(all_errors)}")

        print("="*70)

        return all_errors

    def find_missing_detections(self):
        """Find manual annotations that ML missed"""
        print("\n" + "="*70)
        print("MISSING DETECTIONS (Manual events not detected by ML)")
        print("="*70)

        missing = []

        for entity in self.manual['Entity'].unique():
            manual_entity = self.manual[self.manual['Entity'] == entity]
            ml_entity = self.ml[self.ml['Entity'] == entity]

            for _, manual_row in manual_entity.iterrows():
                manual_time = manual_row['Time (s)']

                # Check if ML detected this
                matches = ml_entity[
                    abs(ml_entity['Time (s)'] - manual_time) <= self.time_tolerance
                ]

                if len(matches) == 0:
                    missing.append({
                        'Entity': entity,
                        'Time (s)': manual_time,
                        'ID': manual_row['ID']
                    })

        if missing:
            print(f"\nFound {len(missing)} missing detections:\n")
            missing_df = pd.DataFrame(missing)
            print(missing_df.to_string(index=False))
        else:
            print("\n✓ No missing detections! All manual events were detected by ML.")

        print("="*70)

        return missing

    def find_false_positives(self):
        """Find ML detections that don't match manual annotations"""
        print("\n" + "="*70)
        print("FALSE POSITIVES (ML detections with no manual match)")
        print("="*70)

        false_positives = []

        for entity in self.ml['Entity'].unique():
            ml_entity = self.ml[self.ml['Entity'] == entity]
            manual_entity = self.manual[self.manual['Entity'] == entity]

            for _, ml_row in ml_entity.iterrows():
                ml_time = ml_row['Time (s)']

                # Check if manual has this
                matches = manual_entity[
                    abs(manual_entity['Time (s)'] - ml_time) <= self.time_tolerance
                ]

                if len(matches) == 0:
                    false_positives.append({
                        'Entity': entity,
                        'Time (s)': ml_time,
                        'ID': ml_row['ID']
                    })

        if false_positives:
            print(f"\nFound {len(false_positives)} false positives:\n")
            fp_df = pd.DataFrame(false_positives)
            print(fp_df.to_string(index=False))
        else:
            print("\n✓ No false positives! All ML detections match manual events.")

        print("="*70)

        return false_positives

    def generate_report(self, output_path=None):
        """Generate complete validation report"""
        print("\n" + "="*70)
        print("ML VALIDATION REPORT")
        print("="*70)
        print(f"Manual annotations: {self.manual.iloc[0, 0] if len(self.manual) > 0 else 'N/A'}")
        print(f"ML detections file: {self.ml.iloc[0, 0] if len(self.ml) > 0 else 'N/A'}")
        print(f"Time tolerance: ±{self.time_tolerance}s")
        print("="*70)

        # Run all analyses
        self.compare_counts()
        metrics = self.calculate_precision_recall()
        timing_errors = self.analyze_timing_errors()
        missing = self.find_missing_detections()
        false_positives = self.find_false_positives()

        # Summary
        print("\n" + "="*70)
        print("SUMMARY")
        print("="*70)

        total_manual = len(self.manual)
        total_ml = len(self.ml)
        total_matched = sum(m['matched_manual'] for m in metrics.values())

        print(f"\nDetection Performance:")
        print(f"  Manual events:      {total_manual}")
        print(f"  ML detections:      {total_ml}")
        print(f"  Correctly matched:  {total_matched}")
        print(f"  Missing detections: {len(missing)}")
        print(f"  False positives:    {len(false_positives)}")

        if timing_errors:
            print(f"\nTiming Accuracy:")
            print(f"  Mean absolute error: {np.mean(np.abs(timing_errors)):.3f}s")

        print("\n" + "="*70)

        # Save to file if requested
        if output_path:
            with open(output_path, 'w') as f:
                f.write("ML VALIDATION REPORT\n")
                f.write("="*70 + "\n\n")
                f.write(f"Total Manual Events: {total_manual}\n")
                f.write(f"Total ML Detections: {total_ml}\n")
                f.write(f"Correctly Matched: {total_matched}\n")
                f.write(f"Missing Detections: {len(missing)}\n")
                f.write(f"False Positives: {len(false_positives)}\n\n")

                if timing_errors:
                    f.write(f"Mean Absolute Timing Error: {np.mean(np.abs(timing_errors)):.3f}s\n")

            print(f"\n✓ Report saved to: {output_path}")


def main():
    """Main function with CLI"""
    parser = argparse.ArgumentParser(
        description='ML Validation Tool - Compare ML detections with manual annotations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic comparison
  python validate_ml.py manual.csv ml_results.csv

  # Adjust time tolerance
  python validate_ml.py manual.csv ml_results.csv --tolerance 2.0

  # Save report to file
  python validate_ml.py manual.csv ml_results.csv --output report.txt
        """
    )

    parser.add_argument('manual_csv', type=str, help='Path to manual annotation CSV')
    parser.add_argument('ml_csv', type=str, help='Path to ML detection CSV')
    parser.add_argument('--tolerance', '-t', type=float, default=1.0,
                       help='Time tolerance in seconds for matching (default: 1.0)')
    parser.add_argument('--output', '-o', type=str, default=None,
                       help='Output file path for report')

    args = parser.parse_args()

    # Validate files
    manual_path = Path(args.manual_csv)
    ml_path = Path(args.ml_csv)

    if not manual_path.exists():
        print(f"Error: Manual annotation file not found: {manual_path}")
        sys.exit(1)

    if not ml_path.exists():
        print(f"Error: ML detection file not found: {ml_path}")
        sys.exit(1)

    try:
        # Run validation
        validator = MLValidator(manual_path, ml_path, time_tolerance=args.tolerance)
        validator.generate_report(output_path=args.output)

    except Exception as e:
        print(f"\nError during validation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
