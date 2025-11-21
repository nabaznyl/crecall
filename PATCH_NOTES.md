# crecall Patch Notes

Version history and changelog in checklist format.

---

## v0.1.0d-3 (preview) - November 21, 2025

**Documentation & Architecture Planning**

- [x] Expanded README with comprehensive memory features roadmap
- [x] Added "Instant Recall" system concept and design
- [x] Documented clip system architecture (lightweight restore points)
- [x] Added crash recovery workflow documentation
- [x] Updated architecture section with detailed multi-tier stack plan
- [x] Expanded PATCH_NOTES with granular feature checklists
- [x] Added todo list persistence planning
- [x] Documented auto-save and crash detection mechanisms
- [x] Added upcoming CLI commands for clip management
- [x] Created comprehensive React/Python/PostgreSQL scaffolding roadmap

**Planning Notes**:
- Focus on solving "lost my place" problem after unexpected crashes
- Memory system as flagship feature and main reason to use crecall
- Clips designed for minimal footprint (~10-50KB) and fast restoration (<100ms)
- Auto-save default: 5 minutes (configurable)

---

## v0.1.0d-2 (preview) - November 20, 2025

**Dash-Only Command Enforcement**

- [x] Require leading `--` or `-` for all commands
- [x] Reject bare command names (e.g., `crecall save` now errors)
- [x] Add comprehensive short flag mappings:
  - `-s` = `--save`
  - `-S` = `--summary` / `--refer`
  - `-t` = `--total`
  - `-T` = `--total-encrypt`
  - `-r` = `--resume`
  - `-p` = `--pause`
  - `-m` = `--memory`
  - `-e` = `--encrypt`
  - `-d` = `--decrypt`
  - `-c` = `--cache`
  - `-D` = `--data`
  - `-x` = `--state`
  - `-v` = `--version`
  - `-h` = `--help`
- [x] Update error message: "Invalid command. Use 'crecall --help' for more information."
- [x] Version display only via `--version` or `-v`

---

## v0.1.0d-1 (preview) - November 20, 2025

**Help Format Revision & Command Flexibility**

- [x] Revert help output to bare commands list (remove header/version line)
- [x] Support both `--` and bare command invocation
- [x] Align script version with package version
- [x] Remove version line from `--summary` output

---

## v0.1.0c-1 (preview) - November 20, 2025

**Command Prefix Transition**

- [x] Switch all commands to `--` prefixed format
- [x] Add invalid no-argument error guidance
- [x] Prefix displayed version with `v` (e.g., `v0.1.0c`)
- [x] Remove version from summary display

---

## v0.1.0b-1 (preview) - November 20, 2025

**Naming & Path Migration**

- [x] Rename `recall_chat` to `recall_memory` throughout codebase
- [x] Add `(preview)` tag to version display
- [x] Default input handling for save command (auto-generates note)
- [x] Simplify help output format
- [x] Data directory migration: `~/.chat_recall` → `~/.recall_memory`

---

## v0.1.0a-1 (preview) - November 20, 2025

**Initial Preview Release**

- [x] Unified bash wrapper for session management
- [x] Checkpoint logging (JSON-lines format)
- [x] Pause/resume semantics
- [x] Encrypted transcripts (AES-256-CBC with PBKDF2)
- [x] Memory tagging subsystem
- [x] Cache pruning functionality
- [x] Data clearance operations
- [x] State management (active/paused)
- [x] Docker context tracking
- [x] Local file storage backend
- [x] Debian package structure
- [x] APT repository integration
- [x] Auto-migration from `~/.chat_recall`

---

## Upcoming Features

### 🎯 Instant Recall System (Flagship Feature - Highest Priority)

**The Problem This Solves**: VS Code crashes, terminal closes, system restarts → you lose your place, context, and todo lists. Starting over is frustrating and time-consuming.

**The Solution**: Near-instantaneous restoration from lightweight "clips" that capture your complete development context.

#### Clip System Implementation
- [ ] **Core Clip Engine**
  - [ ] Clip data structure design (JSON schema)
  - [ ] Clip creation algorithm (context capture)
  - [ ] Clip compression (minimize storage footprint)
  - [ ] Clip storage (local + database hybrid)
  - [ ] Clip indexing (fast lookup by time/tag/project)

