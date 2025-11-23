#!/usr/bin/env bash
set -euo pipefail

# Quick mutation testing runner for CI and local use
# Usage: ./scripts/run_mutation_tests.sh [--paths-to-mutate PATHS]

PATHS_TO_MUTATE=${1:-backend/app}
JOBS=${2:-2}

echo "Installing dev requirements..."
python -m pip install --upgrade pip
pip install -r backend/requirements-dev.txt

echo "Running mutmut on paths: ${PATHS_TO_MUTATE} (jobs=${JOBS})"
# run mutmut but don't fail the whole script if it returns non-zero (survived mutants)
mutmut run --paths-to-mutate ${PATHS_TO_MUTATE} -j ${JOBS} || true

echo "Writing results..."
mutmut results --show-only-survived > mutation-results.txt || true
echo "Saved mutation-results.txt"

exit 0
