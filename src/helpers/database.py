"""Database connection and session management"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from helpers.config import get_settings

# Get settings
settings = get_settings()

# Create async engine for PostgreSQL with asyncpg driver
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.SQLALCHEMY_ECHO,
    future=True,
    pool_pre_ping=True,
)

# Create session factory - compatible with both old and new SQLAlchemy versions
try:
    from sqlalchemy.ext.asyncio import async_sessionmaker
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
except ImportError:
    from sqlalchemy.orm import sessionmaker as sync_sessionmaker
    AsyncSessionLocal = sync_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

# Base class for ORM models
Base = declarative_base()


async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connection"""
    await engine.dispose()