#!/usr/bin/env python3
"""
Initialize the DOGEPAL database with proper configuration.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Set environment variables
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite+aiosqlite:///./dogepal_fixed.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["BACKEND_CORS_ORIGINS"] = '["*"]'

# Import SQLAlchemy components
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Import models
from app.models.spending import Base

# Create async engine with SQLite
engine = create_async_engine(
    os.environ["SQLALCHEMY_DATABASE_URI"],
    echo=True,  # Enable SQL echo for debugging
    future=True,
    poolclass=NullPool,
    connect_args={"check_same_thread": False},
)

# Create async session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=True,
    autocommit=False,
)

async def create_tables():
    """Create all database tables."""
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully")

async def main():
    """Main function to initialize the database."""
    try:
        await create_tables()
        print("✅ Database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        await engine.dispose()
        print("✅ Database connection closed.")

if __name__ == "__main__":
    print("Starting DOGEPAL database initialization...")
    asyncio.run(main())
    print("Initialization process completed.")
