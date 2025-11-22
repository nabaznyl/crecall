# CONTEXT_SNAPSHOT (Phase 0)
Date: 2025-11-21

## 1. Purpose (Transitional)
The project currently functions as a durable, queryable store for session context: capturing sessions, clips (contextual artifacts), and memories (derived or user-added recall units). It aspires to become a portable "personal recall layer" for development/research workflows across environments.

## 2. Current Stability
- Test Suite: 49 passing (async + legacy) after identifier alignment.
- Infrastructure: Deterministic startup; background tasks gated by `CRECALL_TEST_MODE`.
- Crash Safety: Signal/thread guards in place.

## 3. Architectural Overview
### Core Entities
- Session: External string `session_id`, internal integer PK. Lifecycle: create → active → archived.
- Clip: Belongs to a session. External `clip_id` (string) planned; currently generated logic TBD. Internal PK ensures referential integrity.
- Memory: References a clip (external string → internal PK). Provides higher-level recall/search enrichment.

### Identifier Pattern
External (user-facing, portable) IDs map to internal PKs via service layer resolution. Benefits: portability, future sharding/migration flexibility. Potential simplification (numeric exposure) noted but deferred.

### Layers
- API: FastAPI endpoints (sync & async sets).
- Service: Resolves external IDs, enforces invariants.
- Schemas: Pydantic v2, minimal validation.
- DB: SQLite (sync+async engines). Migration groundwork exists (alembic; PostgreSQL migration doc present).
- Utilities: Crash detection, autosave (gated in tests).

## 4. Strategic Gaps
| Area | Gap | Impact |
|------|-----|--------|
| Vision | Not documented | Reactive scope drift |
| Data Lifecycle | No archival/purge spec | Potential uncontrolled growth |
| Documentation | Fragmented across many markdowns | High onboarding friction |
| Operational Tooling | No CI, metrics, release automation | Slow iteration, hidden regressions |
| Real-world Workflows | Not formalized | Hard to validate usefulness |
| Performance | No baseline metrics | Optimization blind spots |
| Observability | No structured logging/metrics | Difficult root cause analysis |
| Differentiation | Not yet articulated | Risk of CRUD commoditization |

## 5. Test Coverage Snapshot
- Async: 23 tests (clips, memories, security, sessions)
- Legacy Sync: 26 tests (clips, memories, sessions, integration)
- Missing: Explicit behavioral workflow tests; performance tests; portability roundtrip tests.

## 6. Decisions Log (Recent)
| Date | Decision | Rationale | Revisit |
|------|----------|-----------|---------|
| 2025-11-21 | Keep external string IDs | Portability & migration resilience | Review after perf baseline |
| 2025-11-21 | Service-layer ID resolution | Encapsulates mapping; prevents schema churn | Stable |
| 2025-11-21 | Test mode gating of background tasks | Deterministic tests | Stable |
| 2025-11-21 | Roadmap Phases 0-9 approved | Provide disciplined progression | Review quarterly |

## 7. Roadmap Summary (Approved)
0 Alignment → 1 Structure → 2 Workflows → 3 Quality → 4 Automation → 5 Performance → 6 Release → 7 Feedback → 8 Enhancements → 9 Hardening.

## 8. Immediate Next Steps
- Draft Vision (VISION.md)
- Data Model Spec (docs/data_model.md)
- Workflows skeleton (docs/workflows.md)
- Archive plan (ARCHIVE_PLAN.md)
- Introduce config & logging modules.

## 9. Open Questions
- Clip external ID generation strategy (semantic vs UUID?)
- Memory search mechanism (simple LIKE vs vector index?)
- Export/import format canonicalization (JSON schema? versioned envelope?)

## 10. Risk Inventory
| Risk | Description | Mitigation |
|------|-------------|------------|
| Scope Creep | Adding features without roadmap mapping | Enforce phase tagging in PRs |
| Data Bloat | No retention → large unindexed DB | Implement archival & pruning in Phase 4 |
| Performance Surprise | Scale drops due to naive queries | Benchmark & index during Phase 5 |
| Low Differentiation | Seen as CRUD store | Define unique workflows & tagging/search enhancements |

## 11. Metrics (To Define)
- Median memory search latency (<150ms target initial)
- Startup time (<3s local)
- Crash recovery fidelity (100% committed sessions)
- Export/import roundtrip integrity (>99.99%)

## 12. Simplification Note
Potential future simplification: expose numeric IDs directly if portability & migration flexibility become low priority. Status: Deferred.

---
END OF SNAPSHOT
