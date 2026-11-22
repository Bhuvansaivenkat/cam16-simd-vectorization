#pragma once
#include <cstddef>
#include <cmath>

namespace cam16 {

// CIE 1931 XYZ tristimulus values (typically scaled to reference white Y_w = 100.0)
struct XYZ {
    float x;
    float y;
    float z;
};

// Surround type in CAM16
enum class SurroundType {
    Average,
    Dim,
    Dark
};

// User-provided viewing conditions
struct ViewingConditions {
    XYZ white_point = {95.047f, 100.0f, 108.883f}; // Standard Illuminant D65
    float L_A = 64.0f;                             // Adapting luminance (cd/m^2)
    float Y_b = 20.0f;                             // Background relative luminance
    SurroundType surround = SurroundType::Average;
    bool discount_illuminant = false;
};

// Precomputed invariants derived from viewing conditions.
// In Computer Organization and Architecture, invariant hoisting separates
// viewing-condition setup from the inner pixel computation loop.
struct CAM16Coefficients {
    // Surround induction factors
    float F;
    float c;
    float N_c;

    // Luminance adaptation and background factors
    float k;
    float F_L;
    float n;
    float N_bb;
    float N_cb;
    float z;
    float D;

    // Adapted white point response
    float R_w_a;
    float G_w_a;
    float B_w_a;
    float A_w; // Achromatic response of reference white
};

// Standard CAM16 perceptual appearance outputs (AoS: Array of Structures)
struct CAM16Output {
    float J; // Lightness [0, 100]
    float C; // Chroma
    float h; // Hue angle in degrees [0, 360)
    float s; // Saturation
    float Q; // Brightness
    float M; // Colourfulness
    float H; // Hue quadrature [0, 400]
    float a; // Cartesian a = C * cos(h)
    float b; // Cartesian b = C * sin(h)
};

// Structure of Arrays (SoA) layout for vectorization
// Aligned to 32-byte boundaries for native 256-bit AVX2 vector loads/stores
struct XYZ_SoA {
    float* x;
    float* y;
    float* z;
    size_t count;
};

struct CAM16Output_SoA {
    float* J;
    float* C;
    float* h;
    float* s;
    float* Q;
    float* M;
    float* H;
    float* a;
    float* b;
    size_t count;
};

} // namespace cam16
