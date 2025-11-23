# REST API Reference

Base URL: `http://localhost:8000/api/v1`

Interactive API documentation available at `/docs` (Swagger UI) and `/redoc` (ReDoc).

---

## Sessions

### Create Session

```http
POST /api/v1/sessions
Content-Type: application/json

{
  "external_id": "work-session-20251122",
  "description": "Optional session description"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "external_id": "work-session-20251122",
  "description": "Optional session description",
  "state": "ACTIVE",
  "created_at": "2025-11-22T10:30:00Z",
  "updated_at": "2025-11-22T10:30:00Z"
}
```

### Get Session

```http
GET /api/v1/sessions/{session_id}
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "external_id": "work-session-20251122",
  "state": "ACTIVE",
  "created_at": "2025-11-22T10:30:00Z",
  "updated_at": "2025-11-22T10:30:00Z",
  "clips": []
}
```

### List Sessions

```http
GET /api/v1/sessions?state=ACTIVE&limit=20&offset=0
```

**Query Parameters**:
- `state` (optional): Filter by session state (ACTIVE, PAUSED, ARCHIVED, PRUNED)
- `limit` (optional): Max results (default: 20)
- `offset` (optional): Pagination offset (default: 0)

**Response** (200 OK):
```json
{
  "sessions": [...],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

### Update Session State

```http
PATCH /api/v1/sessions/{session_id}
Content-Type: application/json

{
  "state": "PAUSED"
}
```

**Response** (200 OK): Updated session object

### Delete Session

```http
DELETE /api/v1/sessions/{session_id}
```

**Response** (204 No Content)

---

## Clips

### Create Clip

```http
POST /api/v1/clips
Content-Type: application/json

{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "external_id": "clip-terminal-output-001",
  "content": "$ git status\nOn branch main...",
  "metadata": {
    "source": "terminal",
    "timestamp": "2025-11-22T10:35:00Z"
  }
}
```

**Response** (201 Created):
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "external_id": "clip-terminal-output-001",
  "content": "$ git status\nOn branch main...",
  "metadata": {...},
  "signature": "HMAC-SHA256-signature-here",
  "integrity_status": "valid",
  "created_at": "2025-11-22T10:35:00Z"
}
```

### Get Clip

```http
GET /api/v1/clips/{clip_id}
```

**Response** (200 OK): Clip object with integrity verification

### List Clips by Session

```http
GET /api/v1/sessions/{session_id}/clips
```

**Response** (200 OK):
```json
{
  "clips": [...],
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Update Clip

```http
PATCH /api/v1/clips/{clip_id}
Content-Type: application/json

{
  "metadata": {
    "tags": ["important", "debug"]
  }
}
```

**Response** (200 OK): Updated clip (new signature generated)

### Delete Clip

```http
DELETE /api/v1/clips/{clip_id}
```

**Response** (204 No Content)

---

## Memories

### Create Memory

```http
POST /api/v1/memories
Content-Type: application/json

{
  "clip_id": "660e8400-e29b-41d4-a716-446655440001",
  "external_id": "memory-git-status-analysis",
  "title": "Git Status Output",
  "content": "Project state shows uncommitted changes in backend/",
  "tags": ["git", "status"]
}
```

**Response** (201 Created):
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "clip_id": "660e8400-e29b-41d4-a716-446655440001",
  "external_id": "memory-git-status-analysis",
  "title": "Git Status Output",
  "content": "Project state shows uncommitted changes in backend/",
  "tags": ["git", "status"],
  "created_at": "2025-11-22T10:40:00Z"
}
```

### Search Memories

```http
GET /api/v1/memories/search?q=git+status&limit=10
```

**Query Parameters**:
- `q` (required): Search query (full-text)
- `limit` (optional): Max results (default: 10)
- `tags` (optional): Filter by tags (comma-separated)

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "title": "Git Status Output",
      "content": "Project state shows uncommitted changes...",
      "tags": ["git", "status"],
      "rank": 0.95,
      "created_at": "2025-11-22T10:40:00Z"
    }
  ],
  "query": "git status",
  "total": 1
}
```

### Get Memory

```http
GET /api/v1/memories/{memory_id}
```

**Response** (200 OK): Memory object

### Update Memory

```http
PATCH /api/v1/memories/{memory_id}
Content-Type: application/json

{
  "tags": ["git", "status", "important"]
}
```

**Response** (200 OK): Updated memory

### Delete Memory

```http
DELETE /api/v1/memories/{memory_id}
```

**Response** (204 No Content)

---

## Import/Export

### Export Session

```http
GET /api/v1/export/sessions/{session_id}
Accept: application/json
```

**Response** (200 OK):
```json
{
  "version": "1.0",
  "exported_at": "2025-11-22T11:00:00Z",
  "session": {...},
  "clips": [...],
  "memories": [...]
}
```

### Import Session

```http
POST /api/v1/import/sessions
Content-Type: application/json

{
  "version": "1.0",
  "session": {...},
  "clips": [...],
  "memories": [...]
}
```

**Response** (201 Created):
```json
{
  "imported_session_id": "550e8400-e29b-41d4-a716-446655440000",
  "clips_imported": 5,
  "memories_imported": 3
}
```

---

## Health & Status

### Health Check

```http
GET /health
```

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2025-11-22T11:05:00Z"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Validation error: external_id is required"
}
```

### 404 Not Found
```json
{
  "detail": "Session not found"
}
```

### 409 Conflict
```json
{
  "detail": "Session with external_id 'work-session-20251122' already exists"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

**Current**: No rate limiting enforced  
**Planned**: 100 requests/minute per IP (v0.2.x)

## Authentication

**Current**: No authentication required  
**Planned**: API key authentication (v0.2.x)

For data model details, see [Data Models](models.md).
