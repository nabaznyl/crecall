# Quick Start

Get crecall running in under 5 minutes.

## Docker (Recommended)

```bash
# Pull and run stable image
docker run -d \
  --name crecall \
  -p 8000:8000 \
  -v ~/.recall_memory:/app/data \
  crecall:stable
```

Access the API documentation at [http://localhost:8000/docs](http://localhost:8000/docs)

## From Source

### Prerequisites

- Python 3.11+ 
- Git

### Steps

```bash
# Clone repository
git clone https://github.com/nabaznyl/crecall.git
cd crecall/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your preferred settings

# Initialize database
python init_db.py

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Verify Installation

```bash
# Health check
curl http://localhost:8000/health

# Create a test session
curl -X POST http://localhost:8000/api/v1/sessions \
  -H "Content-Type: application/json" \
  -d '{"external_id": "test-session-001"}'
```

## Next Steps

- [Configuration Guide](CONFIGURATION.md) - Customize your setup
- [Data Model](data_model.md) - Understand sessions, clips, and memories
- [Workflows](workflows.md) - Learn common usage patterns
- [API Reference](api/rest.md) - Explore the full API

## Troubleshooting

**Port 8000 already in use**:
```bash
uvicorn app.main:app --reload --port 8001
```

**Database initialization fails**:
```bash
# Clean slate (development only)
rm -f crecall.db
python init_db.py
```

**Import errors**:
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/path/to/crecall/backend:$PYTHONPATH
```

For more help, see [DEVELOPMENT.md](DEVELOPMENT.md) or [open an issue](https://github.com/nabaznyl/crecall/issues).
