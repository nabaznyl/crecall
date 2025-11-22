# Semantic Memory Search Plan

## Objective
Enable high-relevance retrieval across memories (and later clips) using hybrid search: keyword (trigram), metadata filters, and vector similarity.

## Components
1. Embeddings generation pipeline.
2. Vector storage (pgvector) or external (Qdrant / Weaviate) optional.
3. Hybrid ranking API endpoint.
4. Incremental backfill for existing memories.

## Embeddings
- Model: sentence-transformers `all-MiniLM-L6-v2` (384 dims) or larger (768 dims) if needed.
- Storage: `embedding vector(384)` column (pgvector) OR separate vector DB.
- Generation triggers:
  - On memory create.
  - Background task for missing embeddings.

## Index Strategy
- `pg_trgm` + GIN for `content` keyword/approximate match.
- `GIN(tags)` for tag filtering.
- `vector` index for embedding similarity: `CREATE INDEX ON memories USING ivfflat (embedding vector_cosine_ops) WITH (lists=100);`

## Query Flow
1. Accept query payload:
```json
{
  "q": "crash recovery refactor",
  "tags": ["bug"],
  "category": "development",
  "importance_gte": 1,
  "limit": 20
}
```
2. Compute embedding for `q`.
3. Vector similarity search top K (e.g., 100).
4. Keyword/trigram search for `q` -> union.
5. Filter by tags/category/importance.
6. Score fusion:
   - `score = w_vec * cosine + w_kw * keyword_rank + w_imp * (importance/5)`
7. Sort by `score DESC`.
8. Return structured hits with explanation fields.

## API Endpoint
`GET /api/memories/search` (simplified) or `POST /api/memories/search` for JSON body.
Response example:
```json
{
  "query": "crash recovery refactor",
  "results": [
    {
      "id": "...",
      "content": "Implemented crash recovery state persistence...",
      "tags": ["crash","state"],
      "importance": 2,
      "score": 0.89,
      "match": {
        "cosine": 0.92,
        "keyword": 0.65,
        "importance_bonus": 0.12
      }
    }
  ]
}
```

## Backfill Steps
1. Identify memories with `embedding IS NULL`.
2. Batch process (e.g., 500 per job) with rate limiting.
3. Track progress: `SELECT count(*) FROM memories WHERE embedding IS NULL;`.
4. Re-index after completion.

## Tooling
- Add embedding service module: `services/embeddings.py`.
- Caching: in-memory LRU for recent queries.
- Retry policy for transient network/model errors.

## Minimal Code Sketch
```python
# services/embeddings.py
from sentence_transformers import SentenceTransformer
_model = SentenceTransformer("all-MiniLM-L6-v2")

def embed(text: str) -> list[float]:
    return _model.encode([text])[0].tolist()
```

```python
# api/memories.py (pseudo)
@router.post('/search')
async def search_memories(payload: SearchPayload, db: Session):
    emb = embed(payload.q)
    results_vec = db.execute(vector_sql, {"emb": emb, "limit": payload.limit * 2}).fetchall()
    results_kw = db.execute(keyword_sql, {"q": f"%{payload.q}%", "limit": payload.limit * 2}).fetchall()
    # merge, score, filter, truncate
```

## Ranking Weights (Tunable)
- `w_vec = 0.6`
- `w_kw = 0.3`
- `w_imp = 0.1`

## Metrics / Validation
- Manual relevance judgment set.
- Precision@10, MRR for dev queries.
- Average embedding latency (<50ms per text locally).

## Future Enhancements
- Add semantic tag suggestions.
- Cross-memory clustering for topic summaries.
- Temporal decay weighting.

---
Focused, minimal footprint; extend gradually.
