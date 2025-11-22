"""
Test configuration and fixtures
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.models import Base
from app.db.session import get_db

# Test database (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class AsyncSessionCompat:
    """Minimal async-compatible wrapper around a synchronous SQLAlchemy Session.

    Provides async def methods used by service layer so legacy sync tests can
    interact with code expecting an AsyncSession without rewriting tests.
    """
    def __init__(self, sync_session):
        self._sync = sync_session

    # Attribute passthrough for typical ORM usage (add, delete, etc.)
    def __getattr__(self, item):
        return getattr(self._sync, item)

    async def execute(self, *args, **kwargs):
        return self._sync.execute(*args, **kwargs)

    async def scalar(self, *args, **kwargs):
        return self._sync.scalar(*args, **kwargs)

    async def commit(self):
        self._sync.commit()

    async def refresh(self, instance):
        self._sync.refresh(instance)

    async def close(self):
        self._sync.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield AsyncSessionCompat(session)
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Test client with database dependency override

    Sets CRECALL_TEST_MODE so lifespan skips background scheduler & signals.
    """
    import os
    os.environ["CRECALL_TEST_MODE"] = "1"

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_session_data():
    """Sample session data for tests"""
    return {
        "session_id": "test-session-123",
        "status": "active",
        "theme_preference": "dark",
    }


@pytest.fixture
def sample_clip_data():
    """Sample clip data for tests"""
    return {
        "name": "test-clip",
        "is_auto": False,
        "content": {"code": "print('hello')", "language": "python"},
    }


@pytest.fixture
def sample_memory_data():
    """Sample memory data for tests"""
    return {
        "content": "This is a test memory",
        "tags": ["test", "example"],
        "category": "note",
        "importance": 1,
    }
