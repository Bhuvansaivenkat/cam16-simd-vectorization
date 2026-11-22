#include "cam16.h"
#include "benchmark.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <iomanip>

struct DatasetRow {
    int id;
    cam16::XYZ xyz;
};

std::vector<DatasetRow> load_xyz_csv(const std::string& filepath) {
    std::vector<DatasetRow> rows;
    std::ifstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Error: Could not open file: " << filepath << std::endl;
        return rows;
    }

    std::string line;
    if (!std::getline(file, line)) return rows;

    while (std::getline(file, line)) {
        if (line.empty()) continue;
        std::stringstream ss(line);
        std::string token;
        
        DatasetRow row;
        if (std::getline(ss, token, ',')) row.id = std::stoi(token);
        if (std::getline(ss, token, ',')) row.xyz.x = std::stof(token);
        if (std::getline(ss, token, ',')) row.xyz.y = std::stof(token);
        if (std::getline(ss, token, ',')) row.xyz.z = std::stof(token);
        
        rows.push_back(row);
    }
    return rows;
}

bool save_cam16_results_csv(const std::string& filepath, 
                            const std::vector<DatasetRow>& inputs, 
                            const std::vector<cam16::CAM16Output>& outputs) {
    std::ofstream file(filepath);
    if (!file.is_open()) return false;

    file << std::fixed << std::setprecision(6);
    file << "Sample_ID,X,Y,Z,J,C,h,s,Q,M,H,a,b\n";
    for (size_t i = 0; i < inputs.size(); ++i) {
        file << inputs[i].id << ","
             << inputs[i].xyz.x << ","
             << inputs[i].xyz.y << ","
             << inputs[i].xyz.z << ","
             << outputs[i].J << ","
             << outputs[i].C << ","
             << outputs[i].h << ","
             << outputs[i].s << ","
             << outputs[i].Q << ","
             << outputs[i].M << ","
             << outputs[i].H << ","
             << outputs[i].a << ","
             << outputs[i].b << "\n";
    }
    return true;
}

bool save_soa_results_csv(const std::string& filepath,
                          const std::vector<DatasetRow>& inputs,
                          const cam16::CAM16Output_SoA& out) {
    std::ofstream file(filepath);
    if (!file.is_open()) return false;

    file << std::fixed << std::setprecision(6);
    file << "Sample_ID,X,Y,Z,J,C,h,s,Q,M,H,a,b\n";
    for (size_t i = 0; i < inputs.size(); ++i) {
        file << inputs[i].id << ","
             << inputs[i].xyz.x << ","
             << inputs[i].xyz.y << ","
             << inputs[i].xyz.z << ","
             << out.J[i] << ","
             << out.C[i] << ","
             << out.h[i] << ","
             << out.s[i] << ","
             << out.Q[i] << ","
             << out.M[i] << ","
             << out.H[i] << ","
             << out.a[i] << ","
             << out.b[i] << "\n";
    }
    return true;
}

