"""Pytest configuration and shared fixtures"""

import pytest
import sys
import os
from pathlib import Path
import asyncio

# Mock environment variables for testing
os.environ["JWT_SECRET_KEY"] = "test-secret-key"
os.environ["ENCRYPTION_KEY"] = "test-encryption-key"
os.environ["TESTING"] = "true"

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool
from helpers.database import Base
from main import app
from models.user import User, UserRole
from helpers.password import hash_password


# Test database URL - using SQLite in-memory for tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
test_engine = None


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def init_test_db(event_loop):
    """Initialize test database - runs once per session"""
    global test_engine
    
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield test_engine
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await test_engine.dispose()


@pytest.fixture
async def db_session(init_test_db):
    """Create database session for tests"""
    async with AsyncSession(init_test_db) as session:
        yield session


@pytest.fixture
def anyio_backend():
    """Configure anyio backend for async tests"""
    return "asyncio"


@pytest.fixture
def csrf_client(init_test_db):
    """Create test client with database override (CSRF middleware is bypassed in test mode)"""
    from fastapi.testclient import TestClient
    
    async def override_get_db():
        async with AsyncSession(init_test_db) as session:
            yield session
    
    from helpers.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    client = TestClient(app)
    yield client
    
    app.dependency_overrides.clear()


@pytest.fixture
async def seeded_client(init_test_db):
    """Create test client with seeded data (admin user)"""
    async with AsyncSession(init_test_db) as session:
        # Check if user already exists
        from sqlalchemy import select
        result = await session.execute(select(User).where(User.username == "admin"))
        existing_user = result.scalar()
        
        if not existing_user:
            hashed_password = hash_password("password")
            user = User(
                username="admin",
                email="admin@test.com",
                hashed_password=hashed_password,
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True
            )
            session.add(user)
            await session.commit()
    
    # Create the client
    async def override_get_db():
        async with AsyncSession(init_test_db) as session:
            yield session
    
    from helpers.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    yield client
    
    app.dependency_overrides.clear()


# Marker for different test types
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )