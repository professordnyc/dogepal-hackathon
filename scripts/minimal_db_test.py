#!/usr/bin/env python3
"""
Minimal test script to verify database connection and table creation.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import Column, Integer, String, JSON

# Create a base class for our models
Base = declarative_base()

# Define a simple model
class TestTable(Base):
    __tablename__ = 'test_table'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    data = Column(JSON, default={})

async def main():
    # Use an in-memory SQLite database for testing
    DATABASE_URL = "sqlite+aiosqlite:///./minimal_test.db"
    
    print(f"Connecting to database: {DATABASE_URL}")
    
    # Create async engine
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
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
    
    # Create a session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Test insert
    async with async_session() as session:
        test_record = TestTable(name="test", data={"key": "value"})
        session.add(test_record)
        await session.commit()
        print("✅ Test record inserted")
        
        # Test query
        result = await session.execute("SELECT * FROM test_table")
        records = result.all()
        print(f"✅ Found {len(records)} records")
        for record in records:
            print(f"  - {record}")
    
    await engine.dispose()
    print("✅ Test completed successfully!")

if __name__ == "__main__":
    print("Starting minimal database test...")
    asyncio.run(main())
