#!/usr/bin/env bash
set -euo pipefail
# Generate SHA256 checksums for key artifacts (Debian packages, binaries, scripts)
# Usage: scripts/generate_checksums.sh > CHECKSUMS.txt

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ARTIFACT_DIRS=("$ROOT_DIR" "$ROOT_DIR/bin" "$ROOT_DIR/debian" "$ROOT_DIR/archives/debian-builds")

for dir in "${ARTIFACT_DIRS[@]}"; do
  if [ -d "$dir" ]; then
    find "$dir" -maxdepth 1 -type f \( -name 'crecall_*' -o -name '*.deb' -o -name '*.dsc' -o -name '*.tar.gz' -o -name 'crecall' \) -print0 2>/dev/null | \
      while IFS= read -r -d '' f; do
        sha256sum "$f" || true
      done
  fi
done
