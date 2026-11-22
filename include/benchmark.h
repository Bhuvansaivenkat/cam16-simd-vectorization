#pragma once
#include <string>
#include <vector>
#include <functional>
#include <chrono>

namespace benchmark {

struct BenchmarkResult {
    std::string implementation_name;
    size_t sample_count;
    double median_ms;
    double mean_ms;
    double min_ms;
    double max_ms;
    double stddev_ms;
    double throughput_mcps; // Million colors per second (Mega-colors/sec)
    double speedup_vs_scalar;
    float checksum;         // Prevents compiler dead-code elimination
};

// Benchmark runner with warm-up cycles and multi-run statistics
BenchmarkResult run_benchmark(
    const std::string& name,
    size_t sample_count,
    int warmup_runs,
    int timed_runs,
    std::function<void()> work_fn,
    std::function<float()> checksum_fn,
    double baseline_median_ms = 0.0
);

// Exports benchmark results to CSV format
void export_benchmark_csv(
    const std::string& filepath,
    const std::vector<BenchmarkResult>& results
);

} // namespace benchmark
