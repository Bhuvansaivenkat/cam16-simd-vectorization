#pragma once
#include "cam16_types.h"
#include <vector>

namespace cam16 {

// Precomputes all invariant parameters from viewing conditions
CAM16Coefficients compute_coefficients(const ViewingConditions& vc);

// Runtime CPU feature check to verify hardware AVX2 and FMA support
bool is_avx2_supported_runtime();

// 1. Scalar Implementation
// Processes one color at a time using standard IEEE 754 scalar math
CAM16Output forward_scalar_single(const XYZ& in, const CAM16Coefficients& coeff);

void forward_scalar_batch(const XYZ* inputs, 
                          CAM16Output* outputs, 
                          size_t count, 
                          const CAM16Coefficients& coeff);

// 2. Auto-Vectorized Implementation
// Structured with __restrict__ pointers and contiguous loops to facilitate compiler auto-vectorization
void forward_auto_batch(const XYZ* __restrict__ inputs, 
                        CAM16Output* __restrict__ outputs, 
                        size_t count, 
                        const CAM16Coefficients& coeff);

void forward_auto_soa(const XYZ_SoA& in, 
                      CAM16Output_SoA& out, 
                      const CAM16Coefficients& coeff);

// 3. Manual AVX2 Vectorized Implementation
// Explicitly uses 256-bit AVX2 intrinsics processing 8 colors per vector iteration
void forward_avx2_batch(const XYZ* inputs, 
                         CAM16Output* outputs, 
                         size_t count, 
                         const CAM16Coefficients& coeff);

void forward_avx2_soa(const XYZ_SoA& in, 
                      CAM16Output_SoA& out, 
                      const CAM16Coefficients& coeff);

// Helper functions for memory allocation with 32-byte alignment (required for AVX2 YMM registers)
void* allocate_aligned(size_t bytes, size_t alignment = 32);
void free_aligned(void* ptr);

} // namespace cam16
