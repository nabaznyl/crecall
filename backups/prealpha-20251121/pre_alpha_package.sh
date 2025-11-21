#!/usr/bin/env bash
set -euo pipefail

# Pre-alpha packaging workflow
# 1. Run lint & tests
# 2. Export OpenAPI schema
# 3. Build Docker stable & nightly
# 4. Create release bundle directory
# 5. Summarize artifacts

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

echo "[1/5] Running backend tests"
if [ -d backend ]; then
  pushd backend >/dev/null
  if command -v pytest >/dev/null; then
    pytest -q || { echo "Tests failed"; exit 1; }
  else
    echo "pytest not installed; skipping tests"
  fi
  popd >/dev/null
fi

echo "[2/5] Exporting OpenAPI schema"
# Skip OpenAPI export if dependencies not met; packaging can proceed with docs
if [ -d backend/venv ] && [ -f backend/venv/bin/python ]; then
  backend/venv/bin/python backend/scripts/export_openapi.py --out backend/openapi.json || echo "OpenAPI export failed (venv)"
else
  echo "Virtual environment not available; skipping OpenAPI export (will use runtime docs)"
fi

echo "[3/5] Building Docker images"
# Skip Docker build if daemon not available; package source bundle instead
if command -v docker >/dev/null && docker info >/dev/null 2>&1; then
  docker build -t crecall:prealpha . || echo "Stable build failed"
  if [ -f Dockerfile.nightly ]; then
    docker build -f Dockerfile.nightly -t crecall:prealpha-nightly . || echo "Nightly build failed"
  fi
else
  echo "Docker not available or daemon not running; skipping image build"
fi

echo "[4/5] Creating release bundle"
BUNDLE_DIR="dist/prealpha"
rm -rf "$BUNDLE_DIR"
mkdir -p "$BUNDLE_DIR"

# Copy source and key files (excluding dev artifacts)
if command -v rsync >/dev/null; then
  rsync -a --exclude-from=.packageignore backend "$BUNDLE_DIR/"
  rsync -a --exclude-from=.packageignore frontend "$BUNDLE_DIR/"
  rsync -a --exclude-from=.packageignore vscode-extension "$BUNDLE_DIR/"
else
  # Fallback to cp with manual excludes
  cp -r backend "$BUNDLE_DIR/backend"
  find "$BUNDLE_DIR/backend" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
  find "$BUNDLE_DIR/backend" -name "*.pyc" -delete 2>/dev/null || true
  find "$BUNDLE_DIR/backend" -name "*.db" -delete 2>/dev/null || true
  rm -f "$BUNDLE_DIR/backend/.env" 2>/dev/null || true
  
  cp -r frontend "$BUNDLE_DIR/frontend"
  rm -rf "$BUNDLE_DIR/frontend/node_modules" "$BUNDLE_DIR/frontend/.next" 2>/dev/null || true
  
  cp -r vscode-extension "$BUNDLE_DIR/vscode-extension"
  rm -rf "$BUNDLE_DIR/vscode-extension/node_modules" "$BUNDLE_DIR/vscode-extension/out" 2>/dev/null || true
fi

cp README.md "$BUNDLE_DIR/README.md" || true
cp INSTALL.md "$BUNDLE_DIR/INSTALL.md" || true
cp PATCH_NOTES.md "$BUNDLE_DIR/PATCH_NOTES.md" || true
cp dist/RELEASE_NOTES.md "$BUNDLE_DIR/RELEASE_NOTES.md" 2>/dev/null || true

# OpenAPI if generated
cp -f backend/openapi.json "$BUNDLE_DIR/openapi.json" 2>/dev/null || true

# Debian package if exists
DEB_PKG=$(ls -1 dist/crecall_*.deb 2>/dev/null | head -1 || true)
if [ -n "$DEB_PKG" ]; then
  cp "$DEB_PKG" "$BUNDLE_DIR/" || true
fi

# Create tarball
TARBALL="dist/crecall-prealpha-$(date +%Y%m%d).tar.gz"
tar czf "$TARBALL" -C dist prealpha
TARBALL_SIZE=$(du -h "$TARBALL" | cut -f1)
echo "Created bundle: $TARBALL ($TARBALL_SIZE)"

# Create checksums
cd dist
sha256sum "$(basename "$TARBALL")" > "$(basename "$TARBALL").sha256"
echo "Checksum: $(cat "$(basename "$TARBALL").sha256")"
cd "$ROOT_DIR"

# Collect summary
echo "[5/5] Summary"
ls -l "$BUNDLE_DIR"

echo "Pre-alpha packaging complete. Artifacts in $BUNDLE_DIR"
