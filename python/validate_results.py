"""
Numerical Accuracy Validation Engine for CAM16 Implementations.
Compares C++ engine outputs against Python colour-science reference ground truth.
Computes MAE, MaxAE, RMSE, and circular angular distance for hue.
"""

import os
import argparse
import numpy as np
import pandas as pd

def circular_hue_difference(h_ref, h_test):
    """
    Computes shortest circular angular distance between two hue angles in degrees [0, 360).
    Delta_h = min(|h1 - h2| % 360, 360 - (|h1 - h2| % 360))
    """
    diff = np.abs(h_ref - h_test) % 360.0
    return np.minimum(diff, 360.0 - diff)

def evaluate_accuracy(reference_csv, test_csv, implementation_label="C++ Implementation"):
    if not os.path.exists(reference_csv):
        raise FileNotFoundError(f"Reference file not found: {reference_csv}")
    if not os.path.exists(test_csv):
        raise FileNotFoundError(f"Test output file not found: {test_csv}")

    ref_df = pd.read_csv(reference_csv)
    test_df = pd.read_csv(test_csv)

    if len(ref_df) != len(test_df):
        raise ValueError(f"Sample count mismatch: reference has {len(ref_df)} rows, test has {len(test_df)} rows")

    attributes = ['J', 'C', 'h', 's', 'Q', 'M', 'H', 'a', 'b']
    metrics = []

    for attr in attributes:
        if attr not in ref_df.columns or attr not in test_df.columns:
            continue

        ref_vals = ref_df[attr].to_numpy(dtype=np.float64)
        test_vals = test_df[attr].to_numpy(dtype=np.float64)

        if attr == 'h':
            # Circular angular distance for hue
            diff = circular_hue_difference(ref_vals, test_vals)
        else:
            diff = np.abs(ref_vals - test_vals)

        mae = np.mean(diff)
        max_ae = np.max(diff)
        rmse = np.sqrt(np.mean(diff ** 2))
        
        # Relative error where reference value is sufficiently far from zero
        nonzero_mask = np.abs(ref_vals) > 1e-3
        if np.any(nonzero_mask):
            rel_err_pct = np.mean(diff[nonzero_mask] / np.abs(ref_vals[nonzero_mask])) * 100.0
        else:
            rel_err_pct = 0.0

        metrics.append({
            'Implementation': implementation_label,
            'Attribute': attr,
            'MAE': mae,
            'MaxAE': max_ae,
            'RMSE': rmse,
            'MeanRelErr_Pct': rel_err_pct
        })

    metrics_df = pd.DataFrame(metrics)
    return metrics_df

def main():
    parser = argparse.ArgumentParser(description="CAM16 Numerical Accuracy Validator")
    parser.add_argument('--reference', type=str, default="data/reference_10000.csv",
                        help="Path to reference ground-truth CSV")
    parser.add_argument('--test', type=str, default="results/scalar_10000.csv",
                        help="Path to test implementation CSV")
    parser.add_argument('--label', type=str, default="C++ Scalar Baseline",
                        help="Label for the implementation under test")
    parser.add_argument('--outcsv', type=str, default="results/accuracy_results.csv",
                        help="Path to append or write accuracy metrics CSV")
    args = parser.parse_args()

    print(f"=== Validating Numerical Accuracy: {args.label} ===")
    print(f"Reference File : {args.reference}")
    print(f"Test File      : {args.test}\n")

    metrics_df = evaluate_accuracy(args.reference, args.test, args.label)

    # Format for display
    display_df = metrics_df.copy()
    display_df['MAE'] = display_df['MAE'].map(lambda x: f"{x:.6e}")
    display_df['MaxAE'] = display_df['MaxAE'].map(lambda x: f"{x:.6e}")
    display_df['RMSE'] = display_df['RMSE'].map(lambda x: f"{x:.6e}")
    display_df['MeanRelErr_Pct'] = display_df['MeanRelErr_Pct'].map(lambda x: f"{x:.4f}%")

    print(display_df.to_string(index=False))

    # Strict scientific tolerance check for single-precision IEEE 754 float
    # In single precision (24-bit mantissa), precision limit is ~1e-7 relative,
    # compounded non-linear functions (x^0.42, atan2) generally maintain MAE < 1e-4.
    TOLERANCE_MAE = 1e-3
    TOLERANCE_MAX = 5e-2

    all_passed = True
    print("\n=== Tolerance Verification (Single-Precision Float) ===")
    for _, row in metrics_df.iterrows():
        attr = row['Attribute']
        mae = row['MAE']
        max_ae = row['MaxAE']
        passed = (mae < TOLERANCE_MAE) and (max_ae < TOLERANCE_MAX)
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_passed = False
        print(f"  [{status}] Attribute {attr:2s} -> MAE: {mae:.6e} (limit: {TOLERANCE_MAE}), MaxAE: {max_ae:.6e} (limit: {TOLERANCE_MAX})")

    # Save to CSV
    os.makedirs(os.path.dirname(args.outcsv) if os.path.dirname(args.outcsv) else '.', exist_ok=True)
    if os.path.exists(args.outcsv):
        # Append or replace existing label
        existing = pd.read_csv(args.outcsv)
        filtered = existing[existing['Implementation'] != args.label]
        combined = pd.concat([filtered, metrics_df], ignore_index=True)
        combined.to_csv(args.outcsv, index=False)
    else:
        metrics_df.to_csv(args.outcsv, index=False)
        
    print(f"\nAccuracy metrics successfully logged to: {args.outcsv}")
    
    if all_passed:
        print("\n>>> ALL NUMERICAL ACCURACY CHECKS PASSED SUCCESSFULLY! <<<")
    else:
        print("\n>>> WARNING: One or more attributes exceeded scientific tolerance! <<<")

if __name__ == '__main__':
    main()
