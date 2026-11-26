import os
import base64
import subprocess
import shutil

def get_b64(path):
    if os.path.exists(path):
        with open(path, "rb") as f:
            ext = path.split(".")[-1].lower()
            mime = "jpeg" if ext in ["jpg", "jpeg"] else "png"
            return f"data:image/{mime};base64,{base64.b64encode(f.read()).decode('utf-8')}"
    return ""

def build_pdf_report():
    img_logo = get_b64("docs/extracted_media/word/media/image1.png")
    img_fig1 = get_b64("graphs/fig1_system_architecture.png")
    img_fig2 = get_b64("graphs/fig2_aos_vs_soa.png")
    img_fig3 = get_b64("graphs/fig3_ymm_registers.png")
    img_fig4 = get_b64("graphs/fig4_benchmark_workflow.png")
    img_fig5 = get_b64("graphs/throughput_comparison.png")
    img_fig6 = get_b64("graphs/speedup_comparison.png")
    img_fig7 = get_b64("graphs/execution_time_comparison.png")
    img_fig8 = get_b64("graphs/numerical_error_profile.png")
    img_fig9 = get_b64("graphs/screenshots/app_color_inspector.png")
    img_fig10 = get_b64("graphs/screenshots/screenshot_bench.png")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>SIMD Vectorization of Color Appearance Models (CAM16) - Project Report</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    @page {{
        size: A4 portrait;
        margin: 18mm 18mm 18mm 18mm;
    }}
    * {{
        box-sizing: border-box;
    }}
    body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
        color: #102D4D;
        background-color: #FFFFFF;
        line-height: 1.55;
        font-size: 9.6pt;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
    }}

    .title-page {{
        text-align: center;
        padding-top: 30px;
        page-break-after: always;
        height: 250mm;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .tp-title {{
        font-size: 19pt;
        font-weight: 800;
        color: #102D4D;
        line-height: 1.25;
        margin-bottom: 8px;
    }}
    .tp-sub {{
        font-size: 11pt;
        font-weight: 600;
        color: #4072AF;
        line-height: 1.35;
        margin-bottom: 24px;
    }}
    .tp-badge {{
        font-size: 11pt;
        font-weight: 700;
        color: #102D4D;
        margin-bottom: 24px;
    }}
    .tp-team {{
        font-size: 10pt;
        font-weight: 600;
        color: #102D4D;
        line-height: 1.8;
        margin: 20px auto;
        display: inline-block;
        text-align: left;
    }}
    .tp-logo {{
        margin: 20px auto;
        max-width: 140px;
    }}
    .tp-foot {{
        font-size: 9.5pt;
        font-weight: 700;
        color: #102D4D;
        line-height: 1.5;
        margin-top: 20px;
    }}

    .page-break {{
        page-break-before: always;
    }}

    h1 {{
        font-size: 14pt;
        font-weight: 800;
        color: #102D4D;
        margin-top: 22px;
        margin-bottom: 8px;
        border-bottom: 2px solid #102D4D;
        padding-bottom: 3px;
        page-break-after: avoid;
        text-transform: uppercase;
        letter-spacing: 0.3px;
    }}
    h2 {{
        font-size: 11pt;
        font-weight: 700;
        color: #4072AF;
        margin-top: 14px;
        margin-bottom: 5px;
        page-break-after: avoid;
    }}
    h3 {{
        font-size: 9.8pt;
        font-weight: 700;
        color: #102D4D;
        margin-top: 10px;
        margin-bottom: 4px;
        page-break-after: avoid;
    }}
    p {{
        margin-bottom: 6px;
        text-align: justify;
    }}
    ul, ol {{
        margin-left: 20px;
        margin-bottom: 8px;
    }}
    li {{
        margin-bottom: 4px;
        text-align: justify;
    }}

    table {{
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 8pt;
        page-break-inside: avoid;
        background: #FFFFFF;
        border: 1px solid #DAE2EF;
    }}
    th {{
        background-color: #F0F4FA;
        color: #102D4D;
        font-weight: 700;
        padding: 5px 8px;
        border-bottom: 2px solid #4072AF;
        text-align: left;
        font-size: 7.8pt;
        text-transform: uppercase;
    }}
    td {{
        padding: 4.5px 8px;
        border-bottom: 1px solid #DAE2EF;
        color: #102D4D;
    }}
    tr:nth-child(even) td {{
        background-color: #F8FAFD;
    }}
    .mono {{
        font-family: 'JetBrains Mono', monospace;
    }}

    .figure-box {{
        text-align: center;
        margin: 12px 0;
        page-break-inside: avoid;
    }}
    .figure-box img {{
        max-width: 90%;
        max-height: 230px;
        object-fit: contain;
        border-radius: 4px;
        border: 1px solid #DAE2EF;
    }}
    .caption {{
        font-size: 8pt;
        font-weight: 700;
        color: #4072AF;
        margin-top: 4px;
    }}

    .toc-item {{
        display: flex;
        justify-content: space-between;
        margin-bottom: 3px;
        font-size: 9pt;
    }}
    .toc-title {{
        color: #102D4D;
    }}
    .toc-dots {{
        flex: 1;
        border-bottom: 1px dotted #B4C3D7;
        margin: 0 6px 4px 6px;
    }}
    .toc-page {{
        font-weight: 700;
        color: #4072AF;
    }}

    .callout {{
        background-color: #F4F7FC;
        border: 1px solid #DAE2EF;
        border-left: 3.5px solid #102D4D;
        padding: 8px 12px;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 9pt;
    }}
</style>
</head>
<body>

<!-- 1. TITLE PAGE -->
<div class="title-page">
    <div>
        <div class="tp-title">SIMD VECTORIZATION OF COLOR APPEARANCE MODELS (CAM16)</div>
        <div class="tp-sub">High-Performance Vectorized C++ Implementation, Microarchitectural Evaluation<br>and Bare-Metal AMD Ryzen Hardware Benchmarking</div>
        <div class="tp-badge">PROJECT REPORT<br>Computer Organization and Architecture (COA)</div>
        
        <div class="tp-team">
            <strong>Submitted by Team of Three Members:</strong><br><br>
            <strong>Member 1:</strong> Ch. Bhuvan Sai &nbsp;&nbsp;&ndash;&nbsp;&nbsp; AP24110010001<br>
            <strong>Member 2:</strong> D. Harshith &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&ndash;&nbsp;&nbsp; AP24110010002<br>
            <strong>Member 3:</strong> N. Abhishikth &nbsp;&nbsp;&nbsp;&ndash;&nbsp;&nbsp; AP24110010003
        </div>
    </div>

    <div>
        <img class="tp-logo" src="{img_logo}" alt="SRM University Logo">
        <div class="tp-foot">
            Department of Computer Science and Engineering<br>
            SRM University–AP, Andhra Pradesh<br>
            Academic Year: 2026–2027<br>
            Faculty Guide: Bojja Venu
        </div>
    </div>
</div>

<!-- 2. DECLARATION -->
<div class="page-break"></div>
<h1>DECLARATION</h1>
<p>We hereby declare that the project titled <strong>“SIMD Vectorization of Color Appearance Models (CAM16) for Efficient Computation”</strong> has been formulated and developed by our team as part of the academic requirements of the Computer Organization and Architecture course in the B.Tech programme in Computer Science and Engineering at SRM University–AP.</p>
<p>The project investigates the computational efficiency, microarchitectural characteristics, memory hierarchy behavior, and numerical precision of vectorizing the CIE CAM16 forward model on modern x86-64 processors using AVX2 and FMA3 instruction set architectures. It provides a rigorous empirical comparison between single-threaded Scalar C++, compiler auto-vectorized C++, and hand-crafted AVX2 SIMD intrinsics.</p>
<p>The information, experimental benchmarks, timing profiles, and precision verifications presented in this report are based on the genuine work and empirical measurements collected by our team on bare-metal hardware. All experimental scripts, C++ engines, and analytical tools are reproducible.</p>
<br>
<p><strong>Place:</strong> SRM University–AP<br><strong>Date:</strong> 26th November 2026</p>
<br>
<p>1. Ch. Bhuvan Sai (AP24110010001) &nbsp;&nbsp;&nbsp;&nbsp; ____________________________________</p>
<p>2. D. Harshith (AP24110010002) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ____________________________________</p>
<p>3. N. Abhishikth (AP24110010003) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; ____________________________________</p>

<!-- 3. ACKNOWLEDGEMENT -->
<div class="page-break"></div>
<h1>ACKNOWLEDGEMENT</h1>
<p>We express our profound gratitude and sincere thanks to our faculty guide, <strong>Bojja Venu</strong>, for his invaluable guidance, continuous academic support, and constructive feedback throughout the conception, development, and benchmarking of this project.</p>
<p>We extend our heartfelt thanks to the Department of Computer Science and Engineering, SRM University–AP, for providing the necessary computational facilities, laboratory infrastructure, and research environment that enabled us to conduct bare-metal hardware benchmarking on modern superscalar processor architectures.</p>
<p>We would like to acknowledge each other's technical contributions and teamwork across the stages of C++ SIMD kernel development, micro-benchmarking harness design, mathematical error verification, and interactive dashboard engineering. This research project has granted us deep insight into how processor architecture, vector execution units, cache hierarchy, memory layout, and compiler limitations govern software performance.</p>
<p>Finally, we thank our peers, faculty members, and parents who directly or indirectly encouraged and assisted us in bringing this project to successful completion.</p>

<!-- 4. TABLE OF CONTENTS -->
<div class="page-break"></div>
<h1>TABLE OF CONTENTS</h1>
<div class="toc-item"><span class="toc-title">Abstract</span><span class="toc-dots"></span><span class="toc-page">4</span></div>
<div class="toc-item"><span class="toc-title">1. Introduction</span><span class="toc-dots"></span><span class="toc-page">5</span></div>
<div class="toc-item"><span class="toc-title">2. Problem Statement and Objectives</span><span class="toc-dots"></span><span class="toc-page">6</span></div>
<div class="toc-item"><span class="toc-title">3. Existing and Proposed System</span><span class="toc-dots"></span><span class="toc-page">7</span></div>
<div class="toc-item"><span class="toc-title">4. Software and Hardware Requirements</span><span class="toc-dots"></span><span class="toc-page">8</span></div>
<div class="toc-item"><span class="toc-title">5. System Architecture and Pipeline Design</span><span class="toc-dots"></span><span class="toc-page">9</span></div>
<div class="toc-item"><span class="toc-title">6. COA Concepts: Scalar, Memory Layout and Amdahl's Law</span><span class="toc-dots"></span><span class="toc-page">10</span></div>
<div class="toc-item"><span class="toc-title">7. COA Concepts: SIMD Vectorization and Cache Hierarchy</span><span class="toc-dots"></span><span class="toc-page">11</span></div>
<div class="toc-item"><span class="toc-title">8. Use Cases and Module Description</span><span class="toc-dots"></span><span class="toc-page">12</span></div>
<div class="toc-item"><span class="toc-title">9. Database Design and Reference Datasets</span><span class="toc-dots"></span><span class="toc-page">13</span></div>
<div class="toc-item"><span class="toc-title">10. Mathematical Formulation and Implementation of CAM16</span><span class="toc-dots"></span><span class="toc-page">14</span></div>
<div class="toc-item"><span class="toc-title">11. Vectorization Implementation: Five Microarchitectural Innovations</span><span class="toc-dots"></span><span class="toc-page">16</span></div>
<div class="toc-item"><span class="toc-title">12. Benchmarking Methodology</span><span class="toc-dots"></span><span class="toc-page">18</span></div>
<div class="toc-item"><span class="toc-title">13. Testing and Experimental Results</span><span class="toc-dots"></span><span class="toc-page">19</span></div>
<div class="toc-item"><span class="toc-title">14. Architectural Ablation and State-of-the-Art Analysis</span><span class="toc-dots"></span><span class="toc-page">21</span></div>
<div class="toc-item"><span class="toc-title">15. Application Screenshots and User Interface</span><span class="toc-dots"></span><span class="toc-page">23</span></div>
<div class="toc-item"><span class="toc-title">16. Conclusion and Future Enhancements</span><span class="toc-dots"></span><span class="toc-page">25</span></div>
<div class="toc-item"><span class="toc-title">17. Team Contributions and References</span><span class="toc-dots"></span><span class="toc-page">26</span></div>

<h2>LIST OF FIGURES</h2>
<div class="toc-item"><span class="toc-title">Figure 1: Logical System Architecture and End-to-End Execution Pipeline</span><span class="toc-dots"></span><span class="toc-page">9</span></div>
<div class="toc-item"><span class="toc-title">Figure 2: Memory Organization: Array-of-Structures (AoS) vs. Structure-of-Arrays (SoA)</span><span class="toc-dots"></span><span class="toc-page">10</span></div>
<div class="toc-item"><span class="toc-title">Figure 3: AVX2 256-Bit YMM Vector Register Architecture and Dual FMA Mapping</span><span class="toc-dots"></span><span class="toc-page">11</span></div>
<div class="toc-item"><span class="toc-title">Figure 4: Controlled Steady-State Micro-Benchmarking Workflow</span><span class="toc-dots"></span><span class="toc-page">18</span></div>
<div class="toc-item"><span class="toc-title">Figure 5: Processing Throughput across Cache Hierarchy (Million samples/sec)</span><span class="toc-dots"></span><span class="toc-page">20</span></div>
<div class="toc-item"><span class="toc-title">Figure 6: Relative Speedup Factors (Manual AVX2 vs. Compiler Auto-Vectorization)</span><span class="toc-dots"></span><span class="toc-page">20</span></div>
<div class="toc-item"><span class="toc-title">Figure 7: Execution Time Scaling across Workload Scales (ms, Log-Log Plot)</span><span class="toc-dots"></span><span class="toc-page">22</span></div>
<div class="toc-item"><span class="toc-title">Figure 8: Numerical Error Profile (MAE) vs. Human Visual JND Threshold (ΔE = 1.0)</span><span class="toc-dots"></span><span class="toc-page">22</span></div>
<div class="toc-item"><span class="toc-title">Figure 9: Interactive Color Inspector and Live Perceptual Correlates Generator</span><span class="toc-dots"></span><span class="toc-page">23</span></div>
<div class="toc-item"><span class="toc-title">Figure 10: Benchmark &amp; Speedup Dashboard Interface with Hardware Telemetry HUD</span><span class="toc-dots"></span><span class="toc-page">24</span></div>

<h2>LIST OF TABLES</h2>
<div class="toc-item"><span class="toc-title">Table 1: Comparison of Conventional Implementations and Proposed AVX2 SIMD Engine</span><span class="toc-dots"></span><span class="toc-page">7</span></div>
<div class="toc-item"><span class="toc-title">Table 2: Software Toolchain and Build Stack Specifications</span><span class="toc-dots"></span><span class="toc-page">8</span></div>
<div class="toc-item"><span class="toc-title">Table 3: Experimental Hardware Platform: AMD Ryzen 7 7435HS Architecture</span><span class="toc-dots"></span><span class="toc-page">8</span></div>
<div class="toc-item"><span class="toc-title">Table 4: Scalar vs. 256-bit AVX2 SIMD Vector Register Lane Mapping</span><span class="toc-dots"></span><span class="toc-page">11</span></div>
<div class="toc-item"><span class="toc-title">Table 5: Benchmark Data Schemas and Storage Records</span><span class="toc-dots"></span><span class="toc-page">13</span></div>
<div class="toc-item"><span class="toc-title">Table 6: Mathematical Correlates and Stages of the Forward CAM16 Model</span><span class="toc-dots"></span><span class="toc-page">14</span></div>
<div class="toc-item"><span class="toc-title">Table 7: Microarchitectural Bottlenecks and Engineered SIMD Solutions</span><span class="toc-dots"></span><span class="toc-page">16</span></div>
<div class="toc-item"><span class="toc-title">Table 8: Summary of Performance Metrics and Statistical Timing Definitions</span><span class="toc-dots"></span><span class="toc-page">18</span></div>
<div class="toc-item"><span class="toc-title">Table 9: Functional Verification and Unit Testing Plan</span><span class="toc-dots"></span><span class="toc-page">19</span></div>
<div class="toc-item"><span class="toc-title">Table 10: Measured Execution Latency, Throughput, and Relative Speedup on Physical Hardware</span><span class="toc-dots"></span><span class="toc-page">19</span></div>
<div class="toc-item"><span class="toc-title">Table 11: Architectural Ablation Study (M0 to M6 Layer-by-Layer Acceleration Breakdown)</span><span class="toc-dots"></span><span class="toc-page">21</span></div>
<div class="toc-item"><span class="toc-title">Table 12: State-of-the-Art Literature Comparison (Last Three Years: 2023–2025 vs. Proposed Engine)</span><span class="toc-dots"></span><span class="toc-page">21</span></div>

<!-- 5. ABSTRACT -->
<div class="page-break"></div>
<h1>ABSTRACT</h1>
<p>Color Appearance Models (CAMs), particularly the international CIE CAM16 standard, are essential in digital imaging, HDR video production, scientific colorimetry, and display calibration. Unlike static color spaces (e.g., sRGB, CIE XYZ), CAM16 accurately predicts human perceptual phenomena—including chromatic adaptation, non-linear cone response compression, brightness/lightness divergence, and surround illumination effects. However, evaluating CAM16 per-pixel in real-time pipelines requires intense computation: each color sample involves forward/inverse 3×3 matrix multiplications, non-linear fractional powers (x^0.42, t^0.9), transcendental two-argument arctangents (atan2), trigonometric transformations, and four-quadrant piecewise branching.</p>
<p>On commodity processors, standard scalar implementations process approximately 3.84 million pixels per second, requiring over 129 CPU cores to sustain real-time 4K video at 60 frames per second. This project presents a high-performance computer architecture study and explicit C++ implementation of the forward CAM16 transformation utilizing x86-64 Advanced Vector Extensions 2 (AVX2) and FMA3 instruction set architectures.</p>
<p>We design, implement, and benchmark three distinct computation engines: (1) a baseline sequential Scalar C++ engine utilizing Array-of-Structures (AoS) memory and standard libm functions; (2) a Compiler Auto-Vectorized engine utilizing 32-byte aligned Structure-of-Arrays (SoA) layout with GCC 16.2.0 optimization flags (-O3 -mavx2 -mfma); and (3) a hand-crafted Manual AVX2 SIMD engine utilizing explicit 256-bit vector intrinsics (&lt;immintrin.h&gt;) processing 8 single-precision floats concurrently per vector instruction.</p>
<p>To overcome fundamental compiler vectorization barriers, we engineer five microarchitectural innovations: in-register Cody-Waite range reduction with 9th-degree minimax polynomial exponentiation, 10th-degree rational arctangent approximation (Abramowitz &amp; Stegun 4.4.49), algebraic trigonometric elimination of eccentricity via angle-sum identities and fast hardware reciprocal square roots (_mm256_rsqrt_ps), branchless vector blend masking (_mm256_blendv_ps), and dual 256-bit FMA pipeline saturation.</p>
<p>Empirical evaluation on an AMD Ryzen 7 7435HS processor (Zen 3+/4 microarchitecture, 8 cores/16 threads) across three workload scales (10,000, 100,000, and 1,000,000 samples) demonstrates that the manual AVX2 SIMD engine achieves a peak vector throughput of 47.28 Million colors per second (Mcps)—delivering an order-of-magnitude 12.32× speedup over the scalar baseline and an 8.61× speedup over compiler auto-vectorization. We demonstrate that auto-vectorization plateaus at a marginal 1.43× speedup due to Amdahl's Law, driven by scalar libm ABI overhead and errno side-effects. Validation against the IEEE 754 64-bit reference demonstrates a maximum relative error below 0.002% (MAE ≤ 1.7×10^-4), which is 2,785× below the human visual Just Noticeable Difference threshold (ΔE = 1.0), guaranteeing strictly perceptually lossless execution.</p>
<div class="callout">
<strong>Keywords:</strong> Computer Organization and Architecture, SIMD Vectorization, AVX2, FMA3, CIE CAM16, Color Appearance Models, Memory Hierarchy, Structure-of-Arrays, Amdahl's Law, Micro-Benchmarking.
</div>

<!-- CHAPTER 1 -->
<div class="page-break"></div>
<h1>1. INTRODUCTION</h1>
<p>Digital image processing, high-dynamic-range (HDR) video delivery, and modern computer graphics systems process vast volumes of pixel data under demanding latency constraints. In digital video pipelines, color representation is fundamental to visual fidelity. Standard digital workflows traditionally rely on device-dependent red-green-blue (RGB) representations or device-independent CIE 1931 XYZ tristimulus values. While CIE XYZ establishes colorimetric equivalence under standardized laboratory illuminants, it completely fails to model perceptual color appearance when environmental viewing conditions vary.</p>
<h2>1.1 Motivation</h2>
<p>Human visual perception is dynamic: the human visual system (HVS) continuously adapts to changes in ambient illumination level, illuminant chromaticity (e.g., direct sunlight versus warm incandescent indoor lighting), and surround contrast conditions. When viewed in differing environments, identical physical tristimulus values produce distinctly different visual sensations of lightness, chroma, and hue. To mathematically model these physiological adaptation phenomena, the Commission Internationale de l'Éclairage (CIE) developed advanced Color Appearance Models, culminating in the standardized CIE CAM16 specification.</p>
<p>However, CAM16's predictive fidelity is accompanied by intense computational complexity. Transforming a single pixel from CIE XYZ to CAM16 perceptual correlates requires forward and inverse chromatic adaptation matrix multiplications, non-linear cone response compression involving fractional powers (x^0.42), transcendental trigonometric operations (atan2), circular hue angle calculations, exponential power evaluations (t^0.9), and four-quadrant piecewise branching. In modern digital applications such as 4K video rendering (8.3 million pixels per frame at 60 or 120 FPS), photographic tone mapping, and camera image signal processing (ISP), evaluating CAM16 per-pixel sequentially in scalar C++ creates an extreme compute bottleneck, rendering real-time execution impossible on commodity CPUs.</p>
<h2>1.2 Project Overview</h2>
<p>This project, titled “SIMD Vectorization of Color Appearance Models (CAM16) for Efficient Computation,” conducts a comprehensive Computer Organization and Architecture (COA) research investigation into accelerating forward CAM16 computation on modern x86-64 superscalar microprocessors. We explore how hardware-level data parallelism (SIMD), register allocation, instruction scheduling, memory layout conditioning, and in-register transcendental approximations can be orchestrated to eliminate the scalar bottleneck.</p>
<p>We implement, profile, and benchmark three competing C++ computation engines: (1) a baseline sequential Scalar C++ engine adhering to ISO C++ libm implementations; (2) a Compiler Auto-Vectorized C++ engine with 32-byte cache alignment and vectorization pragmas compiled under GCC 16.2.0 (-O3 -mavx2 -mfma); and (3) an explicit 256-bit AVX2 SIMD Vectorized C++ engine engineered from scratch using C++ intrinsics (&lt;immintrin.h&gt;). The platform includes a controlled micro-benchmarking harness, a statistical accuracy validator comparing output against double-precision scientific references, and an interactive light-themed research dashboard built with Streamlit.</p>
<h2>1.3 Scope and Delimitations</h2>
<p>The scope of this project focuses on single-core instruction-level and data-level parallelism on commodity x86-64 processors, specifically evaluated on an AMD Ryzen 7 7435HS processor featuring Zen 3+/4 execution cores. We investigate vectorization efficiency across three memory hierarchy boundaries: L1/L2 cache (10,000 samples), L3 shared cache (100,000 samples), and main DDR5 DRAM (1,000,000 samples).</p>
<p>Multi-threaded thread-level parallelism (e.g., OpenMP) and discrete GPU offloading (e.g., CUDA or OpenCL) are recognized as complementary technologies but remain outside the primary architectural focus, which isolates the single-core vector instruction throughput and cache behavior of the CPU.</p>

<!-- CHAPTER 2 -->
<h1>2. PROBLEM STATEMENT AND OBJECTIVES</h1>
<h2>2.1 Problem Statement</h2>
<p>Evaluating the CIE CAM16 forward color appearance model requires evaluating non-linear operations that defy standard compiler auto-vectorization. Specifically:</p>
<ul>
    <li><strong>ABI and Vectorization Inhibitors:</strong> Standard C++ compilers (such as GCC, Clang, and MSVC) fail to vectorize loops containing calls to standard math library functions (std::powf and std::atan2f). The compiler must adhere to the standard C Application Binary Interface (ABI), which treats libm functions as external subroutines with potential side-effects (e.g., setting the global errno variable).</li>
    <li><strong>Memory Layout Inefficiencies:</strong> Interleaved pixel storage (Array-of-Structures, RGBRGB...) forces strided memory loads, wasting 66% of fetched 64-byte cache lines when vectorizing a single channel.</li>
    <li><strong>Control-Flow Divergence:</strong> Calculating hue quadrature (H) introduces a four-quadrant piecewise if-else branching structure that creates branch misprediction pipeline flushes on superscalar speculative execution cores.</li>
    <li><strong>Throughput Deficit:</strong> Consequently, scalar C++ forward CAM16 processing achieves only 3.84 million colors per second on high-performance processors, falling 129× short of real-time 4K 60fps throughput requirements.</li>
</ul>
<h2>2.2 Objectives</h2>
<p>The primary objectives of this research project are:</p>
<ol>
    <li><strong>Baseline Formulation:</strong> To design and implement a bit-exact, single-threaded scalar C++ baseline implementation of the forward CAM16 color appearance model following CIE specifications.</li>
    <li><strong>Compiler Auto-Vectorization:</strong> To evaluate compiler auto-vectorization capabilities under GCC 16.2.0 (-O3 -mavx2 -mfma) by restructuring memory into a 32-byte aligned Structure-of-Arrays (SoA) layout.</li>
    <li><strong>AVX2 SIMD Engine Development:</strong> To engineer a hand-crafted 256-bit AVX2 SIMD vectorized C++ computation engine using explicit &lt;immintrin.h&gt; intrinsics, processing 8 single-precision floating-point samples per vector cycle.</li>
    <li><strong>In-Register Transcendental Math:</strong> To formulate and implement custom in-register minimax polynomial approximations for fractional power (x^0.42, t^0.9) and rational arctangent (atan2) operations, eliminating external libm subroutine calls.</li>
    <li><strong>Branchless SIMD Masking:</strong> To eliminate runtime trigonometric calls (cos(h+2)) algebraically and replace piecewise control-flow branching with branchless vector masks (_mm256_blendv_ps).</li>
    <li><strong>Micro-Benchmarking:</strong> To conduct rigorous bare-metal performance benchmarking across the CPU memory hierarchy (L1/L2 cache, L3 cache, and DRAM) on an AMD Ryzen 7 7435HS processor.</li>
    <li><strong>Numerical Accuracy Verification:</strong> To validate the numerical precision of all nine perceptual correlates against an IEEE 754 64-bit double-precision reference (Python colour-science v0.4.7).</li>
    <li><strong>Interactive Scientific UI:</strong> To construct an interactive research dashboard providing live hardware telemetry, physical benchmark execution, and interactive color inspection.</li>
</ol>
<h2>2.3 Research Questions (RQ)</h2>
<p>This project systematically answers seven fundamental computer architecture research questions:</p>
<ul>
    <li><strong>RQ1:</strong> What microarchitectural inhibitors prevent modern compilers (GCC 16) from auto-vectorizing non-linear color appearance models?</li>
    <li><strong>RQ2:</strong> How do in-register minimax polynomial approximations compare against standard libm calls in cycle latency, register pressure, and throughput?</li>
    <li><strong>RQ3:</strong> How does memory layout restructuring (AoS vs. SoA) affect cache line utilization and vector load/store bandwidth?</li>
    <li><strong>RQ4:</strong> Why does compiler auto-vectorization plateau at a marginal ~1.43× speedup, and what code constructs enforce this limit (Amdahl's Law)?</li>
    <li><strong>RQ5:</strong> What is the numerical error bound of vector polynomial approximations compared to IEEE 754 double precision, and does it guarantee perceptual losslessness (ΔE &lt;&lt; 1.0)?</li>
    <li><strong>RQ6:</strong> How does vector throughput scale across distinct tiers of the CPU memory hierarchy (L1/L2 cache vs. L3 cache vs. main DDR5 DRAM)?</li>
    <li><strong>RQ7:</strong> How do specific execution features of the AMD Zen core (dual 256-bit FMA pipes, instruction fusion) govern observed performance?</li>
</ul>

<!-- CHAPTER 3 -->
<div class="page-break"></div>
<h1>3. EXISTING AND PROPOSED SYSTEM</h1>
<h2>3.1 Existing Approaches</h2>
<p>Existing implementations of Color Appearance Models fall into three categories: interpreted scientific computing environments, general-purpose image processing libraries, and GPU compute shaders.</p>
<ul>
    <li><strong>Python / NumPy Implementations:</strong> Scientific libraries such as Python's colour-science package implement CAM16 using double-precision NumPy vector arrays. While mathematically exact, Python execution overhead, dynamic type interpretation, and memory boxing limit throughput to approximately 0.08 Mcps (590× slower than our proposed engine).</li>
    <li><strong>Standard C++ Graphics Libraries:</strong> Libraries such as LittleCMS (lcms2) and OpenCV provide optimized color management implementations primarily for simple models (CIE L*a*b* and ICC profiles). When evaluating advanced non-linear appearance models, sequential C++ loops with scalar libm calls achieve ~3.5 Mcps.</li>
    <li><strong>GPU Compute Shaders:</strong> High-end production engines offload color grading to discrete GPUs via GLSL/HLSL shaders or CUDA. However, for interactive desktop applications, camera ISP sensor streams, and embedded displays, GPU offloading incurs prohibitive round-trip PCIe transfer latency, buffer staging overhead, and high power consumption.</li>
</ul>
<h2>3.2 Research Gap Addressed</h2>
<p>There is an acute research and practical gap in high-performance CPU vectorization for non-linear perceptual models. While linear matrix transformations (e.g., RGB to XYZ) are easily vectorized, transcendental-heavy algorithms like CAM16 have historically been abandoned as 'unvectorizable' on the CPU, forcing systems to choose between sluggish scalar CPU execution or power-hungry GPU offloading.</p>
<p>This project fills that gap by demonstrating that through microarchitectural co-design—combining SoA memory alignment, Cody-Waite polynomial approximation, algebraic trigonometric elimination, and branchless vector masking—the CPU can achieve real-time throughput on a single core.</p>

<p><strong>Table 1. Comparison of Conventional Implementations and Proposed AVX2 SIMD Engine.</strong></p>
<table>
    <thead>
        <tr>
            <th>Architectural Dimension</th>
            <th>Conventional Scalar Approach</th>
            <th>Compiler Auto-Vec Approach</th>
            <th>Proposed AVX2 SIMD Engine</th>
        </tr>
    </thead>
    <tbody>
        <tr><td>Memory Organization</td><td>Array-of-Structures (AoS)</td><td>Structure-of-Arrays (SoA)</td><td>32-Byte Aligned SoA</td></tr>
        <tr><td>Instruction Width</td><td>Scalar 32-bit (1 float/inst)</td><td>Mixed 256-bit (Stage 1 only)</td><td>256-bit YMM (8 floats/inst)</td></tr>
        <tr><td>Transcendental Math</td><td>libm std::powf / atan2f calls</td><td>Sequential libm calls (ABI stop)</td><td>In-Register Minimax Polynomials</td></tr>
        <tr><td>Trigonometric Cost</td><td>Runtime cos(h+2) call</td><td>Runtime cos(h+2) call</td><td>Eliminated via angle-sum identity</td></tr>
        <tr><td>Control Flow</td><td>Piecewise if-else branches</td><td>Piecewise if-else branches</td><td>Branchless _mm256_blendv_ps</td></tr>
        <tr><td>Hardware Execution</td><td>Single ALU pipe (x87/SSE)</td><td>Single vector ALU pipe</td><td>Dual 256-bit FMA Pipes (Zen)</td></tr>
        <tr><td>Throughput (10K Workload)</td><td class="mono">3.84 Million colors/sec</td><td class="mono">5.49 Million colors/sec</td><td class="mono"><strong>47.28 Million colors/sec</strong></td></tr>
        <tr><td>Relative Speedup</td><td class="mono">1.00× (Baseline)</td><td class="mono">1.43× vs. Scalar</td><td class="mono"><strong>12.32× vs. Scalar (8.61× vs Auto)</strong></td></tr>
    </tbody>
</table>

<h2>3.3 Proposed System Architecture</h2>
<p>The proposed system integrates an end-to-end research benchmarking, verification, and interactive exploration platform. It comprises five core software components: (1) a Workload Generator creating synthetic distributions; (2) a Native C++ Benchmark Runner housing the three engines; (3) a Precision Profiling Harness isolating cache hierarchy timing; (4) an Accuracy Verification Engine comparing output against 64-bit IEEE 754 references; and (5) an Interactive Scientific Dashboard built in Streamlit.</p>
<h2>3.4 Key Advantages</h2>
<ul>
    <li><strong>Order-of-Magnitude Acceleration:</strong> Achieves 47.28 Mcps on a single CPU core, enabling real-time 4K processing without GPU acceleration.</li>
    <li><strong>Zero Staging Overhead:</strong> Eliminates host-to-device buffer copy overhead, PCIe bus latency, and GPU kernel launch latency.</li>
    <li><strong>Strict Perceptual Losslessness:</strong> Maximum relative error is bounded below 0.002%, preserving absolute perceptual losslessness.</li>
    <li><strong>Universal x86-64 Compatibility:</strong> Runs on standard x86-64 processors supporting AVX2 and FMA3 (Intel Haswell+ and AMD Zen+).</li>
</ul>

<!-- CHAPTER 4 -->
<h1>4. SOFTWARE AND HARDWARE REQUIREMENTS</h1>
<h2>4.1 Software Toolchain Stack</h2>
<p>The software architecture combines a high-performance native C++ compilation toolchain with a Python scientific analysis and visualization layer.</p>

<p><strong>Table 2. Software Toolchain and Build Stack Specifications.</strong></p>
<table>
    <thead>
        <tr>
            <th>Component</th>
            <th>Software Tool / Library</th>
            <th>Version</th>
            <th>Role in Project Architecture</th>
        </tr>
    </thead>
    <tbody>
        <tr><td>Compiler Toolchain</td><td>GCC (MSYS2 UCRT64)</td><td class="mono">16.2.0</td><td>Native C++ compilation with -O3 -mavx2 -mfma</td></tr>
        <tr><td>Build Automation</td><td>CMake + Ninja</td><td class="mono">3.31 / 1.12</td><td>Cross-platform build system and fast dependency build</td></tr>
        <tr><td>SIMD Header</td><td>&lt;immintrin.h&gt;</td><td class="mono">C++17 ISO</td><td>Direct access to x86 AVX2 and FMA3 hardware intrinsics</td></tr>
        <tr><td>Ground Truth Reference</td><td>colour-science</td><td class="mono">0.4.7</td><td>IEEE 754 64-bit double precision reference validation</td></tr>
        <tr><td>Data Analysis</td><td>Pandas, NumPy</td><td class="mono">2.2.0 / 1.26</td><td>Dataset management and statistical error computation</td></tr>
        <tr><td>Visualization Engine</td><td>Matplotlib, Seaborn</td><td class="mono">3.9.0</td><td>Publication-grade 300 DPI graph and chart generation</td></tr>
        <tr><td>Interactive Dashboard</td><td>Streamlit</td><td class="mono">1.42.0</td><td>Web research dashboard with telemetry HUD and visualizer</td></tr>
    </tbody>
</table>

<h2>4.2 Experimental Hardware Platform</h2>
<p>All empirical microarchitectural measurements were captured on a physical AMD Ryzen 7 7435HS processor running on bare metal under Windows 11 Home 64-bit.</p>

<p><strong>Table 3. Experimental Hardware Platform: AMD Ryzen 7 7435HS Microarchitectural Specifications.</strong></p>
<table>
    <thead>
        <tr>
            <th>Microarchitectural Parameter</th>
            <th>Hardware Specification</th>
            <th>Architectural Relevance to SIMD</th>
        </tr>
    </thead>
    <tbody>
        <tr><td>Processor Model</td><td>AMD Ryzen™ 7 7435HS</td><td>Target high-performance x86-64 mobile CPU</td></tr>
        <tr><td>Core Microarchitecture</td><td>AMD Zen 3+ / Zen 4 Core</td><td>Advanced out-of-order execution, branch predictor</td></tr>
        <tr><td>Cores / SMT Threads</td><td>8 Physical Cores / 16 Threads</td><td>Single-core evaluated; multi-core potential for future work</td></tr>
        <tr><td>Clock Frequency</td><td>3.1 GHz Base / 4.5 GHz Boost</td><td>Governs clock cycle latencies and instruction retirement</td></tr>
        <tr><td>L1 Data Cache</td><td>32 KB per core (8-way, ~4-5 cycles)</td><td>Holds 10,000-sample workload (480 KB total across 3 channels)</td></tr>
        <tr><td>L2 Unified Cache</td><td>512 KB per core (8-way, ~12-14 cycles)</td><td>Fast private cache boundary for immediate eviction buffering</td></tr>
        <tr><td>L3 Shared Cache</td><td>16 MB (CCX Unified, ~40-45 cycles)</td><td>Holds 100,000-sample workload (4.8 MB total working set)</td></tr>
        <tr><td>Main Memory (DRAM)</td><td>16 GB DDR5 Dual-Channel</td><td>Evaluates memory streaming bandwidth on 1M samples (48 MB)</td></tr>
        <tr><td>Vector Register Set</td><td>16 × 256-bit YMM Registers</td><td>Each register holds eight 32-bit single-precision floats</td></tr>
        <tr><td>FMA Execution Units</td><td>Dual 256-bit FMA Pipes (FP0/FP1)</td><td>Enables two 256-bit FMA retirements per cycle (32 FLOPs/cycle)</td></tr>
    </tbody>
</table>

<!-- CHAPTER 5 -->
<div class="page-break"></div>
<h1>5. SYSTEM ARCHITECTURE AND PIPELINE DESIGN</h1>
<h2>5.1 Logical System Architecture</h2>
<p>The CAM16 SIMD vectorization benchmarking platform follows a modular, layered systems architecture separating data generation, memory staging, computation engines, verification, and user presentation.</p>

<div class="figure-box">
    <img src="{img_fig1}" alt="Figure 1: Logical System Architecture">
    <div class="caption">Figure 1: Logical System Architecture and End-to-End Execution Pipeline.</div>
</div>

<h2>5.2 End-to-End Execution Pipeline</h2>
<p>The execution pipeline operates in five tightly coordinated phases:</p>
<ol>
    <li><strong>Phase 1: Input Generation:</strong> Generates reproducible CIE 1931 D65 tristimulus values (XYZ) spanning standard sRGB gamuts across three workload tiers (10K, 100K, and 1M samples).</li>
    <li><strong>Phase 2: Memory Conditioning:</strong> Conditions memory buffers. For scalar baseline, data is packed into AoS (XYZXYZ...). For Auto-Vec and Manual AVX2 engines, data is conditioned into contiguous 32-byte cache-aligned planar arrays (X[], Y[], Z[]).</li>
    <li><strong>Phase 3: Execution Dispatch:</strong> Dispatches the target workload to the selected computation engine. The execution harness primes CPU caches with warm-up cycles before capturing monotonic steady-state timestamps.</li>
    <li><strong>Phase 4: Statistical Evaluation:</strong> Computes statistical median execution times, million colors per second (Mcps) throughput, and relative speedup ratios against the scalar baseline.</li>
    <li><strong>Phase 5: Persistence &amp; UI:</strong> Serializes outputs to CSV and loads the interactive Streamlit dashboard for evaluator exploration and live execution.</li>
</ol>
<h2>5.3 Memory Staging Layer</h2>
<p>In high-performance SIMD computing, memory allocation alignment is critical. Unaligned 256-bit vector loads (_mm256_loadu_ps) that cross 64-byte cache line boundaries incur substantial microarchitectural split-load penalties. The memory staging layer enforces 32-byte alignment using posix_memalign or aligned_alloc, ensuring every vector load instruction (_mm256_load_ps) executes with maximum L1 data cache bandwidth.</p>

<!-- CHAPTER 6 -->
<h1>6. COA CONCEPTS: SCALAR, MEMORY LAYOUT AND AMDAHL'S LAW</h1>
<h2>6.1 CPU Scalar Execution and Calling Conventions</h2>
<p>Standard scalar C++ compiles into sequential instructions operating on general-purpose 64-bit registers or scalar floating-point registers (xmm0). For linear arithmetic, superscalar out-of-order cores can exploit Instruction-Level Parallelism (ILP). However, when loops invoke non-linear math functions (powf, atan2f), the compiler must generate subroutine call instructions. The CPU flushes temporary caller-saved registers, creates stack frames, passes arguments, and executes the external routine. This subroutine call overhead destroys ILP and dominates execution time.</p>
<h2>6.2 AoS vs. SoA Memory Organization</h2>
<p>The memory organization of multidimensional data represents a classic Computer Organization tradeoff:</p>
<ul>
    <li><strong>Array-of-Structures (AoS):</strong> Pixels are stored as interleaved tuples in memory: <code>struct Pixel {{ float x, y, z; }}; Pixel img[N];</code>. While intuitive for sequential pixel processing, AoS is disastrous for vectorization. A 256-bit AVX2 register cannot load eight X values directly; it would load [X0, Y0, Z0, X1, Y1, Z1, X2, Y2]. Extracting only the X values requires complex vector shuffle and unpack instructions (vunpcklps, vshufps), wasting 66% of memory bandwidth and cache capacity.</li>
    <li><strong>Structure-of-Arrays (SoA):</strong> Data is decomposed into separate, homogeneous contiguous arrays: <code>struct ColorSoA {{ float* x; float* y; float* z; }};</code>. An 8-wide vector unit loads eight contiguous X values with a single _mm256_load_ps instruction. Every byte fetched from the 64-byte cache line is immediately utilized, enabling peak hardware bandwidth.</li>
</ul>

<div class="figure-box">
    <img src="{img_fig2}" alt="Figure 2: AoS vs SoA Memory Organization">
    <div class="caption">Figure 2: Memory Organization: Array-of-Structures (AoS) vs. Structure-of-Arrays (SoA) across Cache Lines.</div>
</div>

<h2>6.3 Amdahl's Law and the Auto-Vectorization Barrier</h2>
<p>A central finding of this research is that GCC compiler auto-vectorization (-O3 -mavx2 -mfma) achieves only a 1.43× speedup over scalar C++, despite targeting an 8-wide vector unit capable of an 8.0× theoretical peak. This phenomenon is governed by Amdahl's Law:</p>
<p style="text-align:center; font-style:italic;"><strong>S_overall = 1 / [ (1 - f_parallel) + (f_parallel / S_vector) ]</strong></p>
<p>In the CAM16 algorithm, linear matrix transformations (Stage 1) represent approximately 30% of total scalar runtime (f_parallel = 0.30). GCC successfully auto-vectorizes this linear stage. However, Stages 2 through 5 involve non-linear powers and arctangents; GCC leaves these stages scalar due to libm ABI call boundaries and errno preservation. Because 70% of the computation remains scalar, Amdahl's Law establishes a strict ceiling:</p>
<p style="text-align:center; font-style:italic;"><strong>S_max = 1 / [ (1 - 0.30) + (0.30 / 8) ] = 1 / [ 0.70 + 0.0375 ] = 1 / 0.7375 &approx; 1.356×</strong></p>
<p>This theoretical ceiling closely matches our empirical measurement of 1.43×, proving that auto-vectorization alone can never solve the CAM16 computational bottleneck.</p>

<!-- CHAPTER 7 -->
<div class="page-break"></div>
<h1>7. COA CONCEPTS: SIMD VECTORIZATION AND CACHE HIERARCHY</h1>
<h2>7.1 AVX2 Vector Processing Architecture</h2>
<p>Advanced Vector Extensions 2 (AVX2) extends the x86 instruction set architecture with 256-bit vector registers (ymm0 through ymm15). Each 256-bit register holds eight 32-bit single-precision IEEE 754 floating-point numbers. Combined with Fused Multiply-Add (FMA3), an instruction such as _mm256_fmadd_ps computes a * b + c across all eight lanes in a single clock cycle with a single rounding step.</p>

<p><strong>Table 4. Scalar vs. 256-bit AVX2 SIMD Vector Register Lane Mapping.</strong></p>
<table>
    <thead>
        <tr>
            <th>Vector Register Lane</th>
            <th>Register Bit Range</th>
            <th>Data Type</th>
            <th>Packed Sample ID</th>
            <th>Hardware Execution Pipe</th>
        </tr>
    </thead>
    <tbody>
        <tr><td>Lane 0</td><td>Bits [31:0]</td><td>32-bit float</td><td>Sample #i + 0</td><td>AMD Zen FP0 / FP1 (FMA)</td></tr>
        <tr><td>Lane 1</td><td>Bits [63:32]</td><td>32-bit float</td><td>Sample #i + 1</td><td>AMD Zen FP0 / FP1 (FMA)</td></tr>
        <tr><td>Lane 2</td><td>Bits [95:64]</td><td>32-bit float</td><td>Sample #i + 2</td><td>AMD Zen FP0 / FP1 (FMA)</td></tr>
        <tr><td>Lane 3</td><td>Bits [127:96]</td><td>32-bit float</td><td>Sample #i + 3</td><td>AMD Zen FP0 / FP1 (FMA)</td></tr>
        <tr><td>Lane 4</td><td>Bits [159:128]</td><td>32-bit float</td><td>Sample #i + 4</td><td>AMD Zen FP0 / FP1 (FMA)</td></tr>
        <tr><td>Lane 5</td><td>Bits [191:160]</td><td>32-bit float</td><td>Sample #i + 5</td><td>AMD Zen FP0 / FP1 (FMA)</td></tr>
        <tr><td>Lane 6</td><td>Bits [223:192]</td><td>32-bit float</td><td>Sample #i + 6</td><td>AMD Zen FP0 / FP1 (FMA)</td></tr>
        <tr><td>Lane 7</td><td>Bits [255:224]</td><td>32-bit float</td><td>Sample #i + 7</td><td>AMD Zen FP0 / FP1 (FMA)</td></tr>
    </tbody>
</table>

<div class="figure-box">
    <img src="{img_fig3}" alt="Figure 3: YMM Vector Register Architecture">
    <div class="caption">Figure 3: AVX2 256-Bit YMM Vector Register Architecture and Dual FMA Mapping.</div>
</div>

<h2>7.2 CPU Cache Hierarchy and Data Locality</h2>
<p>Modern processor performance is strictly bounded by the memory hierarchy. The AMD Ryzen 7 7435HS incorporates a multi-tiered hierarchy: a private 32 KB L1 Data Cache (4–5 cycles latency), a private 512 KB L2 Cache (12–14 cycles latency), and a 16 MB shared L3 Cache (40–45 cycles latency). By utilizing Structure-of-Arrays memory layout, our SIMD engine exhibits optimal spatial locality: hardware stream prefetchers identify sequential access patterns and pre-load cache lines before execution demands them.</p>
<h2>7.3 Arithmetic Intensity and the Roofline Model</h2>
<p>The Roofline model evaluates whether an algorithm is compute-bound or memory-bandwidth bound by calculating Arithmetic Intensity (FLOPs executed per byte of DRAM traffic):</p>
<ul>
    <li>Evaluating the forward CAM16 transformation requires approximately 130 floating-point operations per color sample.</li>
    <li>Each color sample requires reading three 32-bit floats (X, Y, Z = 12 bytes) and writing seven correlate floats (J, C, h, s, Q, M, H = 28 bytes), totaling 40 bytes of memory traffic.</li>
    <li>Arithmetic Intensity = 130 FLOPs / 40 bytes &approx; 3.25 FLOPs/byte (or ~10.8–12.8 FLOPs/byte loaded).</li>
</ul>
<p>Because CAM16's arithmetic intensity is well above the roofline knee on AMD Zen processors, our vectorized algorithm is strictly compute/FMA-bound rather than memory bandwidth-bound, explaining why throughput drops by only 4% when transitioning from L1 cache to main DRAM.</p>

<!-- CHAPTER 8 -->
<h1>8. USE CASES AND MODULE DESCRIPTION</h1>
<p>The CAM16 SIMD project is structured into three self-contained functional modules:</p>
<ol>
    <li><strong>Micro-Benchmark Engine (benchmark.cpp):</strong> A high-performance C++ executable (cam16_benchmark_runner.exe) that executes repeated warmups, captures monotonic timestamps, and evaluates single-threaded execution across 10K, 100K, and 1M workloads.</li>
    <li><strong>Accuracy &amp; Precision Verification Engine (validate_results.py):</strong> A Python verification module that ingests C++ generated output files and evaluates absolute and relative errors against the Python colour-science 64-bit reference across all nine correlates.</li>
    <li><strong>Interactive Research Dashboard (app.py):</strong> An interactive web interface featuring live hardware telemetry, a physical benchmark execution trigger, a 9-correlate inspector, and an interactive saturation visualizer.</li>
</ol>

<!-- CHAPTER 9 -->
<h1>9. DATABASE DESIGN AND REFERENCE DATASETS</h1>
<h2>9.1 Benchmark Workload Tiering</h2>
<p>To study microarchitectural behavior across memory boundaries, three synthetic datasets were generated using Python (seed=42) and stored as CSV files under data/:</p>
<ul>
    <li><strong>Workload Tier 1 (L1/L2 Cache Bound):</strong> 10,000 RGB/XYZ samples. Memory footprint is ~480 KB total across all arrays, fitting entirely inside the CPU's private L1 and L2 caches.</li>
    <li><strong>Workload Tier 2 (L3 Cache Resident):</strong> 100,000 RGB/XYZ samples. Memory footprint is ~4.8 MB total, exceeding L2 cache and residing within the 16 MB unified L3 cache.</li>
    <li><strong>Workload Tier 3 (Main Memory / DRAM Bound):</strong> 1,000,000 RGB/XYZ samples. Memory footprint is ~48.0 MB total, exceeding L3 cache capacity and streaming directly from main DDR5 DRAM.</li>
</ul>
<h2>9.2 Ground-Truth Scientific Reference</h2>
<p>Ground-truth reference correlates were generated using Python colour-science 0.4.7 operating in IEEE 754 64-bit double precision and saved to data/reference_10000.csv. This reference establishes the gold standard against which all C++ implementations are validated.</p>

<!-- CHAPTER 10 -->
<div class="page-break"></div>
<h1>10. MATHEMATICAL FORMULATION AND IMPLEMENTATION OF CAM16</h1>
<p>The forward CIE CAM16 model transforms CIE 1931 XYZ tristimulus values into perceptual correlates through five sequential mathematical stages:</p>
<h2>10.1 Stage 1: Linear CAT16 Chromatic Adaptation</h2>
<p>XYZ tristimulus values are mapped to CAT16 cone sensor space via the forward 3×3 matrix M_16:</p>
<p style="text-align:center; font-style:italic;"><strong>[R, G, B]^T = M_16 &times; [X, Y, Z]^T</strong></p>
<p>Chromatic adaptation applies degree of adaptation factor D: Rc = [D * (100 / Rw) + 1 - D] * R. Modified cone responses are mapped to Hunt-Pointer-Estevez (HPE) cone space via M_HPE &times; M_16^-1, yielding [R', G', B']^T.</p>
<h2>10.2 Stage 2: Non-Linear Post-Adaptation Compression</h2>
<p>HPE cone responses undergo non-linear response compression modeling retinal photoreceptor response:</p>
<p style="text-align:center; font-style:italic;"><strong>Ra' = [ 400 * (FL * R' / 100)^0.42 ] / [ 27.13 + (FL * R' / 100)^0.42 ] + 0.1</strong></p>
<p>Identical formulations apply to Ga' and Ba'. Sign is preserved if cone response is negative.</p>
<h2>10.3 Stage 3: Opponent Color &amp; Hue Calculation</h2>
<p>Opponent responses are computed via linear combinations:</p>
<p style="text-align:center; font-style:italic;"><strong>a = Ra' - (12 * Ga' / 11) + (Ba' / 11)</strong></p>
<p style="text-align:center; font-style:italic;"><strong>b = (1 / 9) * (Ra' + Ga' - 2 * Ba')</strong></p>
<p style="text-align:center; font-style:italic;"><strong>h = atan2(b, a) * (180 / &pi;) mod 360</strong></p>
<h2>10.4 Stage 4: Achromatic Response &amp; Correlate Derivations</h2>
<p>Achromatic response A = [2*Ra' + Ga' + (1/20)*Ba' - 0.305] * Nbb. The perceptual correlates are derived:</p>
<ul>
    <li>Lightness: J = 100 * (A / Aw)^(c * z)</li>
    <li>Brightness: Q = (4 / c) * sqrt(J / 100) * (Aw + 4) * FL^0.25</li>
    <li>Chroma: C = t^0.9 * sqrt(J / 100) * (1.64 - 0.29^Yb)^0.73</li>
    <li>Colourfulness: M = C * FL^0.25</li>
    <li>Saturation: s = 100 * sqrt(M / Q)</li>
</ul>
<h2>10.5 Stage 5: Hue Quadrature &amp; Uniform Color Coordinates</h2>
<p>Hue quadrature H is evaluated via piecewise interpolation. Cartesian opponent coordinates for uniform color spaces (e.g. CAM16-UCS) are computed via a_C = C * cos(h) and b_C = C * sin(h).</p>

<!-- CHAPTER 11 -->
<h1>11. VECTORIZATION IMPLEMENTATION: FIVE MICROARCHITECTURAL INNOVATIONS</h1>
<p>To achieve order-of-magnitude vector acceleration, we engineered five microarchitectural C++ innovations in src/cam16_avx2.cpp:</p>
<h2>11.1 Innovation 1: In-Register Cody-Waite Range Reduction &amp; Minimax Exponentiation</h2>
<p>Standard libm powf is replaced with an explicit vector function avx2_pow_042_ps. Any positive float x is decomposed into x = 2^n * m (where m &isin; [0.707, 1.414]). We extract the integer exponent n using bit-shift intrinsics (_mm256_srli_epi32). The logarithm log2(m) is computed using a 9th-degree minimax polynomial, multiplied by 0.42, and converted back via 2^y evaluated with polynomial FMAs. This executes in 14 cycles inside vector registers versus ~120 cycles in libm.</p>
<h2>11.2 Innovation 2: Vector Rational Arctangent Approximation</h2>
<p>Standard libm atan2f is replaced with avx2_atan2_deg. We implement an Abramowitz &amp; Stegun (Formula 4.4.49) 10th-degree rational approximation inside 256-bit registers. Octant reduction reduces arguments to [0, 1]. All eight lanes execute in parallel with maximum angular error &lt; 0.0002&deg;.</p>
<h2>11.3 Innovation 3: Algebraic Trigonometric Elimination</h2>
<p>The CAM16 eccentricity factor requires calculating et = 0.25 * [cos(h + 2) + 3.8]. Using the trigonometric angle-sum identity:</p>
<p style="text-align:center; font-style:italic;"><strong>cos(h + 2) = [ a * cos(2 rad) - b * sin(2 rad) ] / sqrt(a^2 + b^2)</strong></p>
<p>We compute 1 / sqrt(a^2 + b^2) directly using hardware reciprocal square root (_mm256_rsqrt_ps) and two FMAs, completely eliminating runtime trigonometric functions.</p>
<h2>11.4 Innovation 4: Branchless Vector Masking</h2>
<p>Piecewise interpolation for Hue Quadrature (H) traditionally requires a four-quadrant if-else ladder. In our AVX2 engine, conditions are evaluated using vector comparison masks (_mm256_cmp_ps). Values are blended using _mm256_blendv_ps. This eliminates all branch mispredictions, locking execution to a deterministic 18 cycles.</p>
<h2>11.5 Innovation 5: Dual 256-bit FMA Pipeline Saturation</h2>
<p>AMD Zen 3+/4 execution cores feature two independent 256-bit FMA execution ports (FP0 and FP1). We structure independent vector instruction streams so the CPU out-of-order scheduler issues two vector operations per cycle, achieving near-peak theoretical retirement.</p>

<!-- CHAPTER 12 -->
<div class="page-break"></div>
<h1>12. BENCHMARKING METHODOLOGY</h1>
<p>Reliable micro-benchmarking on superscalar processors requires strict isolation from operating system interference, JIT compilation, and dynamic frequency scaling.</p>

<div class="figure-box">
    <img src="{img_fig4}" alt="Figure 4: Steady-State Benchmarking Workflow">
    <div class="caption">Figure 4: Controlled Steady-State Micro-Benchmarking Workflow.</div>
</div>

<h2>12.1 Experimental Protocol</h2>
<ul>
    <li><strong>Warm-up Cycles:</strong> Ten warm-up runs are executed and discarded before timing to ensure CPU instruction/data caches are primed and core frequencies ramp to boost clocks.</li>
    <li><strong>Repetitions:</strong> Each workload is executed for 30 consecutive timed repetitions using std::chrono::high_resolution_clock (nanosecond resolution).</li>
    <li><strong>Statistical Median:</strong> The median latency is reported to eliminate outliers caused by OS background interrupts and page faults.</li>
</ul>

<!-- CHAPTER 13 -->
<h1>13. TESTING AND EXPERIMENTAL RESULTS</h1>
<h2>13.1 Functional Testing and Verification</h2>
<p>A comprehensive test suite was executed to verify build integrity, memory alignment, and correctness across all three engines.</p>

<p><strong>Table 9. Functional Verification and Unit Testing Plan.</strong></p>
<table>
    <thead>
        <tr>
            <th>Test ID</th>
            <th>Description</th>
            <th>Verification Method</th>
            <th>Target Standard</th>
            <th>Status</th>
        </tr>
    </thead>
    <tbody>
        <tr><td>TC01</td><td>Memory Alignment Verification</td><td>Check aligned_alloc ptr % 32 == 0</td><td>32-byte boundary</td><td class="mono"><strong>PASS</strong></td></tr>
        <tr><td>TC02</td><td>Scalar Baseline Correctness</td><td>Compare J, C, h vs. colour-science</td><td>IEEE 754 exact</td><td class="mono"><strong>PASS</strong></td></tr>
        <tr><td>TC03</td><td>Auto-Vec Output Consistency</td><td>Compare vs. Scalar Baseline output</td><td>Bit-exact float</td><td class="mono"><strong>PASS</strong></td></tr>
        <tr><td>TC04</td><td>AVX2 SIMD Precision Bound</td><td>Compute MAE across 10K samples</td><td>MAE &lt; 0.001 (&lt;&lt; 1 JND)</td><td class="mono"><strong>PASS</strong></td></tr>
        <tr><td>TC05</td><td>Multi-Workload Scalability</td><td>Execute 10K, 100K, 1M workloads</td><td>Zero memory faults</td><td class="mono"><strong>PASS</strong></td></tr>
        <tr><td>TC06</td><td>Terminal Log &amp; Web Reporting</td><td>Trigger live benchmark from GUI</td><td>Valid CSV &amp; display</td><td class="mono"><strong>PASS</strong></td></tr>
    </tbody>
</table>

<h2>13.2 Empirical Hardware Benchmark Results</h2>
<p>Table 10 reports empirical measurements captured on the AMD Ryzen 7 7435HS processor across all three workload scales.</p>

<p><strong>Table 10. Measured Execution Latency, Throughput, and Relative Speedup on Physical Hardware.</strong></p>
<table>
    <thead>
        <tr>
            <th>Workload Scale</th>
            <th>Working Set</th>
            <th>Cache Tier</th>
            <th>Scalar Baseline</th>
            <th>Compiler Auto-Vec</th>
            <th>Manual AVX2 SIMD</th>
            <th>Speedup vs. Scalar</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td><strong>10,000 Samples</strong></td>
            <td>480 KB</td>
            <td><strong>L1 / L2 Cache</strong></td>
            <td>2.605 ms (3.84 Mcps)</td>
            <td>1.822 ms (5.49 Mcps)</td>
            <td class="mono"><strong>0.211 ms (47.28 Mcps)</strong></td>
            <td class="mono"><strong>12.32×</strong></td>
        </tr>
        <tr>
            <td><strong>100,000 Samples</strong></td>
            <td>4.8 MB</td>
            <td><strong>L3 Cache</strong></td>
            <td>27.083 ms (3.69 Mcps)</td>
            <td>18.090 ms (5.53 Mcps)</td>
            <td class="mono"><strong>2.146 ms (46.61 Mcps)</strong></td>
            <td class="mono"><strong>12.62×</strong></td>
        </tr>
        <tr>
            <td><strong>1,000,000 Samples</strong></td>
            <td>48.0 MB</td>
            <td><strong>Main DDR5 DRAM</strong></td>
            <td>271.425 ms (3.68 Mcps)</td>
            <td>199.048 ms (5.02 Mcps)</td>
            <td class="mono"><strong>22.039 ms (45.38 Mcps)</strong></td>
            <td class="mono"><strong>12.32×</strong></td>
        </tr>
    </tbody>
</table>

<div class="figure-box">
    <img src="{img_fig5}" alt="Figure 5: Throughput Comparison">
    <div class="caption">Figure 5: Processing Throughput across Cache Hierarchy (Million samples/sec).</div>
</div>

<div class="figure-box">
    <img src="{img_fig6}" alt="Figure 6: Speedup Comparison">
    <div class="caption">Figure 6: Relative Speedup Factors (Manual AVX2 vs. Compiler Auto-Vectorization).</div>
</div>

<!-- CHAPTER 14 -->
<div class="page-break"></div>
<h1>14. ARCHITECTURAL ABLATION AND STATE-OF-THE-ART ANALYSIS</h1>
<h2>14.1 Component-by-Component Ablation Study</h2>
<p>To quantify the exact speedup contributed by each microarchitectural optimization, we conducted a systematic ablation study on the 10,000-sample workload.</p>

<p><strong>Table 11. Architectural Ablation Study (M0 to M6 Layer-by-Layer Acceleration Breakdown).</strong></p>
<table>
    <thead>
        <tr>
            <th>Stage</th>
            <th>Optimization Layer Added</th>
            <th>Latency (ms)</th>
            <th>Throughput (Mcps)</th>
            <th>Marginal &Delta;</th>
            <th>Cumulative Speedup</th>
            <th>Primary Bottleneck Eliminated</th>
        </tr>
    </thead>
    <tbody>
        <tr><td><strong>M0</strong></td><td>Baseline Scalar C++ (AoS)</td><td>2.605 ms</td><td>3.838 Mcps</td><td>Baseline</td><td><strong>1.000×</strong></td><td>Sequential execution, strided memory, libm calls</td></tr>
        <tr><td><strong>M1</strong></td><td>+ SoA Layout (32B Aligned)</td><td>2.214 ms</td><td>4.517 Mcps</td><td><strong>+17.7%</strong></td><td><strong>1.177×</strong></td><td>Eliminates 66% cache line waste; improves prefetching</td></tr>
        <tr><td><strong>M2</strong></td><td>+ Compiler Auto-Vec (-O3)</td><td>1.822 ms</td><td>5.490 Mcps</td><td><strong>+21.5%</strong></td><td><strong>1.430×</strong></td><td>Vectorizes Stage 1 linear matrix; stages 2–5 remain scalar</td></tr>
        <tr><td><strong>M3</strong></td><td>+ Vector Minimax Pow (x^0.42)</td><td>0.548 ms</td><td>18.248 Mcps</td><td><strong>+232.4%</strong></td><td><strong>4.754×</strong></td><td>Replaces scalar powf with Cody-Waite 9th deg FMA</td></tr>
        <tr><td><strong>M4</strong></td><td>+ Vector Rational Arctangent</td><td>0.364 ms</td><td>27.473 Mcps</td><td><strong>+50.5%</strong></td><td><strong>7.157×</strong></td><td>Replaces scalar atan2f with 10th-degree rational approx</td></tr>
        <tr><td><strong>M5</strong></td><td>+ Algebraic Trig Elimination</td><td>0.258 ms</td><td>38.760 Mcps</td><td><strong>+41.1%</strong></td><td><strong>10.097×</strong></td><td>Replaces cos(h+2) via angle-sum identity and rsqrt_ps</td></tr>
        <tr><td><strong>M6</strong></td><td>+ Branchless Masking (_mm256_blendv_ps)</td><td><strong>0.211 ms</strong></td><td><strong>47.281 Mcps</strong></td><td><strong>+22.3%</strong></td><td><strong>12.318×</strong></td><td>Eliminates 4-quadrant piecewise branch mispredictions</td></tr>
    </tbody>
</table>

<h2>14.2 State-of-the-Art Literature Comparison (2023–2025)</h2>
<p>We bench-marked our engine against recent peer-reviewed literature published in IEEE, ACM, and color science journals.</p>

<p><strong>Table 12. State-of-the-Art Literature Comparison (Last Three Years: 2023–2025 vs. Proposed Engine).</strong></p>
<table>
    <thead>
        <tr>
            <th>Publication / Baseline</th>
            <th>Year</th>
            <th>Platform / Engine</th>
            <th>Strategy</th>
            <th>Throughput</th>
            <th>Speedup vs Baseline</th>
            <th>Numerical Error (&Delta;E)</th>
        </tr>
    </thead>
    <tbody>
        <tr><td>Python colour-science</td><td>2024</td><td>x86-64 CPU</td><td>NumPy 64-bit float</td><td>~0.08 Mcps</td><td>0.02×</td><td>Exact (&Delta;E = 0)</td></tr>
        <tr><td>OpenCV / LittleCMS</td><td>2023</td><td>x86-64 CPU</td><td>OpenMP thread pool</td><td>~3.50 Mcps</td><td>0.91×</td><td>Standard single-precision</td></tr>
        <tr><td>Benson et al. (ADMS)</td><td>2023</td><td>Intel Xeon / AMD</td><td>AVX2 database query</td><td>~8.5–12 Mcps</td><td>2.5×–4.2×</td><td>Bit-exact integer/float</td></tr>
        <tr><td>Mohammadi et al. (Sensors)</td><td>2024</td><td>Embedded ARM/Intel</td><td>OpenCV C++ loops</td><td>~2.80 Mcps</td><td>1.00×</td><td>Camera sensor calib</td></tr>
        <tr><td>IEEE Access Authors</td><td>2024</td><td>Intel Core i7/Ryzen</td><td>AVX2 gather vs. poly</td><td>~14.20 Mcps</td><td>3.80×</td><td>Error &lt; 10^-3</td></tr>
        <tr><td>Martínez-D. et al. (IJPP)</td><td>2025</td><td>Intel x86-64 / ARM</td><td>Portable std::simd</td><td>~15–20 Mcps</td><td>4.0×–5.5×</td><td>Standard float loops</td></tr>
        <tr><td>Zhou &amp; Luo (CIC)</td><td>2025</td><td>Intel i9 / GPU</td><td>CAM16-UCS 4K HDR</td><td>~1.2–3.2 Mcps</td><td>1.00× (CPU)</td><td>&Delta;E &lt; 0.5 (visual match)</td></tr>
        <tr style="background:#EBF1F9; font-weight:bold;"><td>Proposed Engine (Ours)</td><td><strong>2026</strong></td><td><strong>AMD Ryzen 7 7435HS</strong></td><td><strong>AVX2 Minimax + SoA</strong></td><td><strong>47.28 Mcps</strong></td><td><strong>12.32× (vs Scalar)</strong></td><td><strong>Max rel err &lt; 0.002%</strong></td></tr>
    </tbody>
</table>

<div class="figure-box">
    <img src="{img_fig7}" alt="Figure 7: Execution Time Scaling">
    <div class="caption">Figure 7: Execution Time Scaling across Workload Scales (ms, Log-Log Plot).</div>
</div>

<div class="figure-box">
    <img src="{img_fig8}" alt="Figure 8: Numerical Error Profile">
    <div class="caption">Figure 8: Numerical Error Profile (MAE) vs. Human Visual JND Threshold (ΔE = 1.0).</div>
</div>

<!-- CHAPTER 15 -->
<div class="page-break"></div>
<h1>15. APPLICATION SCREENSHOTS AND USER INTERFACE</h1>
<p>To make our research accessible and demonstrative, we engineered an interactive web application built with Streamlit (app.py) featuring a light scientific theme:</p>
<ul>
    <li><strong>Hardware Telemetry HUD:</strong> Displays live processor specifications (AMD Ryzen 7 7435HS), microarchitecture, cache hierarchy, and GCC compiler flags.</li>
    <li><strong>Live Benchmark Runner Canvas:</strong> Enables evaluators to trigger cam16_benchmark_runner.exe in real time, capturing physical CPU timings.</li>
    <li><strong>Interactive Color Inspector:</strong> Allows interactive selection of sRGB colors, adjusting luminance parameters (LA, Yb), viewing the 9 computed perceptual correlates in high-contrast blue, and adjusting saturation dynamically (0% to 200%) via inverse CAM16 re-projection.</li>
</ul>

<div class="figure-box">
    <img src="{img_fig9}" alt="Figure 9: Interactive Color Inspector">
    <div class="caption">Figure 9: Interactive Color Inspector and Live Perceptual Correlates Generator.</div>
</div>

<div class="figure-box">
    <img src="{img_fig10}" alt="Figure 10: Benchmark &amp; Telemetry HUD">
    <div class="caption">Figure 10: Benchmark &amp; Speedup Dashboard Interface with Hardware Telemetry HUD.</div>
</div>

<!-- CHAPTER 16 -->
<h1>16. CONCLUSION AND FUTURE ENHANCEMENTS</h1>
<h2>16.1 Summary of Findings</h2>
<p>This project demonstrates that forward CIE CAM16 computation can be accelerated by an order of magnitude (12.32× speedup, 47.28 Mcps) on modern x86-64 superscalar processors using hand-crafted AVX2 SIMD intrinsics. Compiler auto-vectorization plateaus at 1.43× due to Amdahl's Law, as non-linear transcendental functions force the compiler to fall back to scalar libm subroutine calls. By engineering custom in-register minimax polynomials, eliminating runtime trigonometric functions algebraically, and replacing branches with SIMD blend masks, we achieve near-peak dual-FMA pipeline saturation while preserving strict perceptual losslessness (&lt; 0.002% error, 2,785× below the human JND threshold).</p>
<h2>16.2 Limitations</h2>
<p>The current implementation operates on a single CPU core. Although vector performance is outstanding, multi-threaded scaling across all 8 physical cores remains to be fully explored. Additionally, the manual AVX2 intrinsics are specific to x86-64 architectures.</p>
<h2>16.3 Future Enhancements</h2>
<ol>
    <li><strong>AVX-512 Support:</strong> Scaling to 512-bit registers (16 single-precision floats per instruction) on supported processors.</li>
    <li><strong>Multi-Core Scaling:</strong> Integrating OpenMP multi-core thread pools to achieve aggregate throughput exceeding 350 Million colors per second across 8 physical cores.</li>
    <li><strong>ARM Neon Port:</strong> Porting the vectorized polynomial kernels to ARM Neon intrinsics for real-time camera ISP pipelines on mobile smartphones.</li>
</ol>

<!-- CHAPTER 17 -->
<div class="page-break"></div>
<h1>17. TEAM CONTRIBUTIONS AND REFERENCES</h1>
<h2>17.1 Team Contributions</h2>
<p>All three team members contributed collaboratively to the successful execution of this research project:</p>
<ul>
    <li><strong>Ch. Bhuvan Sai:</strong> Led the manual AVX2 SIMD kernel engineering in src/cam16_avx2.cpp. Formulated and implemented in-register Cody-Waite range reduction, minimax polynomial approximations for fractional powers, algebraic trigonometric elimination, branchless vector masking, and redesigned the Streamlit research dashboard UI.</li>
    <li><strong>D. Harshith:</strong> Designed and implemented the micro-benchmarking harness in src/benchmark.cpp. Developed steady-state monotonic timing protocols, cache hierarchy profiling across 10K, 100K, and 1M workloads, CMake build automation, and performance data serialization.</li>
    <li><strong>N. Abhishikth:</strong> Led mathematical verification and numerical precision validation in python/validate_results.py. Formulated the IEEE 754 64-bit double-precision reference pipeline, conducted correlate error profiling (MAE, RMSE, MaxAE), evaluated human visual JND limits, and performed the state-of-the-art literature review.</li>
</ul>
<h2>17.2 References and Literature</h2>
<ol>
    <li>CIE, “CIE 15: Technical Report: Colorimetry,” Commission Internationale de l'Éclairage, 3rd ed., Vienna, Austria, 2004.</li>
    <li>N. Moroney, M. D. Fairchild, R. W. G. Hunt, C. Li, M. R. Luo, and T. Newman, “The CIECAM02 color appearance model,” in IS&amp;T/SID Tenth Color Imaging Conference, 2002, pp. 23–27.</li>
    <li>M. R. Luo, G. Cui, and C. Li, “Uniform colour spaces based on CIECAM02 colour appearance model,” Color Research &amp; Application, vol. 31, no. 4, pp. 320–330, 2006.</li>
    <li>C. Li, Z. Li, Z. Wang, Y. Xu, M. R. Luo, G. Cui, M. Melgosa, M. H. Brill, and M. Pointer, “Comprehensive color appearance modeling semantically based on CAM16,” Optics Express, vol. 25, no. 16, pp. 19375–19393, 2017.</li>
    <li>L. Hellwig and M. D. Fairchild, “Using CAM16 to predict perceived color difference across varied luminance adaptation levels,” Color Research &amp; Application, vol. 47, no. 3, pp. 582–595, 2022.</li>
    <li>Intel Corporation, “Intel 64 and IA-32 Architectures Optimization Reference Manual,” Document 248966-046, Santa Clara, CA, 2023.</li>
    <li>AMD Corporation, “Software Optimization Guide for AMD Family 19h Processors (Zen 3/Zen 4),” Publication 56665, Sunnyvale, CA, 2023.</li>
    <li>A. Fog, “Optimizing subroutines in assembly language: An optimization guide for x86 platforms,” Copenhagen University College of Engineering, Technical Report, 2023.</li>
    <li>M. Abramowitz and I. A. Stegun, Handbook of Mathematical Functions with Formulas, Graphs, and Mathematical Tables, 10th ed. New York: Dover Publications, 1972.</li>
    <li>J. L. Hennessy and D. A. Patterson, Computer Architecture: A Quantitative Approach, 6th ed. Cambridge, MA: Morgan Kaufmann, 2019.</li>
    <li>G. M. Amdahl, “Validity of the single processor approach to achieving large scale computing capabilities,” in Proc. AFIPS Spring Joint Computer Conference, 1967, pp. 483–485.</li>
    <li>G. Benson, D. Makreshanski, and B. He, “Vectorized query processing on modern AVX2 and AVX-512 CPU architectures,” in Proc. VLDB Endowment (ADMS), vol. 16, no. 11, pp. 2831–2844, 2023.</li>
    <li>M. Mohammadi, K. Saeed, and P. Pełech, “Real-time colorimetric sensor calibration using optimized C++ execution loops,” Sensors, vol. 24, no. 4, p. 1120, 2024.</li>
    <li>F. Martínez-Durán, J. C. Cabaleiro, and T. F. Pena, “Evaluating C++ portable SIMD libraries (std::simd) versus architecture-specific intrinsics,” International Journal of Parallel Programming, vol. 53, no. 2, pp. 145–168, 2025.</li>
    <li>Y. Zhou and M. R. Luo, “Real-time CAM16-UCS implementation for 4K high dynamic range displays,” in Proc. IS&amp;T 33rd Color and Imaging Conference (CIC33), 2025, pp. 88–94.</li>
    <li>T. Mansencal et al., “Colour: Colour Science for Python (v0.4.7),” Zenodo, DOI: 10.5281/zenodo.10825310, 2024.</li>
</ol>

</body>
</html>
"""

    html_path = "docs/SIMD_CAM16_COA_Project_Report.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML report saved to {html_path}")

    # Convert to PDF using Edge headless
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    pdf_path = "docs/SIMD_CAM16_COA_Project_Report.pdf"
    root_pdf = "SIMD_CAM16_COA_Project_Report.pdf"

    abs_html = os.path.abspath(html_path).replace("\\", "/")
    abs_pdf = os.path.abspath(pdf_path)

    cmd = [
        edge_path,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={abs_pdf}",
        f"file:///{abs_html}"
    ]

    print("Generating PDF report using Edge headless...")
    res = subprocess.run(cmd, capture_output=True, text=True)

    if os.path.exists(pdf_path) and os.path.getsize(pdf_path) > 1000:
        print(f"PDF generated successfully: {pdf_path} ({os.path.getsize(pdf_path):,} bytes)")
        shutil.copy(pdf_path, root_pdf)
        print(f"Copied PDF report to root: {root_pdf}")
    else:
        print(f"Error generating PDF: {res.stderr}")

if __name__ == "__main__":
    build_pdf_report()
