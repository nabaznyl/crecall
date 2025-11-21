#!/usr/bin/env bash
set -euo pipefail

# Build multi-arch images (requires docker buildx configured)
# Usage: scripts/docker_build_all.sh <tag>

TAG="${1:-crecall:latest}"
PLATFORMS="linux/amd64,linux/arm64"

echo "[docker] Building $TAG for $PLATFORMS"
if ! docker buildx inspect >/dev/null 2>&1; then
  echo "[docker] buildx not initialized. Run: docker buildx create --use" >&2
  exit 1
fi

docker buildx build --platform "$PLATFORMS" -t "$TAG" . --progress=plain --load

echo "[docker] Done"
