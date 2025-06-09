#!/usr/bin/env python3
"""
Test database initialization with a fresh approach.
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
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite+aiosqlite:///dogepal_test.db"
os.environ["DEBUG"] = "True"

# Import SQLAlchemy components
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

# Import models to ensure they are registered with SQLAlchemy
from app.models.spending import Base, Spending, Recommendation

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

async def add_sample_data():
    """Add sample data to the database."""
    print("Adding sample data...")
    async with async_session_factory() as session:
        # Create sample spending
        spending = Spending(
            transaction_id="TEST123",
            user_id="test_user",
            user_type="solopreneur",
            department="IT",
            project_name="Test Project",
            borough="Manhattan",
            date="2025-06-09",
            vendor="Test Vendor",
            category="software",
            amount=1000.0,
            justification="Test transaction",
            approval_status="approved",
            metadata_={"test": "data"}
        )
        session.add(spending)
        await session.commit()
        
        # Create sample recommendation
        recommendation = Recommendation(
            spending_id=spending.id,
            recommendation_type="cost_saving",
            title="Test Recommendation",
            description="This is a test recommendation",
            potential_savings=100.0,
            implementation_effort="low",
            status="pending",
            metadata_={"test": "data"}
        )
        session.add(recommendation)
        await session.commit()
        
        print("✅ Sample data added successfully")

async def main():
    """Main function to test database initialization."""
    try:
        await create_tables()
        await add_sample_data()
        print("✅ Database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    print("Starting database test...")
    asyncio.run(main())
    print("Test completed.")
