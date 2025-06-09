"""Script to reset the database and seed with test data."""
import asyncio
import random
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON

# Define the database URL with absolute path
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'dogepal.db'))
DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

# Create a base class for declarative models
Base = declarative_base()

# Define models directly in the script to avoid import issues
class Spending(Base):
    """Spending model."""
    __tablename__ = "spending"
    
    transaction_id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    user_type = Column(String)
    department = Column(String)
    project_name = Column(String)
    borough = Column(String)
    spending_date = Column(Date)
    vendor = Column(String)
    category = Column(String)
    amount = Column(Float)
    justification = Column(String)
    approval_status = Column(String)
    metadata_field = Column("metadata", SQLiteJSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Recommendation(Base):
    """Recommendation model."""
    __tablename__ = "recommendation"
    
    id = Column(String, primary_key=True, index=True)
    transaction_id = Column(String, ForeignKey('spending.transaction_id', ondelete='CASCADE'))
    recommendation_type = Column(String)
    title = Column(String)
    description = Column(String)
    potential_savings = Column(Float)
    confidence_score = Column(Float)
    priority = Column(String)
    explanation = Column(String)
    metadata_field = Column("metadata", SQLiteJSON, default=dict)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Sample data
DEPARTMENTS = ["Technology", "HR", "Finance", "Operations", "Public Works"]
BOROUGHS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
VENDORS = ["Acme Inc.", "Tech Solutions", "Office Supplies Co", "City Services", "Global Tech"]
CATEGORIES = ["Software", "Hardware", "Services", "Office Supplies", "Training"]
RECOMMENDATION_TYPES = ["cost_saving", "budget_optimization", "vendor_consolidation"]

# Create a new async engine for this script
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"check_same_thread": False}
)

# Create session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def drop_all_tables():
    """Drop all tables in the database."""
    print("\n🔨 Dropping all tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    print("✅ All tables dropped.")

async def create_tables():
    """Create all tables defined in models."""
    print("\n🔧 Creating tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created.")

async def create_sample_data():
    """Create sample data for testing."""
    print("\n🌱 Adding sample data...")
    
    async with async_session() as session:
        # Create sample spending records
        for i in range(1, 11):  # Create 10 sample records
            spending = Spending(
                transaction_id=f"TXN{1000 + i}",
                user_id=f"user_{random.randint(1, 3)}",
                user_type=random.choice(["admin", "manager", "staff"]),
                department=random.choice(DEPARTMENTS),
                project_name=f"Project {chr(65 + i % 5)}",
                borough=random.choice(BOROUGHS),
                spending_date=datetime.now() - timedelta(days=random.randint(1, 30)),
                vendor=random.choice(VENDORS),
                category=random.choice(CATEGORIES),
                amount=round(random.uniform(100, 10000), 2),
                justification=f"Purchase for {random.choice(['office', 'project', 'team'])} needs",
                approval_status=random.choice(["pending", "approved", "rejected"])
            )
            session.add(spending)
            
            # Add a recommendation for some spending records
            if i % 2 == 0:  # Add recommendations to half the records
                rec = Recommendation(
                    id=f"REC{1000 + i}",
                    transaction_id=spending.transaction_id,
                    recommendation_type=random.choice(RECOMMENDATION_TYPES),
                    title=f"Recommendation for {spending.vendor}",
                    description=f"Consider consolidating purchases with {spending.vendor}",
                    potential_savings=round(spending.amount * random.uniform(0.1, 0.3), 2),
                    confidence_score=round(random.uniform(0.6, 0.95), 2),
                    priority=random.choice(["low", "medium", "high"]),
                    explanation="AI analysis suggests potential cost savings through vendor consolidation.",
                    status="pending"
                )
                session.add(rec)
        
        await session.commit()
    
    print("✅ Sample data added.")

async def main():
    """Main function to reset and seed the database."""
    print("🚀 Starting database reset and seed...")
    
    try:
        await drop_all_tables()
        await create_tables()
        await create_sample_data()
        print("\n✨ Database reset and seeded successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
