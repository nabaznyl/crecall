# Build Standards Documentation

This document describes the build standards and infrastructure for crecall, including the three build channels: **stable**, **nightly**, and **dev**.

## Build Channels

### Stable
- **Purpose:** Production-ready releases
- **Versioning:** `MAJOR.MINOR.PATCH-stable-BUILD` (e.g., `0.1.0-stable-1`)
- **Branch:** `main`
- **Schedule:** Manual releases when ready
- **Artifacts:** Full distribution packages, signed tarballs, Debian packages, Docker images
- **Quality Gates:** All tests pass, code reviewed, documentation updated

### Nightly
- **Purpose:** Latest development builds for testing
- **Versioning:** `MAJOR.MINOR.PATCH-nightly-YYYYMMDD+SHA` (e.g., `0.1.0-nightly-20251121+a1b2c3d`)
- **Branch:** `develop`
- **Schedule:** Automated daily at 2 AM UTC
- **Artifacts:** Tarballs, Docker images (tagged as `:nightly`)
- **Quality Gates:** Tests pass, automated builds only

### Dev
- **Purpose:** Local development and testing
- **Versioning:** `MAJOR.MINOR.PATCH-dev-BUILD` (e.g., `0.1.0-dev-6`)
- **Branch:** Any feature branch
- **Schedule:** On-demand by developers
- **Artifacts:** Local builds only
- **Quality Gates:** Minimal, for rapid iteration

## Version Management

### VERSION File

The `VERSION` file is the single source of truth for version numbers:

```bash
VERSION=0.1.0
CHANNEL=dev
BUILD_NUMBER=6
FULL_VERSION=${VERSION}-${CHANNEL}-${BUILD_NUMBER}
```

### Version Bumping

Use the version bump script:

```bash
# Bump patch version (0.1.0 -> 0.1.1)
./scripts/version-bump.sh patch stable

# Bump minor version (0.1.0 -> 0.2.0)
./scripts/version-bump.sh minor stable

# Bump major version (0.1.0 -> 1.0.0)
./scripts/version-bump.sh major stable

# Bump build number only (0.1.0-dev-6 -> 0.1.0-dev-7)
./scripts/version-bump.sh build dev
```

The script automatically updates:
- `VERSION` file
- `backend/pyproject.toml`
- `backend/app/main.py`
- `frontend/package.json`
- `vscode-extension/package.json`
- `bin/crecall`
- `README.md`

## Build Scripts

### Stable Release Build

```bash
./scripts/build-stable.sh
```

**Requirements:**
- VERSION file must have `CHANNEL=stable`
- All tests must pass
- Documentation updated

**Outputs to `dist/`:**
- `crecall-{VERSION}.tar.gz` - Full source tarball
- `crecall-{VERSION}.vsix` - VS Code extension
- `crecall_{VERSION}.deb` - Debian package
- Python wheel files
- `SHA256SUMS` - Checksums for all artifacts

### Nightly Build

```bash
./scripts/build-nightly.sh
```

**Features:**
- Generates date-based version automatically
- Temporarily modifies version files (restored after build)
- Creates `BUILD_INFO.txt` with build metadata
- Outputs to `dist-nightly/`

**Outputs:**
- `crecall-{VERSION}-nightly-{DATE}+{SHA}.tar.gz`
- `crecall-{VERSION}-nightly-{DATE}+{SHA}.vsix`
- `SHA256SUMS.txt`
- `BUILD_INFO.txt`

### Release Automation

```bash
./scripts/release.sh stable patch
```

**Full release workflow:**
1. Pre-flight checks (clean git, correct branch)
2. Version bump
3. Prompt for PATCH_NOTES.md update
4. Prompt for debian/changelog update
5. Run test suite
6. Build release artifacts
7. Commit changes
8. Create git tag
9. Display next steps (push, create GitHub release)

## Docker Images

### Building Images

**Stable:**
```bash
docker build -t crecall:stable .
# or
docker-compose build crecall-stable
```

**Nightly:**
```bash
docker build -f Dockerfile.nightly -t crecall:nightly .
# or
docker-compose build crecall-nightly
```

