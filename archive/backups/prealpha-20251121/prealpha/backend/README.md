# crecall Backend

FastAPI backend for crecall session management and memory system.

## Setup

1. Create virtual environment and install dependencies:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. Initialize database:
```bash
python init_db.py
```

4. Run development server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Configuration
│   ├── db/            # Database models
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Business logic
│   └── main.py        # FastAPI app
├── migrations/        # Alembic migrations
├── tests/            # Tests
├── requirements.txt
└── pyproject.toml
```

## Endpoints

### Sessions
- `POST /api/sessions` - Create session
- `GET /api/sessions` - List sessions
- `GET /api/sessions/{id}` - Get session
- `PUT /api/sessions/{id}` - Update session
- `DELETE /api/sessions/{id}` - Delete session
- `GET /api/sessions/{id}/summary` - Get summary

### Clips
- `POST /api/clips` - Create clip
- `GET /api/clips` - List clips
- `GET /api/clips/{id}` - Get clip
- `DELETE /api/clips/{id}` - Delete clip
- `POST /api/clips/prune` - Prune old clips

### Memories
- `POST /api/memories` - Create memory
- `GET /api/memories` - List memories
- `GET /api/memories/{id}` - Get memory
- `PUT /api/memories/{id}` - Update memory
- `DELETE /api/memories/{id}` - Delete memory
- `POST /api/memories/search` - Search memories
