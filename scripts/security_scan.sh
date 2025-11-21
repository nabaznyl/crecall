#!/usr/bin/env bash
set -euo pipefail

echo "[security-scan] Starting consolidated security audit"

if command -v pip-audit >/dev/null 2>&1; then
  echo "[pip-audit] Running..." && pip-audit || echo "[pip-audit] Completed with findings"
else
  echo "[pip-audit] Not installed. Install with: pip install pip-audit"
fi

if command -v safety >/dev/null 2>&1; then
  echo "[safety] Running..." && safety check || echo "[safety] Completed with findings"
else
  echo "[safety] Not installed. Install with: pip install safety"
fi

if [ -f "package.json" ]; then
  if command -v npm >/dev/null 2>&1; then
    echo "[npm audit] Running..." && npm audit || echo "[npm audit] Completed with findings"
  else
    echo "[npm audit] npm not available"
  fi
fi

if command -v trivy >/dev/null 2>&1; then
  echo "[trivy fs] Scanning filesystem..." && trivy fs . || echo "[trivy] Completed with findings"
else
  echo "[trivy] Not installed. Install from https://aquasecurity.github.io/trivy/"
fi

echo "[security-scan] Finished"