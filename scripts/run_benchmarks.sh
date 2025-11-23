#!/usr/bin/env bash
set -euo pipefail

# Helper to install dev deps, run benchmarks, and run regression check.
# Usage: ./scripts/run_benchmarks.sh [--threshold 0.05]

THRESHOLD=0.05
if [[ ${1-} == "--threshold" && -n ${2-} ]]; then
  THRESHOLD=$2
fi

echo "Installing backend requirements..."
python3 -m pip install --upgrade pip
python3 -m pip install -r backend/requirements.txt

echo "Installing backend package in editable mode..."
python3 -m pip install -e backend

mkdir -p backend/benchmarks
TIMESTAMP=$(date -u +"%Y%m%dT%H%M%SZ")
RESULTS=backend/benchmarks/results-${TIMESTAMP}.json

echo "Running pytest-benchmark -> ${RESULTS}"
pytest backend/tests/benchmarks --benchmark-only --benchmark-json=${RESULTS}

echo "Running regression checker against backend/benchmarks/baseline.json (threshold=${THRESHOLD})"
python3 backend/benchmarks/check_regressions.py --baseline backend/benchmarks/baseline.json --current ${RESULTS} --threshold ${THRESHOLD}

echo "Benchmarks completed successfully. Results: ${RESULTS}"
