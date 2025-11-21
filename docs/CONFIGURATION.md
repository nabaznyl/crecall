# Configuration Settings Schema

Complete reference for crecall configuration options.

---

## Backend Configuration

### Environment Variables (.env)

#### Application
```env
APP_NAME=crecall
DEBUG=True  # Set to False in production
```

#### Database
```env
# SQLite (default, single-user)
DATABASE_URL=sqlite+aiosqlite:///./crecall.db

# PostgreSQL (team/production)
POSTGRES_URL=postgresql+asyncpg://user:password@localhost:5432/crecall
```

#### Security
```env
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### CORS
```env
CORS_ORIGINS=["http://localhost:5173","http://localhost:3000"]
```

#### Clip System
```env
AUTO_CLIP_INTERVAL=300        # Seconds (5 minutes default)
MAX_CLIPS=100                 # Keep last N clips
CLIP_RETENTION_DAYS=7         # Delete clips older than N days
```

#### Memory System
```env
DEFAULT_MEMORY_LIMIT=20       # Default number to return in list
```

---

## User Preferences (~/.crecallrc)

**Status:** Planned (not yet implemented)

```yaml
# Auto-save settings
auto_save:
  enabled: true
  interval: 300  # seconds
  on_git_commit: true
  on_file_save: false

# Clip settings
clips:
  max_count: 100
  retention_days: 7
  naming: "sequential"  # sequential | timestamp | custom
  
# Memory settings
memory:
  default_limit: 20
  auto_categorize: false
  search_mode: "full-text"  # keyword | full-text | semantic | all
  
# Crash recovery
recovery:
  auto_restore: true
  prompt_on_start: true
  golden_backup: true
  
# UI preferences
ui:
  theme: "dark"  # light | dark | auto
  sidebar_position: "left"  # left | right
  
# Git integration
git:
  auto_clip_on_commit: true
  auto_clip_on_branch: true
  link_memories_to_commits: true
```

---

## Clip Content Structure

### Minimal Clip (Auto-generated)
```json
{
  "timestamp": "2025-11-21T14:23:00Z",
  "session_id": "session-xyz",
  "working_directory": "/home/user/project",
  "git": {
    "branch": "main",
    "commit": "abc123def456",
    "dirty": false
  },
  "files": [],  # Empty for minimal footprint
  "terminal": {
    "history": []  # Last 5 commands
  },
  "memories": []  # Last 5 memories
}
```

### Standard Clip
```json
{
  "timestamp": "2025-11-21T14:23:00Z",
  "session_id": "session-xyz",
  "working_directory": "/home/user/project",
  "git": {
    "branch": "main",
    "commit": "abc123def456",
    "dirty": false
  },
  "files": [
    {
      "path": "src/main.py",
      "line": 42,
      "column": 10
    }
  ],
  "terminal": {
    "history": ["git commit", "pytest", "npm run build"]
  },
  "env": {
    "NODE_ENV": "development",
    "PYTHON_ENV": ".venv"
  },
  "docker": {
    "context": "default",
    "containers": []
  },
  "memories": [
    {
      "content": "Fixed bug in authentication",
      "timestamp": "2025-11-21T14:20:00Z"
    }
  ]
}
```

### Complete Clip (Maximum detail)
```json
{
  "timestamp": "2025-11-21T14:23:00Z",
  "session_id": "session-xyz",
  "working_directory": "/home/user/project",
  "git": {
    "branch": "main",
    "commit": "abc123def456",
    "dirty": true,
    "staged_files": ["src/main.py"],
    "modified_files": ["README.md"]
  },
  "files": [
    {
      "path": "src/main.py",
      "line": 42,
      "column": 10,
      "selection": null
    },
    {
      "path": "tests/test_auth.py",
      "line": 15,
      "column": 1,
      "selection": {"start": {"line": 15, "col": 1}, "end": {"line": 20, "col": 30}}
    }
  ],
  "terminal": {
    "history": ["git commit -m 'fix'", "pytest", "npm run build"],
    "cwd": "/home/user/project",
    "scrollback": 50
  },
  "env": {
    "NODE_ENV": "development",
    "PYTHON_ENV": ".venv",
    "PATH": "/usr/local/bin:/usr/bin"
  },
  "docker": {
    "context": "default",
    "containers": [
      {"name": "postgres", "status": "running"},
      {"name": "redis", "status": "stopped"}
    ]
  },
  "memories": [
    {
      "id": 123,
      "content": "Fixed bug in authentication",
      "timestamp": "2025-11-21T14:20:00Z",
      "tags": ["bug", "auth"]
    }
  ],
  "todos": [],  # AI chat todos (not user todos)
  "custom": {}  # User-defined fields
}
```

---

## Settings Priorities

1. **Environment variables** (highest priority)
2. **User config** (`~/.crecallrc`)
3. **Project config** (`.crecall/config`)
4. **Defaults** (lowest priority)

---

## Configurable vs Fixed

### User-Configurable ✓
- Auto-save interval
- Max clips to keep
- Clip retention days
- Memory default limit
- Search mode
- UI theme
- Git integration options

### Fixed (System) ✗
- Database schema
- API endpoints
- Encryption algorithm
- Core security settings

---

## Example Usage

### Change auto-save interval to 10 minutes
```yaml
# ~/.crecallrc
auto_save:
  interval: 600
```

### Disable auto-clip on git commit
```yaml
# ~/.crecallrc
git:
  auto_clip_on_commit: false
```

### Use PostgreSQL instead of SQLite
```env
# backend/.env
POSTGRES_URL=postgresql+asyncpg://user:pass@localhost:5432/crecall
DATABASE_URL=  # Clear SQLite URL
```

---

This schema will be implemented as features are developed.
