# crecall Pre-Alpha Release
**Version:** 0.1.0-prealpha  
**Build Date:** 2025-11-21  
**Bundle:** crecall-prealpha-20251121.tar.gz (158 KB)

## Overview
First pre-alpha source release of crecall - contextual recall and memory management system for development workflows.

## What's Included
- **Backend** (FastAPI async service)
  - Session, clip, and memory management APIs
  - PostgreSQL/SQLite support with Alembic migrations
  - Retention policies with auto-pruning
  - Integrity verification (HMAC signing)
  - Export/import with encryption (JWE)
  - Remote sync (SSH/SCP/SFTP)
  - Branch safety & rogue branch detection
  - WebSocket real-time updates
  - Metrics endpoints (JSON + Prometheus)
  - Rate limiting with dynamic overrides
  - Clip restoration endpoint
  
- **Frontend** (React/Vite)
  - Session browser with search
  - Memory timeline visualization
  - Dark theme
  - Real-time WebSocket integration

- **VS Code Extension**
  - Auto-clip creation on significant events
  - Memory capture commands
  - Session management from status bar
  - Quick restore from clips

## Installation

### From Source Tarball
```bash
tar xzf crecall-prealpha-20251121.tar.gz
cd prealpha

# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # Edit as needed
alembic upgrade head
uvicorn app.main:app --reload

# Frontend setup (separate terminal)
cd frontend
npm install
npm run dev

# VS Code extension
cd vscode-extension
npm install
npm run compile
# Install via Extensions: Install from VSIX (after packaging with vsce)
```

## Configuration
- **Backend:** Edit `backend/.env` for database, Redis, security settings
- **Frontend:** Edit `frontend/.env` for API URL
- **Retention:** Default 100 clips per session; configure via `/api/clips/retention/config`

## Known Limitations
- OpenAPI schema export requires running server (dependencies not bundled)
- Docker images not included (build from source)
- PostgreSQL optional; SQLite default
- Redis optional (in-memory fallback)
- Semantic search requires optional dependencies (sentence-transformers, FAISS)

## Next Steps
- Install dependencies and start services
- Create first session via CLI: `crecall session create "Initial Session"`
- Open frontend at http://localhost:5173
- Install VS Code extension for integrated workflow

## Support
See README.md and INSTALL.md in bundle for detailed setup instructions.

## Security Notes
- Change default SECRET_KEY in production
- Review rate limit settings in .env
- Enable HTTPS for production deployments
- Use PostgreSQL for multi-user scenarios
