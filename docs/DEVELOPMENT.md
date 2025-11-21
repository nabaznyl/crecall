# crecall Development Guide

## Quick Start

### Backend (Python FastAPI)

```bash
cd backend
source ../.venv/bin/activate  # or: . ../.venv/bin/activate
cp .env.example .env
python init_db.py
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Visit: http://localhost:8000/docs

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

---

## Project Status

### ✅ Completed

- [x] Git repository initialized
- [x] Documentation (README, PATCH_NOTES, ARCHITECTURE)
- [x] Backend scaffolding (FastAPI + SQLAlchemy)
- [x] Database models (Sessions, Clips, Memories, Checkpoints)
- [x] API endpoints (REST + Pydantic schemas)
- [x] Frontend scaffolding (React + Vite + TypeScript)
- [x] SQLite database initialized

### 🚧 In Progress

- [ ] Frontend UI components
- [ ] API integration in frontend
- [ ] Authentication system
- [ ] Clip creation engine
- [ ] Auto-save scheduler
- [ ] VS Code extension (basic)

### 📋 Planned

- [ ] WebSocket support (real-time updates)
- [ ] PostgreSQL setup for multi-user
- [ ] Crash recovery implementation
- [ ] Git integration hooks
- [ ] Memory search (full-text + semantic)
- [ ] VS Code extension (deep integration)

---

## Architecture Overview

```
crecall/
├── bin/              # CLI (current working version)
├── backend/          # FastAPI + SQLAlchemy + SQLite/PostgreSQL
├── frontend/         # React + TypeScript + Vite
├── database/         # DB schemas and migrations
├── docs/            # Additional documentation
└── scripts/         # Build and deployment scripts
```

### Technology Stack

**Backend:**
- FastAPI (async web framework)
- SQLAlchemy 2.0 (async ORM)
- SQLite (local) / PostgreSQL (team)
- Pydantic v2 (validation)
- APScheduler (auto-save)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- TBD: UI library (shadcn/ui recommended)
- TBD: State management (Zustand or React Query)

**CLI:**
- Current: Bash wrapper (working)
- Future: Python CLI calling API

---

## Development Workflow

1. **Make changes**
2. **Test locally**:
   - Backend: `pytest`
   - Frontend: `npm test`
3. **Commit to Git**:
   ```bash
   git add .
   git commit -m "feat: description"
   git push
   ```

### Branch Strategy

- `main` - Stable releases
- `develop` - Active development
- `feature/*` - New features
- `fix/*` - Bug fixes

---

## Configuration

### Backend (.env)

```env
DATABASE_URL=sqlite+aiosqlite:///./crecall.db
POSTGRES_URL=  # Optional for PostgreSQL
AUTO_CLIP_INTERVAL=300  # 5 minutes
MAX_CLIPS=100
CLIP_RETENTION_DAYS=7
```

### Frontend

TBD - Configuration will be added as UI develops

---

## API Endpoints

See full documentation at: http://localhost:8000/docs

**Key endpoints:**
- `POST /api/sessions` - Create session
- `POST /api/clips` - Create clip
- `POST /api/memories` - Add memory
- `GET /api/clips` - List clips
- `POST /api/clips/prune` - Prune old clips

---

## Testing

### Backend
```bash
cd backend
pytest
```

### Frontend
```bash
cd frontend
npm test
```

---

## Deployment

### Development
- Backend: `uvicorn app.main:app --reload`
- Frontend: `npm run dev`

### Production
- Backend: Systemd service or Docker
- Frontend: `npm run build` → static files
- Database: PostgreSQL recommended

---

## Troubleshooting

### Database locked (SQLite)
- Only one writer at a time
- Consider PostgreSQL for multi-user

### CORS errors
- Check `CORS_ORIGINS` in backend `.env`
- Default allows `localhost:5173` (Vite) and `localhost:3000`

### Import errors
- Ensure virtual environment activated
- `pip install -r requirements.txt`

---

## Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Update documentation
5. Submit for review

---

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)
- [React Docs](https://react.dev/)
- [Vite Docs](https://vitejs.dev/)
