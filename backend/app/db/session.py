import logging
import asyncio
import os
from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncEngine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from contextlib import asynccontextmanager

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


# Global engine and session factory
_engine: Optional[AsyncEngine] = None
_async_session_factory = None

# Base class for all models
Base = declarative_base()

# Lock for thread-safe initialization
_init_lock = asyncio.Lock()


def get_engine() -> AsyncEngine:
    """Get the database engine, initializing it if necessary."""
    global _engine
    if _engine is None:
        raise RuntimeError("Database engine not initialized. Call init_db() first.")
    return _engine


def get_async_session_factory():
    """Get the async session factory, initializing it if necessary."""
    global _async_session_factory
    if _async_session_factory is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _async_session_factory


async def init_db() -> None:
    """
    Initialize the database connection and create tables if they don't exist.
    This function is idempotent and thread-safe.
    """
    global _engine, _async_session_factory
    
    # Fast path: if already initialized
    if _engine is not None:
        return
        
    # Use lock for thread safety
    async with _init_lock:
        # Check again in case another coroutine initialized while we were waiting
        if _engine is not None:
            return
            
        logger.info("Initializing database engine...")
        
        # Create async engine with SQLite-specific configuration
        _engine = create_async_engine(
            settings.SQLALCHEMY_DATABASE_URI,
            echo=settings.DEBUG,  # Enable SQL echo in debug mode
            future=True,
            poolclass=NullPool,  # Required for SQLite with asyncio
            connect_args={"check_same_thread": False},  # SQLite-specific for async
        )
        
        # Create async session factory
        _async_session_factory = sessionmaker(
            _engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
        )
        
        logger.info("Database engine initialized")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields DB sessions.
    
    Yields:
        AsyncSession: Database session
        
    Raises:
        RuntimeError: If database is not initialized
    """
    await init_db()  # Ensure DB is initialized
    
    # Get a new session from the factory
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.exception("Database session error")
            raise
        finally:
            await session.close()


def get_async_session() -> AsyncSession:
    """
    Get an async database session.
    
    Returns:
        AsyncSession: A new database session
        
    Raises:
        RuntimeError: If database is not initialized
    """
    session_factory = get_async_session_factory()
    return session_factory()


async def create_tables() -> None:
    """
    Create all database tables.
    
    This is idempotent and safe to call multiple times.
    """
    from sqlalchemy import inspect
    from sqlalchemy.schema import CreateTable
    
    # Ensure the database is initialized
    await init_db()
    
    # Import models to ensure all tables are registered with SQLAlchemy
    import backend.app.models.spending  # noqa: F401
    
    engine = get_engine()
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        # Check if tables already exist
        inspector = inspect(engine.sync_engine)
        existing_tables = inspector.get_table_names()
        
        # Create tables that don't exist
        for table in Base.metadata.sorted_tables:
            if table.name not in existing_tables:
                logger.info(f"Creating table: {table.name}")
                await conn.run_sync(lambda conn, t=table: t.create(conn))
    
    logger.info("All tables created successfully")


async def drop_tables() -> None:
    """
    Drop all database tables.
    
    WARNING: This will delete all data in the database.
    """
    # Ensure the database is initialized
    await init_db()
    
    # Import models to ensure all tables are registered with SQLAlchemy
    import backend.app.models.spending  # noqa: F401
    
    engine = get_engine()
    
    # Drop all tables
    async with engine.begin() as conn:
        # Drop all tables in reverse order of dependency
        for table in reversed(Base.metadata.sorted_tables):
            logger.info(f"Dropping table: {table.name}")
            await conn.run_sync(lambda conn, t=table: t.drop(conn, checkfirst=True))
    
    logger.info("All tables dropped successfully")


# Initialize the database when this module is imported if environment variable is set
# This is disabled by default to prevent issues with event loops
if os.getenv("INIT_DB_ON_STARTUP", "false").lower() == "true":
    # Don't use asyncio.run() here as it can cause event loop issues
    # Instead, we'll let the application handle the initialization
    pass
