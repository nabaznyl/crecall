"""Structured in-process metrics collection service.

Provides lightweight counters and latency histograms with optional label dimensions.
Supports on-demand snapshot for /api/metrics endpoint.
"""

from __future__ import annotations

import threading
import time
from typing import Dict, Tuple


class MetricsCollector:
    def __init__(self):
        self._lock = threading.Lock()
        self._counters: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], int] = {}
        self._latency: Dict[Tuple[str, Tuple[Tuple[str, str], ...]], list] = {}
        self._started = time.time()

    @staticmethod
    def _labels_tuple(labels: Dict[str, str]) -> Tuple[Tuple[str, str], ...]:
        return tuple(sorted(labels.items()))

    def increment(self, name: str, amount: int = 1, labels: Dict[str, str] | None = None):
        key = (name, self._labels_tuple(labels or {}))
        with self._lock:
            self._counters[key] = self._counters.get(key, 0) + amount

    def observe_latency(self, name: str, value_ms: float, labels: Dict[str, str] | None = None):
        key = (name, self._labels_tuple(labels or {}))
        with self._lock:
            bucket = self._latency.setdefault(key, [])
            bucket.append(value_ms)
            # simple cap to prevent unbounded growth
            if len(bucket) > 5000:
                del bucket[:1000]

    def snapshot(self) -> Dict[str, object]:
        with self._lock:
            counters_out = []
            for (name, labels), value in self._counters.items():
                counters_out.append({"name": name, "labels": dict(labels), "value": value})
            latency_out = []
            for (name, labels), samples in self._latency.items():
                if samples:
                    sorted_samples = sorted(samples)
                    count = len(samples)
                    avg = sum(samples) / count
                    p95 = sorted_samples[int(0.95 * (count - 1))]
                    p99 = sorted_samples[int(0.99 * (count - 1))]
                    latency_out.append(
                        {
                            "name": name,
                            "labels": dict(labels),
                            "count": count,
                            "avg_ms": round(avg, 2),
                            "p95_ms": round(p95, 2),
                            "p99_ms": round(p99, 2),
                        }
                    )
            return {
                "uptime_seconds": round(time.time() - self._started, 2),
                "counters": counters_out,
                "latency": latency_out,
            }

    def prometheus(self) -> str:
        lines = [
            "# HELP crecall_uptime_seconds Uptime of the crecall backend",
            "# TYPE crecall_uptime_seconds gauge",
            f"crecall_uptime_seconds {round(time.time() - self._started, 2)}",
        ]
        # Counters
        for (name, labels), value in self._counters.items():
            label_str = ",".join([f"{k}='{v}'" for k, v in labels])
            lines.append(
                f"crecall_counter_total{{metric='{name}'{(','+label_str) if label_str else ''}}} {value}"
            )
        # Latency summaries
        for (name, labels), samples in self._latency.items():
            if not samples:
                continue
            sorted_samples = sorted(samples)
            count = len(samples)
            avg = sum(samples) / count
            p95 = sorted_samples[int(0.95 * (count - 1))]
            p99 = sorted_samples[int(0.99 * (count - 1))]
            label_str = ",".join([f"{k}='{v}'" for k, v in labels])
            prefix = f"crecall_latency_ms_summary{{metric='{name}'{(','+label_str) if label_str else ''}}}"
            lines.append(f"{prefix} {round(avg,2)}")
            lines.append(f"{prefix}_p95 {round(p95,2)}")
            lines.append(f"{prefix}_p99 {round(p99,2)}")
        return "\n".join(lines) + "\n"


metrics = MetricsCollector()
