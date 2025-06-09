"""Simple test script to verify basic functionality."""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./dogepal.db"
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False},
)

# Base class for models
Base = declarative_base()

# Simple model
class TestModel(Base):
    __tablename__ = "test_model"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    value = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    metadata_field = Column(JSON, default=dict)

async def test_db():
    """Test database operations."""
    # Create session factory
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with async_session() as session:
        # Create a test record
        test = TestModel(
            name="Test Record",
            value=42.0,
            metadata_field={"test": "data"}
        )
        session.add(test)
        await session.commit()
        
        print("Successfully created test record!")
        
        # Query the record
        result = await session.execute(TestModel.__table__.select())
        record = result.first()
        print(f"Retrieved record: {record}")
        
        await session.close()

if __name__ == "__main__":
    asyncio.run(test_db())
