# crecall Phase 2-3 Development Roadmap

**Status**: Planning Phase  
**Target Timeline**: Q4 2025 - Q1 2026  
**Release Version**: v0.2.0 - v0.3.0  

---

## Executive Summary

Phase 2-3 focuses on enabling instant environment recovery and multi-user support. Building on the stable v0.1.0d-7 foundation (59.20% coverage, 85 tests passing), we will implement advanced features to unlock production use cases:

- **Phase 2 (Dec 2025)**: Instant Recovery Engine, Observability, Performance Tuning
- **Phase 3 (Jan 2026)**: Authentication & Multi-user, Lifecycle Hardening

---

## Phase 2: Instant Recovery & Observability (4 weeks)

### 2.1: Instant Restore Engine

**Objective**: Enable users to restore environment state from any clip.

#### Deliverables
- `POST /sessions/{id}/restore?clip_id=…` - Restore endpoint
- Environmental variable restoration
- File state snapshot (opt-in)
- Process state hints (for manual re-execution)

#### Acceptance Criteria
- [ ] Restore endpoint created and tested
- [ ] All memory/clips preserved post-restore
- [ ] State verification available via checksum
- [ ] Test coverage: >80%

#### Effort Estimate: 40 hours
- Endpoint implementation: 16h
- State restoration logic: 16h
- Tests & validation: 8h

#### Blocked By
- None (can start immediately)

#### Depends On
- None

---

### 2.2: Memory Browser UI

**Objective**: Web interface for searching and ranking memories.

#### Deliverables
- React/Vue component library
- Search UI with filters (category, importance, tags, date range)
- Ranking visualization (score breakdown: text + recency + importance)
- Bulk operations (export, delete, tag)

#### Acceptance Criteria
- [ ] Search endpoint tested with 100 memories
- [ ] Ranking visualization matches backend scoring
- [ ] Filter combinations work correctly
- [ ] Performance: <500ms render time

#### Effort Estimate: 60 hours
- Backend API enhancements: 8h
- Frontend components: 32h
- Integration & testing: 20h

#### Blocked By
- None (can use existing search API)

#### Depends On
- Memory search API (ready in v0.1.0d-7)

---

### 2.3: Prometheus Exporter

**Objective**: Real-world deployment monitoring.

#### Deliverables
- `/metrics/prom` endpoint (partial in v0.1.0d-7, expand coverage)
- Dashboard templates (Grafana JSON)
- Alert rules (Prometheus)
- Documentation

#### Metrics to Export
- Session count/status distribution
- Memory creation/search rates
- API latency p50/p95/p99
- Database connection pool stats
- Cache hit/miss rates

#### Acceptance Criteria
- [ ] Metrics endpoint returns valid Prometheus format
- [ ] Scrape interval <100ms
- [ ] Grafana dashboard functional
- [ ] Alert rules firing correctly on anomalies

#### Effort Estimate: 30 hours
- Metrics collection: 12h
- Dashboard/rules: 12h
- Docs & testing: 6h

#### Blocked By
- Metrics service (partially ready; expand in Phase 2)

#### Depends On
- None (can integrate with existing metrics framework)

---

### 2.4: Performance Tuning

**Objective**: Achieve <100ms p95 latency for all endpoints.

#### Profiling Tasks
- [ ] Identify hot paths (database queries, compute)
- [ ] Benchmark memory search with 10k+ memories
- [ ] Profile API endpoint response times
- [ ] Analyze cache hit rates

#### Optimization Opportunities
1. **Database**: Batch queries, add indexes on (session_id, category, importance)
2. **Caching**: In-memory LRU for frequent searches
3. **Async**: Parallelize independent API calls
4. **Serialization**: Consider msgpack for large exports

#### Acceptance Criteria
- [ ] Search latency: <50ms (100 memories)
- [ ] API p95: <100ms
- [ ] Memory usage: <150 MB (venv + runtime)
- [ ] Benchmark report documented

#### Effort Estimate: 35 hours
- Profiling & analysis: 12h
- Implementation: 16h
- Benchmarking & validation: 7h

#### Blocked By
- None (parallel with other Phase 2 work)

#### Depends On
- Base API (ready)

---

### Phase 2 Success Criteria
- ✅ Instant Restore Engine: Working, >80% tested
- ✅ Memory Browser: MVP with search + ranking visualization
- ✅ Prometheus Exporter: Production-ready
- ✅ Performance: <100ms p95 latency verified
- ✅ Overall coverage: 65-70%

---

## Phase 3: Authentication & Multi-user Support (4 weeks)

### 3.1: JWT Authentication

**Objective**: Secure API with token-based authentication.

#### Deliverables
- JWT token generation & validation
- `/api/auth/login` endpoint
- `/api/auth/refresh` endpoint
- Token expiration & rotation strategy

#### Implementation Details
```python
# Example token payload
{
  "sub": "user_123",           # Subject (user ID)
  "iat": 1637423456,           # Issued at
  "exp": 1637509856,           # Expiration (24h)
  "scopes": ["sessions:read", "memories:write"]
}
```

#### Acceptance Criteria
- [ ] JWT tokens validated on all endpoints
- [ ] Token refresh working
- [ ] Expired tokens rejected
- [ ] Test coverage: >85%

#### Effort Estimate: 25 hours
- JWT implementation: 10h
- Middleware integration: 8h
- Tests: 7h

#### Blocked By
- None (can implement in parallel)

#### Depends On
- None

---

### 3.2: User Session Scoping

**Objective**: Isolate user data; prevent cross-user access.

