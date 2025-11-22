# crecall Documentation

**Version:** v0.1.0d-7 (preview)  
**Status:** Active Development  
**Last Updated:** 2025-11-21

---

## Overview

crecall is a portable personal recall layer for technical and research workflows. It captures evolving session context (decisions, code fragments, references) as structured clips and elevates them into searchable memories, enabling rapid, trustworthy reconstruction of past reasoning across machines and time.

**Core Problem**: Ephemeral context decays quickly after crashes, restarts, or interruptions. Reconstructing "why" decisions were made wastes time and risks errors.

**Solution**: Structured capture (sessions → clips → memories), external stable IDs for portability, and designed lifecycle: enrichment, search, archival, pruning.

---

## Quick Navigation

| Document | Purpose |
|----------|---------|
| [Installation](installation.md) | Setup instructions for all deployment models |
| [Version History](changelog.md) | Complete version history and patch notes |
| [Data Model](data_model.md) | Entity specs, relationships, lifecycle |
| [Workflows](workflows.md) | Core user journeys and operational flows |
| [Configuration](CONFIGURATION.md) | Environment variables, settings, tuning |
| [Development](DEVELOPMENT.md) | Developer setup, testing, contribution |
| [Quality](quality.md) | Test tiers, coverage goals, CI |

---

## Key Concepts

### Sessions
Containers for related work. External string `session_id` maps to internal PK. Lifecycle: active → frozen → archived.

### Clips
Contextual artifacts belonging to a session. Planned external `clip_id` for portability. Captures code, notes, metadata.

### Memories
Higher-level recall units derived from clips. Annotated, tagged, searchable. Links to clips for traceability.

### External vs Internal Identifiers
- **External**: Stable strings (session_id, clip_id) for API/export
- **Internal**: Integer PKs for relational integrity
- **Mapping**: Service layer resolves external → internal

---

## Architecture

**Layers:**
- **API**: FastAPI endpoints (sync & async)
- **Service**: ID resolution, invariant enforcement
- **Schemas**: Pydantic v2 validation
- **DB**: SQLite (sync+async) or PostgreSQL
- **Utilities**: Crash detection, autosave, config, logging

**Identifier Pattern Benefits:**
- Portability across environments
- Migration/sharding flexibility
- Decoupled client-visible IDs from storage

---

## Current Status

**Phase 0 (Alignment)**: ✅ Complete  
**Phase 1 (Structure)**: 🔄 In Progress (docs consolidation, config/logging done)

**Test Suite**: 49/49 passing (async + legacy)  
**Infrastructure**: Deterministic startup, crash-safe, structured logging

---

## Roadmap Phases

0. **Alignment**: Vision, data model, snapshot (✅)
1. **Structure**: Docs consolidation, config/logging, archive (🔄)
2. **Workflows**: Implement 3 core journeys (session, search, export/import)
3. **Quality**: Test tiers, coverage gating
4. **Automation**: Retention, backups, crash routines
5. **Performance**: Benchmarks, indexing
6. **Release**: CI/CD, artifact versioning
7. **Feedback**: Usage telemetry
8. **Enhancements**: Advanced search, tagging
9. **Hardening**: Observability, security review

---

## Success Metrics (Targets)

- Clip creation latency: <75ms local
- Memory search (<10k clips): <150ms p50, <300ms p95
- Export/import fidelity: 100%
- Crash recovery: 0 unrecoverable sessions
- Startup (cold): <3s with <50k clips
- Test coverage: >85% by Phase 5

---

## Support & Feedback

**Docs**: See index above for detailed guides  
**Issues**: Track in project repository  
**Vision**: [../VISION.md](../VISION.md)  
**Snapshot**: [../CONTEXT_SNAPSHOT.md](../CONTEXT_SNAPSHOT.md)

---

Built to solve real problems. Never lose context again.
