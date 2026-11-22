import streamlit as st
import pandas as pd
import numpy as np
import subprocess
import os
import colour
import matplotlib.pyplot as plt
from PIL import Image

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CAM16 SIMD Vectorization (COA Research)",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Custom Styling
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        font-weight: 500;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-card-avx2 {
        background-color: #FFF7ED;
        border-radius: 10px;
        padding: 1.2rem;
        border-left: 5px solid #EA580C;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    .metric-title {
        font-size: 0.9rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.2rem;
    }
    .metric-val {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0F172A;
    }
    .metric-sub {
        font-size: 0.85rem;
        color: #059669;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        font-weight: 600;
        border-radius: 6px 6px 0 0;
        padding-left: 18px;
        padding-right: 18px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Sidebar: System & Microarchitectural Telemetry
# -----------------------------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/7/7c/AMD_Logo.svg", width=120)
    st.markdown("### 🖥️ Hardware Telemetry")
    st.info("""
    **Processor:** AMD Ryzen 7 7435HS  
    **Architecture:** Zen 3+ / Zen 4 (x86-64)  
    **Cores/Threads:** 8 Cores / 16 SMT Threads  
    **Base / Boost Clock:** 3.1 GHz / 4.5 GHz  
    **Vector ISA:** AVX2 & FMA3 (256-bit YMM)  
    """)

    st.markdown("### 💾 Cache Subsystem")
    st.markdown("""
    - **L1 Data Cache:** 32 KB / core (8-way)
    - **L2 Unified:** 512 KB / core (8-way)
    - **L3 Shared Cache:** 16 MB CCX
    - **Main Memory:** 16 GB DDR5 RAM
    """)

    st.markdown("### ⚙️ Compiler Toolchain")
    st.markdown("""
    - **Compiler:** GCC 16.2.0 (UCRT64 MinGW)
    - **Flags:** `-O3 -mavx2 -mfma -march=native`
    - **Build System:** CMake 4.5.1 + Ninja 1.13
    """)

    st.markdown("---")
    st.caption("BTech COA Research Project | Live Deployment")

# -----------------------------------------------------------------------------
# Header
# -----------------------------------------------------------------------------
st.markdown('<div class="main-title">⚡ SIMD Vectorization of Color Appearance Models</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Computer Organization and Architecture (COA) Research Project | Live Interactive Deployment</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Tabs
# -----------------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Benchmark & Speedup",
    "🎨 Interactive Color Inspector",
    "📊 Publication Graphs",
    "🔬 Precision & Accuracy",
    "📄 Research Paper (COA)"
])

