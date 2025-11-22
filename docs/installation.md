# Installation Guide

**Version:** v0.1.0d-7 (preview)  
**Updated:** 2025-11-21

---

## Prerequisites

- Python 3.10+
- Git
- Optional: Docker, PostgreSQL

---

## Installation from Source (Recommended)

### 1. Clone Repository
```bash
git clone https://github.com/crecall/crecall.git
cd crecall
```

### 2. Backend Setup
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

Access API docs: http://localhost:8000/docs

### 3. Frontend Setup (Optional)
```bash
cd frontend
npm install
npm run dev
# Access at http://localhost:5173
```

### 4. VS Code Extension (Optional)
```bash
cd vscode-extension
npm install
npm run compile
# Package: npx vsce package
# Install via Extensions > Install from VSIX
```

---

## Docker Installation

### Using Docker Compose
```bash
# Stable release
docker-compose up crecall-stable

# Nightly build
docker-compose --profile nightly up crecall-nightly

# Development with hot-reload
docker-compose --profile dev up crecall-dev
```

### Standalone Docker
```bash
# Stable
docker run -p 8000:8000 -v ~/.recall_memory:/root/.recall_memory crecall:stable

# Nightly
docker run -p 8000:8000 -v ~/.recall_memory:/root/.recall_memory crecall:nightly
```

---

## Database Configuration

### SQLite (Default)
No additional setup required. Database created automatically at `./crecall.db`.

### PostgreSQL (Production)

1. **Create database**:
   ```bash
   createdb crecall
   ```

2. **Configure connection**:
   ```bash
   export POSTGRES_URL=postgresql+asyncpg://user:pass@localhost:5432/crecall
   # Or add to backend/.env
   ```

3. **Run migrations**:
   ```bash
   cd backend
   source venv/bin/activate
   alembic upgrade head
   ```

4. **Migrate existing SQLite data** (optional):
   ```bash
   python scripts/migrate_to_postgres.py \
       --sqlite sqlite:///crecall.db \
       --postgres postgresql+psycopg2://user:pass@localhost:5432/crecall
   ```

---

## Configuration

### Environment Variables

Edit `backend/.env`:

```env
# Application
APP_NAME=crecall
DEBUG=True  # Set False in production

# Database
DATABASE_URL=sqlite+aiosqlite:///./crecall.db
# For PostgreSQL:
# POSTGRES_URL=postgresql+asyncpg://user:pass@localhost:5432/crecall

# Centralized config (Phase 1)
ENVIRONMENT=local
LOG_LEVEL=INFO
BACKUP_DIR=backups
DB_URL=sqlite+aiosqlite:///./crecall.db

# Security
SECRET_KEY=change-this-in-production
MAX_REQUESTS_PER_MINUTE=120

# Clip system
AUTO_CLIP_INTERVAL=300  # 5 minutes
MAX_CLIPS=100
CLIP_RETENTION_DAYS=7

# Memory system
DEFAULT_MEMORY_LIMIT=20
```

See [CONFIGURATION.md](CONFIGURATION.md) for complete reference.

---

## Verification

### Backend Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status": "healthy"}
```

### Run Tests
```bash
cd backend
CRECALL_TEST_MODE=1 pytest -v
# Expected: 49 passed
```

### Performance Benchmark (Future)
```bash
python scripts/benchmark.py
```

---

## Troubleshooting

### Backend won't start
- Check `.env` exists and `DB_URL` is set
- Verify Python 3.10+ with `python3 --version`
- Run `alembic upgrade head` to apply migrations

### Frontend connection errors
- Verify backend running on port 8000
- Check `frontend/.env` has correct `VITE_API_URL`

### Database migration issues
- Reset: `alembic downgrade base && alembic upgrade head`
- Check `alembic_version` table exists

### Test failures
- Ensure `CRECALL_TEST_MODE=1` set
- Check no conflicting processes on port 8000
- Clear `.pytest_cache` and retry

---

## Uninstall

### Remove application
```bash
# Stop services
docker-compose down  # If using Docker

# Remove data (interactive confirmation)
crecall data clear

# Or manually:
rm -rf ~/.recall_memory
rm -rf /path/to/crecall
```

---

## Next Steps

- [Configuration](CONFIGURATION.md) - Customize settings
- [Workflows](workflows.md) - Learn core operations
- [Development](DEVELOPMENT.md) - Contribute to project

---

**Installation complete!** Start with:
```bash
crecall --help
```