- [ ] **Auto-Clip Generation**
  - [ ] Configurable auto-save timer (default: 5 minutes)
  - [ ] Trigger on significant events (git commit, file save, command execution)
  - [ ] Smart clip deduplication (don't save identical states)
  - [ ] Clip rotation policy (keep last N, prune old)
  - [ ] Background worker for non-blocking saves

- [ ] **Context Capture**
  - [ ] Working directory and git state
  - [ ] Open files list with cursor positions
  - [ ] Terminal command history (last N commands)
  - [ ] Environment variables (filtered/sanitized)
  - [ ] Docker context and containers
  - [ ] Active todo list state
  - [ ] Recent memory items
  - [ ] IDE state (via plugins)

- [ ] **Instant Restore**
  - [ ] `crecall --recall` command (restore most recent)
  - [ ] `crecall --recall <clip-id>` (restore specific)
  - [ ] `crecall --recall --list` (browse available clips)
  - [ ] Fast parsing (<100ms target)
  - [ ] Progressive restoration (critical first, optional later)
  - [ ] Conflict resolution (handle changed files)

- [ ] **Crash Detection & Recovery**
  - [ ] Detect unexpected terminations
  - [ ] Auto-recovery prompt on next session
  - [ ] Emergency restore mode (`--emergency-restore`)
  - [ ] Recovery verification (check clip integrity)
  - [ ] Fallback to previous clip if corruption detected

#### CLI Commands for Clips
- [ ] `crecall --clip [name]` - Create named clip manually
- [ ] `crecall --recall [clip-id]` - Restore from clip
- [ ] `crecall --clips list` - Show all available clips
- [ ] `crecall --clips prune --older-than <days>` - Clean old clips
- [ ] `crecall --clips export <clip-id>` - Export clip data
- [ ] `crecall --clips import <file>` - Import clip
- [ ] `crecall --clips diff <clip1> <clip2>` - Compare two clips

---

### 🧠 Memory System Expansion (Core Feature)

**Goal**: Make memory the primary reason developers choose crecall. Rich, searchable, linked memory system.

- [ ] **Enhanced Memory Commands**
  - [ ] `--memory search <query>` - Keyword/phrase search
  - [ ] `--memory search --date <range>` - Time-based filtering
  - [ ] `--memory search --tag <tag>` - Tag-based queries
  - [ ] `--memory tag <id> <tags>` - Add tags to memory
  - [ ] `--memory link <memory-id> <checkpoint-id>` - Link memory to checkpoint
  - [ ] `--memory edit <id>` - Edit existing memory
  - [ ] `--memory delete <id>` - Remove memory item
  - [ ] `--memory export [--format=json|md|csv]` - Export memories
  - [ ] `--memory import <file>` - Import from file
  - [ ] `--memory stats` - Usage statistics and analytics

- [ ] **Memory Organization**
  - [ ] Hierarchical categories/folders
  - [ ] Custom tagging system
  - [ ] Auto-categorization (ML-based)
  - [ ] Priority/importance levels
  - [ ] Color coding in UI

- [ ] **Memory Intelligence**
  - [ ] Semantic search (not just keyword)
  - [ ] Memory suggestions (AI-powered)
  - [ ] Pattern detection (recurring themes)
  - [ ] Workflow analytics from memory data
  - [ ] Memory clustering (related items)

- [ ] **Memory Linking**
  - [ ] Link to specific checkpoints
  - [ ] Link to git commits
  - [ ] Link to file changes
  - [ ] Link to other memories
  - [ ] Bidirectional relationships

- [ ] **Memory Visualization**
  - [ ] Timeline view (chronological)
  - [ ] Graph view (connections)
  - [ ] Tag cloud
  - [ ] Heatmap (activity over time)

---

### 🔄 Session Management & Crash Recovery

- [ ] **Session Continuity**
  - [ ] Session pause/resume with full context
  - [ ] Multi-session support (parallel projects)
  - [ ] Session branching (experimental workflows)
  - [ ] Session merging (combine branches)
  - [ ] Session templates (predefined workflows)

- [ ] **Crash Recovery Features**
  - [ ] Automatic crash detection on startup
  - [ ] Recovery wizard (guided restoration)
  - [ ] Partial recovery options (choose what to restore)
  - [ ] Recovery history (previous crash recoveries)
  - [ ] Recovery validation (verify restored state)

- [ ] **Todo List Persistence**
  - [ ] Auto-save todo state to clips
  - [ ] Restore todo lists after crash
  - [ ] Todo history (track completed items)
  - [ ] Todo analytics (completion rates, time tracking)

- [ ] **Context Preservation**
  - [ ] File positions (line/column)
  - [ ] Terminal scrollback
  - [ ] Shell environment variables
  - [ ] Docker container states
  - [ ] Network connections/ports

---

### 🌐 Multi-Tier Architecture

- [ ] **React Frontend**
  - [ ] Project scaffolding (Vite + React + TypeScript)
  - [ ] Component library setup (shadcn/ui or MUI)
  - [ ] Memory browser interface
  - [ ] Session timeline visualization
  - [ ] Clip manager dashboard
  - [ ] Real-time updates (WebSocket)
  - [ ] Authentication UI
  - [ ] Settings/preferences panel
  - [ ] Dark mode support
  - [ ] Responsive design (mobile-friendly)

- [ ] **Python API (FastAPI)**
  - [ ] Project scaffolding (FastAPI + Pydantic + SQLAlchemy)
  - [ ] Database models (sessions, checkpoints, memories, clips)
  - [ ] RESTful endpoints (CRUD operations)
  - [ ] Memory search engine (full-text + semantic)
  - [ ] Clip creation/restoration engine
  - [ ] Auto-save scheduler (background tasks)
  - [ ] WebSocket server (real-time updates)
  - [ ] Authentication (JWT tokens)
  - [ ] Authorization (role-based access)
  - [ ] API documentation (OpenAPI/Swagger)
  - [ ] Rate limiting and caching
  - [ ] Export/import utilities

- [ ] **PostgreSQL Database**
  - [ ] Database schema design
  - [ ] Migration scripts (Alembic)
  - [ ] Full-text search indexes
  - [ ] Performance optimization (query tuning)
  - [ ] Backup/restore automation
  - [ ] Data retention policies
  - [ ] Migration from file-based storage
  - [ ] Replication setup (optional)

---

### 🔌 Integrations & Extensions

- [ ] **IDE Plugins**
  - [ ] VS Code extension
    - [ ] Status bar integration
    - [ ] Sidebar panel (memory browser)
    - [ ] Commands palette integration
    - [ ] Auto-clip on file save
    - [ ] Crash recovery wizard
  - [ ] JetBrains plugin (IntelliJ, PyCharm, etc.)
  - [ ] Vim/Neovim plugin

- [ ] **Git Integration**
  - [ ] Auto-clip on commit
  - [ ] Auto-clip on branch switch
  - [ ] Git hooks (post-commit, post-merge)
  - [ ] Link memories to commits
  - [ ] Commit message templates with memories

- [ ] **External Tools**
  - [ ] Webhook support (Slack, Discord, etc.)
  - [ ] CI/CD integration (GitHub Actions, GitLab CI)
  - [ ] Project management (Jira, Trello)
  - [ ] Note-taking apps (Obsidian, Notion)

---

### 🛠️ Developer Experience

- [ ] **Configuration**
  - [ ] `~/.crecallrc` support (YAML/JSON/TOML)
  - [ ] Per-project config (`.crecall/config`)
  - [ ] Environment variable overrides
  - [ ] Config validation and schema

- [ ] **CLI Enhancements**
  - [ ] Shell completion (bash, zsh, fish)
  - [ ] Colored output (success/error/warning)
  - [ ] Progress bars for long operations
  - [ ] Interactive prompts (fuzzy search)
  - [ ] Verbose/debug modes

- [ ] **Documentation**
  - [ ] Man pages (`man crecall`)
  - [ ] Comprehensive user guide
  - [ ] API reference documentation
  - [ ] Video tutorials
  - [ ] Migration guides

- [ ] **Testing & Quality**
  - [ ] Unit tests (pytest)
  - [ ] Integration tests
  - [ ] E2E tests (frontend + backend)
  - [ ] Performance benchmarks
  - [ ] Security audits

---

### 📊 Analytics & Insights

- [ ] **Workflow Analytics**
  - [ ] Time tracking per project/session
  - [ ] Context switching frequency
  - [ ] Productivity patterns
  - [ ] Most used commands
  - [ ] Memory usage patterns

- [ ] **Reporting**
  - [ ] Daily/weekly summaries
  - [ ] Export analytics data
  - [ ] Custom reports
  - [ ] Visualization dashboards

---

## Version Numbering

- **Format**: `vMAJOR.MINOR.PATCH-BUILD(preview)`
- **Current**: `v0.1.0d-2(preview)`
- **Patch increments** indicate bug fixes or minor changes within same feature set
- **Build number** (`-1`, `-2`) tracks Debian package iterations
- **Preview tag** remains until stable release (v1.0.0)

---

## Development Notes

- All changes tracked in `debian/changelog`
- Package builds via `dpkg-buildpackage`
- Local APT repo at `~/repo/crecall/`
- Source tree at `/home/anonmaly/crecall/`
