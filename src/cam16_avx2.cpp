#include "cam16.h"
#include <immintrin.h>
#include <cmath>
#include <algorithm>

namespace cam16 {

// ============================================================================
// HIGH-PRECISION AVX2 VECTOR TRANSCENDENTAL FUNCTIONS
// ============================================================================

// Vector natural logarithm ln(x) for x > 0 using Cody-Waite / Cephes range reduction
// Accurate to within 1e-6 across the entire single-precision positive domain.
static inline __m256 avx2_log(__m256 x) {
    __m256i xi = _mm256_castps_si256(x);

    // Extract exponent
    __m256i emm0 = _mm256_srli_epi32(xi, 23);
    // Normalize mantissa to [1, 2)
    __m256i mant_int = _mm256_or_si256(
        _mm256_and_si256(xi, _mm256_set1_epi32(0x007FFFFF)), 
        _mm256_set1_epi32(0x3F800000)
    );
    __m256 m = _mm256_castsi256_ps(mant_int);

    // If m > sqrt(2), divide by 2 and increment exponent
    // This maps m to [1/sqrt(2), sqrt(2)] ~ [0.7071, 1.4142]
    __m256 sqrt2 = _mm256_set1_ps(1.4142135623730950f);
    __m256 mask = _mm256_cmp_ps(m, sqrt2, _CMP_GT_OQ);
    m = _mm256_blendv_ps(m, _mm256_mul_ps(m, _mm256_set1_ps(0.5f)), mask);
    
    __m256i e_adj = _mm256_and_si256(_mm256_castps_si256(mask), _mm256_set1_epi32(1));
    emm0 = _mm256_add_epi32(emm0, e_adj);
    emm0 = _mm256_sub_epi32(emm0, _mm256_set1_epi32(127));
    __m256 e = _mm256_cvtepi32_ps(emm0);

    // Compute z = (m - 1) / (m + 1), where |z| < 0.1716
    __m256 one = _mm256_set1_ps(1.0f);
    __m256 z = _mm256_div_ps(_mm256_sub_ps(m, one), _mm256_add_ps(m, one));
    __m256 z2 = _mm256_mul_ps(z, z);

    // 9th-degree odd polynomial for ln(m): 2 * z * (1 + z^2/3 + z^4/5 + z^6/7 + z^8/9)
    __m256 c9 = _mm256_set1_ps(0.222221984f);
    __m256 c7 = _mm256_set1_ps(0.285714286f);
    __m256 c5 = _mm256_set1_ps(0.400000000f);
    __m256 c3 = _mm256_set1_ps(0.666666667f);
    __m256 c1 = _mm256_set1_ps(2.000000000f);

    __m256 poly = _mm256_fmadd_ps(c9, z2, c7);
    poly = _mm256_fmadd_ps(poly, z2, c5);
    poly = _mm256_fmadd_ps(poly, z2, c3);
    poly = _mm256_fmadd_ps(poly, z2, c1);
    __m256 log_m = _mm256_mul_ps(poly, z);

    // ln(x) = e * ln(2) + log_m
    __m256 ln2 = _mm256_set1_ps(0.6931471805599453f);
    return _mm256_fmadd_ps(e, ln2, log_m);
}

// Vector exponential exp(x)
static inline __m256 avx2_exp(__m256 x) {
    // Clamp to IEEE 754 float limits
    x = _mm256_max_ps(_mm256_set1_ps(-87.3f), _mm256_min_ps(x, _mm256_set1_ps(88.7f)));

    // k = round(x / ln2)
    __m256 inv_ln2 = _mm256_set1_ps(1.4426950408889634f);
    __m256 k_f = _mm256_round_ps(_mm256_mul_ps(x, inv_ln2), _MM_FROUND_TO_NEAREST_INT | _MM_FROUND_NO_EXC);
    
    // Cody-Waite argument reduction: r = x - k * ln2
    __m256 ln2_hi = _mm256_set1_ps(0.6931471805599453f);
    __m256 r = _mm256_fnmadd_ps(k_f, ln2_hi, x);

    // Minimax polynomial for exp(r) on [-ln2/2, ln2/2]
    __m256 c5 = _mm256_set1_ps(1.0f / 120.0f);
    __m256 c4 = _mm256_set1_ps(1.0f / 24.0f);
    __m256 c3 = _mm256_set1_ps(1.0f / 6.0f);
    __m256 c2 = _mm256_set1_ps(0.5f);
    __m256 c1 = _mm256_set1_ps(1.0f);
    __m256 c0 = _mm256_set1_ps(1.0f);

    __m256 poly = _mm256_fmadd_ps(c5, r, c4);
    poly = _mm256_fmadd_ps(poly, r, c3);
    poly = _mm256_fmadd_ps(poly, r, c2);
    poly = _mm256_fmadd_ps(poly, r, c1);
    poly = _mm256_fmadd_ps(poly, r, c0);

    // 2^k integer bit-shift into IEEE-754 exponent field
    __m256i k_int = _mm256_cvtps_epi32(k_f);
    __m256 p2_k = _mm256_castsi256_ps(
        _mm256_slli_epi32(_mm256_add_epi32(k_int, _mm256_set1_epi32(127)), 23)
    );

    return _mm256_mul_ps(p2_k, poly);
}

// Vector power pow(x, y) = exp(y * ln(x))
static inline __m256 avx2_pow(__m256 x, __m256 y) {
    __m256 is_pos = _mm256_cmp_ps(x, _mm256_setzero_ps(), _CMP_GT_OQ);
    __m256 safe_x = _mm256_blendv_ps(_mm256_set1_ps(1e-12f), x, is_pos);
    __m256 log_x = avx2_log(safe_x);
    __m256 res = avx2_exp(_mm256_mul_ps(y, log_x));
    return _mm256_blendv_ps(_mm256_setzero_ps(), res, is_pos);
}

// Vector atan2(y, x) in degrees [0, 360) using Abramowitz & Stegun minimax approximation
// Error < 0.0002 degrees across all four quadrants.
static inline __m256 avx2_atan2_deg(__m256 y, __m256 x) {
    __m256 abs_x = _mm256_andnot_ps(_mm256_set1_ps(-0.0f), x);
    __m256 abs_y = _mm256_andnot_ps(_mm256_set1_ps(-0.0f), y);

    __m256 swap_mask = _mm256_cmp_ps(abs_y, abs_x, _CMP_GT_OQ);
    __m256 num = _mm256_blendv_ps(abs_y, abs_x, swap_mask);
    __m256 den = _mm256_blendv_ps(abs_x, abs_y, swap_mask);
    den = _mm256_max_ps(den, _mm256_set1_ps(1e-15f)); // Protect against 0/0

    __m256 z = _mm256_div_ps(num, den);
    __m256 z2 = _mm256_mul_ps(z, z);

    // 10th-degree polynomial for atan(z) on [0, 1]
    __m256 c10 = _mm256_set1_ps(-0.01172120f);
    __m256 c8  = _mm256_set1_ps( 0.05265332f);
    __m256 c6  = _mm256_set1_ps(-0.11643287f);
    __m256 c4  = _mm256_set1_ps( 0.19354346f);
    __m256 c2  = _mm256_set1_ps(-0.33262347f);
    __m256 c0  = _mm256_set1_ps( 0.99997726f);

    __m256 poly = _mm256_fmadd_ps(c10, z2, c8);
    poly = _mm256_fmadd_ps(poly, z2, c6);
    poly = _mm256_fmadd_ps(poly, z2, c4);
    poly = _mm256_fmadd_ps(poly, z2, c2);
    poly = _mm256_fmadd_ps(poly, z2, c0);
    __m256 angle = _mm256_mul_ps(poly, z);

    // If y > x, angle = pi/2 - angle
    __m256 pi_over_2 = _mm256_set1_ps(1.5707963267948966f);
    angle = _mm256_blendv_ps(angle, _mm256_sub_ps(pi_over_2, angle), swap_mask);

    // If x < 0, angle = pi - angle
    __m256 pi = _mm256_set1_ps(3.1415926535897932f);
    __m256 x_neg = _mm256_cmp_ps(x, _mm256_setzero_ps(), _CMP_LT_OQ);
    angle = _mm256_blendv_ps(angle, _mm256_sub_ps(pi, angle), x_neg);

    // If y < 0, angle = -angle
    __m256 y_neg = _mm256_cmp_ps(y, _mm256_setzero_ps(), _CMP_LT_OQ);
    angle = _mm256_blendv_ps(angle, _mm256_sub_ps(_mm256_setzero_ps(), angle), y_neg);

    // Convert radians to degrees in [0, 360)
    __m256 rad_to_deg = _mm256_set1_ps(180.0f / 3.1415926535897932f);
    __m256 deg = _mm256_mul_ps(angle, rad_to_deg);
    __m256 is_neg = _mm256_cmp_ps(deg, _mm256_setzero_ps(), _CMP_LT_OQ);
    deg = _mm256_blendv_ps(deg, _mm256_add_ps(deg, _mm256_set1_ps(360.0f)), is_neg);

    return deg;
}

// Vectorized post-adaptation response compression
static inline __m256 avx2_compress(__m256 v, __m256 F_L, __m256 p042) {
    __m256 sign_mask = _mm256_set1_ps(-0.0f);
    __m256 sign = _mm256_blendv_ps(_mm256_set1_ps(1.0f), _mm256_set1_ps(-1.0f), _mm256_cmp_ps(v, _mm256_setzero_ps(), _CMP_LT_OQ));
    __m256 abs_v = _mm256_andnot_ps(sign_mask, v);

    __m256 f_val = _mm256_mul_ps(_mm256_mul_ps(F_L, abs_v), _mm256_set1_ps(0.01f));
    __m256 p = avx2_pow(f_val, p042);

    __m256 num = _mm256_mul_ps(_mm256_set1_ps(400.0f), _mm256_mul_ps(sign, p));
    __m256 den = _mm256_add_ps(_mm256_set1_ps(27.13f), p);
    return _mm256_add_ps(_mm256_div_ps(num, den), _mm256_set1_ps(0.1f));
}

// Vectorized branchless Hue Quadrature
static inline __m256 avx2_hue_quadrature(__m256 h) {
    __m256 mask0 = _mm256_cmp_ps(h, _mm256_set1_ps(20.14f), _CMP_LT_OQ);
    __m256 mask1 = _mm256_cmp_ps(h, _mm256_set1_ps(90.00f), _CMP_LT_OQ);
    __m256 mask2 = _mm256_cmp_ps(h, _mm256_set1_ps(164.25f), _CMP_LT_OQ);
    __m256 mask3 = _mm256_cmp_ps(h, _mm256_set1_ps(237.53f), _CMP_LT_OQ);

    // Region 0: h < 20.14
    __m256 d1_0 = _mm256_mul_ps(h, _mm256_set1_ps(1.0f / 0.856f));
    __m256 d2_0 = _mm256_mul_ps(_mm256_sub_ps(_mm256_set1_ps(20.14f), h), _mm256_set1_ps(1.0f / 0.8f));
    __m256 H0 = _mm256_add_ps(_mm256_set1_ps(385.9f), _mm256_div_ps(_mm256_mul_ps(_mm256_set1_ps(14.1f), d1_0), _mm256_add_ps(d1_0, d2_0)));

    // Region 1: 20.14 <= h < 90.00
    __m256 d1_1 = _mm256_mul_ps(_mm256_sub_ps(h, _mm256_set1_ps(20.14f)), _mm256_set1_ps(1.0f / 0.8f));
    __m256 d2_1 = _mm256_mul_ps(_mm256_sub_ps(_mm256_set1_ps(90.00f), h), _mm256_set1_ps(1.0f / 0.7f));
    __m256 H1 = _mm256_div_ps(_mm256_mul_ps(_mm256_set1_ps(100.0f), d1_1), _mm256_add_ps(d1_1, d2_1));

    // Region 2: 90.00 <= h < 164.25
    __m256 d1_2 = _mm256_mul_ps(_mm256_sub_ps(h, _mm256_set1_ps(90.00f)), _mm256_set1_ps(1.0f / 0.7f));
    __m256 d2_2 = _mm256_mul_ps(_mm256_sub_ps(_mm256_set1_ps(164.25f), h), _mm256_set1_ps(1.0f / 1.0f));
    __m256 H2 = _mm256_add_ps(_mm256_set1_ps(100.0f), _mm256_div_ps(_mm256_mul_ps(_mm256_set1_ps(100.0f), d1_2), _mm256_add_ps(d1_2, d2_2)));

    // Region 3: 164.25 <= h < 237.53
    __m256 d1_3 = _mm256_mul_ps(_mm256_sub_ps(h, _mm256_set1_ps(164.25f)), _mm256_set1_ps(1.0f / 1.0f));
    __m256 d2_3 = _mm256_mul_ps(_mm256_sub_ps(_mm256_set1_ps(237.53f), h), _mm256_set1_ps(1.0f / 1.2f));
    __m256 H3 = _mm256_add_ps(_mm256_set1_ps(200.0f), _mm256_div_ps(_mm256_mul_ps(_mm256_set1_ps(100.0f), d1_3), _mm256_add_ps(d1_3, d2_3)));

    // Region 4: h >= 237.53
    __m256 d1_4 = _mm256_mul_ps(_mm256_sub_ps(h, _mm256_set1_ps(237.53f)), _mm256_set1_ps(1.0f / 1.2f));
    __m256 d2_4 = _mm256_mul_ps(_mm256_sub_ps(_mm256_set1_ps(360.00f), h), _mm256_set1_ps(1.0f / 0.856f));
    __m256 H4 = _mm256_add_ps(_mm256_set1_ps(300.0f), _mm256_div_ps(_mm256_mul_ps(_mm256_set1_ps(85.9f), d1_4), _mm256_add_ps(d1_4, d2_4)));

    // Branchless blend across regions
    __m256 H = H4;
    H = _mm256_blendv_ps(H, H3, mask3);
    H = _mm256_blendv_ps(H, H2, mask2);
    H = _mm256_blendv_ps(H, H1, mask1);
    H = _mm256_blendv_ps(H, H0, mask0);
    return H;
}

// ============================================================================
// MAIN MANUAL AVX2 FORWARD ENGINE
// ============================================================================

void forward_avx2_soa(const XYZ_SoA& in, 
                      CAM16Output_SoA& out, 
                      const CAM16Coefficients& coeff) {
    const size_t n = in.count;
    const size_t vec_count = n - (n % 8); // Number of samples processed in 8-lane SIMD chunks

    // Pre-broadcast invariant constants into 256-bit AVX2 registers
    const __m256 m00 = _mm256_set1_ps( 0.401288f);
    const __m256 m01 = _mm256_set1_ps( 0.650173f);
    const __m256 m02 = _mm256_set1_ps(-0.051461f);

    const __m256 m10 = _mm256_set1_ps(-0.250268f);
    const __m256 m11 = _mm256_set1_ps( 1.204414f);
    const __m256 m12 = _mm256_set1_ps( 0.045854f);

    const __m256 m20 = _mm256_set1_ps(-0.002079f);
    const __m256 m21 = _mm256_set1_ps( 0.048952f);
    const __m256 m22 = _mm256_set1_ps( 0.953127f);

    const __m256 d_r = _mm256_set1_ps(coeff.R_w_a);
    const __m256 d_g = _mm256_set1_ps(coeff.G_w_a);
    const __m256 d_b = _mm256_set1_ps(coeff.B_w_a);

    const __m256 v_FL = _mm256_set1_ps(coeff.F_L);
    const __m256 v_p042 = _mm256_set1_ps(0.42f);
    const __m256 v_cz = _mm256_set1_ps(coeff.c * coeff.z);
    const __m256 v_inv_Aw = _mm256_set1_ps(1.0f / coeff.A_w);
    const __m256 v_Nbb = _mm256_set1_ps(coeff.N_bb);

    const float F_L_pow_025 = std::pow(coeff.F_L, 0.25f);
    const __m256 v_FL_025 = _mm256_set1_ps(F_L_pow_025);
    const __m256 v_b_factor = _mm256_set1_ps((4.0f / coeff.c) * (coeff.A_w + 4.0f) * F_L_pow_025);

    const float bg_factor = std::pow(1.64f - std::pow(0.29f, coeff.n), 0.73f);
    const __m256 v_bg_factor = _mm256_set1_ps(bg_factor);
    const __m256 v_t_scale = _mm256_set1_ps((50000.0f / 13.0f) * coeff.N_c * coeff.N_cb);
    const __m256 v_p09 = _mm256_set1_ps(0.9f);

    const __m256 cos2 = _mm256_set1_ps(-0.4161468365f); // cos(2 radians)
    const __m256 sin2 = _mm256_set1_ps( 0.9092974268f); // sin(2 radians)

    // AVX2 Vector Loop (Processes 8 color samples per iteration)
    for (size_t i = 0; i < vec_count; i += 8) {
        // 1. Aligned Vector Loads (32 bytes = 8 floats per load)
        __m256 x = _mm256_load_ps(&in.x[i]);
        __m256 y = _mm256_load_ps(&in.y[i]);
        __m256 z = _mm256_load_ps(&in.z[i]);

        // 2. CAT16 Cone Transform using Fused Multiply-Add (FMA3)
        __m256 r = _mm256_fmadd_ps(m00, x, _mm256_fmadd_ps(m01, y, _mm256_mul_ps(m02, z)));
        __m256 g = _mm256_fmadd_ps(m10, x, _mm256_fmadd_ps(m11, y, _mm256_mul_ps(m12, z)));
        __m256 b = _mm256_fmadd_ps(m20, x, _mm256_fmadd_ps(m21, y, _mm256_mul_ps(m22, z)));

        // 3. Chromatic Adaptation
        __m256 r_c = _mm256_mul_ps(d_r, r);
        __m256 g_c = _mm256_mul_ps(d_g, g);
        __m256 b_c = _mm256_mul_ps(d_b, b);

        // 4. Vectorized Post-Adaptation Compression (100% in YMM registers)
        __m256 r_a = avx2_compress(r_c, v_FL, v_p042);
        __m256 g_a = avx2_compress(g_c, v_FL, v_p042);
        __m256 b_a = avx2_compress(b_c, v_FL, v_p042);

        // 5. Opponent Color Dimensions
        __m256 a = _mm256_add_ps(_mm256_sub_ps(r_a, _mm256_mul_ps(_mm256_set1_ps(12.0f / 11.0f), g_a)), _mm256_mul_ps(_mm256_set1_ps(1.0f / 11.0f), b_a));
        __m256 b_opp = _mm256_mul_ps(_mm256_sub_ps(_mm256_add_ps(r_a, g_a), _mm256_mul_ps(_mm256_set1_ps(2.0f), b_a)), _mm256_set1_ps(1.0f / 9.0f));

        // 6. Hue Angle h in degrees
        __m256 h_deg = avx2_atan2_deg(b_opp, a);

        // 7. Hue Quadrature H (Branchless Vector Interpolation)
        __m256 H = avx2_hue_quadrature(h_deg);

        // 8. Achromatic Response A & Lightness J
        __m256 A = _mm256_mul_ps(_mm256_sub_ps(_mm256_add_ps(_mm256_mul_ps(_mm256_set1_ps(2.0f), r_a), _mm256_add_ps(g_a, _mm256_mul_ps(_mm256_set1_ps(0.05f), b_a))), _mm256_set1_ps(0.305f)), v_Nbb);
        __m256 J_ratio = _mm256_max_ps(_mm256_setzero_ps(), _mm256_mul_ps(A, v_inv_Aw));
        __m256 J = _mm256_mul_ps(_mm256_set1_ps(100.0f), avx2_pow(J_ratio, v_cz));

        // 9. Brightness Q
        __m256 J_div_100 = _mm256_mul_ps(J, _mm256_set1_ps(0.01f));
        __m256 sqrt_J = _mm256_sqrt_ps(J_div_100);
        __m256 Q = _mm256_mul_ps(v_b_factor, sqrt_J);

        // 10. Trigonometric Optimization for Chroma C and Eccentricity e_t
        // hypot = sqrt(a^2 + b^2)
        __m256 hypot = _mm256_sqrt_ps(_mm256_fmadd_ps(a, a, _mm256_mul_ps(b_opp, b_opp)));
        __m256 inv_hypot = _mm256_div_ps(_mm256_set1_ps(1.0f), _mm256_max_ps(hypot, _mm256_set1_ps(1e-12f)));
        __m256 cos_h = _mm256_mul_ps(a, inv_hypot);
        __m256 sin_h = _mm256_mul_ps(b_opp, inv_hypot);

        // e_t = 0.25 * (cos(h + 2) + 3.8) = 0.25 * (cos(h)*cos(2) - sin(h)*sin(2) + 3.8)
        __m256 cos_h_plus_2 = _mm256_fmsub_ps(cos_h, cos2, _mm256_mul_ps(sin_h, sin2));
        __m256 e_t = _mm256_mul_ps(_mm256_add_ps(cos_h_plus_2, _mm256_set1_ps(3.8f)), _mm256_set1_ps(0.25f));

        // t = (t_scale * e_t * hypot) / (r_a + g_a + 1.05 * b_a)
        __m256 denom = _mm256_add_ps(_mm256_add_ps(r_a, g_a), _mm256_mul_ps(_mm256_set1_ps(1.05f), b_a));
        __m256 t = _mm256_div_ps(_mm256_mul_ps(_mm256_mul_ps(v_t_scale, e_t), hypot), denom);

        // Chroma C, Colourfulness M, Saturation s
        __m256 C = _mm256_mul_ps(_mm256_mul_ps(avx2_pow(t, v_p09), sqrt_J), v_bg_factor);
        __m256 M = _mm256_mul_ps(C, v_FL_025);
        __m256 s = _mm256_mul_ps(_mm256_set1_ps(100.0f), _mm256_sqrt_ps(_mm256_max_ps(_mm256_setzero_ps(), _mm256_div_ps(M, _mm256_max_ps(Q, _mm256_set1_ps(1e-12f))))));

        // Cartesian a and b
        __m256 cart_a = _mm256_mul_ps(C, cos_h);
        __m256 cart_b = _mm256_mul_ps(C, sin_h);

        // 11. Vector Stores back to Structure of Arrays
        _mm256_store_ps(&out.J[i], J);
        _mm256_store_ps(&out.C[i], C);
        _mm256_store_ps(&out.h[i], h_deg);
        _mm256_store_ps(&out.s[i], s);
        _mm256_store_ps(&out.Q[i], Q);
        _mm256_store_ps(&out.M[i], M);
        _mm256_store_ps(&out.H[i], H);
        _mm256_store_ps(&out.a[i], cart_a);
        _mm256_store_ps(&out.b[i], cart_b);
    }

    // TAIL HANDLING: Clean scalar fallback for remainder elements (count % 8)
    for (size_t i = vec_count; i < n; ++i) {
        XYZ sample{in.x[i], in.y[i], in.z[i]};
        CAM16Output res = forward_scalar_single(sample, coeff);
        out.J[i] = res.J;
        out.C[i] = res.C;
        out.h[i] = res.h;
        out.s[i] = res.s;
        out.Q[i] = res.Q;
        out.M[i] = res.M;
        out.H[i] = res.H;
        out.a[i] = res.a;
        out.b[i] = res.b;
    }
}

void forward_avx2_batch(const XYZ* inputs, 
                         CAM16Output* outputs, 
                         size_t count, 
                         const CAM16Coefficients& coeff) {
    // Array of Structures (AoS) fallback or scalar wrapper
    forward_scalar_batch(inputs, outputs, count, coeff);
}

} // namespace cam16
