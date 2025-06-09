#!/usr/bin/env python3
"""
Initialize the database with sample data.
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
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite+aiosqlite:///./dogepal.db"
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

# Import models to ensure they are registered with SQLAlchemy
from app.models.spending import Spending, Recommendation

# Import the init_db function
from app.db.init_db import init_db

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def main() -> None:
    print("Initializing database...")
    
    try:
        # Create tables first
        print("Creating database tables...")
        await create_tables()
        
        # Initialize with sample data
        print("Adding sample data...")
        async with async_session_factory() as session:
            await init_db(session)
            await session.commit()
            print("✅ Database initialized successfully!")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        if 'session' in locals():
            await session.rollback()
        raise
    finally:
        if 'engine' in locals():
            await engine.dispose()
            print("✅ Database connection closed.")

if __name__ == "__main__":
    print("Starting database initialization...")
    asyncio.run(main())
    print("Done.")
