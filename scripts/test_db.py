#!/usr/bin/env python3
"""
Test database connection and table creation.
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
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite+aiosqlite:///./test_dogepal.db"
os.environ["DEBUG"] = "True"

# Import SQLAlchemy components
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

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

# Base class for models
Base = declarative_base()

async def create_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main():
    """Main function to test database connection."""
    print("Testing database connection...")
    
    try:
        # Test connection
        async with engine.connect() as conn:
            print("✅ Successfully connected to the database")
        
        # Create tables
        print("Creating tables...")
        await create_tables()
        print("✅ Tables created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
