# Data Models

API request/response schemas using Pydantic v2 validation.

---

## Session

### SessionCreate (Request)

```python
{
  "external_id": str,          # Required, unique user-facing identifier
  "description": str | None    # Optional session description
}
```

**Validation**:
- `external_id`: 1-255 chars, alphanumeric + hyphens/underscores
- `description`: Max 1000 chars

### SessionResponse

```python
{
  "id": UUID,                  # Internal database ID
  "external_id": str,          # User-facing identifier
  "description": str | None,
  "state": SessionState,       # ACTIVE | PAUSED | ARCHIVED | PRUNED
  "created_at": datetime,
  "updated_at": datetime
}
```

### SessionState Enum

```python
class SessionState(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ARCHIVED = "ARCHIVED"
    PRUNED = "PRUNED"
```

**State Transitions**:
```
ACTIVE → PAUSED → ARCHIVED → PRUNED
  ↓         ↓
  └─────────┘ (can return to ACTIVE)
```

---

## Clip

### ClipCreate (Request)

```python
{
  "session_id": UUID,          # Required, parent session
  "external_id": str,          # Required, unique within session
  "content": str,              # Required, clip content
  "metadata": dict | None      # Optional JSON metadata
}
```

**Validation**:
- `content`: Max 100,000 chars
- `metadata`: Valid JSON object, max 10KB serialized

### ClipResponse

```python
{
  "id": UUID,
  "session_id": UUID,
  "external_id": str,
  "content": str,
  "metadata": dict | None,
  "signature": str,            # HMAC-SHA256 signature
  "integrity_status": str,     # "valid" | "invalid" | "missing"
  "created_at": datetime,
  "updated_at": datetime
}
```

**Integrity Status**:
- `valid`: Content matches signature
- `invalid`: Content tampered (signature mismatch)
- `missing`: No signature (legacy data)

---

## Memory

### MemoryCreate (Request)

```python
{
  "clip_id": UUID,             # Required, source clip
  "external_id": str,          # Required, unique identifier
  "title": str,                # Required, memory title
  "content": str,              # Required, enriched content
  "tags": list[str] | None     # Optional tags for categorization
}
```

**Validation**:
- `title`: 1-500 chars
- `content`: Max 50,000 chars
- `tags`: Max 20 tags, each 1-50 chars

### MemoryResponse

```python
{
  "id": UUID,
  "clip_id": UUID,
  "external_id": str,
  "title": str,
  "content": str,
  "tags": list[str],
  "created_at": datetime,
  "updated_at": datetime
}
```

### MemorySearchResult

```python
{
  "id": UUID,
  "title": str,
  "content": str,              # May be truncated for preview
  "tags": list[str],
  "rank": float,               # Search relevance score (0.0-1.0)
  "created_at": datetime,
  "highlight": str | None      # Search term context (optional)
}
```

---

## Import/Export

### ExportFormat

```python
{
  "version": str,              # Format version (e.g., "1.0")
  "exported_at": datetime,
  "session": SessionResponse,
  "clips": list[ClipResponse],
  "memories": list[MemoryResponse]
}
```

**Notes**:
- Uses `external_id` for all references (portable)
- `signature` fields preserved for integrity verification
- Metadata serialized as JSON

### ImportResult

```python
{
  "imported_session_id": UUID,
  "clips_imported": int,
  "memories_imported": int,
  "warnings": list[str] | None  # Optional import warnings
}
```

**Import Behavior**:
- Creates new internal IDs
- Preserves external IDs (fails on conflict)
- Recalculates signatures with current signing key

---

## Pagination

### PaginatedResponse (Generic)

```python
{
  "items": list[T],            # Generic item list
  "total": int,                # Total matching items
  "limit": int,                # Items per page
  "offset": int                # Current offset
}
```

**Query Parameters**:
- `limit`: 1-100 (default: 20)
- `offset`: 0+ (default: 0)

---

## Error Models

### ValidationError

```python
{
  "detail": [
    {
      "loc": ["body", "external_id"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### HTTPException

```python
{
  "detail": str                # Human-readable error message
}
```

---

## Field Constraints Summary

| Field | Min | Max | Pattern |
|-------|-----|-----|---------|
| `external_id` | 1 | 255 | `^[a-zA-Z0-9_-]+$` |
| `description` | 0 | 1000 | Any |
| `clip.content` | 1 | 100,000 | Any |
| `memory.title` | 1 | 500 | Any |
| `memory.content` | 1 | 50,000 | Any |
| `tags` (each) | 1 | 50 | `^[a-zA-Z0-9_-]+$` |
| `metadata` (serialized) | 0 | 10,240 bytes | Valid JSON |

---

## Type Definitions

### UUID Format
```
550e8400-e29b-41d4-a716-446655440000
```
Standard UUID4 (RFC 4122)

### Datetime Format
```
2025-11-22T10:30:00Z
```
ISO 8601 with UTC timezone

### HMAC Signature Format
```
base64-encoded-SHA256-signature
```
HMAC-SHA256, base64-encoded output

---

For API endpoint details, see [REST API Reference](rest.md).  
For entity relationships, see [Data Model](../data_model.md).
