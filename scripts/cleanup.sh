#!/usr/bin/env bash
set -euo pipefail
# crecall workspace cleanup utility
# Usage:
#   ./scripts/cleanup.sh --dry-run   # show what would be removed
#   ./scripts/cleanup.sh --execute   # perform deletions
#   ./scripts/cleanup.sh --help      # show help
# Options:
#   --keep-backups N   Keep most recent N backup tarballs (default 1)
#   --max-age-days D   Delete backup tarballs older than D days (if not kept)
#   --purge-venv       Remove backend/venv (requires reinstall later)
#   --purge-dist       Remove dist/ build artifacts
#   --purge-pyc        Remove all __pycache__ and *.pyc files
#   --purge-db         Remove local sqlite db files (crecall.db)
#   --extra PATH       Extra path to evaluate (can repeat)
#   --dry-run          Do not delete; list only
#   --execute          Perform deletions

KEEP_BACKUPS=1
MAX_AGE_DAYS=0
MODE="dry"
PURGE_VENV=0
PURGE_DIST=0
PURGE_PYC=0
PURGE_DB=0
EXTRA_PATHS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --keep-backups) KEEP_BACKUPS="$2"; shift 2;;
    --max-age-days) MAX_AGE_DAYS="$2"; shift 2;;
    --purge-venv) PURGE_VENV=1; shift;;
    --purge-dist) PURGE_DIST=1; shift;;
    --purge-pyc) PURGE_PYC=1; shift;;
    --purge-db) PURGE_DB=1; shift;;
    --extra) EXTRA_PATHS+=("$2"); shift 2;;
    --dry-run) MODE="dry"; shift;;
    --execute) MODE="exec"; shift;;
    --help) sed -n '1,40p' "$0"; exit 0;;
    *) echo "Unknown arg: $1"; exit 1;;
  esac
done

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
NOW_TS=$(date +%s)
CUT_TS=$(( NOW_TS - MAX_AGE_DAYS*24*3600 ))

log() { echo "[$MODE] $*"; }
would_delete() { log "DELETE: $1"; }
perform_delete() {
  if [[ $MODE == "exec" ]]; then
    rm -rf -- "$1"
    log "Deleted $1"
  else
    would_delete "$1"
  fi
}

# Collect targets
TARGETS=()

if [[ $PURGE_DIST -eq 1 && -d "$ROOT_DIR/dist" ]]; then
  TARGETS+=("$ROOT_DIR/dist")
fi
if [[ $PURGE_VENV -eq 1 && -d "$ROOT_DIR/backend/venv" ]]; then
  TARGETS+=("$ROOT_DIR/backend/venv")
fi
if [[ $PURGE_DB -eq 1 ]]; then
  [[ -f "$ROOT_DIR/crecall.db" ]] && TARGETS+=("$ROOT_DIR/crecall.db")
  [[ -f "$ROOT_DIR/backend/crecall.db" ]] && TARGETS+=("$ROOT_DIR/backend/crecall.db")
fi

# Backup retention
BACKUP_DIR="$ROOT_DIR/backups"
if [[ -d "$BACKUP_DIR" ]]; then
  mapfile -t tarballs < <(ls -1t "$BACKUP_DIR"/*.tar.gz 2>/dev/null || true)
  idx=0
  for tb in "${tarballs[@]}"; do
    (( idx++ ))
    if (( idx <= KEEP_BACKUPS )); then
      continue
    fi
    if (( MAX_AGE_DAYS > 0 )); then
      mt=$(stat -c %Y "$tb")
      if (( mt > CUT_TS )); then
        continue
      fi
    fi
    TARGETS+=("$tb")
  done
fi

# Pycache / pyc scanning
if [[ $PURGE_PYC -eq 1 ]]; then
  while IFS= read -r d; do TARGETS+=("$d"); done < <(find "$ROOT_DIR" -type d -name '__pycache__')
  while IFS= read -r f; do TARGETS+=("$f"); done < <(find "$ROOT_DIR" -type f -name '*.pyc')
fi

# Extra paths
for p in "${EXTRA_PATHS[@]}"; do
  [[ -e "$p" ]] && TARGETS+=("$p") || log "Extra path missing: $p"
done

log "Cleanup targets collected: ${#TARGETS[@]}"
for t in "${TARGETS[@]}"; do
  perform_delete "$t"
done

log "Cleanup complete."

if [[ $MODE == "dry" ]]; then
  log "Run again with --execute to perform deletions."
fi
