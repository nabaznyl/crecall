# crecall - Session Recall and Transcript Tool

**Current Version:** v0.1.0d-6 (preview)  
**Status:** Active Development - Memory Features Coming Soon!
**UI Theme:** Default Dark Mode (toggleable light mode) • Settings menu available

Session continuity and checkpoint logging with encryption, pause/resume semantics, and **intelligent memory management**.

**Data Directory:** `~/.recall_memory` (auto-migrates from `~/.recall_chat` or `~/.chat_recall`)

> **See:** [PATCH_NOTES.md](PATCH_NOTES.md) for detailed version history and upcoming features.

---

## 🎯 Why crecall?

**Never lose your place again.** Built to solve the frustration of unexpected crashes, restarts, and context loss:

- **Crash Recovery**: Resume exactly where you left off, even after unexpected shutdowns
- **Session Continuity**: Automatic checkpoints preserve your workflow state
- **Memory Intelligence**: Track important milestones, decisions, and context (expanded features coming soon!)
- **Encrypted Security**: AES-256 encryption for sensitive session data

**Primary Goal:** Make crecall the go-to tool for developers who need reliable session persistence and intelligent memory management across their workflow.

---

## ✨ New Updates & Features

### 🆕 Latest (v0.1.0d-2 (preview))
- ✅ **Dash-Only Commands**: All commands now require `--` or `-` prefix for clarity
- ✅ **Short Flags**: Quick access with single-character flags (`-s`, `-m`, `-r`, etc.)
- ✅ **Improved Error Messages**: Better guidance when commands are incorrect
- ✅ **Version Control**: Consistent version display via `--version` or `-v`

### 🚀 Coming Soon (Priority Features)

**Memory System Overhaul** - *The heart of crecall and main reason to use this application*
- 🔜 **Instant Recall (`crecall --recall`)**: Near-instantaneous session restoration from lightweight "clips" (restore points with minimal footprint)
- 🔜 **Memory Clips**: Automatic backup points created during workflow - think Git commits for your entire development context
- 🔜 **Memory Search**: Find memories by keyword, date, tag, or semantic context
- 🔜 **Memory Tags & Categories**: Organize with custom tags, auto-categorization, and hierarchical structure
- 🔜 **Memory Linking**: Auto-connect memories to specific checkpoints, commits, and file changes
- 🔜 **Memory Export/Import**: Full data portability (Markdown, JSON, CSV, custom formats)
- 🔜 **Memory Analytics**: Workflow insights, productivity patterns, context switching analysis
- 🔜 **Contextual Memory**: Track open files, cursor positions, terminal state, Docker context
- 🔜 **Smart Memory Suggestions**: AI-powered recommendations for what to remember
- 🔜 **Auto-Save**: Configurable auto-checkpoint (default 5-min intervals) - never lose your place again!

**Crash Recovery & Session Continuity** - *Built to solve the "lost my place" problem*
- 🔜 **Intelligent Crash Recovery**: Resume exactly where you left off after unexpected shutdowns
- 🔜 **Session Restore Points**: Lightweight clips capture your complete workflow state
- 🔜 **Todo List Persistence**: Automatic tracking and restoration of active todo lists
- 🔜 **Context Preservation**: File positions, terminal commands, working directories, environment variables
- 🔜 **Recovery Timeline**: Visual history of all restore points with quick navigation
- 🔜 **Multi-Project Recovery**: Independent crash recovery for concurrent projects
- 🔜 **Emergency Restore**: `crecall --emergency-restore` for critical data recovery

**Enhanced Session Management**
- 🔜 **Session Branching**: Create alternate timelines for experimentation
- 🔜 **Session Merging**: Combine work from multiple branches
- 🔜 **Session Diff**: Compare states between any two restore points
- 🔜 **Session Replay**: Step through your workflow history
- 🔜 **Multi-Session Dashboard**: Manage all active projects from single interface

**Developer Experience**
- 🔜 **Git Integration**: Auto-checkpoint on commits, branches, merges
- 🔜 **IDE Plugins**: Deep VS Code integration (status bar, sidebar, commands)
- 🔜 **Configuration Files**: Comprehensive customization via `~/.crecallrc`
- 🔜 **CLI Enhancements**: Autocomplete, colored output, progress bars
- 🔜 **Webhook Support**: Integrate with external tools (Slack, Discord, etc.)

---

## 📦 Installation

### Build Package

```bash
cd ~/crecall
dpkg-buildpackage -us -uc
```

Creates `../crecall_0.1.0d-2_all.deb`