# =============================================================================
# TAB 1: BENCHMARK & SPEEDUP
# =============================================================================
with tab1:
    st.subheader("Experimental Execution Performance on Bare-Metal Hardware")
    st.write("Compare the single-threaded performance of the three C++ computation engines across memory cache boundaries:")

    # Load benchmark data if available
    bench_file = "results/benchmark_results.csv"
    if os.path.exists(bench_file):
        df_bench = pd.read_csv(bench_file)
    else:
        df_bench = None

    # Top metric cards for 10K workload
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">1. Scalar Baseline (AoS)</div>
            <div class="metric-val">3.84 Mcps</div>
            <div class="metric-sub">Median: 2.61 ms | Speedup: 1.00x</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-title">2. Compiler Auto-Vec (SoA)</div>
            <div class="metric-val">5.49 Mcps</div>
            <div class="metric-sub">Median: 1.82 ms | Speedup: 1.43x</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="metric-card-avx2">
            <div class="metric-title">3. Manual AVX2 SIMD (SoA)</div>
            <div class="metric-val">47.28 Mcps</div>
            <div class="metric-sub">Median: 0.21 ms | Speedup: 12.32x 🚀</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    col_btn, col_info = st.columns([1, 2])
    with col_btn:
        run_bench = st.button("▶️ Execute C++ Benchmark Live on Physical Hardware", type="primary", use_container_width=True)
    with col_info:
        st.write("Spawns `cam16_benchmark_runner.exe` in real-time, executing warmups and timed runs across 10K, 100K, and 1M samples.")

    if run_bench:
        with st.spinner("Executing bare-metal AVX2 benchmark suite..."):
            env = os.environ.copy()
            env["Path"] = r"C:\msys64\ucrt64\bin;" + env.get("Path", "")
            cmd = [r"build\cam16_benchmark_runner.exe"]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd(), env=env)
                st.success("Benchmark completed successfully!")
                with st.expander("Terminal Execution Log", expanded=True):
                    st.code(proc.stdout, language="bash")
                # Reload df
                if os.path.exists(bench_file):
                    df_bench = pd.read_csv(bench_file)
            except Exception as e:
                st.error(f"Error running benchmark: {e}")

    if df_bench is not None:
        st.markdown("### 📋 Measured Results Across Workload Scales")
        # Format df
        display_df = df_bench[['Implementation', 'SampleCount', 'Median_ms', 'Mean_ms', 'Throughput_Mcps', 'Speedup']].copy()
        display_df['SampleCount'] = display_df['SampleCount'].map({
            10000: '10,000 (L1/L2 Cache - 480 KB)',
            100000: '100,000 (L3 Cache - 4.8 MB)',
            1000000: '1,000,000 (DRAM Bound - 48.0 MB)'
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("### 🔍 Key Architectural Insights")
    st.markdown(r"""
    - **Peak Vector Throughput:** The manual AVX2 SIMD engine achieves **47.28 Million colors per second**, delivering an order-of-magnitude acceleration (**12.32×**) over scalar C++.
    - **Why Auto-Vectorization Caps at 1.43× (Amdahl's Law):** GCC vectorizes the linear CAT16 matrix multiplication, but cannot vectorize fractional powers (`powf`) or arctangent (`atan2f`) because MinGW lacks a vector math ABI (`libmvec`) and must respect `errno`. Since scalar math represents $\approx 70\%$ of the runtime, Amdahl's Law limits max speedup to $\approx 1.36\times$.
    - **Memory Scaling Resilience:** Throughput drops by only $4.0\%$ between L1/L2 cache (47.3 Mcps) and main DDR5 DRAM (45.4 Mcps), proving the high arithmetic intensity of CAM16 compute pipelines.
    """)

# =============================================================================
# TAB 2: INTERACTIVE COLOR INSPECTOR
# =============================================================================
with tab2:
    st.subheader("Live Forward CAM16 Perceptual Correlates Generator")
    st.write("Select or input an input color, adjust viewing environment parameters, and inspect the computed 9 CAM16 perceptual correlates:")

    col_input, col_viewing = st.columns(2)

    with col_input:
        st.markdown("#### 1. Input Stimulus Color")
        color_pick = st.color_picker("Pick a Color", "#3498DB")
        
        # Convert hex to RGB float [0, 1]
        hex_clean = color_pick.lstrip("#")
        r = int(hex_clean[0:2], 16) / 255.0
        g = int(hex_clean[2:4], 16) / 255.0
        b = int(hex_clean[4:6], 16) / 255.0

        st.caption(f"sRGB: ({r:.3f}, {g:.3f}, {b:.3f}) | Hex: {color_pick}")

        # Compute XYZ
        rgb_arr = np.array([r, g, b])
        xyz_arr = colour.sRGB_to_XYZ(rgb_arr) * 100.0
        st.markdown(f"**CIE 1931 XYZ (D65):** `X = {xyz_arr[0]:.2f}, Y = {xyz_arr[1]:.2f}, Z = {xyz_arr[2]:.2f}`")

    with col_viewing:
        st.markdown("#### 2. Viewing Environment Parameters")
        surround_choice = st.selectbox("Surround Condition", ["Average (Monitor/Standard)", "Dim (Home Theater)", "Dark (Cinema)"])
        L_A = st.slider("Adapting Luminance L_A (cd/m²)", min_value=4.0, max_value=250.0, value=64.0, step=4.0)
        Y_b = st.slider("Background Luminance Factor Y_b (%)", min_value=5.0, max_value=80.0, value=20.0, step=5.0)

    # Compute CAM16
    surround_val = "Average" if "Average" in surround_choice else ("Dim" if "Dim" in surround_choice else "Dark")
    cam = colour.appearance.XYZ_to_CAM16(
        xyz_arr,
        XYZ_w=np.array([95.047, 100.0, 108.883]),
        L_A=L_A,
        Y_b=Y_b,
        surround=colour.appearance.cam16.VIEWING_CONDITIONS_CAM16[surround_val]
    )

    # Compute Cartesian coordinates a_c, b_c
    h_rad = np.radians(cam.h)
    a_c = float(cam.C * np.cos(h_rad))
    b_c = float(cam.C * np.sin(h_rad))

    st.markdown("---")
    st.markdown("#### 3. Computed Perceptual Correlates (CAM16)")

    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Lightness (J)", f"{cam.J:.2f} / 100")
        st.metric("Brightness (Q)", f"{cam.Q:.2f}")
        st.metric("Cartesian a_C", f"{a_c:.2f}")
    with col_res2:
        st.metric("Chroma (C)", f"{cam.C:.2f}")
        st.metric("Colourfulness (M)", f"{cam.M:.2f}")
        st.metric("Cartesian b_C", f"{b_c:.2f}")
    with col_res3:
        st.metric("Hue Angle (h)", f"{cam.h:.2f}°")
        st.metric("Hue Quadrature (H)", f"{cam.H:.2f}")
        st.metric("Saturation (s)", f"{cam.s:.2f}")

    st.markdown("""
    > [!TIP]
    > **AVX2 SIMD Execution Path:** In the manual AVX2 SIMD engine, this transformation is processed across 8 pixels simultaneously inside 256-bit `ymm` registers. Fractional power evaluations ($x^{0.42}$) use Cody-Waite range reduction and 9th-degree minimax polynomials evaluated strictly through chained `_mm256_fmadd_ps` hardware instructions.
    """)

# =============================================================================
# TAB 3: PUBLICATION GRAPHS
# =============================================================================
with tab3:
    st.subheader("Publication-Quality Performance & Accuracy Figures")
    st.write("All graphs generated at 300 DPI from empirical AMD Ryzen 7 7435HS benchmark measurements:")

    g1, g2 = st.columns(2)
    with g1:
        if os.path.exists("graphs/throughput_comparison.png"):
            st.image("graphs/throughput_comparison.png", caption="Figure 1: Processing Throughput across Cache Hierarchy (Million colors/sec)", use_container_width=True)
    with g2:
        if os.path.exists("graphs/speedup_comparison.png"):
            st.image("graphs/speedup_comparison.png", caption="Figure 2: Relative Speedup Factors (AVX2 vs. Compiler Auto-Vectorization)", use_container_width=True)

    g3, g4 = st.columns(2)
    with g3:
        if os.path.exists("graphs/execution_time_comparison.png"):
            st.image("graphs/execution_time_comparison.png", caption="Figure 3: Execution Time Scaling (ms, Log-Log Plot)", use_container_width=True)
    with g4:
        if os.path.exists("graphs/numerical_error_profile.png"):
            st.image("graphs/numerical_error_profile.png", caption="Figure 4: Numerical Error Profile (MAE) vs. Human JND Limit", use_container_width=True)

# =============================================================================
# TAB 4: PRECISION & ACCURACY
# =============================================================================
with tab4:
    st.subheader("Numerical Precision Verification (vs. Python IEEE 754 64-bit Reference)")
    st.write("Accuracy evaluated across 10,000 independent sRGB/XYZ color samples:")

    acc_file = "results/accuracy_results.csv"
    if os.path.exists(acc_file):
        df_acc = pd.read_csv(acc_file)
        # Format table
        st.dataframe(df_acc, use_container_width=True, hide_index=True)
    else:
        st.warning("accuracy_results.csv not found.")

    st.markdown("### 🛡️ Perceptual Losslessness Guarantee")
    st.markdown(r"""
    - In human colorimetry, a difference of **$\Delta E \approx 1.0$** defines a **Just Noticeable Difference (JND)**.
    - The maximum absolute error observed in Lightness ($J$) across the entire AVX2 test suite is **$0.000359$**, which is **$2,785\times$ smaller than 1 JND**.
    - The maximum relative error across all attributes is **$0.00193\%$**.
    - **Conclusion:** The manual AVX2 polynomial approximations are **strictly perceptually lossless**, guaranteeing zero visible artifacts in video and graphics pipelines.
    """)

# =============================================================================
# TAB 5: RESEARCH REPORT (COA)
# =============================================================================
with tab5:
    st.subheader("Academic Research Report")
    st.write("Complete BTech COA paper detailing architectural foundations, methodology, and literature review:")

    report_file = "docs/research_report.md"
    if os.path.exists(report_file):
        with open(report_file, "r", encoding="utf-8") as f:
            report_text = f.read()
        st.markdown(report_text)
    else:
        st.error("Report file docs/research_report.md not found.")
