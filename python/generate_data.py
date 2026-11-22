"""
Reproducible Colour Dataset Generator for CAM16 SIMD Performance & Accuracy Evaluation.
Generates controlled benchmark cases (black, white, primaries, secondaries, greys, boundaries)
and deterministic random sRGB->XYZ distributions using a fixed random seed.
"""

import os
import argparse
import numpy as np
import pandas as pd
import colour

SEED = 42

# Linear sRGB to CIE 1931 XYZ matrix (D65 illuminant, 2-degree observer)
M_sRGB_to_XYZ = np.array([
    [0.4124564, 0.3575761, 0.1804375],
    [0.2126729, 0.7151522, 0.0721750],
    [0.0193339, 0.1191920, 0.9503041]
])

def srgb_to_linear(srgb):
    """Applies inverse sRGB transfer function (IEC 61966-2-1)."""
    srgb = np.clip(srgb, 0.0, 1.0)
    linear = np.where(
        srgb <= 0.04045,
        srgb / 12.92,
        np.power((srgb + 0.055) / 1.055, 2.4)
    )
    return linear

def srgb_to_xyz(srgb):
    """Converts non-linear sRGB [0, 1] to CIE 1931 XYZ scaled to Y_w = 100."""
    linear = srgb_to_linear(srgb)
    xyz = np.dot(linear, M_sRGB_to_XYZ.T) * 100.0
    return xyz

def generate_controlled_test_cases():
    """Generates standard boundary, neutral, and extreme color test samples."""
    cases = []
    
    # 1. Neutral axis & boundaries
    cases.append(('Pure Black (near-zero)', [1e-5, 1e-5, 1e-5]))
    cases.append(('Near-Black',             [0.005, 0.005, 0.005]))
    cases.append(('Dark Grey (10%)',        [0.10, 0.10, 0.10]))
    cases.append(('Quarter Grey (25%)',     [0.25, 0.25, 0.25]))
    cases.append(('Mid Grey (50%)',         [0.50, 0.50, 0.50]))
    cases.append(('Bright Grey (75%)',      [0.75, 0.75, 0.75]))
    cases.append(('Near White (95%)',       [0.95, 0.95, 0.95]))
    cases.append(('Pure White (100%)',      [1.00, 1.00, 1.00]))

    # 2. Saturated primaries & secondaries
    cases.append(('Primary Red',     [1.0, 0.0, 0.0]))
    cases.append(('Primary Green',   [0.0, 1.0, 0.0]))
    cases.append(('Primary Blue',    [0.0, 0.0, 1.0]))
    cases.append(('Secondary Yellow', [1.0, 1.0, 0.0]))
    cases.append(('Secondary Cyan',   [0.0, 1.0, 1.0]))
    cases.append(('Secondary Magenta', [1.0, 0.0, 1.0]))

    # 3. Pastel / Low-Chroma colors
    cases.append(('Pastel Pink',     [0.9, 0.7, 0.7]))
    cases.append(('Pastel Mint',     [0.7, 0.9, 0.8]))
    cases.append(('Pastel Sky',      [0.7, 0.8, 0.9]))
    cases.append(('Pastel Lavender', [0.85, 0.75, 0.9]))

    # 4. Numerical boundary conditions (near-zero per-channel)
    cases.append(('Near-zero Red',    [1e-4, 0.5, 0.5]))
    cases.append(('Near-zero Green',  [0.5, 1e-4, 0.5]))
    cases.append(('Near-zero Blue',   [0.5, 0.5, 1e-4]))
    
    names = [c[0] for c in cases]
    srgb_vals = np.array([c[1] for c in cases], dtype=np.float64)
    xyz_vals = srgb_to_xyz(srgb_vals)
    return names, xyz_vals

def generate_dataset(total_count, seed=SEED):
    """
    Generates a deterministic dataset containing controlled edge cases
    followed by pseudo-random sRGB-derived XYZ samples.
    """
    names, controlled_xyz = generate_controlled_test_cases()
    controlled_count = len(controlled_xyz)
    
    if total_count < controlled_count:
        raise ValueError(f"total_count must be at least {controlled_count}")
        
    random_count = total_count - controlled_count
    
    rng = np.random.default_rng(seed)
    random_srgb = rng.uniform(0.0, 1.0, size=(random_count, 3))
    random_xyz = srgb_to_xyz(random_srgb)
    
    # Combine controlled cases and random samples
    all_xyz = np.vstack([controlled_xyz, random_xyz])
    
    df = pd.DataFrame({
        'Sample_ID': np.arange(total_count),
        'X': all_xyz[:, 0],
        'Y': all_xyz[:, 1],
        'Z': all_xyz[:, 2]
    })
    return df

def main():
    parser = argparse.ArgumentParser(description="Generate reproducible XYZ datasets for CAM16 benchmarking")
    parser.add_argument('--sizes', nargs='+', type=int, default=[10000, 100000, 1000000],
                        help="Workload sizes to generate (default: 10000 100000 1000000)")
    parser.add_argument('--outdir', type=str, default="data", help="Output directory")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    
    print(f"=== Generating Reproducible CAM16 Workload Datasets (Seed: {SEED}) ===")
    for size in args.sizes:
        outfile = os.path.join(args.outdir, f"colors_{size}.csv")
        print(f"Generating {size:,} samples -> {outfile} ...", end="", flush=True)
        df = generate_dataset(size, seed=SEED)
        df.to_csv(outfile, index=False, float_format="%.6f")
        filesize_mb = os.path.getsize(outfile) / (1024 * 1024)
        print(f" Done ({filesize_mb:.2f} MB)")
        
    print("\nDataset generation complete!")

if __name__ == '__main__':
    main()
