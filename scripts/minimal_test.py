#!/usr/bin/env python3
"""
Minimal test script to isolate database creation issues.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from datetime import datetime

# Define a minimal model
Base = declarative_base()

class Spending(Base):
    __tablename__ = "spending"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True)
    vendor = Column(String, index=True)
    date = Column(String)  # Storing as string for simplicity
    metadata_ = Column("metadata", JSON, default={})

class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    spending_id = Column(Integer, ForeignKey("spending.id"), index=True)
    recommendation_type = Column(String, index=True)
    title = Column(String)
    description = Column(String)
    potential_savings = Column(Float)
    status = Column(String, default="pending")
    metadata_ = Column("metadata", JSON, default={})

async def main():
    # Create an in-memory SQLite database for testing
    DATABASE_URL = "sqlite+aiosqlite:///./test_minimal.db"
    
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
    
    # Add sample data
    print("Adding sample data...")
    async with sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)() as session:
        # Add a spending record
        spending = Spending(
            transaction_id="TEST123",
            user_id="test_user",
            amount=1000.0,
            category="software",
            vendor="Test Vendor",
            date="2025-06-09",
            metadata_={"test": "data"}
        )
        session.add(spending)
        await session.commit()
        
        # Add a recommendation
        recommendation = Recommendation(
            spending_id=spending.id,
            recommendation_type="cost_saving",
            title="Test Recommendation",
            description="This is a test recommendation",
            potential_savings=100.0,
            status="pending",
            metadata_={"test": "data"}
        )
        session.add(recommendation)
        await session.commit()
        
        print("✅ Sample data added successfully")
    
    await engine.dispose()
    print("✅ Test completed successfully!")

if __name__ == "__main__":
    print("Starting minimal database test...")
    asyncio.run(main())
