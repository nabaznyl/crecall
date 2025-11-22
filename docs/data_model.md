# Data Model Specification (Draft v0.1)
Date: 2025-11-21

## Overview
Structured entities with clear external (portable) vs internal (storage) identifiers. External IDs are stable across export/import; internal IDs optimize local relational integrity.

## Entity: Session
| Field | Type | External? | Required | Notes |
|-------|------|-----------|----------|-------|
| id | int | No | Yes | Internal PK |
| session_id | str | Yes | Yes | Human-readable / generated stable identifier |
| created_at | datetime | - | Yes | UTC timestamp |
| updated_at | datetime | - | Yes | Updated on mutation |
| status | enum(active, frozen, archived) | - | Yes | Lifecycle phase |

### Invariants
- `session_id` unique among active + archived sessions.
- `status` transitions: active → frozen → archived (prune only from archived).

### Lifecycle Events
- Create: allocate session_id.
- Freeze: disallow new clips (except recovery). 
- Archive: eligible for retention pruning.

## Entity: Clip
| Field | Type | External? | Required | Notes |
|-------|------|-----------|----------|-------|
| id | int | No | Yes | Internal PK |
| clip_id | str | Yes | Planned | Stable externally portable identifier |
| session_id (ext) | str | Yes | Yes | Resolved to internal session PK |
| session_fk | int | No | Yes | Internal FK after resolution |
| content | text | - | Yes | Raw captured data (code, note, snippet) |
| metadata | json | - | Optional | Arbitrary metadata (source, tags) |
| created_at | datetime | - | Yes | Capture time |

### Invariants
- Belongs to exactly one session.
- `clip_id` unique globally (post-introduction).

### Lifecycle
- Capture → (optional) enrich metadata → (optional) promote to memory.

## Entity: Memory
| Field | Type | External? | Required | Notes |
|-------|------|-----------|----------|-------|
| id | int | No | Yes | Internal PK |
| linked_clip_id (ext) | str | Yes | Yes | Resolves to internal clip PK |
| clip_fk | int | No | Yes | Internal resolved FK |
| annotations | text/json | - | Optional | User-curated insight or rationale |
| tags | array[str] | - | Optional | Categorization |
| created_at | datetime | - | Yes | Creation time |
| updated_at | datetime | - | Yes | Enrichment time |

### Lifecycle
- Create (link clip) → enrich (annotations/tags) → searchable → archival.

## Relationships
- Session 1 — N Clips
- Clip 1 — 0..1 Memory (one memory per clip baseline; extensibility open)

## External vs Internal Mapping Flow
1. API receives `session_id` / `linked_clip_id` (string).
2. Service layer resolves to internal PK; creates parent if allowed (session auto-create policy currently enabled for clips, review later).
3. Persistence uses integer FK for relational joins.

## Archival & Retention (Future Phase 4)
Policy dimensions:
- Age threshold (e.g., archive sessions >30d inactive).
- Activity sparsity (few clips + age → archive earlier).
- Size-based pruning (target DB size; oldest archived pruned first after export verification).

## Export/Import Envelope (Planned)
```json
{
  "version": "1.0",
  "exported_at": "<UTC ISO>",
  "sessions": [ ... ],
  "clips": [ ... ],
  "memories": [ ... ],
  "integrity": {
    "hash_algo": "sha256",
    "manifest_hash": "..."
  }
}
```
Roundtrip integrity requires stable external IDs + deterministic ordering.

## Open Design Questions
- Introduce `clip_id` generation now (UUID vs slug vs hash of content)?
- Memory multi-link (support linking multiple clips?) vs keep single for simplicity.
- Tag ontology (free-form vs controlled vocabulary)?

## Deferred Simplifications
Expose numeric IDs directly if external portability becomes non-essential. Status: deferred.

---
END DATA MODEL SPEC
