# AI Context Injection Integration Plan

## Objective
Provide high-quality, structured development context (clips + memories + session metadata) to AI assistants (code generation, reasoning, summarization) while enforcing privacy and minimizing prompt token bloat.

## Core Sources
1. Recent Clips (chronological restore points)
2. High-importance Memories (importance >= 2)
3. Active Session Metadata (status, working dir, git branch/commit)
4. Relevant Historical Memories (semantic similarity to user query)
5. Optional: Last N terminal commands (filtered for secrets)

## Pipeline Overview
```
User Query -> Intent Analyzer -> Context Selector -> Sanitizer -> Prompt Assembler -> Model
```

## Steps
1. Intent Analyzer:
   - Classify query category (debug, design, refactor, recall, docs).
   - Adjust context weighting (e.g. refactor -> more code-related clips; debug -> recent error memories).
2. Context Selector:
   - Start with latest clip + previous clip diff.
   - Add top-K semantic memory matches (K=5) via embedding similarity.
   - Add high-importance memories (last 10 with importance >=2).
3. Sanitizer:
   - Strip secrets (keys, tokens) via regex + entropy heuristics.
   - Remove excessively long command outputs (>2KB).
4. Prompt Assembler:
   - Structured sections: SYSTEM + CONTEXT + QUERY.
   - Token budget manager: truncate low-priority memories if > limit.
5. Model Interface:
   - Provide pluggable backends (OpenAI, local, Azure).

## Data Structures
```json
{
  "clip": {
    "id": "clip-20251121-142330",
    "created_at": "2025-11-21T14:23:30Z",
    "git": {"branch": "feature/refactor", "commit": "abc123"},
    "paths": ["src/components/App.tsx", "backend/app/api/memories.py"],
    "todo_state": ["Implement semantic search"],
    "env_context": {"python": "3.11"}
  },
  "previous_clip_diff": {
    "changed_files": ["frontend/src/App.tsx"],
    "added_memories": 2
  },
  "memories": [
    {"id": "m1", "content": "Refactor plan: split search into vector + keyword.", "importance": 2},
    {"id": "m2", "content": "Crash recovery implemented with state.json persistence.", "importance": 2}
  ]
}
```

## Sanitization Patterns
- API keys: `[A-Za-z0-9_\-]{32,}`
- AWS style: `AKIA[0-9A-Z]{16}`
- Generic secret markers: `(?i)(token|secret|key|passwd|password)`
- High entropy substrings: Shannon entropy > 4.0 across sliding window -> mask

## Prompt Template (Skeleton)
```
SYSTEM: You are assisting with development context reasoning.
CONTEXT:
Current Clip:
- ID: {clip.id}
- Time: {clip.created_at}
- Git: {clip.git.branch}@{clip.git.commit}
Paths in Focus:
{clip.paths}
High-Importance Memories:
{memories}
Recent Changes:
{previous_clip_diff.changed_files}
User Query:
{query}
TASK: Provide targeted assistance using ONLY provided context.
```

## API Endpoint
`POST /api/context/assemble`
Request:
```json
{"query": "How do I implement semantic search ranking?", "max_tokens": 2000}
```
Response:
```json
{"prompt": "SYSTEM: ...", "sections": {"clip": {...}, "memories": [...]}}
```

## Implementation Outline
- `services/context_builder.py`: orchestrates pipeline.
- `services/sanitizer.py`: regex + entropy scanning.
- `services/intent.py`: simple keyword classifier (later ML model).
- `api/context.py`: endpoint.

## Minimal Class Sketch
```python
class ContextBuilder:
    def __init__(self, db):
        self.db = db
    def assemble(self, query: str, limit: int = 5):
        intent = classify_intent(query)
        clip = get_latest_clip(self.db)
        prev_clip = get_previous_clip(self.db)
        memories = select_memories(self.db, query, intent, limit)
        sanitized = sanitize([clip, prev_clip, *memories])
        return build_prompt(clip, prev_clip, memories, query)
```

## Metrics
- Average prompt assembly latency.
- Token count distribution.
- Secret leakage incidents (should be zero).
- Relevance feedback (thumbs up/down stored per response).

## Future Enhancements
- Dynamic weighting (reinforcement from user approvals).
- Memory summarization layers (hierarchical context compression).
- Multi-user separation (namespace isolation).
- Streaming retrieval for large context sets.

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Prompt overflow | Token budget manager w/ priority tiers |
| Secret leakage | Multi-pass sanitization + denylist testing |
| Low relevance | Intent model iteration + feedback loop |
| Performance lag | Async batch embedding + caching |

---
Lean, extensible path to AI-aware context injection.
