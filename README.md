# crecall

**Version:** v0.1.0d-7 (preview)  
**Status:** Active Development  
**Build Channels:** Stable | Nightly | Dev

Portable personal recall layer for technical workflows. Never lose context after crashes, restarts, or interruptions.

---

## Quick Start

### Docker (Recommended)
```bash
docker run -p 8000:8000 -v ~/.recall_memory:/root/.recall_memory crecall:stable
```
Access: http://localhost:8000/docs

### From Source
```bash
git clone https://github.com/crecall/crecall.git
cd crecall/backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

See [docs/installation.md](docs/installation.md) for complete setup.

---

## Documentation

**📚 Full Documentation**: [https://nabaznyl.github.io/crecall/](https://nabaznyl.github.io/crecall/)

**Local Docs**:
```bash
pip install mkdocs-material
mkdocs serve
# Visit http://localhost:8000
```

### Quick Links

| Guide | Purpose |
|-------|---------|
| [Quick Start](docs/quick-start.md) | Get running in 5 minutes |
| [Installation](docs/installation.md) | Setup (source, Docker, PostgreSQL) |
| [Configuration](docs/CONFIGURATION.md) | Environment & settings |
| [API Reference](docs/api/rest.md) | REST API documentation |
| [Contributing](docs/contributing.md) | How to contribute |
| [Architecture](docs/architecture.md) | System design & patterns |

**Architecture & Planning**:
- [Vision](VISION.md) - Product intent, personas, metrics
- [Context Snapshot](CONTEXT_SNAPSHOT.md) - Architecture & gaps
- [Roadmap](ROADMAP.md) - Milestones & KPIs
- [Build Standards](BUILD_STANDARDS.md) - CI/CD & releases

---

## What is crecall?

**Problem**: Ephemeral context (terminal buffers, scratch notes, decisions) decays quickly after crashes or restarts. Reconstructing "why" wastes time.

**Solution**:
- **Structured Capture**: Sessions → Clips → Memories
- **Portable IDs**: External string identifiers for export/import
- **Fast Restore**: Lightweight snapshots (<100ms restore target)
- **Lifecycle Management**: Enrichment, search, archival, pruning

**Primary Users**:
- Developer-Researcher Hybrids (frequent context pivots)
- Independent Analysts (fragmented findings collection)
- Power User Knowledge Gardeners (long-running multi-session projects)

---

## Key Features

**Current (v0.1.0d-7)**:
- ✅ Session/clip/memory API (REST + async)
- ✅ External vs internal identifier pattern
- ✅ Crash-safe startup (deterministic, gated background tasks)
- ✅ Centralized config & structured logging
- ✅ 84 passing tests + comprehensive test coverage
- ✅ Professional build infrastructure (stable/nightly/dev)
- ✅ PostgreSQL migration support
- ✅ CI/CD with automated quality checks (Black, Ruff, pytest)

**Planned (Roadmap)**:
- 🔜 Instant recall from lightweight clips
- 🔜 Semantic memory search (FTS + embeddings)
- 🔜 Automated retention & backup policies
- 🔜 Git integration (auto-clip on commit)
- 🔜 VS Code deep integration
- 🔜 Advanced tagging & categorization

---

## Architecture

**Layers**:
- API: FastAPI (async endpoints)
- Service: ID resolution, invariant enforcement
- Schemas: Pydantic v2 validation
- DB: SQLite (dev) / PostgreSQL (prod)
- Utilities: Config, logging, crash detection, autosave

**Pattern**: External string IDs (session_id, clip_id) → Service layer → Internal integer PKs

**Benefits**: Portability, migration flexibility, decoupled client/storage

---

## Status & Roadmap

**Phase 0 (Alignment)**: ✅ Complete  
**Phase 1 (Structure)**: ✅ Complete  
**Phase 2 (Workflows)**: ⏳ Next (session lifecycle, search, export/import)  
**Phase 3 (Quality)**: Test tier markers, coverage gating  
**Phase 4-9**: Automation → Performance → Release → Feedback → Enhancements → Hardening

See [Roadmap](ROADMAP.md) for detailed milestones.

---

## Development

```bash
# Backend
cd backend && source venv/bin/activate
pytest -v                    # Run tests
black app/ tests/            # Format
pylint app/                  # Lint

# Build stable release
./scripts/build-stable.sh

# Nightly build
./scripts/build-nightly.sh
```

### Pre-commit Hooks
Install and activate automated formatting & security checks:
```bash
pip install pre-commit
pre-commit install
```
Hooks run on staged changes (Black, Ruff, pip-audit, basic hygiene). Use `SKIP=pip-audit git commit -m ...` to bypass selectively.

### Type Checking (Mypy)
Run incremental static analysis:
```bash
mypy app
```
Configuration lives in `backend/pyproject.toml` under `[tool.mypy]`.

## CI & Observability

Quick references for the CI observability and smoke-test helpers added to this repository:

- **OTEL smoke-tests:** Two CI jobs validate OpenTelemetry:
	- `otel-import-check` (fast) verifies OTEL packages import cleanly across Python versions.
	- `otel-integration` (full) installs runtime deps and runs an in-memory OTEL integration smoke test that asserts spans are produced.

- **Run smoke checks locally:**
	- Install import-check deps: `pip install -r backend/requirements-otel.txt`
	- Run the lightweight import check: `python .github/scripts/otel_smoke.py`
	- For integration smoke (requires app code): run the app in a venv or rely on the script which imports `backend/app`; the integration script uses a `TestClient` and will run without network: `python .github/scripts/otel_integration_smoke.py`.

- **Fetch CI artifacts:** A helper script `./.automation/ci_fetch_artifacts.sh` can dispatch the `otel-smoke` workflow, poll for completion and download artifacts. It requires a GitHub token with access to the repo set as `GITHUB_TOKEN`.

See `docs/observability.md` for more details and examples.

### SBOM Generation (CI)
CycloneDX SBOMs (Python & Node) produced automatically in CI (`sbom` job). Artifacts appear under `sbom-artifacts` in workflow runs.

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for complete guide.

---

## Success Metrics

- Clip creation: <75ms
- Memory search (<10k clips): <150ms p50
- Export/import fidelity: 100%
- Crash recovery: 0 data loss
- Startup: <3s (<50k clips)
- Test coverage: >85%

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow & standards.

---

## License

[MIT License](LICENSE) - See LICENSE file for details.

---

**Built to solve real problems. Never lose context again.**
