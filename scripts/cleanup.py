#!/usr/bin/env python3
"""Advanced cleanup utility for crecall workspace.

Features:
- Dry-run and execute modes
- Age-based deletion for backup tarballs
- Size-based reporting for large files (> threshold)
- JSON report output

Usage:
  python scripts/cleanup.py --dry-run
  python scripts/cleanup.py --execute --max-age-days 30 --keep-backups 2
  python scripts/cleanup.py --json-report cleanup_report.json

"""
from __future__ import annotations
import argparse
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKUPS = ROOT / "backups"

def collect_backup_deletions(keep: int, max_age_days: int):
    targets = []
    if not BACKUPS.is_dir():
        return targets
    tarballs = sorted(BACKUPS.glob("*.tar.gz"), key=lambda p: p.stat().st_mtime, reverse=True)
    cutoff = time.time() - max_age_days * 86400 if max_age_days > 0 else 0
    for idx, tb in enumerate(tarballs):
        if idx < keep:
            continue
        if cutoff and tb.stat().st_mtime > cutoff:
            continue
        targets.append(tb)
    return targets

def collect_pycache_and_pyc():
    targets = []
    for path in ROOT.rglob("__pycache__"):
        targets.append(path)
    for path in ROOT.rglob("*.pyc"):
        targets.append(path)
    return targets

def collect_large_files(min_size_mb: int):
    large = []
    thresh = min_size_mb * 1024 * 1024
    for path in ROOT.rglob("*"):
        if path.is_file():
            try:
                size = path.stat().st_size
            except OSError:
                continue
            if size >= thresh:
                large.append({"path": str(path.relative_to(ROOT)), "size_bytes": size})
    return sorted(large, key=lambda x: x["size_bytes"], reverse=True)

def delete_paths(paths):
    for p in paths:
        if p.is_dir():
            for child in sorted(p.rglob("*"), reverse=True):
                if child.is_file():
                    try:
                        child.unlink()
                    except OSError:
                        pass
            try:
                p.rmdir()
            except OSError:
                pass
        else:
            try:
                p.unlink()
            except OSError:
                pass

def main():
    parser = argparse.ArgumentParser(description="crecall advanced cleanup")
    parser.add_argument("--dry-run", action="store_true", help="List targets without deleting")
    parser.add_argument("--execute", action="store_true", help="Perform deletions")
    parser.add_argument("--keep-backups", type=int, default=1, help="Keep most recent N backup tarballs")
    parser.add_argument("--max-age-days", type=int, default=0, help="Delete backups older than days (if not kept)")
    parser.add_argument("--purge-pyc", action="store_true", help="Remove __pycache__ and .pyc files")
    parser.add_argument("--list-large", type=int, default=50, help="Report files >= size in MB (default 50MB)")
    parser.add_argument("--json-report", type=str, help="Write JSON report to file")
    args = parser.parse_args()

    if args.execute and args.dry_run:
        parser.error("Use either --dry-run or --execute, not both")

    backup_targets = collect_backup_deletions(args.keep_backups, args.max_age_days)
    pyc_targets = collect_pycache_and_pyc() if args.purge_pyc else []
    large_files = collect_large_files(args.list_large)

    report = {
        "backup_deletions": [str(p) for p in backup_targets],
        "pyc_deletions": [str(p) for p in pyc_targets],
        "large_files": large_files,
        "mode": "dry-run" if args.dry_run or not args.execute else "execute",
    }

    if args.json_report:
        with open(args.json_report, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)

    print(json.dumps(report, indent=2))

    if args.execute:
        delete_paths(backup_targets + pyc_targets)
        print("Deletion completed.")
    else:
        print("Dry-run; no deletions performed.")

if __name__ == "__main__":
    main()
