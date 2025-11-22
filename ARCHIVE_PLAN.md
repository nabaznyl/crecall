# ARCHIVE_PLAN (Draft v0.1)
Date: 2025-11-21

## Candidates for Archival
| Path | Category | Rationale | Action |
|------|----------|-----------|--------|
| backups/prealpha-20251121/ | Backup set | Legacy pre-alpha raw dump | Move to archive/backups/ |
| backups/prealpha-20251121-backup.tar.gz | Backup artifact | Retain for provenance | Move & record checksum |
| backups/prealpha-20251121-backup.tar.gz.sha256 | Integrity file | Needed for verification | Move with artifact |
| PRE_ALPHA_NOTES.md | Legacy notes | Superseded by CONTEXT_SNAPSHOT.md | Move then reference index |
| ADAPTATION_BRAINSTORM.md | Ideation doc | Incorporated into VISION.md direction | Move |
| CLIP_DEMO.md | Early demo | Replace with formal workflow docs | Move |
| STEP_6_CRASH_DETECTION.md | Point-in-time fix | Summarized in test results & utils docs | Move |
| TESTING_CHECKLIST.md | Fragmented testing guidance | Consolidate into Quality phase docs | Move |
| SEMANTIC_SEARCH_PLAN.md | Future enhancement | Keep but mark Phase 8 | Move (tag enhancement) |

## Retention Policy (Initial)
- Keep archived artifacts indefinitely until size threshold defined in Phase 4.
- Maintain SHA256 checksum for each binary export file.

## Archive Directory Structure (Planned)
```
archive/
  backups/
  legacy_notes/
  demos/
  enhancement_plans/
  CHANGELOG_ARCHIVE.md
```

## Execution Steps (Phase 1)
1. Create subdirectories.
2. Move files preserving relative paths.
3. Update docs/index.md with archival references.
4. Add `ARCHIVE_README.md` describing policy & retrieval.

## Open Questions
- Compression format standardization (tar.gz vs zstd).
- Automated rotation triggers (size, age, activity).

---
END ARCHIVE PLAN