int main() {
    std::cout << "=================================================================\n";
    std::cout << "  CAM16 SIMD Performance & Architecture Benchmarking Suite (COA)\n";
    std::cout << "=================================================================\n\n";

    // 1. Hardware SIMD Feature Check
    bool has_avx2 = cam16::is_avx2_supported_runtime();
    std::cout << "[1] Hardware SIMD Feature Check:\n";
    std::cout << "    - AVX2 & FMA3 CPU Capability: " 
              << (has_avx2 ? "DETECTED & SUPPORTED (256-bit YMM Available)" : "NOT SUPPORTED") 
              << "\n\n";

    if (!has_avx2) {
        std::cerr << "CRITICAL ERROR: AVX2 instructions not supported on this processor!\n";
        return 1;
    }

    // 2. Setup Viewing Conditions (CIE D65, Average Surround)
    cam16::ViewingConditions vc{};
    cam16::CAM16Coefficients coeff = cam16::compute_coefficients(vc);

    std::cout << "[2] Viewing Condition Parameters:\n";
    std::cout << "    - Reference White D65:      [" << vc.white_point.x << ", " << vc.white_point.y << ", " << vc.white_point.z << "]\n";
    std::cout << "    - Adapting Luminance (L_A): " << vc.L_A << " cd/m^2\n";
    std::cout << "    - Background Factor (Y_b):  " << vc.Y_b << "\n";
    std::cout << "    - Adaptation Factor (D):    " << coeff.D << "\n";
    std::cout << "    - White Point Achromatic A_w: " << coeff.A_w << "\n\n";

    // 3. Workload Suite: 10K, 100K, 1M samples
    std::vector<size_t> workload_sizes = {10000, 100000, 1000000};
    std::vector<benchmark::BenchmarkResult> all_benchmark_results;

    std::cout << "=========================================================================================\n";
    std::cout << "  MULTI-WORKLOAD EXPERIMENTAL BENCHMARKING (Single-Threaded Execution)\n";
    std::cout << "=========================================================================================\n";

    for (size_t target_size : workload_sizes) {
        std::string filename = "data/colors_" + std::to_string(target_size) + ".csv";
        std::cout << "\n>>> Workload: " << target_size << " Samples (File: " << filename << ") <<<\n";
        
        std::vector<DatasetRow> dataset = load_xyz_csv(filename);
        if (dataset.empty()) {
            std::cerr << "    ERROR: Could not load " << filename << "! Skipping workload.\n";
            continue;
        }

        size_t count = dataset.size();
        std::cout << "    Loaded " << count << " samples into memory. Pre-allocating buffers...\n";

        // Setup AoS memory
        std::vector<cam16::XYZ> xyz_inputs(count);
        for (size_t i = 0; i < count; ++i) {
            xyz_inputs[i] = dataset[i].xyz;
        }
        std::vector<cam16::CAM16Output> scalar_outputs(count);

        // Setup SoA memory (32-byte aligned for AVX2 YMM registers)
        cam16::XYZ_SoA in_soa;
        in_soa.count = count;
        in_soa.x = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        in_soa.y = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        in_soa.z = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));

        for (size_t i = 0; i < count; ++i) {
            in_soa.x[i] = dataset[i].xyz.x;
            in_soa.y[i] = dataset[i].xyz.y;
            in_soa.z[i] = dataset[i].xyz.z;
        }

        cam16::CAM16Output_SoA auto_out_soa;
        auto_out_soa.count = count;
        auto_out_soa.J = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        auto_out_soa.C = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        auto_out_soa.h = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        auto_out_soa.s = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        auto_out_soa.Q = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        auto_out_soa.M = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        auto_out_soa.H = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        auto_out_soa.a = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        auto_out_soa.b = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));

        cam16::CAM16Output_SoA avx2_out_soa;
        avx2_out_soa.count = count;
        avx2_out_soa.J = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        avx2_out_soa.C = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        avx2_out_soa.h = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        avx2_out_soa.s = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        avx2_out_soa.Q = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        avx2_out_soa.M = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        avx2_out_soa.H = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        avx2_out_soa.a = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));
        avx2_out_soa.b = static_cast<float*>(cam16::allocate_aligned(count * sizeof(float), 32));

        // For the 10,000 dataset, save the verification files
        if (count == 10000) {
            cam16::forward_scalar_batch(xyz_inputs.data(), scalar_outputs.data(), count, coeff);
            save_cam16_results_csv("results/scalar_10000.csv", dataset, scalar_outputs);

            cam16::forward_auto_soa(in_soa, auto_out_soa, coeff);
            save_soa_results_csv("results/auto_10000.csv", dataset, auto_out_soa);

            cam16::forward_avx2_soa(in_soa, avx2_out_soa, coeff);
            save_soa_results_csv("results/avx2_10000.csv", dataset, avx2_out_soa);
        }

        // Iteration counts based on workload size
        int warmup_runs = 5;
        int timed_runs = (count <= 10000) ? 25 : ((count <= 100000) ? 15 : 10);

        std::cout << "    Benchmarking (Warmup: " << warmup_runs << " runs, Timed: " << timed_runs << " runs)...\n";

        // 1. Scalar Baseline
        auto scalar_bench = benchmark::run_benchmark(
            "Scalar Baseline",
            count,
            warmup_runs,
            timed_runs,
            [&]() {
                cam16::forward_scalar_batch(xyz_inputs.data(), scalar_outputs.data(), count, coeff);
            },
            [&]() -> float {
                return scalar_outputs[0].J + scalar_outputs[count - 1].J;
            }
        );

        // 2. Compiler Auto-Vectorization (SoA)
        auto auto_bench = benchmark::run_benchmark(
            "Compiler Auto-Vec (SoA)",
            count,
            warmup_runs,
            timed_runs,
            [&]() {
                cam16::forward_auto_soa(in_soa, auto_out_soa, coeff);
            },
            [&]() -> float {
                return auto_out_soa.J[0] + auto_out_soa.J[count - 1];
            },
            scalar_bench.median_ms
        );

        // 3. Manual AVX2 SIMD (SoA)
        auto avx2_bench = benchmark::run_benchmark(
            "Manual AVX2 SIMD (SoA)",
            count,
            warmup_runs,
            timed_runs,
            [&]() {
                cam16::forward_avx2_soa(in_soa, avx2_out_soa, coeff);
            },
            [&]() -> float {
                return avx2_out_soa.J[0] + avx2_out_soa.J[count - 1];
            },
            scalar_bench.median_ms
        );

        // Print comparative table
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "    ---------------------------------------------------------------------------------\n";
        std::cout << "    Implementation           Median (ms)  Mean (ms)  StdDev    Throughput (Mcps)  Speedup\n";
        std::cout << "    ---------------------------------------------------------------------------------\n";
        std::cout << "    " << std::left << std::setw(25) << scalar_bench.implementation_name
                  << std::right << std::setw(11) << scalar_bench.median_ms
                  << std::setw(11) << scalar_bench.mean_ms
                  << std::setw(10) << scalar_bench.stddev_ms
                  << std::setw(18) << scalar_bench.throughput_mcps
                  << std::setw(10) << "1.000x\n";

        std::cout << "    " << std::left << std::setw(25) << auto_bench.implementation_name
                  << std::right << std::setw(11) << auto_bench.median_ms
                  << std::setw(11) << auto_bench.mean_ms
                  << std::setw(10) << auto_bench.stddev_ms
                  << std::setw(18) << auto_bench.throughput_mcps
                  << std::setw(9) << auto_bench.speedup_vs_scalar << "x\n";

        std::cout << "    " << std::left << std::setw(25) << avx2_bench.implementation_name
                  << std::right << std::setw(11) << avx2_bench.median_ms
                  << std::setw(11) << avx2_bench.mean_ms
                  << std::setw(10) << avx2_bench.stddev_ms
                  << std::setw(18) << avx2_bench.throughput_mcps
                  << std::setw(9) << avx2_bench.speedup_vs_scalar << "x\n";
        std::cout << "    ---------------------------------------------------------------------------------\n";

        all_benchmark_results.push_back(scalar_bench);
        all_benchmark_results.push_back(auto_bench);
        all_benchmark_results.push_back(avx2_bench);

        // Free aligned buffers
        cam16::free_aligned(in_soa.x);
        cam16::free_aligned(in_soa.y);
        cam16::free_aligned(in_soa.z);

        cam16::free_aligned(auto_out_soa.J);
        cam16::free_aligned(auto_out_soa.C);
        cam16::free_aligned(auto_out_soa.h);
        cam16::free_aligned(auto_out_soa.s);
        cam16::free_aligned(auto_out_soa.Q);
        cam16::free_aligned(auto_out_soa.M);
        cam16::free_aligned(auto_out_soa.H);
        cam16::free_aligned(auto_out_soa.a);
        cam16::free_aligned(auto_out_soa.b);

        cam16::free_aligned(avx2_out_soa.J);
        cam16::free_aligned(avx2_out_soa.C);
        cam16::free_aligned(avx2_out_soa.h);
        cam16::free_aligned(avx2_out_soa.s);
        cam16::free_aligned(avx2_out_soa.Q);
        cam16::free_aligned(avx2_out_soa.M);
        cam16::free_aligned(avx2_out_soa.H);
        cam16::free_aligned(avx2_out_soa.a);
        cam16::free_aligned(avx2_out_soa.b);
    }

    // Export comprehensive results across all workloads
    std::string results_csv = "results/benchmark_results.csv";
    benchmark::export_benchmark_csv(results_csv, all_benchmark_results);
    std::cout << "\n[6] Successfully logged full multi-workload benchmark results to: " << results_csv << "\n";
    std::cout << "=========================================================================================\n";

    return 0;
}
