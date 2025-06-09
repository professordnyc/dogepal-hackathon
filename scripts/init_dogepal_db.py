#!/usr/bin/env python3
"""
Initialize the DOGEPAL database with proper configuration and sample data.
"""
import asyncio
import os
import sys
from pathlib import Path
from datetime import date, datetime
from typing import Dict, Any

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

# Import models
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
    
    # Sample spending data
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
            "metadata_": {"source": "manual_entry", "reviewed_by": "admin@example.com"}
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
            "metadata_": {"source": "api_import", "po_number": "PO-2023-456"}
        }
    ]
    
    async with async_session_factory() as session:
        # Add sample spending records
        spendings = []
        for data in sample_spending:
            spending = Spending(**data)
            session.add(spending)
            spendings.append(spending)
        
        await session.commit()
        
        # Add sample recommendations
        if spendings:
            # Recommendation for first spending
            rec1 = Recommendation(
                id="REC001",
                transaction_id=spendings[0].transaction_id,
                type="vendor_consolidation",
                title="Consolidate Software Subscriptions",
                description="Consider consolidating with DataSense for additional 15% discount on annual plans.",
                potential_savings=180.00,
                confidence_score=0.85,
                priority="high",
                explanation="Based on analysis of current subscriptions and vendor pricing.",
                status="pending",
                metadata_={"vendor_contact": "sales@datasense.com"}
            )
            session.add(rec1)
            
            # Recommendation for second spending
            rec2 = Recommendation(
                id="REC002",
                transaction_id=spendings[1].transaction_id,
                type="bulk_purchase",
                title="Bulk Purchase Opportunity",
                description="Consider bulk purchase of sensors for additional 20% discount on orders over $10,000.",
                potential_savings=700.00,
                confidence_score=0.75,
                priority="medium",
                status="pending",
                metadata_={"min_order": 10000, "valid_until": "2023-12-31"}
            )
            session.add(rec2)
            
            await session.commit()
        
        print(f"✅ Added {len(sample_spending)} spending records and 2 recommendations")

async def main():
    """Main function to initialize the database."""
    try:
        await create_tables()
        await add_sample_data()
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