### Local Repository Setup

```bash
mkdir -p ~/repo/crecall
cp ../crecall_0.1.0d-2_all.deb ~/repo/crecall/
cd ~/repo/crecall
dpkg-scanpackages . /dev/null > Packages
echo "deb [trusted=yes] file://$HOME/repo/crecall ./" | sudo tee /etc/apt/sources.list.d/crecall-local.list
sudo apt update
```

### Install via APT

```bash
sudo apt install crecall
```

---

## 🚀 Usage

**All commands require dash prefixes (`--` or short `-` form). Bare commands will error.**

### Command Reference

| Long Form             | Short | Description                          |
|-----------------------|-------|--------------------------------------|
| `--save [note]`       | `-s`  | Save checkpoint (auto-note if blank) |
| `--summary`, `--refer`| `-S`  | Show session summary                 |
| `--total <file>`      | `-t`  | Plain transcript & pause             |
| `--total-encrypt <file>` | `-T` | Encrypted transcript & pause      |
| `--resume --yes`      | `-r`  | Resume from pause                    |
| `--pause`             | `-p`  | Pause session                        |
| `--memory add <text>` | `-m`  | Add memory item                      |
| `--memory list [N]`   | `-m`  | List last N memories (default 20)    |
| `--memory clear`      | `-m`  | Clear memory log                     |
| `--recall [clip-id]`  | *Coming Soon* | Instant restore from clip  |
| `--clip [name]`       | *Coming Soon* | Create named restore point |
| `--encrypt <file>`    | `-e`  | Encrypt file (creates .enc)          |
| `--decrypt <file.enc>`| `-d`  | Decrypt file                         |
| `--cache prune --keep-last N [--dry-run]` | `-c` | Prune log entries |
| `--data clear`        | `-D`  | Wipe all data (interactive confirm)  |
| `--state`             | `-x`  | Show state JSON                      |
| `--version`           | `-v`  | Show version                         |
| `--help`              | `-h`  | Show help                            |

### Examples

```bash
# Save checkpoint with auto-generated note
crecall --save
crecall -s

# Save with custom note
crecall --save "Completed feature X"

# View session summary
crecall --summary
crecall -S

# Memory management (core feature - more commands coming!)
crecall --memory add "Critical milestone achieved"
crecall --memory list 10
crecall -m list

# Create encrypted transcript
crecall --total-encrypt session_transcript.txt
crecall -T session_transcript.txt

# Resume after pause or crash
crecall --resume --yes

# Encryption utilities
crecall --encrypt sensitive.txt
crecall --decrypt sensitive.txt.enc

# Maintenance
crecall --cache prune --keep-last 100 --dry-run
crecall --cache prune --keep-last 100
crecall --data clear

# Version and help
crecall --version
crecall -v
crecall --help

# Toggle UI theme (web dashboard)
# Default is dark mode; click the "Light Mode" / "Dark Mode" button in header.
# Preference persists in localStorage under key: crecall-theme

# Open settings menu (interactive)
crecall --settings
crecall -o
```

---

## 🎨 Features

### Current Capabilities

- ✅ **Checkpoint Logging**: JSON-lines format with timestamps, notes, working directory, Docker context
- ✅ **Pause/Resume Semantics**: State management for workflow control
- ✅ **Encrypted Transcripts**: AES-256-CBC with PBKDF2, auto-generated passphrase
- ✅ **Memory Tagging**: Persistent memory log for important milestones
- ✅ **Cache Pruning**: Keep last N entries, dry-run preview
- ✅ **Data Migration**: Auto-migrates from legacy directories on first run
- ✅ **Short Flags**: Single-character alternatives for all commands
- ✅ **Theme Toggle**: Switch between dark and light modes (default dark, persisted)
- ✅ **Settings Menu**: Interactive CLI config for auto-save, clip retention, theme, auto-clip

### Planned Capabilities

**Memory Features** *(Primary Development Focus)*
- 🔜 Contextual memory linking to checkpoints
- 🔜 Memory search and filtering by keyword/date/tags
- 🔜 Memory categories and custom tags
- 🔜 Memory export/import (Markdown, JSON, CSV)
- 🔜 Memory analytics and workflow insights
- 🔜 Enhanced CLI commands and future API endpoints

**Session Management**
- 🔜 Auto-save with 5-minute intervals (configurable)
- 🔜 Crash recovery and session restoration
- 🔜 Multi-session/multi-project support
- 🔜 Session branching and merging

