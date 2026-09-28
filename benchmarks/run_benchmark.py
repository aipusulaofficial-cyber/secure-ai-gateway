"""Deterministic local benchmark harness."""
from __future__ import annotations

import argparse
import json
import time


def run(iterations: int) -> dict:
    samples = []
    errors = 0
    for _ in range(iterations):
        started = time.perf_counter()
        try:
            _ = sum(range(1000))
        except Exception:
            errors += 1
        samples.append((time.perf_counter() - started) * 1000)
    ordered = sorted(samples)

    def pct(q: float) -> float:
        return ordered[min(len(ordered) - 1, int(len(ordered) * q))]

    return {"iterations": iterations, "throughput_ops_per_sec": iterations / (sum(samples) / 1000) if samples else 0, "latency_ms": {"p50": pct(0.50), "p95": pct(0.95), "p99": pct(0.99)}, "error_rate": errors / iterations if iterations else 0, "measurement": "local harness; not a production performance claim"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=1000)
    args = parser.parse_args()
    print(json.dumps(run(max(1, args.iterations)), indent=2))
