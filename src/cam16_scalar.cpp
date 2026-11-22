#include "cam16.h"
#include <cstdlib>
#include <cmath>
#include <algorithm>
#include <iostream>

#if defined(_WIN32)
#include <malloc.h>
#endif

namespace cam16 {

bool is_avx2_supported_runtime() {
    return __builtin_cpu_supports("avx2") && __builtin_cpu_supports("fma");
}

void* allocate_aligned(size_t bytes, size_t alignment) {
#if defined(_WIN32)
    return _aligned_malloc(bytes, alignment);
#else
    void* ptr = nullptr;
    if (posix_memalign(&ptr, alignment, bytes) != 0) {
        return nullptr;
    }
    return ptr;
#endif
}

void free_aligned(void* ptr) {
#if defined(_WIN32)
    _aligned_free(ptr);
#else
    free(ptr);
#endif
}

// Post-adaptation non-linear response compression forward
static inline float post_adaptation_compression(float v, float F_L) {
    float abs_v = std::abs(v);
    float f_val = (F_L * abs_v) / 100.0f;
    float p = std::pow(f_val, 0.42f);
    float sign = (v >= 0.0f) ? 1.0f : -1.0f;
    return (400.0f * sign * p) / (27.13f + p) + 0.1f;
}

CAM16Coefficients compute_coefficients(const ViewingConditions& vc) {
    CAM16Coefficients coeff{};
    
    // Surround induction factors according to CIE CAM16 specification
    switch (vc.surround) {
        case SurroundType::Average:
            coeff.F = 1.0f;
            coeff.c = 0.69f;
            coeff.N_c = 1.0f;
            break;
        case SurroundType::Dim:
            coeff.F = 0.9f;
            coeff.c = 0.59f;
            coeff.N_c = 0.9f;
            break;
        case SurroundType::Dark:
            coeff.F = 0.8f;
            coeff.c = 0.525f;
            coeff.N_c = 0.8f;
            break;
    }

    // Luminance level adaptation factor k and F_L
    coeff.k = 1.0f / (5.0f * vc.L_A + 1.0f);
    float k4 = coeff.k * coeff.k * coeff.k * coeff.k;
    float k4_comp = 1.0f - k4;
    coeff.F_L = 0.2f * k4 * (5.0f * vc.L_A) + 0.1f * (k4_comp * k4_comp) * std::cbrt(5.0f * vc.L_A);

    // Degree of chromatic adaptation D
    if (vc.discount_illuminant) {
        coeff.D = 1.0f;
    } else {
        coeff.D = coeff.F * (1.0f - (1.0f / 3.6f) * std::exp((-vc.L_A - 42.0f) / 92.0f));
        coeff.D = std::clamp(coeff.D, 0.0f, 1.0f);
    }

    // Background induction factors
    coeff.n = vc.Y_b / vc.white_point.y;
    coeff.z = 1.48f + std::sqrt(coeff.n);
    coeff.N_bb = 0.725f * std::pow(1.0f / coeff.n, 0.2f);
    coeff.N_cb = coeff.N_bb;

    // CAT16 cone response transformation matrix (Hunt-Pointer-Estevez sharp)
    float R_w =  0.401288f * vc.white_point.x + 0.650173f * vc.white_point.y - 0.051461f * vc.white_point.z;
    float G_w = -0.250268f * vc.white_point.x + 1.204414f * vc.white_point.y + 0.045854f * vc.white_point.z;
    float B_w = -0.002079f * vc.white_point.x + 0.048952f * vc.white_point.y + 0.953127f * vc.white_point.z;

    // Store chromatic adaptation coefficients for reference white:
    // D_RGB = D * (Y_w / RGB_w) + 1 - D
    coeff.R_w_a = coeff.D * (vc.white_point.y / R_w) + 1.0f - coeff.D;
    coeff.G_w_a = coeff.D * (vc.white_point.y / G_w) + 1.0f - coeff.D;
    coeff.B_w_a = coeff.D * (vc.white_point.y / B_w) + 1.0f - coeff.D;

    // Adapted whitepoint cone responses
    float R_wc = coeff.R_w_a * R_w;
    float G_wc = coeff.G_w_a * G_w;
    float B_wc = coeff.B_w_a * B_w;

    // Post-adaptation non-linear response compression for reference white
    float R_aw = post_adaptation_compression(R_wc, coeff.F_L);
    float G_aw = post_adaptation_compression(G_wc, coeff.F_L);
    float B_aw = post_adaptation_compression(B_wc, coeff.F_L);

    // Achromatic response for reference white A_w
    coeff.A_w = (2.0f * R_aw + G_aw + (1.0f / 20.0f) * B_aw - 0.305f) * coeff.N_bb;

    return coeff;
}

// Hue quadrature interpolation table according to CAM16 / CIECAM02 specification
static inline float compute_hue_quadrature(float h) {
    if (h < 20.14f) {
        float d1 = h / 0.856f;
        float d2 = (20.14f - h) / 0.8f;
        return 385.9f + (14.1f * d1) / (d1 + d2);
    } else if (h < 90.00f) {
        float d1 = (h - 20.14f) / 0.8f;
        float d2 = (90.00f - h) / 0.7f;
        return (100.0f * d1) / (d1 + d2);
    } else if (h < 164.25f) {
        float d1 = (h - 90.00f) / 0.7f;
        float d2 = (164.25f - h) / 1.0f;
        return 100.0f + (100.0f * d1) / (d1 + d2);
    } else if (h < 237.53f) {
        float d1 = (h - 164.25f) / 1.0f;
        float d2 = (237.53f - h) / 1.2f;
        return 200.0f + (100.0f * d1) / (d1 + d2);
    } else {
        float d1 = (h - 237.53f) / 1.2f;
        float d2 = (360.0f - h) / 0.856f;
        return 300.0f + (85.9f * d1) / (d1 + d2);
    }
}

CAM16Output forward_scalar_single(const XYZ& in, const CAM16Coefficients& coeff) {
    // 1. Transform XYZ to cone responses via CAT16
    float R =  0.401288f * in.x + 0.650173f * in.y - 0.051461f * in.z;
    float G = -0.250268f * in.x + 1.204414f * in.y + 0.045854f * in.z;
    float B = -0.002079f * in.x + 0.048952f * in.y + 0.953127f * in.z;

    // 2. Chromatic adaptation: RGB_c = D_RGB * RGB
    float R_c = coeff.R_w_a * R;
    float G_c = coeff.G_w_a * G;
    float B_c = coeff.B_w_a * B;

    // 3. Post-adaptation non-linear response compression
    float R_a = post_adaptation_compression(R_c, coeff.F_L);
    float G_a = post_adaptation_compression(G_c, coeff.F_L);
    float B_a = post_adaptation_compression(B_c, coeff.F_L);

    // 4. Opponent color dimensions
    float a = R_a - 12.0f * G_a / 11.0f + B_a / 11.0f;
    float b = (R_a + G_a - 2.0f * B_a) / 9.0f;

    // 5. Hue angle h (degrees in [0, 360))
    float h_rad = std::atan2(b, a);
    float h_deg = h_rad * (180.0f / 3.14159265358979323846f);
    if (h_deg < 0.0f) h_deg += 360.0f;

    // 6. Eccentricity factor e_t
    float e_t = 0.25f * (std::cos(h_rad + 2.0f) + 3.8f);

    // 7. Hue quadrature H
    float H = compute_hue_quadrature(h_deg);

    // 8. Achromatic response A
    float A = (2.0f * R_a + G_a + (1.0f / 20.0f) * B_a - 0.305f) * coeff.N_bb;

    // 9. Lightness J
    float J = 100.0f * std::pow(std::max(0.0f, A / coeff.A_w), coeff.c * coeff.z);

    // 10. Brightness Q
    float F_L_pow_025 = std::pow(coeff.F_L, 0.25f);
    float Q = (4.0f / coeff.c) * std::sqrt(J / 100.0f) * (coeff.A_w + 4.0f) * F_L_pow_025;

    // 11. Chroma C, Colourfulness M, Saturation s
    float denom = R_a + G_a + (21.0f / 20.0f) * B_a;
    float t = ((50000.0f / 13.0f) * coeff.N_c * coeff.N_cb * e_t * std::sqrt(a * a + b * b)) / denom;
    float C = std::pow(t, 0.9f) * std::sqrt(J / 100.0f) * std::pow(1.64f - std::pow(0.29f, coeff.n), 0.73f);
    float M = C * F_L_pow_025;
    float s = 100.0f * std::sqrt(std::max(0.0f, M / Q));

    CAM16Output out{};
    out.J = J;
    out.C = C;
    out.h = h_deg;
    out.s = s;
    out.Q = Q;
    out.M = M;
    out.H = H;
    out.a = C * std::cos(h_rad);
    out.b = C * std::sin(h_rad);
    return out;
}

void forward_scalar_batch(const XYZ* inputs, CAM16Output* outputs, size_t count, const CAM16Coefficients& coeff) {
    for (size_t i = 0; i < count; ++i) {
        outputs[i] = forward_scalar_single(inputs[i], coeff);
    }
}

} // namespace cam16
