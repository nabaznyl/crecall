#!/usr/bin/env python3
"""Simple benchmark regression checker for pytest-benchmark JSON output.

Compares the mean time of each benchmark between a baseline and current run.
Exits with code 2 if regressions exceed the threshold for any benchmark.

Usage:
  python3 backend/benchmarks/check_regressions.py --baseline baseline.json --current current.json --threshold 0.05

If baseline file is missing, the script writes a message and exits 0 (CI should upload the current results as artifact).
"""
import argparse
import json
import sys
from pathlib import Path


def load_bench(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def index_by_name(data):
    rv = {}
    for b in data.get("benchmarks", []):
        rv[b.get("name")] = b
    return rv


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--baseline", required=True)
    p.add_argument("--current", required=True)
    p.add_argument("--threshold", type=float, default=0.05)
    args = p.parse_args()

    baseline_path = Path(args.baseline)
    current_path = Path(args.current)
    if not current_path.exists():
        print(f"Current benchmark file not found: {current_path}")
        sys.exit(1)

    if not baseline_path.exists():
        print(f"Baseline not found ({baseline_path}). Skipping regression check and uploading current run as baseline artifact.")
        sys.exit(0)

    base = load_bench(baseline_path)
    cur = load_bench(current_path)
    base_idx = index_by_name(base)
    cur_idx = index_by_name(cur)

    regressions = []
    for name, cb in cur_idx.items():
        bb = base_idx.get(name)
        if not bb:
            continue
        try:
            # try median then mean
            cur_mean = cb.get("stats", {}).get("mean") or cb.get("stats", {}).get("median")
            base_mean = bb.get("stats", {}).get("mean") or bb.get("stats", {}).get("median")
            if cur_mean is None or base_mean is None:
                continue
            # regression if current is slower than baseline by threshold
            if cur_mean > base_mean * (1.0 + args.threshold):
                pct = (cur_mean - base_mean) / base_mean
                regressions.append((name, base_mean, cur_mean, pct))
        except Exception:
            continue

    if regressions:
        print("Benchmark regressions detected:")
        for r in regressions:
            print(f" - {r[0]}: baseline={r[1]:.6f}s current={r[2]:.6f}s delta={r[3]*100:.2f}%")
        sys.exit(2)

    print("No significant benchmark regressions detected.")
    sys.exit(0)


if __name__ == "__main__":
    main()