**Integration & Extensibility**
- 🔜 Git hooks for automatic checkpoints
- 🔜 IDE plugins (VS Code, JetBrains)
- 🔜 Webhook support for external tools
- 🔜 Plugin/extension system

---

## 🗂️ Data Format

### Encryption

- **Algorithm**: AES-256-CBC with PBKDF2
- **Passphrase Storage**: `~/.recall_memory/passphrase` (auto-generated, chmod 600)
- **Created On**: First encrypted operation

### File Locations

- **Log**: `~/.recall_memory/recall.log` (JSON-lines)
- **State**: `~/.recall_memory/state.json` (active/paused)
- **Memory**: `~/.recall_memory/recall_memory.log` (timestamped entries)
- **Transcripts**: `~/.recall_memory/transcripts/` (plain and .enc)

---

## 🏗️ Architecture

### Current: CLI Wrapper (v0.1.0d-2 (preview))

- Bash-based unified command dispatcher
- Local file storage (JSON-lines format)
- OpenSSL encryption (AES-256-CBC)
- Memory logging with timestamps
- State management (active/paused)

### Planned: Multi-Tier Stack with Instant Recall System

**Core Philosophy**: Minimal footprint, maximum speed. Think "Git for your entire dev context" - lightweight, fast, recoverable.

#### 1. **React Frontend** (Interactive Web Dashboard)
   - **Memory Browser**: Search, filter, tag, and navigate all memories
   - **Session Timeline**: Visual workflow history with restore points
   - **Instant Recall Dashboard**: One-click restoration to any clip
   - **Real-time Monitoring**: Live session state, auto-save indicators
   - **Clip Manager**: Create, name, and organize restore points
   - **Diff Viewer**: Compare any two session states
   - **Analytics Dashboard**: Workflow insights and productivity metrics
   - **Encryption Key Management**: Secure passphrase handling UI

#### 2. **Python API (FastAPI)** (High-Performance Backend)
   - **RESTful Endpoints**: Full CRUD for memories, sessions, clips
   - **Memory Search Engine**: Full-text, semantic, and keyword search
   - **Clip Creation Engine**: Lightweight snapshot generator
   - **Restore Engine**: Fast state reconstruction from clips
   - **Session Management**: Multi-session orchestration
   - **Auto-Save Scheduler**: Configurable background checkpoints
   - **Crash Detection**: Monitor for unexpected terminations
   - **WebSocket Support**: Real-time updates to frontend
   - **Authentication**: JWT-based auth for multi-user setups
   - **Export/Import**: Bulk operations and data portability

#### 3. **PostgreSQL Database** (Robust Data Layer)
   - **Sessions Table**: Track all active and historical sessions
   - **Checkpoints Table**: Full checkpoint data with metadata
   - **Memories Table**: Tagged, searchable memory items
   - **Clips Table**: Lightweight restore points (compressed state)
   - **Context Table**: File positions, environment vars, terminal state
   - **Full-Text Search**: PostgreSQL's built-in FTS for memories
   - **Indexes**: Optimized for time-range and keyword queries
   - **Migration Tools**: Seamless upgrade from file-based storage
   - **Backup/Restore**: Automated daily backups

#### 4. **Clip System** (The Innovation)
   
**What is a Clip?**
- Lightweight snapshot of your complete development context
- Captures: working directory, open files, cursor positions, terminal history, environment variables, Docker context, todo lists, active memories
- Compressed JSON format (~10-50KB per clip vs. full session data)
- Stored locally and/or in database
- Tagged with automatic metadata (timestamp, git branch, project, etc.)

**How Clips Work**:
```bash
# Automatic clips every 5 minutes (configurable)
[Auto-clip created: 2025-11-21T14:23:00Z]

# Manual clip creation
crecall --clip "before-refactor"
[Clip created: before-refactor (clip-20251121-142330)]

# Instant restoration
crecall --recall
[Restored to: clip-20251121-142330 (2 minutes ago)]

# Restore specific clip
crecall --recall before-refactor
[Restored to: before-refactor (15 minutes ago)]

# List available clips
crecall --clips list
  clip-20251121-142330  [2 min ago]   Auto-clip
  before-refactor       [15 min ago]  Manual: "before-refactor"
  after-bug-fix         [1 hour ago]  Manual: "after-bug-fix"
```

**Clip Contents** (minimal footprint):
- Session metadata (timestamp, status, version)
- Working directory path
- Git context (branch, commit hash, dirty status)
- Open files list with cursor positions
- Terminal command history (last 20 commands)
- Environment variables (filtered for safety)
- Active todo list state
- Recent memories (last 10 items)
- Docker context
- Total size: ~10-50KB per clip (vs. full session: MBs)

