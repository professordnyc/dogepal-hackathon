#!/usr/bin/env python3
"""
Direct database initialization script using SQLAlchemy Core.
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import date, datetime
import uuid

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import SQLAlchemy components
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import MetaData, Table, Column, String, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.sql import text

# Database URL
DATABASE_URL = "sqlite+aiosqlite:///./dogepal.db"

# Create async engine with SQLite
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Enable SQL echo for debugging
    future=True,
    connect_args={"check_same_thread": False},
)

# Create metadata object
metadata = MetaData()

# Define tables
spending_table = Table(
    "spending",
    metadata,
    Column("transaction_id", String, primary_key=True, index=True),
    Column("user_id", String, index=True),
    Column("user_type", String, index=True),
    Column("department", String, index=True),
    Column("project_name", String, index=True),
    Column("borough", String, index=True),
    Column("date", Date, index=True),
    Column("vendor", String, index=True),
    Column("category", String, index=True),
    Column("amount", Float),
    Column("justification", String),
    Column("approval_status", String, index=True),
    Column("metadata", JSON, default={}),
    Column("created_at", DateTime),
    Column("updated_at", DateTime),
)

recommendations_table = Table(
    "recommendations",
    metadata,
    Column("id", String, primary_key=True, index=True),
    Column("transaction_id", String, ForeignKey("spending.transaction_id")),
    Column("type", String, index=True),
    Column("title", String),
    Column("description", String),
    Column("potential_savings", Float),
    Column("confidence_score", Float),
    Column("priority", String),
    Column("explanation", String),
    Column("metadata", JSON, default={}),
    Column("status", String, index=True),
    Column("created_at", DateTime),
    Column("updated_at", DateTime),
)

# Sample data
sample_spending = [
    {
        "transaction_id": "TXN20230601001",
        "user_id": "user_123",
        "user_type": "solopreneur",
        "department": "Technology",
        "project_name": "AI Skills Initiative",
        "borough": "Manhattan",
        "date": date(2023, 6, 1),
        "vendor": "DataSense",
        "category": "software",
        "amount": 1200.00,
        "justification": "Annual subscription renewal",
        "approval_status": "approved",
        "metadata": {"source": "manual_entry", "reviewed_by": "admin@example.com"},
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "transaction_id": "TXN20230602001",
        "user_id": "user_456",
        "user_type": "startup",
        "department": "Operations",
        "project_name": "Smart Waste Pilot",
        "borough": "Brooklyn",
        "date": date(2023, 6, 2),
        "vendor": "WasteTech",
        "category": "hardware",
        "amount": 3500.00,
        "justification": "Purchase of smart sensors for waste management",
        "approval_status": "approved",
        "metadata": {"source": "api_import", "po_number": "PO-2023-456"},
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
]

sample_recommendations = [
    {
        "id": "REC001",
        "transaction_id": "TXN20230601001",
        "type": "vendor_consolidation",
        "title": "Consolidate Software Subscriptions",
        "description": "Consider consolidating with DataSense for additional 15% discount on annual plans.",
        "potential_savings": 180.00,
        "confidence_score": 0.85,
        "priority": "high",
        "explanation": "Based on analysis of current subscriptions and vendor pricing.",
        "metadata": {"vendor_contact": "sales@datasense.com"},
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    {
        "id": "REC002",
        "transaction_id": "TXN20230602001",
        "type": "bulk_purchase",
        "title": "Bulk Purchase Opportunity",
        "description": "Consider bulk purchase of sensors for additional 20% discount on orders over $10,000.",
        "potential_savings": 700.00,
        "confidence_score": 0.75,
        "priority": "medium",
        "explanation": "Based on vendor pricing tiers and project requirements.",
        "metadata": {"min_order": 10000, "valid_until": "2023-12-31"},
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
]

async def create_tables():
    """Create all database tables."""
    print("Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    print("✅ Tables created successfully")

async def insert_sample_data():
    """Insert sample data into the database."""
    print("Inserting sample data...")
    
    # Insert spending data
    async with engine.begin() as conn:
        for spending in sample_spending:
            await conn.execute(
                spending_table.insert().values(**spending)
            )
        print(f"✅ Inserted {len(sample_spending)} spending records")
        
        # Insert recommendation data
        for recommendation in sample_recommendations:
            await conn.execute(
                recommendations_table.insert().values(**recommendation)
            )
        print(f"✅ Inserted {len(sample_recommendations)} recommendation records")

async def verify_data():
    """Verify the inserted data."""
    print("Verifying data...")
    
    async with engine.connect() as conn:
        # Check spending records
        result = await conn.execute(text("SELECT COUNT(*) FROM spending"))
        spending_count = result.scalar()
        print(f"✅ Found {spending_count} spending records")
        
        # Check recommendation records
        result = await conn.execute(text("SELECT COUNT(*) FROM recommendations"))
        recommendation_count = result.scalar()
        print(f"✅ Found {recommendation_count} recommendation records")
        
        # Show sample data
        result = await conn.execute(text("SELECT * FROM spending LIMIT 1"))
        spending = result.fetchone()
        if spending:
            print(f"✅ Sample spending: {spending}")
        
        result = await conn.execute(text("SELECT * FROM recommendations LIMIT 1"))
        recommendation = result.fetchone()
        if recommendation:
            print(f"✅ Sample recommendation: {recommendation}")

async def main():
    """Main function to initialize the database."""
    try:
        print(f"Initializing database at {DATABASE_URL}")
        await create_tables()
        await insert_sample_data()
        await verify_data()
        print("✅ Database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise
    finally:
        await engine.dispose()
        print("✅ Database connection closed.")

if __name__ == "__main__":
    print("Starting direct database initialization...")
    asyncio.run(main())
    print("Initialization process completed.")
