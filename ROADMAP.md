# crecall ROADMAP (Consolidated)

## Near-Term (Active)
- Theme toggle & persistence (DONE)
- Version alignment & patch note automation (IN PROGRESS)
- Context assembly API stub (DONE; expand to semantic selection)
- Embeddings service feature flag (DONE; enable with `CRECALL_ENABLE_EMBEDDINGS=1`)
- Integrity hashing script (`scripts/generate_checksums.sh`) (DONE)
- PostgreSQL migration prep (`MIGRATION_POSTGRESQL.md`) (READY)

## Next Implementation Targets
1. Alembic migrations for Postgres bootstrap.
2. Vector + trigram hybrid memory search.
3. Prompt context builder endpoint full version (`/api/context/assemble`).
4. Clip engine minimal schema & storage abstraction.
5. Git hook enrichment (auto-clip on commit).

## Core Pillars
| Pillar | Focus |
|--------|-------|
| Recall | Fast clip restore (<100ms target) |
| Memory | Rich searchable context (importance, tags, semantic) |
| Integrity | Signed + hashed artifacts, tamper detection |
| Intelligence | Semantic ranking, AI context injection |
| Resilience | Crash detection, recovery wizard, auto-save |

## Planned Milestones
### M1: Stable API Base
- Postgres backend operational.
- Alembic migrations tracked.
- Basic auth & user preference (theme).

### M2: Semantic Memory
- Embeddings generation live.
- `/api/memories/search` hybrid ranking.
- Memory relevance metrics instrumentation.

### M3: Clip Engine Alpha
- Manual clip creation via API.
- Auto-clip scheduler.
- Restore CLI command functional.

### M4: Context Intelligence
- Full context assembly (sanitization + scoring).
- AI prompt templates served.
- Feedback loop endpoints.

### M5: Integrity & Security
- Hash chain for clips.
- Release signing integrated.
- Secret scanning enforced pre-commit.

## Supporting Docs
- `MIGRATION_POSTGRESQL.md` – DB transition plan.
- `SEMANTIC_SEARCH_PLAN.md` – Hybrid relevance design.
- `AI_CONTEXT_INJECTION.md` – Prompt assembly pipeline.
- `SECURITY_PROTOCOLS.md` – Hardening steps.
- `BRAND_LICENSE_AGREEMENT.md` – Protective licensing.
- `ADAPTATION_BRAINSTORM.md` – Expansion and strategy.

## Feature Flags
| Flag | Env Var | Description |
|------|---------|-------------|
| Embeddings | `CRECALL_ENABLE_EMBEDDINGS=1` | Enables sentence-transformers model load |
| (future) Semantic Search | `CRECALL_ENABLE_SEM_SEARCH=1` | Activates vector ranking path |
| (future) Context AI | `CRECALL_ENABLE_CONTEXT_AI=1` | Enables enriched prompt assembly |

## Debt / Cleanup
- Replace AES-CBC with AES-GCM for transcripts (authenticity).
- Enforce JWT algorithm whitelisting.
- Normalize memory/tag lowercasing.
- Add pagination to clip/memory list endpoints.

## KPIs (Later)
- Average restore latency
- Memory search relevance (P@10)
- Crash recovery success rate
- Artifact integrity verification coverage

---
This roadmap consolidates individual plan docs for quick scanning.