**Dev:**
```bash
docker build -f Dockerfile.dev -t crecall:dev .
# or
docker-compose up crecall-dev
```

### Running Containers

**Stable (production):**
```bash
docker run -p 8000:8000 -v ~/.recall_memory:/root/.recall_memory crecall:stable
```

**Nightly:**
```bash
docker run -p 8001:8000 -v ~/.recall_memory:/root/.recall_memory crecall:nightly
```

**Dev (with live reload):**
```bash
docker run -p 8002:8000 -p 5173:5173 -v $(pwd):/app crecall:dev
```

### Multi-Stage Build Optimization

All Dockerfiles use multi-stage builds:
1. **Backend Builder** - Installs Python dependencies
2. **Frontend Builder** - Builds React app
3. **Production** - Minimal runtime image

Benefits:
- Smaller final image (~200MB vs ~1GB)
- Faster builds with layer caching
- Security: no build tools in production

## CI/CD Pipeline

GitHub Actions workflow (`.github/workflows/ci-cd.yml`) handles:

### On Pull Request
- Lint code (Black, Pylint, ESLint, Prettier)
- Run test suite across Python versions (3.10, 3.11, 3.12)
- Upload coverage to Codecov

### On Push to main
- Run full build
- Trigger stable release if tagged

### On Push to develop
- Run full build
- Build nightly Docker image

### On Schedule (Daily 2 AM UTC)
- Build nightly artifacts
- Upload to artifact storage
- Tag Docker image as `:nightly`

### On Git Tag (v*)
- Build stable release
- Create GitHub Release
- Upload all artifacts
- Push Docker images with version tags

## Quality Gates

### Stable Release Checklist
- [ ] All tests pass (unit, integration)
- [ ] Code coverage >= 80%
- [ ] All linters pass (Black, Pylint, ESLint)
- [ ] Documentation updated
- [ ] PATCH_NOTES.md updated
- [ ] Debian changelog updated
- [ ] Manual testing completed
- [ ] Security scan clean (Trivy)
- [ ] PR approved by maintainer
- [ ] On `main` branch

### Nightly Build Checklist
- [ ] Tests pass on `develop` branch
- [ ] Automated build succeeds
- [ ] Docker image builds

### Dev Build
- [ ] Compiles without errors
- [ ] Basic functionality works

## Artifact Signing

For stable releases, sign tarballs with GPG:

```bash
# Generate detached signature
gpg --detach-sign --armor dist/crecall-{VERSION}.tar.gz

# Verify signature
gpg --verify dist/crecall-{VERSION}.tar.gz.asc dist/crecall-{VERSION}.tar.gz
```

## Distribution

### Stable Releases
- GitHub Releases (primary)
- Package repositories (future: apt, npm, PyPI)
- Docker Hub: `crecall/crecall:latest`, `crecall/crecall:0.1.0`

### Nightly Builds
- GitHub Actions artifacts (7-day retention)
- Docker Hub: `crecall/crecall:nightly`
- CDN/Download server (future)

## Checksums & Integrity

All builds generate SHA256 checksums:

```bash
# Generate checksums
./scripts/generate_checksums.sh > SHA256SUMS

# Verify artifact
sha256sum -c SHA256SUMS
```

## Rollback Procedures

If a release has issues:

1. **Tag Previous Version:**
   ```bash
   git tag v0.1.0-stable-2-rollback v0.1.0-stable-1
   ```

2. **Revert Changes:**
   ```bash
   git revert <commit-sha>
   ```

3. **Rebuild and Release:**
   ```bash
   ./scripts/release.sh stable patch
   ```

4. **Update Documentation:**
   - Add rollback note to PATCH_NOTES.md
   - Update GitHub release description

## Future Enhancements

- [ ] Automated package publishing (PyPI, npm, apt repo)
- [ ] Multi-architecture Docker builds (amd64, arm64)
- [ ] Release notes generation from commits
- [ ] Automated security scanning in CI
- [ ] Performance benchmarking in CI
- [ ] Smoke tests for Docker images
- [ ] Blue/green deployment for nightly

---

For questions about build infrastructure, see CONTRIBUTING.md or open an issue.
