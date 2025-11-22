# Testing & Review Checklist - Pre-Alpha v0.1.0

## Phase 1: Core Backend Services

### Database & Models
- [ ] Test SQLite initialization (default)
- [ ] Test PostgreSQL connection & migration
- [ ] Verify all model relationships (Session, Clip, Memory)
- [ ] Test Alembic migration rollback/upgrade
- [ ] Check database indexes performance

### API Endpoints - Sessions
- [ ] POST /api/sessions (create)
- [ ] GET /api/sessions (list)
- [ ] GET /api/sessions/{id}
- [ ] PUT /api/sessions/{id}
- [ ] DELETE /api/sessions/{id}
- [ ] GET /api/sessions/{id}/branch-status
- [ ] PUT /api/admin/rate-limit

### API Endpoints - Clips
- [ ] POST /api/clips (create)
- [ ] GET /api/clips (list, filter by session)
- [ ] GET /api/clips/{id}
- [ ] DELETE /api/clips/{id}
- [ ] POST /api/clips/prune
- [ ] GET /api/clips/retention/stats
- [ ] POST /api/clips/retention/prune
- [ ] GET /api/clips/retention/config
- [ ] PUT /api/clips/retention/config
- [ ] POST /api/clips/{id}/restore (NEW)

### API Endpoints - Memories
- [ ] POST /api/memories (create)
- [ ] GET /api/memories (list, search)
- [ ] GET /api/memories/{id}
- [ ] PUT /api/memories/{id}
- [ ] DELETE /api/memories/{id}
- [ ] GET /api/memories/search (advanced filters)

### Export/Import & Remote Sync
- [ ] POST /api/export/full (unencrypted)
- [ ] POST /api/export/full (with encryption)
- [ ] POST /api/import/full (validation)
- [ ] POST /api/remote/sync/push (SSH/SCP)
- [ ] POST /api/remote/sync/pull (SSH/SCP)
- [ ] Test schema version compatibility

### Security & Middleware
- [ ] Verify security headers on all responses
- [ ] Test rate limiting (exceed threshold)
- [ ] Test dynamic rate limit updates
- [ ] Verify request ID generation
- [ ] Test integrity signing on clip creation
- [ ] Test integrity verification on clip fetch
- [ ] Check invalid signature handling

### Metrics & Monitoring
- [ ] GET /api/metrics (JSON format)
- [ ] GET /metrics/prom (Prometheus format)
- [ ] Verify counter increments (clip_created, pruned, rate_limit_block)
- [ ] Check latency histogram buckets
- [ ] Test metrics under load

### WebSocket Real-time
- [ ] Connect to /ws endpoint
- [ ] Verify clip.created broadcast
- [ ] Verify clip.deleted broadcast
- [ ] Verify memory.created broadcast
- [ ] Test multiple concurrent connections

### Services - Retention
- [ ] Auto-prune on clip creation
- [ ] Manual prune (dry run)
- [ ] Manual prune (execute)
- [ ] Config update persistence
- [ ] Verify preserve_manual_clips flag
- [ ] Check logging output

### Services - Branch Safety
- [ ] Detect divergent branches
- [ ] Flag rogue branches
- [ ] Test merge suggestions

### Services - Cache (Optional)
- [ ] Redis connection (if enabled)
- [ ] In-memory fallback
- [ ] Cache hit/miss behavior

### Services - Semantic Search (Optional)
- [ ] FAISS index creation
- [ ] Embedding generation
- [ ] Similarity search

## Phase 2: Frontend

### Core UI
- [ ] Session list rendering
- [ ] Session creation form
- [ ] Memory search interface
- [ ] Memory creation modal
- [ ] Dark theme consistency

### WebSocket Integration
- [ ] Real-time session updates
- [ ] Real-time memory updates
- [ ] Connection status indicator

### Navigation & UX
- [ ] Routing between views
- [ ] Form validation
- [ ] Error handling & display
- [ ] Loading states

## Phase 3: VS Code Extension

### Commands
- [ ] crecall.createSession
- [ ] crecall.createClip
- [ ] crecall.createMemory
- [ ] crecall.searchMemories
- [ ] crecall.showMemories

### Status Bar
- [ ] Session switcher display
- [ ] Session update on selection
- [ ] Active session persistence

### Auto-clip
- [ ] Trigger on file save (significant)
- [ ] Trigger on git commit
- [ ] Capture working directory
- [ ] Capture git metadata

### API Integration
- [ ] Correct endpoint URLs
- [ ] Error handling
- [ ] Response parsing

## Phase 4: CLI Tools

### bin/crecall
- [ ] session create
- [ ] session list
- [ ] clip create
- [ ] clip list
- [ ] memory create
- [ ] memory search
- [ ] export
- [ ] import
- [ ] sync push
- [ ] sync pull

## Phase 5: Build & Deployment

### Docker
- [ ] Stable image build
- [ ] Nightly image build
- [ ] Multi-arch support (amd64, arm64)
- [ ] Health check endpoint
- [ ] Container startup

### Scripts
- [ ] pre_alpha_package.sh (clean bundle)
- [ ] security_scan.sh (vulnerabilities)
- [ ] docker_build_all.sh (multi-arch)
- [ ] benchmark.py (performance baseline)

### Documentation
- [ ] README accuracy
- [ ] INSTALL instructions
- [ ] PATCH_NOTES completeness
- [ ] RELEASE_NOTES clarity
- [ ] API docs (/docs endpoint)

## Phase 6: Performance & Optimization

### Load Testing
- [ ] Benchmark clip creation (100 clips)
- [ ] Benchmark memory search (1000 memories)
- [ ] Concurrent WebSocket connections (10+)
- [ ] Rate limit threshold accuracy
- [ ] Database query performance

### Resource Usage
- [ ] Memory footprint (idle)
- [ ] Memory footprint (load)
- [ ] CPU usage patterns
- [ ] Disk I/O efficiency

## Phase 7: Edge Cases & Error Handling

### Error Scenarios
- [ ] Database connection failure
- [ ] Invalid session ID
- [ ] Missing clip
- [ ] Malformed request body
- [ ] Export with no data
- [ ] Import schema mismatch
- [ ] Remote sync auth failure
- [ ] Rate limit exceeded response
- [ ] Integrity verification failure

### Data Integrity
- [ ] Clip content preservation
- [ ] Memory metadata accuracy
- [ ] Session state consistency
- [ ] Git metadata capture

## Phase 8: Upgrade Paths

### Identified Improvements
- [ ] Full-text search for memories (PostgreSQL tsvector)
- [ ] Semantic ranking with score threshold
- [ ] Memory linking (relationships)
- [ ] Session timeline visualization
- [ ] Clip diff comparison
- [ ] Multi-user authentication (JWT)
- [ ] Role-based access control
- [ ] Conflict resolution for remote sync
- [ ] AI-powered memory suggestions
- [ ] Session replay engine

### Bug Fixes Needed
- [ ] (To be populated during testing)

### Performance Optimizations
- [ ] (To be identified via benchmarks)

---

**Instructions:**
1. Work through each phase sequentially
2. Mark items complete as verified
3. Document issues in Bug Fixes section
4. Propose optimizations in Performance section
5. After each phase, commit findings
6. Iterate: Fix → Retest → Update → Continue
