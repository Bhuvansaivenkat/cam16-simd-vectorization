import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# Set publication style
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 14

os.makedirs('graphs', exist_ok=True)

# -------------------------------------------------------------
# 1. Load Data
# -------------------------------------------------------------
bench_df = pd.read_csv('results/benchmark_results.csv')
acc_df = pd.read_csv('results/accuracy_results.csv')

print("Loaded benchmark results:")
print(bench_df[['Implementation', 'SampleCount', 'Median_ms', 'Throughput_Mcps', 'Speedup']])

palette = {
    'Scalar Baseline': '#4A5568',          # Dark Slate Grey
    'Compiler Auto-Vec (SoA)': '#3182CE',  # Blue
    'Manual AVX2 SIMD (SoA)': '#DD6B20'   # Vivid Orange/Amber
}

# -------------------------------------------------------------
# GRAPH 1: Execution Time Comparison (Log-Log)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5.5), dpi=300)

for impl in ['Scalar Baseline', 'Compiler Auto-Vec (SoA)', 'Manual AVX2 SIMD (SoA)']:
    sub = bench_df[bench_df['Implementation'] == impl].sort_values('SampleCount')
    ax.plot(sub['SampleCount'], sub['Median_ms'], marker='o', linewidth=2.2, markersize=7, 
            label=impl, color=palette[impl])
    for x, y in zip(sub['SampleCount'], sub['Median_ms']):
        offset_y = 1.25 if impl == 'Compiler Auto-Vec (SoA)' else (0.75 if impl == 'Manual AVX2 SIMD (SoA)' else 1.2)
        ax.annotate(f"{y:.2f} ms", (x, y), textcoords="offset points", xytext=(0, 8 if offset_y > 1 else -14),
                    ha='center', fontsize=9, fontweight='semibold', color=palette[impl])

ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xticks([10000, 100000, 1000000])
ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
ax.set_xticklabels(['10K (L1/L2 Cache)', '100K (L3 Cache)', '1M (DRAM Bound)'])
ax.set_xlabel('Workload Sample Size (Memory Hierarchy Tier)')
ax.set_ylabel('Execution Time (ms, log scale)')
ax.set_title('CAM16 Forward Model: Execution Time vs. Workload Scale')
ax.grid(True, which="both", ls="--", alpha=0.5)
ax.legend(loc='upper left', frameon=True, shadow=True)
plt.tight_layout()
fig.savefig('graphs/execution_time_comparison.png', dpi=300)
plt.close(fig)
print("Saved graphs/execution_time_comparison.png")

# -------------------------------------------------------------
# GRAPH 2: Throughput Comparison (Million Colors / Second)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(9, 5.5), dpi=300)

sample_counts = [10000, 100000, 1000000]
workload_labels = ['10K Samples\n(480 KB - L1/L2)', '100K Samples\n(4.8 MB - L3)', '1M Samples\n(48 MB - DRAM)']
x = np.arange(len(sample_counts))
bar_width = 0.26

impls = ['Scalar Baseline', 'Compiler Auto-Vec (SoA)', 'Manual AVX2 SIMD (SoA)']

for i, impl in enumerate(impls):
    sub = bench_df[bench_df['Implementation'] == impl].sort_values('SampleCount')
    throughputs = sub['Throughput_Mcps'].values
    bars = ax.bar(x + (i - 1) * bar_width, throughputs, width=bar_width, 
                  label=impl, color=palette[impl], edgecolor='black', linewidth=0.8, alpha=0.9)
    for bar, val in zip(bars, throughputs):
        ax.text(bar.get_x() + bar.get_width()/2.0, bar.get_height() + 0.8,
                f"{val:.1f} M/s", ha='center', va='bottom', fontsize=9, fontweight='bold', rotation=0)

ax.set_xticks(x)
ax.set_xticklabels(workload_labels)
ax.set_xlabel('Workload Scale & Working Set Size')
ax.set_ylabel('Throughput (Million Samples / Second)')
ax.set_title('CAM16 Processing Throughput Across Memory Hierarchy')
ax.set_ylim(0, 56)
ax.grid(True, axis='y', ls='--', alpha=0.5)
ax.legend(loc='upper right', frameon=True, shadow=True)
plt.tight_layout()
fig.savefig('graphs/throughput_comparison.png', dpi=300)
plt.close(fig)
print("Saved graphs/throughput_comparison.png")

