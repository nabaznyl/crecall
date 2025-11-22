# Phase 2 Development Plan: Instant Restore Engine

## Overview

**Start Date**: November 21, 2025  
**Duration**: 4 weeks (target)  
**Target Coverage**: 65-70% (from current 59.20%)  
**Branch**: `feature/phase-2-instant-restore`

---

## Pre-Development Status

### Completed Milestones
- ✅ Phase 1 v0.1.0d-7 Release (85/85 tests passing)
- ✅ GitHub repository created and configured
- ✅ CI/CD workflows deployed (3 automated pipelines)
- ✅ Branch protection rules configured
- ✅ Security vulnerabilities fixed (Bandit issues resolved)
- ✅ Dependencies updated (Starlette 0.50.0, python-jose 3.5.0)
- ✅ Code formatting & import sorting standardized
- ✅ Dependency vulnerabilities reduced (6 → 3 remaining)

### Remaining Vulnerabilities
- ⚠️ ecdsa 0.19.1: Side-channel attacks (not immediate threat)
- ⚠️ pip 25.1.1: Symlink attack (dev-only, not runtime)
- ℹ️ All other vulnerabilities resolved

---

## Phase 2 Scope

### Feature 1: Instant Restore Engine (Priority 1)

#### Objective
Enable users to restore a session to any previous point in time by restoring individual clips, with automatic context assembly.

#### Endpoints
```
POST /sessions/{session_id}/restore
  - Query: clip_id (optional, default: latest)
  - Query: timestamp (optional, restore at point-in-time)
  - Returns: restored session state + context

GET /sessions/{session_id}/restore-options
  - Returns: available restore points (clips with timestamps)
  - Filters: date range, tags, importance

POST /sessions/{session_id}/restore-preview
  - Preview restore operation without committing
  - Returns: what would be restored
```

#### Implementation Tasks
1. **Restore Controller** (4 hours)
   - `POST /sessions/{id}/restore` endpoint
   - `GET /sessions/{id}/restore-options` endpoint
   - `POST /sessions/{id}/restore-preview` endpoint
   - Input validation & error handling

2. **Restore Service Layer** (6 hours)
   - `RestoreService` class with state machine
   - Clip retrieval & ordering
   - Context assembly algorithm
   - Conflict resolution (duplicate IDs)

3. **Database Queries** (2 hours)
   - Query clips by session + timestamp range
   - Retrieve associated memories for context
   - Pagination for large result sets

4. **Testing** (6 hours)
   - Unit tests: restore logic (8 tests)
   - Integration tests: state transitions (4 tests)
   - Error cases: missing clips, conflicts (4 tests)
   - Performance: restore speed benchmarks (2 tests)

5. **Documentation** (2 hours)
   - API documentation
   - Usage examples
   - Architecture diagrams

**Total Effort**: ~20 hours  
**Expected Tests**: +18 tests (85 → 103)  
**Expected Coverage**: 61-62% (from 59.20%)

---

### Feature 2: Memory Browser UI (Priority 2)

#### Objective
Build an interactive web interface for searching and visualizing memories with ranking visualization.

#### Components
```
Frontend (React/Vue):
- MemorySearch component: text input + filters
- RankingVisualization: score breakdown (text + recency + importance)
- ResultsList: paginated memory grid
- FilterPanel: date, tags, importance sliders
- ContextPanel: selected memory + associated clips

Backend (API):
- GET /memories/search (existing, enhanced)
- New response format: includes ranking breakdown
- Cache layer for performance
```

#### Implementation Tasks
1. **Frontend Setup** (4 hours)
   - Choose framework (React preferred)
   - Set up Vite/Webpack build
   - Create component structure
   - API client integration

2. **Search Component** (6 hours)
   - Text input with debouncing
   - Real-time search results
   - Filter UI (date range, tags)
   - Importance slider

3. **Ranking Visualization** (6 hours)
   - Display ranking scores
   - Visual breakdown (text vs recency vs importance)
   - Color coding by score contribution
   - Tooltips & explanations

4. **Results Display** (4 hours)
   - Memory card grid layout
   - Context panel with clip associations
   - Pagination controls
   - Loading states

5. **Performance Optimization** (4 hours)
   - Client-side caching
   - Lazy loading for large sets
   - Debouncing search queries
   - Virtualization for large lists

