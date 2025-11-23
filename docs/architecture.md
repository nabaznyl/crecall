# Architecture

## System Overview

crecall is a FastAPI-based personal knowledge management system with async SQLAlchemy for data persistence.

```
┌─────────────────┐
│   REST API      │  FastAPI + Pydantic v2 validation
│   /api/v1/*     │
└────────┬────────┘
         │
┌────────▼────────┐
│  Service Layer  │  Business logic, HMAC integrity
│  (async)        │
└────────┬────────┘
         │
┌────────▼────────┐
│  Repository     │  SQLAlchemy async ORM
│  (async)        │
└────────┬────────┘
         │
┌────────▼────────┐
│   Database      │  SQLite (dev) / PostgreSQL (prod)
│                 │
└─────────────────┘
```

## Core Components

### API Layer (`app/api/`)
- **Routers**: Session, clip, memory, import/export endpoints
- **Dependencies**: Centralized DB session management
- **Validation**: Pydantic v2 schemas with strict type checking

### Service Layer (`app/services/`)
- **Business Logic**: Session lifecycle, clip enrichment, memory search
- **Integrity**: HMAC-based content verification
- **Async Operations**: All I/O operations are async

### Data Layer (`app/models/`)
- **ORM Models**: SQLAlchemy async declarative models
- **Repositories**: Query builders and CRUD operations
- **Migrations**: Alembic for schema evolution

### Configuration (`app/config.py`)
- **Centralized Settings**: Pydantic BaseSettings
- **Environment Variables**: `.env` support
- **Validation**: Type-safe configuration

## Data Flow

### Session Creation
```
POST /api/v1/sessions
  ↓
SessionService.create_session()
  ↓
SessionRepository.create()
  ↓
Database INSERT
  ↓
Response (external_id, internal_id)
```

### Clip with Integrity
```
POST /api/v1/clips
  ↓
ClipService.create_clip()
  ↓
IntegrityService.sign(content)
  ↓
ClipRepository.create(clip + signature)
  ↓
Database INSERT
  ↓
Response (clip + integrity_valid: true)
```

### Memory Search
```
GET /api/v1/memories/search?q=term
  ↓
MemoryService.search_memories()
  ↓
MemoryRepository.full_text_search()
  ↓
Database SELECT (FTS5 on SQLite)
  ↓
Response (ranked results)
```

## Design Principles

### External vs Internal IDs
- **External ID**: User-facing string identifier (portable across systems)
- **Internal ID**: Database UUID (optimized for relations)
- **Why**: Enables export/import without ID collision

### Async-First
- All database operations use `async`/`await`
- FastAPI async request handlers
- SQLAlchemy async session management

### Integrity by Design
- HMAC signatures on clip content
- Verification on retrieval
- Tamper detection in `integrity_status` field

### Lifecycle States
Sessions progress through defined states:
```
ACTIVE → PAUSED → ARCHIVED → PRUNED
```

### Crash Safety
- Deterministic startup sequence
- Background tasks gated until DB ready
- Graceful degradation on missing config

## Security Model

### Content Integrity
- HMAC-SHA256 signatures using `SIGNING_KEY`
- Stored alongside content in `signature` column
- Validated on read; status exposed in API

### Secrets Management
- `.env` for local development
- Environment variables in production
- Never commit secrets to version control

### Container Security
- Non-root user (UID 1000)
- Tini init process (PID 1 signal handling)
- Health checks for orchestration

## Performance Considerations

### Database
- Async connection pooling
- Indexed foreign keys
- Full-text search via FTS5 (SQLite) or tsvector (PostgreSQL)

### API
- Async endpoints reduce blocking I/O
- Pagination for large result sets
- Efficient query patterns in repositories

### Resource Constraints
- Target: <100ms restore for 1000-clip session
- Memory: <50MB baseline footprint
- Disk: FTS index overhead ~20% of content size

## Deployment Patterns

### Development
- SQLite database
- Hot reload (`--reload`)
- Local `.env` configuration

### Production
- PostgreSQL database
- Gunicorn + Uvicorn workers
- Environment variables
- Docker with health checks

### CI/CD
- GitHub Actions for quality, security, container scans
- Multi-Python matrix (3.11, 3.12, 3.13)
- Coverage enforcement (80% threshold)
- Release automation (SBOMs, wheel, sdist)

## Extension Points

### Custom Enrichment
Extend `ClipService` to add metadata during creation:
```python
async def enrich_clip(clip: Clip) -> Clip:
    # Add tags, extract entities, etc.
    return clip
```

### Search Plugins
Implement `SearchStrategy` interface for custom ranking:
```python
class SemanticSearch(SearchStrategy):
    async def search(self, query: str) -> List[Memory]:
        # Vector similarity, etc.
        pass
```

### Export Formats
Add new serialization formats in `ExportService`:
```python
async def export_markdown(session_id: str) -> str:
    # Custom markdown template
    pass
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| API | FastAPI 0.115+ |
| Validation | Pydantic v2 |
| ORM | SQLAlchemy 2.0 (async) |
| Database | SQLite (dev), PostgreSQL (prod) |
| Migration | Alembic |
| Testing | pytest + pytest-asyncio |
| Linting | Black, Ruff |
| Type Checking | mypy |
| Container | Docker + tini |
| CI/CD | GitHub Actions |

## References

- [Data Model](data_model.md) - Entity specifications
- [Workflows](workflows.md) - User journeys
- [Quality](quality.md) - Testing standards
- [Build Standards](BUILD_STANDARDS.md) - CI/CD pipeline
