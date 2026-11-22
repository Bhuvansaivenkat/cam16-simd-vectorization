# SIMD-Based Vectorization of Color Appearance Models (CAM16) for Efficient Computation
**Computer Organization and Architecture (COA) Academic Research Project**

## 1. Project Overview
This project investigates the computational efficiency, microarchitectural characteristics, and numerical accuracy of vectorizing the **CIE CAM16 Color Appearance Model** forward transformation using x86-64 **AVX2 SIMD intrinsics**.

We evaluate three distinct implementation strategies:
1. **Scalar C++ Baseline:** Conventional sequential Array-of-Structures (AoS) implementation following standard CIE CAM16 formulations using ISO C++ `std::powf` and `std::atan2f`.
2. **Compiler Auto-Vectorized C++:** 32-byte aligned Structure-of-Arrays (SoA) layout with loop-independence hints (`__restrict__`, `#pragma GCC ivdep`) compiled under GCC 16.2.0 (`-O3 -mavx2 -mfma`).
3. **Manual AVX2 Vectorized C++:** Explicit 256-bit SIMD intrinsics (`<immintrin.h>`) processing 8 single-precision floating-point color samples per vector cycle, featuring custom in-register Cody-Waite / minimax polynomial transcendental math, algebraic trigonometric elimination, and branchless vector masking (`_mm256_blendv_ps`).

---

## 2. Hardware and Environment Specification
- **Host Architecture:** x86-64
- **Processor:** AMD Ryzen 7 7435HS (8 Cores, 16 Logical Processors, Zen 3+/4)
- **Clock Frequency:** Base 3.1 GHz, Boost up to 4.5 GHz
- **Cache Topology:** L1 Data Cache 256 KB (32 KB/core), L2 Cache 4 MB (512 KB/core), L3 Cache 16 MB shared
- **Supported SIMD ISAs:** SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, AVX, AVX2, FMA3
- **Operating System:** Microsoft Windows 11 Home 64-bit (Build 26300)
- **Compiler:** GCC 16.2.0 (MSYS2 UCRT64 toolchain)
- **Build System:** CMake 4.5.1 with Ninja 1.13.2 generator
- **Reference Scientific Library:** Python `colour-science` 0.4.7

---

## 3. Directory Structure
```
CAM16_SIMD_Project/
|-- CMakeLists.txt          # Root CMake build configuration
|-- README.md               # Project overview, instructions, and benchmark summary
|-- data/                   # Reproducible input color datasets (10K, 100K, 1M samples)
|   |-- colors_10000.csv
|   |-- colors_100000.csv
|   |-- colors_1000000.csv
|   `-- reference_10000.csv # IEEE 754 double-precision reference output
|-- include/
|   |-- cam16_types.h       # Data structures (XYZ, ViewingConditions, SoA, AoS)
|   |-- cam16.h             # Function declarations for Scalar, Auto-Vec, and AVX2
|   `-- benchmark.h         # Timing harness and statistics
|-- src/
|   |-- main.cpp            # Application entry point and multi-workload benchmark runner
|   |-- cam16_scalar.cpp    # Baseline scalar forward model
|   |-- cam16_auto.cpp      # Compiler auto-vectorized forward model
|   |-- cam16_avx2.cpp      # Manual AVX2 256-bit SIMD implementation
|   `-- benchmark.cpp       # Micro-benchmarking execution engine
|-- python/
|   |-- generate_data.py    # Synthetic XYZ workload generator (seed=42)
|   |-- cam16_reference.py  # Reference CAM16 computation via colour-science
|   |-- validate_results.py # Accuracy validation (MAE, RMSE, MaxAE, circular hue)
|   `-- plot_results.py     # Graph generator (execution time, throughput, speedup)
|-- results/
|   |-- benchmark_results.csv # Multi-workload benchmark timings, throughput, and speedups
|   |-- accuracy_results.csv  # 9-attribute precision profile (MAE, MaxAE, RMSE)
|   |-- scalar_10000.csv
|   |-- auto_10000.csv
|   `-- avx2_10000.csv
|-- graphs/                 # High-resolution benchmark comparison plots (300 DPI PNG)
|   |-- execution_time_comparison.png
|   |-- throughput_comparison.png
|   |-- speedup_comparison.png
|   `-- numerical_error_profile.png
|-- docs/
|   `-- research_report.md  # Comprehensive academic research report
`-- research papers/        # Ground-truth literature repository (14 research papers)
```

