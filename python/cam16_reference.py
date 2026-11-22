"""
CAM16 Reference Implementation using Python colour-science library.
Serves as the ground-truth baseline for numerical accuracy validation against C++ implementations.
"""

import sys
import os
import argparse
import numpy as np
import pandas as pd
import colour
from colour.appearance.cam16 import XYZ_to_CAM16, VIEWING_CONDITIONS_CAM16

# Standard Illuminant D65 reference white point (CIE 1931 2-degree observer)
DEFAULT_WHITE_POINT = np.array([95.047, 100.000, 108.883])
DEFAULT_L_A = 64.0   # Adapting luminance (cd/m^2)
DEFAULT_Y_B = 20.0   # 20% background luminance factor
DEFAULT_SURROUND = "Average"

def run_cam16_reference(xyz_array, xyz_w=DEFAULT_WHITE_POINT, L_A=DEFAULT_L_A, Y_b=DEFAULT_Y_B, surround_str=DEFAULT_SURROUND):
    """
    Computes CAM16 correlates for an array of XYZ tristimulus values.
    Input xyz_array: shape (N, 3), range [0, 100]
    Returns DataFrame with columns: [J, C, h, s, Q, M, H, a, b]
    """
    surround = VIEWING_CONDITIONS_CAM16[surround_str]
    
    # Vectorized execution across all samples using colour-science
    res = XYZ_to_CAM16(xyz_array, xyz_w, L_A=L_A, Y_b=Y_b, surround=surround)
    
    # Compute Cartesian a and b from Chroma C and Hue angle h (in radians)
    h_rad = np.radians(res.h)
    a_cartesian = res.C * np.cos(h_rad)
    b_cartesian = res.C * np.sin(h_rad)
    
    df = pd.DataFrame({
        'J': res.J,
        'C': res.C,
        'h': res.h,
        's': res.s,
        'Q': res.Q,
        'M': res.M,
        'H': res.H,
        'a': a_cartesian,
        'b': b_cartesian
    })
    return df

def process_csv_file(input_csv, output_csv):
    """Reads XYZ samples from input_csv, computes CAM16 correlates, and writes output_csv."""
    print(f"Loading XYZ samples from: {input_csv}")
    data = pd.read_csv(input_csv)
    
    required_cols = ['X', 'Y', 'Z']
    for col in required_cols:
        if col not in data.columns:
            raise ValueError(f"Input CSV missing required column: {col}. Existing: {list(data.columns)}")
            
    xyz_array = data[['X', 'Y', 'Z']].to_numpy(dtype=np.float64)
    print(f"Computing CAM16 correlates for {len(xyz_array)} color samples...")
    
    ref_df = run_cam16_reference(xyz_array)
    
    # Retain input XYZ alongside outputs
    combined = pd.concat([data[['X', 'Y', 'Z']], ref_df], axis=1)
    
    os.makedirs(os.path.dirname(output_csv) if os.path.dirname(output_csv) else '.', exist_ok=True)
    combined.to_csv(output_csv, index=False)
    print(f"Reference results successfully saved to: {output_csv}")
    print("Summary statistics of reference output:")
    print(ref_df.describe().round(4).to_string())

def run_self_test():
    """Runs a controlled mathematical validation test on key benchmark colors."""
    print("=== Running CAM16 Reference Self-Test on Benchmark Colors ===")
    test_colors = {
        'Reference White (D65)': [95.047, 100.0, 108.883],
        'Mid-Grey (50% Y)':       [47.5235, 50.0, 54.4415],
        'Dark Grey (10% Y)':      [9.5047, 10.0, 10.8883],
        'Sample Red':             [57.0, 29.0, 3.0],
        'Sample Green':           [14.0, 45.0, 9.0],
        'Sample Blue':            [18.0, 7.0, 95.0],
        'Sample Yellow':          [78.0, 92.0, 12.0],
        'Standard Test Sample':   [19.01, 20.00, 21.78]
    }
    
    xyz_list = list(test_colors.values())
    names = list(test_colors.keys())
    
    df = run_cam16_reference(np.array(xyz_list))
    df.insert(0, 'Color_Name', names)
    print(df.to_string(index=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CAM16 Reference Implementation via colour-science")
    parser.add_argument('--input', type=str, help="Path to input XYZ CSV file")
    parser.add_argument('--output', type=str, help="Path to save CAM16 output CSV file")
    parser.add_argument('--test', action='store_true', help="Run standalone self-test on standard test patches")
    
    args = parser.parse_args()
    
    if args.test or (args.input is None and args.output is None):
        run_self_test()
    elif args.input and args.output:
        process_csv_file(args.input, args.output)
    else:
        parser.print_help()
