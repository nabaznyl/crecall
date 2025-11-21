# Pre-Alpha Release Backup Manifest
**Date:** 2025-11-21  
**Backup Archive:** prealpha-20251121-backup.tar.gz (328 KB)  
**SHA256:** 1bd0960da2f6e0a6750c6551e85ccea073f756aadcd72e879c4c9acb0bac7e0e

## Contents

### Release Artifacts
- `crecall-prealpha-20251121.tar.gz` - Main release tarball (159 KB)
- `crecall-prealpha-20251121.tar.gz.sha256` - Release checksum
- `prealpha/` - Extracted source bundle (119 files)
  - backend/ - FastAPI service
  - frontend/ - React/Vite UI
  - vscode-extension/ - VS Code integration
  - Documentation (README.md, INSTALL.md, PATCH_NOTES.md, RELEASE_NOTES.md)

### Build/Package Configuration
- `.packageignore` - Exclusion patterns for release bundles
- `pre_alpha_package.sh` - Packaging script
- `PRE_ALPHA_NOTES.md` - Pre-alpha development notes

### Git Snapshot
- `git-commits.txt` - Last 5 commits
- `git-diff-stat.txt` - Change statistics from last 5 commits

## Release Highlights
- Dynamic rate limiting with runtime updates
- Clip restoration endpoint (state reconstruction)
- Comprehensive security middleware
- Metrics collection (JSON + Prometheus)
- Export/import with encryption
- Remote sync (SSH/SCP/SFTP)
- PostgreSQL migration support
- Branch safety detection

## Restore Instructions
```bash
# Extract backup
tar xzf prealpha-20251121-backup.tar.gz

# Verify release tarball
sha256sum -c crecall-prealpha-20251121.tar.gz.sha256

# Extract release
tar xzf crecall-prealpha-20251121.tar.gz
cd prealpha

# Follow INSTALL.md for setup
```

## Notes
- Clean source distribution (no .env, .db, __pycache__)
- All dependencies listed in requirements.txt
- VS Code extension requires packaging with vsce
- Docker builds require daemon access
- OpenAPI export requires running server
