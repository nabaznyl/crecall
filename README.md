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

**Start Here**: [docs/README.md](docs/README.md)

| Guide | Purpose |
|-------|---------|
| [Installation](docs/installation.md) | Setup (source, Docker, PostgreSQL) |
| [Configuration](docs/CONFIGURATION.md) | Environment & settings |
| [Data Model](docs/data_model.md) | Entities, relationships, lifecycle |
| [Workflows](docs/workflows.md) | Core user journeys |
| [Development](docs/DEVELOPMENT.md) | Developer setup & testing |
| [Version History](docs/changelog.md) | Complete changelog |
| [Quality](docs/quality.md) | Test tiers & coverage |

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
- ✅ 49/49 passing tests (async + legacy suites)
- ✅ Professional build infrastructure (stable/nightly/dev)
- ✅ PostgreSQL migration support

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

TBD - Project license to be determined. See [BRAND_LICENSE_AGREEMENT.md](BRAND_LICENSE_AGREEMENT.md) for protective draft.

---

**Built to solve real problems. Never lose context again.**
