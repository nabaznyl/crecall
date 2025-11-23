#!/usr/bin/env python3
"""Validate pip-licenses JSON output against policy.

Usage:
  scripts/license_check.py --files backend/pip-licenses.json [other_files...]

Exits with code 1 if any package has an UNKNOWN/empty license or matches a disallowed license.
DISALLOWED_LICENSES env var (comma-separated) can be used to mark additional licenses as disallowed.
"""
import argparse
import json
import os
import sys
from typing import List


def load_json(path: str):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_issues(data, disallowed: List[str]):
    issues = []
    for entry in data:
        name = entry.get("Name") or entry.get("name")
        license_field = entry.get("License") or entry.get("license") or ""
        lf = (license_field or "").strip()
        if not lf or lf.upper() == "UNKNOWN":
            issues.append((name, license_field, "unknown"))
            continue
        for d in disallowed:
            if d.upper() in lf.upper():
                issues.append((name, license_field, f"disallowed:{d}"))
                break
    return issues


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", nargs="+", required=True)
    args = parser.parse_args()
    disallowed_env = os.getenv("DISALLOWED_LICENSES", "")
    disallowed = [x.strip() for x in disallowed_env.split(",") if x.strip()]
    all_issues = []
    for p in args.files:
        if not os.path.exists(p):
            print(f"Warning: file not found: {p}")
            continue
        try:
            data = load_json(p)
        except Exception as e:
            print(f"Failed to read {p}: {e}")
            continue
        issues = find_issues(data, disallowed)
        if issues:
            for it in issues:
                all_issues.append((p, it[0], it[1], it[2]))

    if all_issues:
        print("License policy violations detected:")
        for f, name, lic, reason in all_issues:
            print(f" - {f}: {name} -> '{lic}' ({reason})")
        sys.exit(1)
    print("No license issues found.")


if __name__ == "__main__":
    main()
