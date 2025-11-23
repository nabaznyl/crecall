# VISION
Date: 2025-11-21 (Draft v0.1)

## 1. Vision Statement
Crecall is a portable personal recall layer for technical and research workflows. It captures evolving session context (decisions, code fragments, references) as structured clips and elevates them into searchable memories, enabling rapid, trustworthy reconstruction of past reasoning across machines and time.

## 2. Primary User Personas (Initial Defaults)
1. Developer-Researcher Hybrid: Frequently pivots between code, documentation, and exploratory notes; needs frictionless capture and later reconstruction.
2. Independent Analyst / Investigator: Collects fragmented findings during deep dives; requires integrity and portability for audit or sharing.
3. Power User Knowledge Gardener: Curates persistent context across long-running multi-session projects.

## 3. Core Problem Statement
Ephemeral context (terminal buffers, scratch notes, temp files) decays quickly. Reconstructing "why" decisions were made wastes time and risks mistakes. Existing tools (basic note apps or raw logs) lack structure, portability, and semantic search tailored to technical iterative workflows.

## 4. Value Proposition Differentiation
- Structured capture (sessions → clips → memories) vs amorphous note dumps.
- External stable IDs for portability (sync, export, diff) vs internal-only references.
- Designed for lifecycle: enrichment, search, archival, prune.
- Future semantic augmentation (tagging, embeddings) layered cleanly on baseline.

## 5. Non-Goals (Explicit Deferral)
- Real-time multi-user collaboration.
- Embedded ML inference pipeline (vector search deferred until baseline solid).
- Full-text OCR / media ingestion.
- Complex access control (single-user local focus first).

## 6. Must-Have First Production Feature Set
- Create & enrich sessions with clips (API + CLI).
- Promote clips into memories (annotate, categorize, link).
- Fast scoped search (session-bounded + global keyword).
- Export/import roundtrip (versioned portable JSON envelope).
- Automated crash snapshot & periodic backup.
- Retention & archival policy (age + sparsity pruning).

## 7. Deployment Model (Initial)
Phase 1–3: Local server (FastAPI) + CLI utilities.
Phase 4–6: Optional dockerized service with persistent volume.
Phase 7+: Pluggable remote sync (encrypted) – deferred until feedback loop maturity.

## 8. Data Scale Expectations
Short term: < 10k clips (single developer).
Medium term: 50k–250k clips (multi-month research backlog).
Long term: 1M+ clips requires indexing, partitioning, and archival tiers.

## 9. Success Metrics (Initial Targets)
- Median clip creation latency < 75ms local.
- Memory search (<=10k clips) < 150ms p50, < 300ms p95.
- Export/import fidelity: 100% entity & relationship restoration.
- Crash recovery: 0 unrecoverable committed sessions.
- Startup (cold) < 3s with <50k clips.
- Test coverage core modules >85% by Phase 5.

## 10. Operational Pillars
- Logging: Structured JSON (timestamp, level, component, correlation/session ID).
- Config: Central validation layer (required envs, fallbacks, version gating).
- Retention: Policy-driven prune (age, inactivity, size thresholds).
- Backup: Scheduled incremental + periodic full snapshots.
- Observability: Counters (clip_create/sec), gauges (active_sessions), timers (search_latency).

## 11. Lifecycle Model (High-Level)
Session: create → enrich → (optional) freeze → archive → prune (export before prune).
Clip: capture → validate → attach metadata → optional promote to memory.
Memory: create (link clip) → enrich (tags) → search & retrieve → archive.

## 12. Phase Mapping (Roadmap Reference)
- Alignment: Vision + model spec lock.
- Structure: Docs consolidation + config/log baseline.
- Workflows: End-to-end session/enrichment/import-export.
- Quality: Tiered tests & coverage gating.
- Automation: Retention, backups, crash routines.
- Performance: Benchmarks & targeted indexing.
- Release: CI/CD, artifact versioning.
- Feedback: Usage telemetry & prioritization loop.
- Enhancements: Advanced search & tagging.
- Hardening: Metrics, security review, threat modeling.

## 13. Open for Revision
This draft is a living artifact. Revisions logged in CHANGE_LOG or ROADMAP with version tags.

---
END VISION DRAFT