---

## 4. Build Instructions (MSYS2 UCRT64)
From PowerShell:
```powershell
# 1. Add UCRT64 toolchain to PATH
$env:Path = "C:\msys64\ucrt64\bin;" + $env:Path

# 2. Configure build with CMake & Ninja
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release

# 3. Build executable
cmake --build build
```

---

## 5. Execution Workflow
1. **Generate Synthetic Workloads:**
   ```powershell
   python python/generate_data.py
   ```
2. **Compute Ground-Truth Reference Output:**
   ```powershell
   python python/cam16_reference.py
   ```
3. **Execute C++ Multi-Workload Benchmarks:**
   ```powershell
   .\build\cam16_benchmark_runner.exe
   ```
4. **Validate Numerical Accuracy Across Attributes:**
   ```powershell
   python python/validate_results.py
   ```
5. **Generate Publication-Quality Plots:**
   ```powershell
   python python/plot_results.py
   ```

---

## 6. Interactive Web Deployment (Live Evaluator Dashboard)
An interactive web application is deployed via Streamlit, allowing evaluators to interact with the CAM16 model, view real-time color conversions, trigger live C++ hardware benchmarks, and explore speedup charts directly in their browser.

### One-Click Launch:
Double-click `run_app.bat` or run:
```powershell
.\run_app.bat
```
*(Or manually in PowerShell)*:
```powershell
python -m streamlit run app.py
```
This automatically starts the local web server and opens the dashboard at `http://localhost:8501`.

---

## 7. Experimental Benchmark Summary

### Single-Core Execution Across Workloads (AMD Ryzen 7 7435HS)
| Workload Size | Engine | Median Time (ms) | Throughput (Million samples/sec) | Speedup vs. Scalar |
| :--- | :--- | :---: | :---: | :---: |
| **10,000 Samples** | Scalar Baseline | 2.605 ms | 3.838 Mcps | **1.000×** |
| *(480 KB - L1/L2 Cache)* | Compiler Auto-Vec (SoA) | 1.822 ms | 5.490 Mcps | **1.430×** |
| | **Manual AVX2 SIMD (SoA)** | **0.211 ms** | **47.281 Mcps** | **12.318×** |
| | | | | |
| **100,000 Samples** | Scalar Baseline | 27.083 ms | 3.692 Mcps | **1.000×** |
| *(4.8 MB - L3 Cache)* | Compiler Auto-Vec (SoA) | 18.090 ms | 5.528 Mcps | **1.497×** |
| | **Manual AVX2 SIMD (SoA)** | **2.146 ms** | **46.605 Mcps** | **12.622×** |
| | | | | |
| **1,000,000 Samples** | Scalar Baseline | 271.425 ms | 3.684 Mcps | **1.000×** |
| *(48.0 MB - DRAM Bound)*| Compiler Auto-Vec (SoA) | 199.048 ms | 5.024 Mcps | **1.364×** |
| | **Manual AVX2 SIMD (SoA)** | **22.039 ms** | **45.375 Mcps** | **12.316×** |

### Numerical Precision Verification (vs. Python `colour-science` 64-bit Reference)
- **Lightness ($J$) MAE:** $6.08 \times 10^{-5}$ (MaxAE: $3.59 \times 10^{-4}$)
- **Chroma ($C$) MAE:** $1.73 \times 10^{-4}$ (MaxAE: $1.88 \times 10^{-3}$)
- **Hue Angle ($h$) MAE:** $1.57 \times 10^{-4\circ}$ (MaxAE: $5.56 \times 10^{-3\circ}$)
- **Brightness ($Q$) MAE:** $6.73 \times 10^{-5}$ (MaxAE: $4.12 \times 10^{-4}$)
- **Maximum Relative Error:** $< 0.002\%$ (orders of magnitude below human JND threshold $\Delta E = 1.0$, guaranteeing strictly perceptually lossless output).

For in-depth microarchitectural analysis, assembly inspections, and answers to research questions RQ1–RQ7, refer to the full academic paper in [docs/research_report.md](file:///d:/coa-proj/docs/research_report.md).
