# crecall Installation Guide

## Pre-Alpha v0.1.0 Installation

### Requirements
- Python 3.10+
- Node.js 18+ (for frontend)
- Git (for version control features)
- Optional: Docker, PostgreSQL, Redis

### Installation from Source

1. **Extract release bundle:**
   ```bash
   tar xzf crecall-prealpha-20251121.tar.gz
   cd prealpha
   ```

2. **Backend setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Configure environment
   cp .env.example .env
   # Edit .env as needed (defaults work for SQLite)
   
   # Initialize database
   alembic upgrade head
   
   # Start backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **Frontend setup** (separate terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   # Access at http://localhost:5173
   ```

4. **VS Code Extension** (optional):
   ```bash
   cd vscode-extension
   npm install
   npm run compile
   # Package: npx vsce package
   # Install via Extensions > Install from VSIX
   ```

### Quick Start (CLI)

```bash
# Create session
crecall session create "Initial session"

# Add memory
crecall memory add "Important note" --category Development

# Create clip
crecall clip create "Checkpoint 1"

# Export data
crecall export --output backup.tar.gz
```

---

## Legacy Package Installation (Deprecated)

**Note:** The following instructions are for the legacy v0.1.0a APT package. Use source installation above for pre-alpha features.

### 1. Repository Configuration (If Available)

The local repository is located at:
```
~/repo/crecall/
```

APT source configured in:
```
/etc/apt/sources.list.d/crecall-local.list
```

### 2. Install Package

```bash
sudo apt update
sudo apt install crecall
```

### 3. Verify Installation

```bash
which crecall           # Should show /usr/bin/crecall
crecall version         # Should show 0.1.0a
crecall help            # Show all commands
```

### 4. First Run

```bash
# Create initial checkpoint
crecall save "Initial checkpoint"

# View summary
crecall summary

# Add memory item
crecall memory add "Installation completed"
```

## Configuration

### Environment Variables (backend/.env)

```bash
# Application
APP_NAME=crecall
DEBUG=True  # Set False in production

# Database
DATABASE_URL=sqlite+aiosqlite:///./crecall.db
# For PostgreSQL:
# POSTGRES_URL=postgresql+asyncpg://user:pass@localhost:5432/crecall

# Security
SECRET_KEY=your-secret-key-change-in-production
MAX_REQUESTS_PER_MINUTE=120

# Optional: Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Optional: Remote sync
REMOTE_SYNC_ENABLED=false
```

### Frontend Configuration (frontend/.env)

```bash
VITE_API_URL=http://localhost:8000/api
```

---

## PostgreSQL Setup (Optional)

For production or multi-user scenarios:

```bash
# Create database
createdb crecall

# Configure connection
export POSTGRES_URL=postgresql+asyncpg://user:pass@localhost:5432/crecall

# Run migrations
cd backend
source venv/bin/activate
alembic upgrade head

# Migrate existing SQLite data (optional)
python scripts/migrate_to_postgres.py \
    --sqlite sqlite:///crecall.db \
    --postgres postgresql+psycopg2://user:pass@localhost:5432/crecall
```

---

## Docker Installation (Alternative)

```bash
# Build images
./scripts/docker_build_all.sh

# Run with docker-compose
docker-compose up -d

# Access:
# - Backend: http://localhost:8000
# - Frontend: http://localhost:5173
# - API Docs: http://localhost:8000/docs
```

---

## Verification

```bash
# Check backend
curl http://localhost:8000/api/metrics

# Check frontend
open http://localhost:5173

# Run tests
cd backend
pytest -v

# Benchmark
python scripts/benchmark.py
```

---

## Troubleshooting

### Backend won't start
- Check `.env` exists and DATABASE_URL is set
- Verify Python 3.10+ with `python3 --version`
- Run `alembic upgrade head` to ensure migrations applied

### Frontend connection errors
- Verify backend is running on port 8000
- Check `frontend/.env` has correct VITE_API_URL

### Database migration issues
- Reset: `alembic downgrade base && alembic upgrade head`
- Check `alembic_version` table exists in database

---

## Legacy Package Notes

The legacy APT package (v0.1.0a) is superseded by the pre-alpha release.

The legacy APT package (v0.1.0a) is superseded by the pre-alpha release.

### Legacy Commands (v0.1.0a)

```bash
# Install from local repo (if available)
sudo apt update
sudo apt install crecall

# Verify
which crecall
crecall version

# First run
crecall save "Initial checkpoint"
crecall summary
```

## Migration from Legacy Versions

The package automatically migrates data from:
- `~/.chat_recall/` (original location)
- `~/.crecall/` (previous test location)

Data is migrated to `~/.recall_chat/` on first run.

## Encryption

- Uses AES-256-CBC with PBKDF2
- Auto-generated passphrase: `~/.recall_chat/passphrase`
- Passphrase is created on first encrypted operation
- Keep passphrase file secure (chmod 600)

## Uninstall

```bash
sudo apt remove crecall
```

To remove all data:
```bash
crecall data clear      # Interactive confirmation
# OR manually:
rm -rf ~/.recall_chat
```

## Rebuild Package

If modifications are needed:

```bash
cd ~/crecall
# Edit files in bin/ or debian/
dpkg-buildpackage -us -uc
cp ../crecall_*.deb ~/repo/crecall/
cd ~/repo/crecall
dpkg-scanpackages . /dev/null > Packages
sudo apt update
sudo apt install --reinstall crecall
```

## Testing

Run test suite with preview script:
```bash
crecall-preview
```

## Support

- Homepage: https://example.com/crecall
- Maintainer: Local Maintainer <maintainer@example.com>
- Version: 0.1.0a (preview build)
