#include "cam16.h"
#include <cmath>
#include <algorithm>

namespace cam16 {

// Forward batch on Array of Structures (AoS) with compiler auto-vectorization hints
void forward_auto_batch(const XYZ* __restrict__ inputs, 
                        CAM16Output* __restrict__ outputs, 
                        size_t count, 
                        const CAM16Coefficients& coeff) {
    #pragma GCC ivdep
    for (size_t i = 0; i < count; ++i) {
        outputs[i] = forward_scalar_single(inputs[i], coeff);
    }
}

// Forward batch on Structure of Arrays (SoA) layout.
// Structured in distinct loop stages to isolate linear vectorizable arithmetic
// from non-linear math library bottlenecks (RQ1, RQ3, RQ4).
void forward_auto_soa(const XYZ_SoA& in, 
                      CAM16Output_SoA& out, 
                      const CAM16Coefficients& coeff) {
    const size_t n = in.count;

    const float* __restrict__ in_x = in.x;
    const float* __restrict__ in_y = in.y;
    const float* __restrict__ in_z = in.z;

    float* __restrict__ out_J = out.J;
    float* __restrict__ out_C = out.C;
    float* __restrict__ out_h = out.h;
    float* __restrict__ out_s = out.s;
    float* __restrict__ out_Q = out.Q;
    float* __restrict__ out_M = out.M;
    float* __restrict__ out_H = out.H;
    float* __restrict__ out_a = out.a;
    float* __restrict__ out_b = out.b;

    // Temporary aligned buffers for intermediate variables
    // Allocating temporary aligned scratchpads facilitates vector register streaming
    std::vector<float> R_c(n), G_c(n), B_c(n);
    std::vector<float> R_a(n), G_a(n), B_a(n);
    std::vector<float> opp_a(n), opp_b(n);

    // STAGE 1: CAT16 Cone Transform & Chromatic Adaptation
    // Pure linear multiply-accumulate arithmetic. Prime candidate for auto-vectorization!
    #pragma GCC ivdep
    for (size_t i = 0; i < n; ++i) {
        float r =  0.401288f * in_x[i] + 0.650173f * in_y[i] - 0.051461f * in_z[i];
        float g = -0.250268f * in_x[i] + 1.204414f * in_y[i] + 0.045854f * in_z[i];
        float b = -0.002079f * in_x[i] + 0.048952f * in_y[i] + 0.953127f * in_z[i];

        R_c[i] = coeff.R_w_a * r;
        G_c[i] = coeff.G_w_a * g;
        B_c[i] = coeff.B_w_a * b;
    }

    // STAGE 2: Post-Adaptation Non-Linear Response Compression
    // Calls powf(v, 0.42). Tests compiler's ability to vectorize fractional powers.
    #pragma GCC ivdep
    for (size_t i = 0; i < n; ++i) {
        auto compress = [&](float v) {
            float abs_v = std::abs(v);
            float f_val = (coeff.F_L * abs_v) / 100.0f;
            float p = std::pow(f_val, 0.42f);
            float sign = (v >= 0.0f) ? 1.0f : -1.0f;
            return (400.0f * sign * p) / (27.13f + p) + 0.1f;
        };

        R_a[i] = compress(R_c[i]);
        G_a[i] = compress(G_c[i]);
        B_a[i] = compress(B_c[i]);
    }

    // STAGE 3: Opponent Color Dimensions & Geometry
    // Computes a, b, hue angle h, and eccentricity factor e_t
    #pragma GCC ivdep
    for (size_t i = 0; i < n; ++i) {
        float a = R_a[i] - 12.0f * G_a[i] / 11.0f + B_a[i] / 11.0f;
        float b = (R_a[i] + G_a[i] - 2.0f * B_a[i]) / 9.0f;
        opp_a[i] = a;
        opp_b[i] = b;

        float h_rad = std::atan2(b, a);
        float h_deg = h_rad * (180.0f / 3.14159265358979323846f);
        if (h_deg < 0.0f) h_deg += 360.0f;
        out_h[i] = h_deg;
    }

    // STAGE 4: Achromatic Response, Lightness J, and Brightness Q
    const float cz = coeff.c * coeff.z;
    const float F_L_pow_025 = std::pow(coeff.F_L, 0.25f);
    const float inv_Aw = 1.0f / coeff.A_w;
    const float b_factor = (4.0f / coeff.c) * (coeff.A_w + 4.0f) * F_L_pow_025;

    #pragma GCC ivdep
    for (size_t i = 0; i < n; ++i) {
        float A = (2.0f * R_a[i] + G_a[i] + (1.0f / 20.0f) * B_a[i] - 0.305f) * coeff.N_bb;
        float J = 100.0f * std::pow(std::max(0.0f, A * inv_Aw), cz);
        float Q = b_factor * std::sqrt(J / 100.0f);

        out_J[i] = J;
        out_Q[i] = Q;
    }

    // STAGE 5: Chroma C, Colourfulness M, Saturation s, and Cartesian Coordinates
    const float bg_factor = std::pow(1.64f - std::pow(0.29f, coeff.n), 0.73f);
    const float t_scale = (50000.0f / 13.0f) * coeff.N_c * coeff.N_cb;

    #pragma GCC ivdep
    for (size_t i = 0; i < n; ++i) {
        float a = opp_a[i];
        float b = opp_b[i];
        float h_deg = out_h[i];
        float h_rad = h_deg * (3.14159265358979323846f / 180.0f);

        float e_t = 0.25f * (std::cos(h_rad + 2.0f) + 3.8f);
        float denom = R_a[i] + G_a[i] + (21.0f / 20.0f) * B_a[i];
        float t = (t_scale * e_t * std::sqrt(a * a + b * b)) / denom;

        float C = std::pow(t, 0.9f) * std::sqrt(out_J[i] / 100.0f) * bg_factor;
        float M = C * F_L_pow_025;
        float s = 100.0f * std::sqrt(std::max(0.0f, M / out_Q[i]));

        out_C[i] = C;
        out_M[i] = M;
        out_s[i] = s;
        out_a[i] = C * std::cos(h_rad);
        out_b[i] = C * std::sin(h_rad);

        // Hue quadrature H piecewise calculation
        if (h_deg < 20.14f) {
            float d1 = h_deg / 0.856f;
            float d2 = (20.14f - h_deg) / 0.8f;
            out_H[i] = 385.9f + (14.1f * d1) / (d1 + d2);
        } else if (h_deg < 90.00f) {
            float d1 = (h_deg - 20.14f) / 0.8f;
            float d2 = (90.00f - h_deg) / 0.7f;
            out_H[i] = (100.0f * d1) / (d1 + d2);
        } else if (h_deg < 164.25f) {
            float d1 = (h_deg - 90.00f) / 0.7f;
            float d2 = (164.25f - h_deg) / 1.0f;
            out_H[i] = 100.0f + (100.0f * d1) / (d1 + d2);
        } else if (h_deg < 237.53f) {
            float d1 = (h_deg - 164.25f) / 1.0f;
            float d2 = (237.53f - h_deg) / 1.2f;
            out_H[i] = 200.0f + (100.0f * d1) / (d1 + d2);
        } else {
            float d1 = (h_deg - 237.53f) / 1.2f;
            float d2 = (360.0f - h_deg) / 0.856f;
            out_H[i] = 300.0f + (85.9f * d1) / (d1 + d2);
        }
    }
}

} // namespace cam16
