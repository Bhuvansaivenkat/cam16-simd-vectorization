cmake_minimum_required(VERSION 3.20)
project(CAM16_SIMD_Project CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Check for GCC / Clang
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    # Base high-performance optimization flags
    set(COMMON_FLAGS -Wall -Wextra -O3)
    
    # AVX2 and FMA3 instruction set flags
    set(AVX2_FLAGS -mavx2 -mfma)
    
    # Vectorization diagnostic flags for compiler inspection
    # Emits compiler decisions on which loops were auto-vectorized and which were missed
    set(VEC_DIAG_FLAGS -fopt-info-vec-optimized-missed)
else()
    message(WARNING "Compiler is not GCC or Clang. MSYS2 UCRT64 GCC is recommended for this project.")
endif()

include_directories(include)

# Scalar implementation module (compiled with standard -O3, baseline)
add_library(cam16_scalar STATIC
    src/cam16_scalar.cpp
)
target_compile_options(cam16_scalar PRIVATE ${COMMON_FLAGS})

# Auto-vectorized implementation module (compiled with -O3 -mavx2 -mfma + vector diagnostics)
add_library(cam16_auto STATIC
    src/cam16_auto.cpp
)
target_compile_options(cam16_auto PRIVATE ${COMMON_FLAGS} ${AVX2_FLAGS} ${VEC_DIAG_FLAGS})

# Manual AVX2 implementation module (compiled with -O3 -mavx2 -mfma)
add_library(cam16_avx2 STATIC
    src/cam16_avx2.cpp
)
target_compile_options(cam16_avx2 PRIVATE ${COMMON_FLAGS} ${AVX2_FLAGS})

# Benchmarking harness library
add_library(cam16_benchmark STATIC
    src/benchmark.cpp
)
target_compile_options(cam16_benchmark PRIVATE ${COMMON_FLAGS})

# Main benchmarking and validation binary
add_executable(cam16_benchmark_runner
    src/main.cpp
)
target_compile_options(cam16_benchmark_runner PRIVATE ${COMMON_FLAGS} ${AVX2_FLAGS})
target_link_libraries(cam16_benchmark_runner PRIVATE
    cam16_scalar
    cam16_auto
    cam16_avx2
    cam16_benchmark
)
