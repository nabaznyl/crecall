# PostgreSQL Migration Plan (crecall)

## Goals
- Replace SQLite with PostgreSQL for concurrency, indexing, full-text + JSON querying.
- Preserve existing data (sessions, clips, memories) with minimal downtime.
- Enable future semantic search & analytics without schema churn.

## Target Schema (Initial)
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE,
  display_name TEXT,
  theme_preference TEXT CHECK (theme_preference IN ('dark','light') ) DEFAULT 'dark',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  started_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  status TEXT CHECK (status IN ('active','paused','ended')) NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE clips (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  label TEXT,
  importance SMALLINT DEFAULT 0 CHECK (importance BETWEEN 0 AND 5),
  git_branch TEXT,
  git_commit TEXT,
  data JSONB NOT NULL, -- compressed/minified snapshot
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE memories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  content TEXT NOT NULL,
  category TEXT,
  importance SMALLINT DEFAULT 0 CHECK (importance BETWEEN 0 AND 5),
  tags TEXT[] DEFAULT '{}',
  embedding vector(768), -- future (pgvector)
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ON sessions (status);
CREATE INDEX ON clips (session_id, created_at DESC);
CREATE INDEX ON memories USING GIN (tags);
CREATE INDEX memories_content_trgm ON memories USING GIN (content gin_trgm_ops);
```

## Migration Steps
1. Add PostgreSQL service (Docker or managed).
2. Install extensions: `CREATE EXTENSION IF NOT EXISTS pg_trgm;` and later `pgvector`.
3. Build SQLAlchemy models mirroring above in `backend/app/db/models.py`.
4. Add Alembic migration: `alembic revision --autogenerate -m "init pg schema"`.
5. Write import script:
   - Parse existing SQLite / file-based logs.
   - Map log entries to sessions, then create synthetic clips if needed.
   - Insert memories with tags; embeddings null initially.
6. Dry run import on staging DB; verify counts and random spot-check.
7. Point app config to PostgreSQL via env var `DATABASE_URL=postgresql+psycopg://...`.
8. Run read-only dual writes (optional safety window): write to both SQLite & PostgreSQL for one day.
9. Decommission SQLite (remove dual write code, archive file).

## Downtime Strategy
- Use dual-write and switched read mode to minimize downtime.
- Provide maintenance flag: if mismatch counts occur, fall back to stale read (SQLite) until resolved.

## Rollback Plan
- Keep last successful import dump (`pg_dump -Fc`).
- If critical failure, switch DB URL back to SQLite and re-run import after fixes.

## Future Extensions
- Add `memory_links` table for graph relations.
- Partition big tables (e.g., clips) by month if growth large.
- Add materialized view for memory search ranking.

## Validation Checklist
- [ ] Row counts match source
- [ ] Spot-check time ordering
- [ ] Tags preserved
- [ ] Importance preserved
- [ ] No orphan session references
- [ ] FTS working: `SELECT * FROM memories WHERE content ILIKE '%crash%'`
- [ ] Trigram search: `SELECT * FROM memories WHERE content % 'restor'`

## Minimal Config Additions
Add to `.env`:
```
DATABASE_URL=postgresql+psycopg://crecall:password@localhost:5432/crecall
```

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Inconsistent imports | Wrap import in transaction batches |
| Missing tags formatting | Normalize to lowercase trimmed strings |
| Slow bulk insert | Use SQLAlchemy bulk operations / COPY |
| FTS mismatch | Validate with sample queries |
| Embedding dimension drift | Centralize embedding config constant |

---
Concise plan; implement incrementally to avoid churn.
