#!/usr/bin/env python3
"""
Test SQLite database connection and table creation.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey

# Create a base class for our models
Base = declarative_base()

# Define a simple model
class TestModel(Base):
    __tablename__ = 'test_table'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    value = Column(Float)
    metadata_ = Column("metadata", JSON, default={})

async def main():
    # Use an in-memory SQLite database for testing
    DATABASE_URL = "sqlite+aiosqlite:///./test_sqlite.db"
    
    print(f"Connecting to database: {DATABASE_URL}")
    
    # Create async engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Enable SQL echo for debugging
        future=True,
        poolclass=NullPool,
        connect_args={"check_same_thread": False},
    )
    
    # Create tables
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created successfully")
    
    # Create a session factory
    async_session_factory = sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    
    # Add some test data
    print("Adding test data...")
    async with async_session_factory() as session:
        # Add a test record
        test_record = TestModel(
            name="Test Record",
            value=42.0,
            metadata_={"test": "data"}
        )
        session.add(test_record)
        await session.commit()
        
        # Query the test record
        result = await session.execute(
            "SELECT * FROM test_table WHERE name = :name",
            {"name": "Test Record"}
        )
        record = result.first()
        
        if record:
            print(f"✅ Found test record: {record}")
        else:
            print("❌ Test record not found")
    
    # Clean up
    await engine.dispose()
    print("✅ Database test completed successfully!")

if __name__ == "__main__":
    print("Starting SQLite database test...")
    asyncio.run(main())
