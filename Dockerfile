# Multi-stage Dockerfile for crecall
# Build: docker build -t crecall:latest .
# Run: docker run -p 8000:8000 -v ~/.recall_memory:/root/.recall_memory crecall:latest

ARG BUILD_CHANNEL=stable
ARG PYTHON_VERSION=3.11
ARG NODE_VERSION=20

# ============================================================================
# Stage 1: Backend Builder
# ============================================================================
FROM python:${PYTHON_VERSION}-slim AS backend-builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY backend/pyproject.toml backend/poetry.lock* ./
COPY backend/app ./app
COPY backend/alembic.ini ./
COPY backend/migrations ./migrations

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi || \
    pip install --no-cache-dir fastapi uvicorn sqlalchemy alembic python-multipart

# ============================================================================
# Stage 2: Frontend Builder
# ============================================================================
FROM node:${NODE_VERSION}-alpine AS frontend-builder

WORKDIR /build

# Copy frontend files
COPY frontend/package*.json ./
COPY frontend/tsconfig.json ./
COPY frontend/vite.config.ts ./
COPY frontend/index.html ./
COPY frontend/src ./src
COPY frontend/public ./public

# Install dependencies and build
RUN npm ci --quiet && \
    npm run build

# ============================================================================
# Stage 3: Production Image
# ============================================================================
FROM python:${PYTHON_VERSION}-slim

LABEL org.opencontainers.image.title="crecall"
LABEL org.opencontainers.image.description="Continuous Recall Memory System"
LABEL org.opencontainers.image.source="https://github.com/crecall/crecall"
LABEL org.opencontainers.image.version="stable"
LABEL org.opencontainers.image.licenses="Proprietary"

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    tini \
    && rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 -s /usr/sbin/nologin crecall && \
    mkdir -p /home/crecall/.recall_memory && chown -R 1000:1000 /home/crecall

# Create app user
# user already created above

WORKDIR /app

# Copy backend from builder
COPY --from=backend-builder /build /app/backend
COPY --from=backend-builder /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy frontend from builder
COPY --from=frontend-builder /build/dist /app/frontend/dist

# Copy CLI binaries
COPY bin/crecall /usr/local/bin/crecall
COPY bin/crecall-recover /usr/local/bin/crecall-recover
RUN chmod +x /usr/local/bin/crecall /usr/local/bin/crecall-recover

# Create data directory
RUN mkdir -p /app/tmp && chown -R 1000:1000 /app/tmp

# Expose backend port
EXPOSE 8000

# Health check (API + docs availability)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fs http://localhost:8000/health && curl -fs http://localhost:8000/docs >/dev/null || exit 1

# Default command
USER 1000
ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