# -------------------------------------------------------------
# GRAPH 3: Speedup Comparison Relative to Scalar Baseline
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.5, 5.5), dpi=300)

impls_speedup = ['Compiler Auto-Vec (SoA)', 'Manual AVX2 SIMD (SoA)']
speedup_palette = {
    'Compiler Auto-Vec (SoA)': '#3182CE',
    'Manual AVX2 SIMD (SoA)': '#DD6B20'
}

bar_width = 0.32
x = np.arange(len(sample_counts))

for i, impl in enumerate(impls_speedup):
    sub = bench_df[bench_df['Implementation'] == impl].sort_values('SampleCount')
    speedups = sub['Speedup'].values
    bars = ax.bar(x + (i - 0.5) * bar_width, speedups, width=bar_width,
                  label=impl, color=speedup_palette[impl], edgecolor='black', linewidth=0.8, alpha=0.9)
    for bar, val in zip(bars, speedups):
        ax.text(bar.get_x() + bar.get_width()/2.0, bar.get_height() + 0.2,
                f"{val:.2f}x", ha='center', va='bottom', fontsize=10, fontweight='bold')

# Reference line for scalar (1.0x)
ax.axhline(1.0, color='#4A5568', linestyle='--', linewidth=1.5, label='Scalar Baseline (1.00x)')
ax.set_xticks(x)
ax.set_xticklabels(workload_labels)
ax.set_xlabel('Workload Scale & Cache Tier')
ax.set_ylabel('Speedup Factor vs. Scalar Baseline')
ax.set_title('Speedup Analysis: Auto-Vectorization vs. Manual AVX2 Intrinsics')
ax.set_ylim(0, 15)
ax.grid(True, axis='y', ls='--', alpha=0.5)
ax.legend(loc='upper left', frameon=True, shadow=True)
plt.tight_layout()
fig.savefig('graphs/speedup_comparison.png', dpi=300)
plt.close(fig)
print("Saved graphs/speedup_comparison.png")

# -------------------------------------------------------------
# GRAPH 4: Numerical Error Profile (Log Scale MAE across Attributes)
# -------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5.5), dpi=300)

attributes = ['J', 'C', 'h', 's', 'Q', 'M', 'H', 'a', 'b']
attr_names = ['J\n(Lightness)', 'C\n(Chroma)', 'h\n(Hue °)', 's\n(Saturation)', 
              'Q\n(Brightness)', 'M\n(Colourfulness)', 'H\n(Hue Quad)', 'a\n(Cartesian)', 'b\n(Cartesian)']

x = np.arange(len(attributes))
bar_width = 0.38

auto_mae = []
avx2_mae = []

for attr in attributes:
    v_auto = acc_df[(acc_df['Implementation'] == 'Compiler Auto-Vec (SoA)') & (acc_df['Attribute'] == attr)]['MAE'].values[0]
    v_avx2 = acc_df[(acc_df['Implementation'] == 'Manual AVX2 SIMD (SoA)') & (acc_df['Attribute'] == attr)]['MAE'].values[0]
    auto_mae.append(v_auto)
    avx2_mae.append(v_avx2)

bars_auto = ax.bar(x - bar_width/2.0, auto_mae, width=bar_width,
                   label='Compiler Auto-Vec vs. Python Ref', color='#3182CE', edgecolor='black', linewidth=0.7, alpha=0.85)
bars_avx2 = ax.bar(x + bar_width/2.0, avx2_mae, width=bar_width,
                   label='Manual AVX2 SIMD vs. Python Ref', color='#DD6B20', edgecolor='black', linewidth=0.7, alpha=0.85)

ax.set_yscale('log')
ax.set_xticks(x)
ax.set_xticklabels(attr_names)
ax.set_xlabel('CAM16 Perceptual Color Attributes')
ax.set_ylabel('Mean Absolute Error (MAE, log scale)')
ax.set_title('Numerical Accuracy Verification: MAE vs. IEEE 754 Python Reference')
ax.axhline(0.01, color='red', linestyle=':', linewidth=1.5, label='Human JND Threshold (ΔE ≈ 1.0, JND sub-threshold ≈ 1e-2)')
ax.grid(True, which="both", ls="--", alpha=0.5)
ax.legend(loc='upper right', frameon=True, shadow=True)
plt.tight_layout()
fig.savefig('graphs/numerical_error_profile.png', dpi=300)
plt.close(fig)
print("Saved graphs/numerical_error_profile.png")

print("All graphs successfully generated!")
