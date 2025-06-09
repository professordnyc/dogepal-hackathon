"""
Reset and initialize the database with the correct schema.
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
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

# Import models to ensure they are registered with SQLAlchemy
from app.models.spending import Base, Spending, Recommendation

# Create async engine with SQLite
engine = create_async_engine(
    os.environ["SQLALCHEMY_DATABASE_URI"],
    echo=True,
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

async def drop_tables():
    """Drop all tables in the database."""
    async with engine.begin() as conn:
        # Drop all tables
        await conn.run_sync(Base.metadata.drop_all)
        await conn.commit()

async def create_tables():
    """Create all tables in the database."""
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

async def main():
    """Main function to reset and initialize the database."""
    print("🚀 Starting database reset...")
    
    try:
        # Drop all tables
        print("🗑️  Dropping existing tables...")
        await drop_tables()
        
        # Create all tables
        print("🔄 Creating new tables...")
        await create_tables()
        
        # Create a session to insert sample data
        print("📝 Inserting sample data...")
        async with async_session_factory() as session:
            # Add sample spending
            spending = Spending(
                transaction_id="TEST123",
                user_id="test_user",
                user_type="admin",
                department="Technology",
                project_name="Test Project",
                borough="Manhattan",
                spending_date="2025-06-09",
                vendor="Test Vendor",
                category="software",
                amount=1000.0,
                justification="Test transaction",
                approval_status="approved"
            )
            session.add(spending)
            await session.commit()
            
            # Add sample recommendation
            recommendation = Recommendation(
                transaction_id=spending.transaction_id,
                recommendation_type="cost_saving",
                title="Test Recommendation",
                description="This is a test recommendation",
                potential_savings=100.0,
                confidence_score=0.9,
                priority="high",
                explanation="This is a test explanation",
                status="pending"
            )
            session.add(recommendation)
            await session.commit()
            
        print("✅ Database reset and initialized successfully!")
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
