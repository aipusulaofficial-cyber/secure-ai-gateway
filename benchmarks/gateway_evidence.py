"""Concurrent HTTP gateway evidence for CI; no production credentials required."""

from __future__ import annotations

import importlib
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

service = importlib.import_module("service")
gateway_domain = importlib.import_module("gateway_domain")
app = service.app


def run(requests: int = 200, workers: int = 16) -> dict[str, object]:
    if requests < 1 or workers < 1:
        raise ValueError("requests and workers must be positive")

    original_authorize = service.authorize
    service.authorize = lambda token, scope: gateway_domain.Decision(True, "ok")
    latencies: list[float] = []
    failures = 0

    def one(index: int) -> tuple[float, bool]:
        started = time.perf_counter()
        with TestClient(app) as client:
            response = client.post(
                "/v1/gateway",
                headers={"x-request-id": f"gateway-evidence-{index}"},
                json={
                    "key": f"evidence-client-{index}",
                    "payload": {"token": "benchmark-token", "scope": "inference"},
                },
            )
        latency = (time.perf_counter() - started) * 1000
        body = response.json() if response.status_code == 200 else {}
        return latency, response.status_code == 200 and body.get("allowed") is True

    wall_started = time.perf_counter()
    try:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = [pool.submit(one, index) for index in range(requests)]
            for future in as_completed(futures):
                latency, ok = future.result()
                latencies.append(latency)
                failures += int(not ok)
    finally:
        service.authorize = original_authorize

    wall_s = time.perf_counter() - wall_started
    ordered = sorted(latencies)

    def pct(q: float) -> float:
        index = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * q)))
        return ordered[index]

    return {
        "requests": requests,
        "workers": workers,
        "failures": failures,
        "error_rate": failures / requests,
        "throughput_rps": round(requests / wall_s, 2),
        "latency_ms": {
            "p50": round(statistics.median(ordered), 3),
            "p95": round(pct(0.95), 3),
            "p99": round(pct(0.99), 3),
        },
        "workload": "FastAPI TestClient -> /v1/gateway -> local rate limit -> policy boundary",
        "auth_fixture": "deterministic policy decision stub; no production credential or secret",
        "measurement": "repeatable CI HTTP gateway acceptance benchmark; not a production hardware claim",
    }


def write_report(path: str | Path) -> dict[str, object]:
    report = run()
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    write_report("artifacts/gateway-evidence.json")
