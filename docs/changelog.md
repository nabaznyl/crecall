# Version History

Complete chronological changelog for crecall.

---

## v0.1.0d-7 (preview) - 2025-11-21

### Infrastructure & Build Standards ✅
- Implemented VERSION file as single source of truth
- Created version management script (`scripts/version-bump.sh`)
- Built stable/nightly/dev build automation
- Multi-stage Dockerfiles for all channels
- GitHub Actions CI/CD pipeline
  - Automated linting (Black, Pylint, ESLint, Prettier)
  - Multi-version testing (Python 3.10, 3.11, 3.12)
  - Nightly builds (2 AM UTC)
  - Security scanning (Trivy)
- Comprehensive test suite (49 passing)
- Professional documentation (CONTRIBUTING.md, BUILD_STANDARDS.md)

### API & Lifecycle Modernization ✅
- FastAPI lifespan context replaces deprecated startup/shutdown
- Timezone-aware UTC timestamps (eliminates naive warnings)
- Session duplicate handling (HTTP 409 vs raw traceback)
- Portable encryption fallback (graceful downgrade)
- Security middleware (headers, request ID, rate limiting scaffold)

### Phase 0 & 1 Foundations ✅
- Vision document with personas, metrics, roadmap
- Context snapshot (architecture, gaps, decisions)
- Data model specification (external vs internal IDs)
- Workflows definition (3 core journeys)
- Archive structure (legacy notes, backups, demos)
- Centralized config & logging modules
- Startup integration validated (49/49 tests passing)

---

## v0.1.0d-6 (preview) - 2025-11-21

### Documentation Consolidation
- Removed redundant summaries (COMPLETION_SUMMARY, EXTENSION_COMPLETION_SUMMARY, SESSION_SUMMARY)
- Streamlined documentation hierarchy
- Version bump across CLI/API/docs
- Cleaned .gitignore references

---

## v0.1.0d-5 (preview) - 2025-11-21

### Housekeeping & Foundations
- Removed duplicate clips route
- Interactive settings menu finalized
- Alembic migration scaffolding prepared
- PostgreSQL migration readiness review
- Planning user theme preference model

---

## v0.1.0d-4 (preview) - 2025-11-21

### Configuration & Planning
- Light/dark theme toggle with persistence
- OS-level theme detection
- Interactive settings menu (`--settings` / `-o`)
- Config file creation (`~/.recall_memory/config.json`)
- Context assembly endpoint stub
- Embeddings service feature-gated
- Integrity checksum script
- Roadmap consolidation
- Security protocols documentation
- Brand license agreement draft

---

## v0.1.0d-3 (preview) - 2025-11-21

### Architecture Documentation
- Expanded memory features roadmap
- Instant recall system design
- Clip system architecture
- Crash recovery workflow
- Multi-tier stack planning
- Todo list persistence planning

---

## v0.1.0d-2 (preview) - 2025-11-20

### Command Interface
- Dash-only command enforcement (require `--` or `-`)
- Comprehensive short flag mappings
- Improved error messages
- Version display standardization

---

## v0.1.0d-1 (preview) - 2025-11-20

### Help & Flexibility
- Help format revision
- Support both `--` and bare commands
- Version alignment
- Cleaner summary output

---

## v0.1.0c-1 (preview) - 2025-11-20

### Command Prefixes
- Switch to `--` prefixed format
- Invalid argument error guidance
- Version prefixing with `v`

---

## v0.1.0b-1 (preview) - 2025-11-20

### Naming & Migration
- Rename `recall_chat` to `recall_memory`
- Add `(preview)` tag to version
- Default input handling for save
- Simplified help format
- Data directory migration

---

## v0.1.0a-1 (preview) - 2025-11-20

### Initial Preview ✅
- Unified bash wrapper
- Checkpoint logging (JSON-lines)
- Pause/resume semantics
- Encrypted transcripts (AES-256-CBC)
- Memory tagging
- Cache pruning
- Data clearance
- State management
- Docker context tracking
- Debian package structure
- APT repository integration
- Auto-migration from legacy directories

---

## Roadmap Highlights

### Phase 0-1 (Current)
- ✅ Vision & data model
- ✅ Config & logging standardization
- 🔄 Docs consolidation
- ⏳ Test tier specification

### Phase 2-3 (Next)
- Workflow implementation (session, search, export)
- Test coverage gating
- Quality standards enforcement

### Phase 4-9 (Future)
- Automation (retention, backups)
- Performance benchmarks
- CI/CD pipeline
- Telemetry & feedback
- Advanced search
- Security hardening

---

## Version Numbering

**Format**: `vMAJOR.MINOR.PATCH-BUILD(preview)`

- **MAJOR**: Breaking changes
- **MINOR**: New features
- **PATCH**: Bug fixes
- **BUILD**: Package iterations (e.g., `-7`)
- **Preview**: Pre-1.0.0 tag

---

## Migration Notes

### v0.1.0a → v0.1.0d
- Auto-migration from `~/.chat_recall` to `~/.recall_memory`
- Bash CLI remains compatible
- API endpoints added (backward compatible)

### Future Migrations
- v1.0.0: PostgreSQL recommended
- Full migration scripts provided
