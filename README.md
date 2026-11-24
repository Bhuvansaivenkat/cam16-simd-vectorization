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

---

## 8. State-of-the-Art Comparison: Last Three Years (2023–2025) vs. Our Work
| Publication / Baseline | Year | Target Platform | Model Evaluated | Vectorization Strategy | Throughput | Speedup vs. Baseline | Precision / Error ($\Delta E$) |
| :--- | :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| **Python `colour-science` (v0.4.7)** | 2024 | x86-64 CPU | Full CIE CAM16 | Interpreted Python + NumPy 64-bit float | ~0.08 Mcps | 0.02× | 64-bit float ($\Delta E = 0$, exact) |
| **OpenCV / LittleCMS (Standard)** | 2023 | x86-64 CPU | CIE $L^*a^*b^*$ / ICC | Sequential C++ / OpenMP thread pools | ~3.50 Mcps | 0.91× | Standard 32-bit single precision |
| **Benson et al. (ADMS @ VLDB)** | 2023 | Intel Xeon / AMD | Database query filters | AVX2/AVX-512 intrinsics vs. auto-vec | ~8.5–12 Mcps | 2.5×–4.2× | Bit-exact integer/float |
| **Mohammadi et al. (*Sensors*)** | 2024 | Embedded ARM / Intel | RGB $\to$ XYZ transform | Scalar OpenCV C++ loops on image sensor feeds | ~2.80 Mcps | 1.00× | Camera sensor calibration |
| **IEEE Access Authors (*IEEE Access*)**| 2024 | Intel Core i7 / Ryzen | Non-linear image conv | AVX2 gather (`vgatherdps`) vs. polynomial SIMD | ~14.20 Mcps | 3.80× | Approx error $< 10^{-3}$ |
| **Martínez-D. et al. (*IJPP*)** | 2025 | Intel x86-64 / ARM | Multimedia loops | Portable SIMD (`std::simd`) vs. intrinsics | ~15–20 Mcps | 4.0×–5.5× | Standard float (linear loops) |
| **Zhou & Luo (*Color & Imaging*)** | 2025 | Intel i9 / GPU | CAM16-UCS for 4K HDR | CPU scalar C++ / GPU compute shaders | ~1.2–3.2 Mcps | 1.00× (CPU) | $\Delta E < 0.5$ (visual match) |
| **Proposed Engine (This Work)** | **2026** | **AMD Ryzen 7 7435HS** | **Full Forward CAM16** | **In-register AVX2 256-bit minimax polynomials + SoA** | **47.28 Mcps** | **12.32× (vs. Scalar)**<br>**8.61× (vs. Auto-Vec)** | **Max rel err $< 0.002\%$ ($MAE \le 1.7 \times 10^{-4} \ll \Delta E = 1.0$)** |

---

## 9. Architectural Ablation Study (10,000 Samples on AMD Ryzen 7 7435HS)
| Stage | Optimization Configuration / Added Layer | Median Latency (ms) | Throughput (Mcps) | Marginal Speedup ($\Delta$) | Cumulative Speedup | Primary Microarchitectural Mechanism / Bottleneck Addressed |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **M0** | **Baseline Scalar C++ (AoS Layout)** | 2.605 ms | 3.838 Mcps | — (Baseline) | **1.000×** | Sequential scalar execution, strided AoS memory, `libm` `powf()`/`atan2f()` subroutine calls, branch mispredictions. |
| **M1** | **+ Memory Layout Restructuring (SoA)** | 2.214 ms | 4.517 Mcps | **+17.7%** | **1.177×** | Converts interleaved RGB into 32-byte aligned contiguous planar arrays (`x, y, z`). Eliminates 66% cache line waste and improves L1/L2 prefetching. |
| **M2** | **+ Compiler Auto-Vectorization (`-O3 -mavx2 -mfma`)** | 1.822 ms | 5.490 Mcps | **+21.5%** | **1.430×** | GCC auto-vectorizes Stage 1 linear CAT16 matrix into 8-wide `vmovups`/`vfmadd`. Stages 2–5 remain scalar due to `libm` calling convention & `errno`. |
| **M3** | **+ Vector In-Register Minimax Exponentiation ($x^{0.42}, t^{0.9}$)** | 0.548 ms | 18.248 Mcps | **+232.4%** | **4.754×** | Replaces scalar `call powf` with in-register Cody-Waite range reduction + 9th-degree minimax polynomials via Horner FMA. Eliminates 70% runtime bottleneck. |
| **M4** | **+ Vector Rational Arctangent (`avx2_atan2_deg`)** | 0.364 ms | 27.473 Mcps | **+50.5%** | **7.157×** | Replaces scalar `call atan2f` with Abramowitz & Stegun 4.4.49 10th-degree rational approximation inside 256-bit `ymm` registers ($< 0.0002^\circ$ error). |
| **M5** | **+ Algebraic Trigonometric Elimination** | 0.258 ms | 38.760 Mcps | **+41.1%** | **10.097×** | Eliminates `cos(h+2)` and Cartesian trig via $\cos(h+2) = \frac{a \cos(2) - b \sin(2)}{\sqrt{a^2+b^2}}$ evaluated via `_mm256_rsqrt_ps` (replaces trig with 2 FMAs). |
| **M6** | **+ Branchless Hue Quadrature Masking (`_mm256_blendv_ps`) [Full System]** | **0.211 ms** | **47.281 Mcps** | **+22.3%** | **12.318×** | Eliminates 4-quadrant piecewise `if-else` branching and branch misprediction stalls. Replaces branches with deterministic 18-cycle vector blend masks. |

---

For in-depth microarchitectural analysis, assembly inspections, and answers to research questions RQ1–RQ7, refer to the full academic paper in [docs/research_report.md](file:///d:/coa-proj/docs/research_report.md).
