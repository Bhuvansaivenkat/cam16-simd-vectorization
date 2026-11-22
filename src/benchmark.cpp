#include "benchmark.h"
#include <iostream>
#include <fstream>
#include <algorithm>
#include <numeric>
#include <cmath>

namespace benchmark {

BenchmarkResult run_benchmark(
    const std::string& name,
    size_t sample_count,
    int warmup_runs,
    int timed_runs,
    std::function<void()> work_fn,
    std::function<float()> checksum_fn,
    double baseline_median_ms
) {
    // Warm-up cycles to prime CPU caches and turbo boost states
    for (int i = 0; i < warmup_runs; ++i) {
        work_fn();
    }

    std::vector<double> timings_ms;
    timings_ms.reserve(timed_runs);

    float last_checksum = 0.0f;
    for (int i = 0; i < timed_runs; ++i) {
        auto start = std::chrono::high_resolution_clock::now();
        work_fn();
        auto end = std::chrono::high_resolution_clock::now();

        std::chrono::duration<double, std::milli> duration = end - start;
        timings_ms.push_back(duration.count());
        last_checksum += checksum_fn(); // Prevent dead code elimination
    }

    std::sort(timings_ms.begin(), timings_ms.end());

    double median_ms = timings_ms[timings_ms.size() / 2];
    double sum = std::accumulate(timings_ms.begin(), timings_ms.end(), 0.0);
    double mean_ms = sum / timings_ms.size();
    double min_ms = timings_ms.front();
    double max_ms = timings_ms.back();

    double accum = 0.0;
    for (double t : timings_ms) {
        accum += (t - mean_ms) * (t - mean_ms);
    }
    double stddev_ms = std::sqrt(accum / timings_ms.size());

    // Million colors per second (Mcps)
    double throughput_mcps = (static_cast<double>(sample_count) / (median_ms / 1000.0)) / 1e6;
    double speedup = (baseline_median_ms > 0.0) ? (baseline_median_ms / median_ms) : 1.0;

    return BenchmarkResult{
        name,
        sample_count,
        median_ms,
        mean_ms,
        min_ms,
        max_ms,
        stddev_ms,
        throughput_mcps,
        speedup,
        last_checksum
    };
}

void export_benchmark_csv(
    const std::string& filepath,
    const std::vector<BenchmarkResult>& results
) {
    std::ofstream file(filepath);
    if (!file.is_open()) {
        std::cerr << "Failed to open benchmark CSV file for writing: " << filepath << std::endl;
        return;
    }

    file << "Implementation,SampleCount,Median_ms,Mean_ms,Min_ms,Max_ms,StdDev_ms,Throughput_Mcps,Speedup,Checksum\n";
    for (const auto& r : results) {
        file << r.implementation_name << ","
             << r.sample_count << ","
             << r.median_ms << ","
             << r.mean_ms << ","
             << r.min_ms << ","
             << r.max_ms << ","
             << r.stddev_ms << ","
             << r.throughput_mcps << ","
             << r.speedup_vs_scalar << ","
             << r.checksum << "\n";
    }
}

} // namespace benchmark