6. **Testing** (4 hours)
   - Unit tests: component logic (6 tests)
   - Integration tests: API interaction (4 tests)
   - E2E tests: user workflows (3 tests)

**Total Effort**: ~28 hours  
**Expected Tests**: +13 tests (103 → 116)  
**Expected Coverage**: 62-63% (from 61-62%)

---

### Feature 3: Prometheus Observability (Priority 3)

#### Objective
Expose metrics for monitoring performance, latency, and system health.

#### Metrics
```
Performance:
- HTTP request latency (p50, p95, p99)
- Database query latency
- Cache hit/miss ratio
- Memory usage

Business:
- Sessions active/archived
- Memories stored/pruned
- Clips created/restored
- Searches performed

Errors:
- 4xx/5xx error rates
- Crash detector triggers
- Retention scheduler runs
```

#### Implementation Tasks
1. **Metrics Setup** (3 hours)
   - Prometheus client integration
   - Meter/counter/histogram definitions
   - Endpoint: `GET /metrics`

2. **Instrumentation** (8 hours)
   - API middleware for request latency
   - Database query instrumentation
   - Cache layer metrics
   - Service method decorators

3. **Dashboards** (4 hours)
   - Grafana dashboard template
   - Key metrics visualization
   - Alert rules (latency, errors)

4. **Testing** (2 hours)
   - Verify metrics collection (3 tests)
   - Load test metric accuracy (2 tests)

**Total Effort**: ~17 hours  
**Expected Tests**: +5 tests (116 → 121)  
**Expected Coverage**: 63-64% (from 62-63%)

---

### Feature 4: Performance Tuning (Priority 4)

#### Objective
Optimize latency to <100ms p95 for key operations.

#### Target Operations
- `GET /memories/search`: <50ms p95
- `POST /sessions/{id}/restore`: <100ms p95
- `GET /sessions/{id}/clips`: <30ms p95

#### Optimization Tasks
1. **Query Optimization** (6 hours)
   - Index analysis & creation
   - Query plan optimization
   - N+1 query elimination
   - Batch operations where possible

2. **Caching Strategy** (6 hours)
   - Redis integration for session cache
   - Query result caching
   - Cache invalidation patterns
   - TTL tuning

3. **Database Indexing** (4 hours)
   - Create indexes on hot queries
   - Analyze table statistics
   - Partition large tables if needed

4. **Load Testing** (4 hours)
   - Create load test scenarios
   - Measure baseline latency
   - Identify bottlenecks
   - Verify improvements

5. **Benchmarking** (2 hours)
   - Document before/after metrics
   - Create performance baseline
   - Continuous monitoring setup

**Total Effort**: ~22 hours  
**Expected Tests**: +4 tests (121 → 125)  
**Expected Coverage**: 64-65% (from 63-64%)

---

## Development Schedule

### Week 1: Instant Restore Engine
| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | Restore controller & basic endpoints | 4 | ⏳ |
| Tue | Restore service layer & logic | 6 | ⏳ |
| Wed | Database queries & testing | 4 | ⏳ |
| Thu | Unit & integration tests | 4 | ⏳ |
| Fri | Documentation & PR review | 2 | ⏳ |

**Sprint 1 Total**: 20 hours | **Tests**: +18 | **Coverage**: 59% → 62%

### Week 2: Memory Browser UI
| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | Frontend setup & component structure | 4 | ⏳ |
| Tue | Search component & filtering | 6 | ⏳ |
| Wed | Ranking visualization | 6 | ⏳ |
| Thu | Results display & pagination | 4 | ⏳ |
| Fri | Testing & PR review | 4 | ⏳ |

**Sprint 2 Total**: 24 hours | **Tests**: +13 | **Coverage**: 62% → 63%

### Week 3: Observability & Performance
| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | Prometheus setup & instrumentation | 6 | ⏳ |
| Tue | Cache optimization & tuning | 6 | ⏳ |
| Wed | Query optimization & indexing | 6 | ⏳ |
| Thu | Load testing & benchmarking | 4 | ⏳ |
| Fri | Documentation & PR review | 2 | ⏳ |

**Sprint 3 Total**: 24 hours | **Tests**: +9 | **Coverage**: 63% → 65%

### Week 4: Integration & Polish
| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Mon | Cross-feature testing | 4 | ⏳ |
| Tue | Performance validation | 4 | ⏳ |
| Wed | Bug fixes & refinements | 4 | ⏳ |
| Thu | Security review | 2 | ⏳ |
| Fri | Release preparation | 2 | ⏳ |