**Recovery Process** (near-instantaneous):
1. Parse clip JSON (~1ms)
2. Restore working directory
3. Restore todo list state
4. Display recent memories
5. Optional: Reopen files in IDE (via plugin)
6. Optional: Restore terminal sessions
7. Total time: <100ms for basic restore, <2s for full IDE integration

---

### Data Flow

```
User Action → CLI/Web UI → Python API → PostgreSQL
                ↓
         Auto-Save Timer → Clip Creation → Local Storage + DB
                ↓
           Crash Occurs → Recovery Prompt → Instant Restore
```

---

### File Structure Evolution

**Current (v0.1.0d-2 (preview))**:
```
~/.recall_memory/
  recall.log              # JSON-lines checkpoints
  state.json              # Active/paused state
  recall_memory.log       # Memory items
  passphrase              # Encryption key
  transcripts/            # Session transcripts
```

**Future (Multi-Tier)**:
```
~/.recall_memory/
  clips/                  # Lightweight restore points
    clip-20251121-142330.json
    before-refactor.json
  state.json
  passphrase
  config.json             # User preferences
  transcripts/
  cache/                  # Temporary data
  backups/                # Daily auto-backups
```

---

## 🔧 Dependencies

- `bash` - Shell interpreter
- `python3` - Future API runtime
- `jq` - JSON processing
- `openssl` - Encryption/decryption

All dependencies auto-installed via APT.

---

## 📝 Preview Build Notice

This is **preview version v0.1.0d-2 (preview)**. Future updates will increment version numbers following semantic versioning.

**Memory features** are under active development and will be the flagship capability of crecall. The tool is designed to ensure you never lose context due to crashes, restarts, or interruptions.

### Theme Toggle (Preview)
The web interface now includes a theme toggle button in the header. Dark mode is the default on first load. The selection is stored in `localStorage` (`crecall-theme`) and applied automatically on future visits. This will later integrate with OS-level preferences and possibly per-session styling.

### Settings Menu (Preview)
Run `crecall --settings` (or `-o`) to adjust:
- Auto-save interval (minutes)
- Clip retention (keep last N clips)
- Theme preference (dark/light) – stored separately from frontend localStorage
- Auto-clip enable flag (future integration)

Configuration stored at: `~/.recall_memory/config.json` and created if missing.

---

## ❓ Questions & Feedback

We're actively shaping crecall's future. Your input matters:

### Memory Feature Priorities
1. **Search Capabilities**: What search features matter most?
   - Keyword/phrase search?
   - Date range filtering?
   - Tag-based queries?
   - Full-text search across all memories?

2. **Organization**: How should memories be organized?
   - Hierarchical categories?
   - Flat tags?
   - Auto-categorization via ML?
   - Custom metadata fields?

3. **Integration**: What tools should crecall integrate with?
   - Git (auto-checkpoint on commit)?
   - IDEs (VS Code, JetBrains)?
   - Project management tools (Jira, Trello)?
   - Note-taking apps (Obsidian, Notion)?

### Architecture & Data
4. **PostgreSQL Migration**: Preserve all CLI-based logs or start fresh?

5. **API Access**: Read-only endpoints initially, or full CRUD from start?

6. **Authentication**: Local-only (no auth) or multi-user with authentication?

7. **Auto-Save Frequency**: 5-minute default good? Should it be configurable?

8. **Crash Recovery**: What information is critical to restore after a crash?
   - Last checkpoint?
   - Active memories?
   - Working directory context?
   - Open files/tabs?

### Developer Experience
9. **Configuration**: What should be configurable via `~/.crecallrc`?

10. **Export Formats**: Besides Markdown/JSON/CSV, what other formats needed?

---

## 📚 Documentation

   • SECURITY_PROTOCOLS.md (hardening roadmap)
   • BRAND_LICENSE_AGREEMENT.md (protective license draft)
- **Installation Guide**: See [INSTALL.md](INSTALL.md)
- **Version History**: See [PATCH_NOTES.md](PATCH_NOTES.md)
- **API Documentation**: Coming soon with Python backend

---

## 🤝 Contributing

Currently in early development. Feedback and feature requests welcome as we build out the memory system and multi-tier architecture.

---

## 📄 License

TBD - Project license to be determined

---

**Built to solve real problems. Designed to never lose your place again.**
# Test change
