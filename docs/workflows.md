# Workflows (Draft v0.1)
Date: 2025-11-21

## Workflow 1: Session Creation & Enrichment
### Goal
Establish a new context container and progressively capture related clips with minimal friction.

### Steps
1. Create session (`POST /sessions {session_id}` or auto-generate) → status: `active`.
2. Capture clip (`POST /clips {session_id, content, metadata?}`) – resolves external ID.
3. Optional metadata enrichment (`PATCH /clips/{clip_id}`) add tags/source.
4. Promote to memory (`POST /memories {linked_clip_id, annotations, tags}`).
5. Freeze session (`POST /sessions/{session_id}/freeze`) when active capture complete → status: `frozen` (prevents stray additions except recovery).
6. Archive (`POST /sessions/{session_id}/archive`) after retention threshold → status: `archived` (eligible for pruning).

### Status Transitions
```
active ──freeze──> frozen ──archive──> archived (irreversible)
         <──activate──┘
```

**Validation Rules:**
- Can only freeze `active` sessions.
- Can only archive `frozen` sessions (must freeze first).
- Can only activate `frozen` sessions (archived sessions cannot be reactivated).
- Attempting invalid transitions returns HTTP 400 with descriptive error.

### Validation Points
- Uniqueness of `session_id`.
- Clip count growth logged.
- Memory creation only if clip exists.
- Status transition validation (active → frozen → archived).

## Workflow 2: Memory Retrieval & Search
### Goal
Rapid reconstruction of prior reasoning tied to session artifacts.

### Steps
1. Query ranked search endpoint (`POST /api/memories/search { query, session_id? }`).
2. Service executes baseline term match (LIKE per term) with optional filters (category, importance, date range, tags, session scope).
3. Compute score = text_match_count + (1/(age_days+1)) + importance*0.5.
4. Return ordered results with score components (text, recency, importance) for experimentation.
5. Optional refinement: tags, date range, category, minimum importance, session scope.

### Future Enhancements
- Switchable search backend (FTS5 / vector embeddings) post Phase 8.
 - Semantic embedding similarity (vector store) combined with lexical score.
 - Tag indexing & JSON containment optimization (PostgreSQL).
 - Learning-to-rank incorporating user feedback signals.

## Workflow 3: Export / Import (Portability)
### Goal
Move or back up all entities with stable external references preserving relations.

### Steps
1. Trigger export (`POST /export`) with scope (all vs session).
2. System builds envelope (version + sessions/clips/memories + integrity manifest).
3. Write artifact to `backups/` with timestamp.
4. Import (`POST /import`) validates version, scans conflicts:
   - External `session_id` collision → strategy (skip, merge, rename).
5. Reconstruct internal PK mappings deterministically.

### Integrity Guarantees (Planned)
- Hash manifest over sorted entity arrays.
- Optionally sign with local key for tamper verification.

## Cross-Cutting Concerns
- Logging: Each step emits structured event with correlation IDs.
- Metrics: counters (`clips_created_total`, `memories_created_total`), timers (`search_latency_ms`).
- Error Handling: Standard error envelope (code, message, detail, correlation_id).

## Non-Goals in Current Workflows
- Real-time collaborative editing.
- Streaming incremental export (full snapshot only initially).

## Open Questions
- Session auto-create on first clip vs explicit session provisioning?
- Conflict resolution policy during import (rename vs merge metadata)?
- Tag indexing needs (B-tree vs array scan) at scale.

---
END WORKFLOWS DRAFT
