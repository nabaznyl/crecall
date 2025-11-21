# crecall Project Structure

This document outlines the multi-tier architecture for crecall.

## Directory Layout

```
crecall/
├── bin/                    # Current CLI scripts
│   ├── crecall
│   └── crecall-preview
├── debian/                 # Debian packaging
├── frontend/              # React web application
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── services/      # API client services
│   │   ├── types/         # TypeScript type definitions
│   │   └── utils/         # Utility functions
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── backend/               # Python FastAPI application
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core configuration
│   │   ├── db/           # Database models & connection
│   │   ├── services/     # Business logic
│   │   ├── schemas/      # Pydantic schemas
│   │   └── utils/        # Utility functions
│   ├── migrations/       # Alembic migrations
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
├── database/             # Database configuration
│   ├── schemas/          # SQL schemas
│   ├── migrations/       # Manual migrations
│   └── seeds/            # Seed data
├── docs/                 # Additional documentation
├── scripts/              # Build and deployment scripts
├── .gitignore
├── .gitattributes
├── README.md
├── PATCH_NOTES.md
└── INSTALL.md
```

## Technology Stack

### Frontend (React)
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **UI Library**: shadcn/ui (Radix UI + Tailwind CSS)
- **State Management**: Zustand or React Query
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **WebSocket**: native WebSocket or Socket.io-client

### Backend (Python)
- **Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose)
- **WebSocket**: FastAPI WebSockets
- **Task Queue**: APScheduler (for auto-save)
- **Testing**: pytest

### Database
- **Primary**: PostgreSQL 14+ (team/production)
- **Local**: SQLite 3 (single-user mode)
- **Full-Text Search**: PostgreSQL built-in FTS
- **Connection Pool**: asyncpg (PostgreSQL), aiosqlite (SQLite)

### Development Tools
- **API Documentation**: OpenAPI/Swagger (auto-generated)
- **Linting**: ESLint (frontend), Ruff (backend)
- **Formatting**: Prettier (frontend), Black (backend)
- **Type Checking**: TypeScript, mypy

## Development Workflow

1. **CLI (current)**: Bash script in `bin/crecall`
2. **Backend API**: FastAPI service on port 8000
3. **Frontend**: React dev server on port 5173
4. **Database**: PostgreSQL on port 5432 (or SQLite file)

## Deployment Strategy

- **CLI**: Continues to work standalone via Debian package
- **Backend**: Systemd service or Docker container
- **Frontend**: Static build served by nginx or integrated into backend
- **Database**: PostgreSQL service or SQLite file in `~/.recall_memory/`
