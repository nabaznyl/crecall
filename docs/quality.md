# Quality Standards

**Phase 3 Specification**  
**Status:** Draft  
**Version:** 0.1

---

## Test Suite Tiers

### Unit Tests
**Scope**: Individual functions, service methods, schema validation  
**Isolation**: Mocked dependencies  
**Markers**: `@pytest.mark.unit`

**Targets**:
- Service layer logic (ID resolution, invariant checks)
- Schema validation (Pydantic models)
- Utility functions (config, logging, helpers)

**Coverage Goal**: >90% for service & util modules

**Naming Convention**: `test_<module>_<function>_<scenario>.py`

**Example**:
```python
@pytest.mark.unit
def test_clip_service_resolve_session_id_creates_missing():
    # Test session auto-create logic
```

---

### Integration Tests
**Scope**: Multi-component interactions (API + service + DB)  
**Isolation**: In-memory DB, no external services  
**Markers**: `@pytest.mark.integration`

**Targets**:
- API endpoint workflows (create session → add clip → retrieve)
- Service-layer coordination
- Database transaction integrity

**Coverage Goal**: >80% for core workflows

**Naming Convention**: `test_integration_<workflow>.py`

**Example**:
```python
@pytest.mark.integration
def test_session_lifecycle_create_enrich_archive():
    # End-to-end session workflow
```

---

### Portability Tests
**Scope**: Export/import, cross-environment data integrity  
**Isolation**: Temporary directories, clean state  
**Markers**: `@pytest.mark.portability`

**Targets**:
- Export envelope generation
- Import conflict resolution
- Roundtrip fidelity (hash verification)

**Coverage Goal**: 100% for export/import paths

**Naming Convention**: `test_portable_<operation>.py`

**Example**:
```python
@pytest.mark.portability
def test_export_import_roundtrip_preserves_relations():
    # Full export/import cycle
```

---

### Behavior Tests (Future)
**Scope**: User-facing scenarios, acceptance criteria  
**Isolation**: Full stack (API + DB + mocked external services)  
**Markers**: `@pytest.mark.behavior`

**Targets**:
- Search workflows (query → rank → return)
- Crash recovery (detect → prompt → restore)
- Retention policies (prune → verify)

---

## Test Execution

### Run All Tests
```bash
CRECALL_TEST_MODE=1 pytest tests/ -v
```

### Run by Tier
```bash
# Unit only
pytest -m unit

# Integration only
pytest -m integration

# Portability only
pytest -m portability
```

### Run Subset
```bash
# Clips module
pytest tests/test_clips.py tests/test_api_clips_async.py

# Sessions
pytest -k session
```

---

## Coverage Thresholds

| Tier | Minimum | Target |
|------|---------|--------|
| Unit | 85% | 90% |
| Integration | 75% | 80% |
| Portability | 95% | 100% |
| Overall | 80% | 85% |

### Generate Coverage Report
```bash
pytest --cov=app --cov-report=html --cov-report=term
open htmlcov/index.html
```

---

## Continuous Integration

### Pre-Commit Checks (Phase 6)
- Lint (Black, Pylint)
- Type check (Mypy)
- Unit tests (<5s runtime target)

### PR Validation
- Full test suite (all tiers)
- Coverage threshold enforcement
- No new warnings

### Nightly Builds
- Extended integration tests
- Performance regression checks
- Security scans

---

## Test Conventions

### Fixtures
- `conftest.py`: Shared fixtures (DB session, test client)
- Scope: `function` (default), `module`, `session`

### Assertions
- Prefer specific assertions (`assert response.status_code == 201`) over generic `assert response.ok`
- Include failure messages: `assert len(items) == 2, f"Expected 2 items, got {len(items)}"`

### Data Factories (Future)
```python
# Factory for test data generation
def create_session(session_id="test-session", status="active"):
    return SessionCreate(session_id=session_id, status=status)
```

---

## Performance Benchmarks (Phase 5)

### Baseline Targets
- Clip creation: <75ms
- Memory search (10k clips): <150ms p50
- Session summary: <50ms
- Startup (cold): <3s

### Regression Detection
Run benchmarks before/after changes:
```bash
python scripts/benchmark.py --baseline baseline.json
# Compare results; fail if >10% regression
```

---

## Current Status

**Implemented**:
- 49 passing tests (async + legacy)
- In-memory DB isolation
- Async & sync test fixtures

**Pending**:
- Test tier markers assignment
- Coverage threshold enforcement
- Behavior test suite scaffolding
- Performance baseline recording

---

## Next Actions (Phase 3)

1. Add pytest markers to existing tests
2. Measure current coverage baseline
3. Identify gaps (service methods without tests)
4. Add integration tests for new workflows
5. Set up coverage reporting in CI

---

See [../TEST_RESULTS.md](../TEST_RESULTS.md) for historical test runs.