#### Deliverables
- User model & database schema
- Middleware to inject user context into requests
- Query filters (session_id WHERE user_id = current_user)
- Tests for cross-user access prevention

#### Implementation Details
```python
# Query pattern
stmt = select(Session).where(
    (Session.session_id == session_id) &
    (Session.user_id == current_user.id)
)
```

#### Acceptance Criteria
- [ ] User A cannot access User B's sessions
- [ ] All endpoints respect user scoping
- [ ] Test coverage: >90%
- [ ] Performance: <10ms overhead per request

#### Effort Estimate: 40 hours
- Schema & model: 12h
- Middleware & query updates: 20h
- Tests: 8h

#### Blocked By
- None (can start immediately)

#### Depends On
- JWT Authentication (Phase 3.1)

---

### 3.3: Role-Based Access Control (RBAC)

**Objective**: Support different permission levels (viewer, editor, admin).

#### Roles
- **admin**: Full access (create users, delete data, view metrics)
- **editor**: Create/modify own sessions & memories
- **viewer**: Read-only access to shared sessions

#### Implementation
```python
# Decorator pattern
@require_role("editor")
async def create_session(...):
    pass
```

#### Acceptance Criteria
- [ ] Roles enforced on all endpoints
- [ ] Permission inheritance working
- [ ] Admin can override user permissions
- [ ] Test coverage: >80%

#### Effort Estimate: 30 hours
- RBAC schema & logic: 12h
- Decorator & middleware: 12h
- Tests: 6h

#### Blocked By
- User Session Scoping (Phase 3.2)

#### Depends On
- JWT Authentication (Phase 3.1)

---

### 3.4: Lifecycle Hardening

**Objective**: Fix non-blocking issues, improve error handling and logging.

#### Tasks
- [ ] Fix "I/O operation on closed file" warning (crash detector shutdown)
- [ ] Improve error messages (structured logging)
- [ ] Add graceful degradation (fallbacks)
- [ ] Enhance database transaction handling

#### Acceptance Criteria
- [ ] Zero test teardown warnings
- [ ] All errors include actionable messages
- [ ] Database rollback on failures
- [ ] Test coverage: >95%

#### Effort Estimate: 25 hours
- Logging infrastructure: 10h
- Transaction handling: 8h
- Testing & validation: 7h

#### Blocked By
- None (can start immediately)

#### Depends On
- None

---

### Phase 3 Success Criteria
- ✅ JWT Authentication: Production-ready
- ✅ User Scoping: All endpoints isolated
- ✅ RBAC: All roles enforced
- ✅ Lifecycle Hardening: Zero warnings
- ✅ Overall coverage: 70-75%
- ✅ Ready for multi-user staging deployment

---

## Resource Allocation

### Team Structure
- **Backend Lead**: 1 FTE (Phases 2-3 core work)
- **Frontend Engineer**: 1 FTE (Memory Browser, UI)
- **QA/Testing**: 0.5 FTE (test automation, performance)
- **DevOps**: 0.25 FTE (Prometheus setup, deployment)

### Sprint Planning
- **Sprint 1** (Dec 1-15): Instant Restore + Memory Browser foundation
- **Sprint 2** (Dec 16-31): Observability + Performance tuning
- **Sprint 3** (Jan 1-15): Authentication & User Scoping
- **Sprint 4** (Jan 16-31): RBAC & Lifecycle hardening

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Database scaling bottleneck | High latency | Medium | Profile early; add indexes; consider sharding |
| Auth complexity | Security issues | Low | Use proven JWT library; security review |
| User migration overhead | Deployment delay | Low | Maintain backward compat API version |
| Performance regression | p95 > 100ms | Medium | Continuous benchmarking; perf gates |

---

## Success Metrics

| Metric | Phase 2 Target | Phase 3 Target |
|--------|----------------|----------------|
| Test coverage | 65-70% | 70-75% |
| API latency p95 | <100ms | <100ms |
| Memory usage | <150 MB | <150 MB |
| Tests passing | 100+ | 130+ |
| Uptime | 99.5% | 99.9% |

---

## Compatibility & Rollback

### Backward Compatibility
- All v0.1.0d-7 APIs remain available
- New endpoints at `/api/v2/…` (optional)
- Legacy mode flag for backward compat

### Rollback Plan
- Feature flags for Phase 3 auth (disable if issues)
- Database migrations reversible
- Binary compatibility with v0.1.0d-7

---

## Known Unknowns

1. **Scaling Strategy**: Cluster vs. single instance?
2. **Real-world Latency**: Performance at scale (10k+ users)?
3. **Auth Integration**: LDAP/OAuth support?
4. **Data Migration**: Path for existing v0.1.0 users?

---

## Next Steps

1. **Immediate** (This week): Review roadmap with stakeholders
2. **Week 1**: Finalize Phase 2 sprint breakdown
3. **Week 2**: Begin Instant Restore Engine implementation
4. **Week 3**: Start Memory Browser frontend design
5. **Week 4**: First release candidate (v0.2.0-rc1)

---

## Document Control

- **Last Updated**: 2025-11-21
- **Version**: 1.0 (Planning)
- **Owner**: Architecture Team
- **Review Cycle**: Bi-weekly (Thursdays)

---

## Sign-Off

**Roadmap approved for execution.**

✅ Phase 2: Ready to start (Instant Recover, Observability)  
✅ Phase 3: Design finalized (Auth, Multi-user)  
✅ Resource allocation: Confirmed  
✅ Risk assessment: Mitigation strategies in place  

**Target delivery**: v0.3.0 by end of January 2026

---

**Roadmap timestamp**: 2025-11-21T03:00:00Z
