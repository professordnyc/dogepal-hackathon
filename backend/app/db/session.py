from contextlib import asynccontextmanager
from typing import AsyncGenerator
import os

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

# Create async engine with SQLite-specific configuration
engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=True,  # Always enable SQL echo for debugging
    future=True,
    poolclass=NullPool,  # Required for SQLite with asyncio
    connect_args={
        "check_same_thread": False,  # SQLite-specific for async
    },
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevent attribute access after commit
    autoflush=True,  # Enable auto-flush for session
    autocommit=False,
)

# Base class for all models
Base = declarative_base()

# Dependency to get DB session
@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields DB sessions.
    Handles session lifecycle including commit/rollback and cleanup.
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()

# For backward compatibility and easy imports
async_session = async_session_factory

# Helper function to get a new async session
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get a new async database session.
    
    Example:
        async with get_async_session() as session:
            result = await session.execute(select(MyModel))
            items = result.scalars().all()
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize database tables
async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

# For testing and development
def create_tables():
    """Synchronous function to create all tables (for testing)."""
    import asyncio
    asyncio.run(init_db())

# For testing and development
def drop_tables():
    """Synchronous function to drop all tables (for testing)."""
    async def _drop_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    import asyncio
    asyncio.run(_drop_tables())