**Sprint 4 Total**: 16 hours | **Buffer for issues**

---

## Success Criteria

### Functional Requirements
- [ ] Restore endpoint returns correct session state
- [ ] Context assembly includes all related memories/clips
- [ ] Conflict resolution handles duplicate IDs
- [ ] UI search returns ranked results in <100ms
- [ ] Ranking visualization shows accurate score breakdown
- [ ] Metrics exposed on `/metrics` endpoint

### Performance Requirements
- [ ] Restore operation: <100ms p95
- [ ] Memory search: <50ms p95
- [ ] Clip retrieval: <30ms p95
- [ ] UI response time: <200ms

### Quality Requirements
- [ ] Total tests: ≥120 (from 85)
- [ ] Coverage: ≥65% (from 59.20%)
- [ ] No new security vulnerabilities
- [ ] All linting checks pass
- [ ] Code review approval required

### Deployment Requirements
- [ ] PR created and merged to main
- [ ] All CI/CD checks pass
- [ ] Branch protection requirements met
- [ ] Documentation updated
- [ ] Release notes prepared

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Restore logic complexity | Medium | High | Start with simple restore, iterate |
| UI performance on large sets | Medium | Medium | Virtualization + caching |
| Database query performance | Low | High | Pre-optimize with indexes |
| Scope creep | High | Medium | Strict feature list, defer nice-to-haves |
| Resource constraints | Low | High | Well-defined sprints with buffers |

---

## Branch & PR Strategy

### Branch
- **Name**: `feature/phase-2-instant-restore`
- **Base**: `main`
- **Created**: November 21, 2025

### Commits
- One commit per feature (logical grouping)
- Commit message format: `feat: <description>`
- Include test additions in same commit

### Pull Request
- Title: `feat: Phase 2 - Instant Restore Engine & UI`
- Description: Link to this plan
- Reviewers: TBD
- Required checks:
  - ✅ All tests pass (120+ tests)
  - ✅ Coverage ≥65%
  - ✅ Code quality (formatting, imports)
  - ✅ Security scan (no new issues)
  - ✅ Code review (1+ approvals)

---

## Testing Strategy

### Unit Tests (Target: 40 tests)
- Restore logic & state transitions
- Memory search ranking
- UI component logic
- Metrics collection
- Cache invalidation

### Integration Tests (Target: 25 tests)
- Restore workflow end-to-end
- Search results accuracy
- API response format
- Database consistency

### Performance Tests (Target: 8 tests)
- Restore latency <100ms
- Search latency <50ms
- Load test (100 concurrent users)
- Memory profiling

### E2E Tests (Target: 5 tests)
- User workflow: search → view → restore
- UI interactions
- Error scenarios

---

## Monitoring & Metrics

### Key Metrics to Track
- Test coverage trend (target: 65%)
- Commit frequency & velocity
- PR review time
- Bug discovery rate
- Performance metrics

### Health Checks
- Daily: Tests passing, coverage maintained
- Weekly: Performance baseline maintained
- Sprint end: Feature complete & tested

---

## Post-Development (Phase 3)

After Phase 2 completion:
1. **Code Review & Approval**
2. **Security Scan & Verification**
3. **Performance Validation**
4. **Documentation Update**
5. **Release Preparation**
6. **Phase 3 Planning**: Multi-user auth, RBAC, lifecycle hardening

---

## Next Immediate Steps

1. ✅ Create feature branch: `feature/phase-2-instant-restore`
2. ✅ Update dependencies (Starlette, python-jose)
3. ✅ Re-run security scans & verify fixes
4. ⏳ Implement Restore Controller
5. ⏳ Implement Restore Service
6. ⏳ Add unit tests (restore logic)
7. ⏳ Build Memory Browser UI
8. ⏳ Add Prometheus metrics
9. ⏳ Performance optimization
10. ⏳ Create PR & merge to main

---

## Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Async**: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- **Prometheus Metrics**: https://prometheus-client-python.readthedocs.io/
- **React Performance**: https://react.dev/reference/react/useMemo
- **Database Optimization**: PostgreSQL Query Planning Docs

---

**Created**: November 21, 2025  
**Last Updated**: November 21, 2025  
**Status**: Ready for Phase 2 Development 🚀
