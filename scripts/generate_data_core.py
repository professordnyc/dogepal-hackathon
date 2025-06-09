"""Script to generate sample data using SQLAlchemy Core."""
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import random
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, JSON, func
from sqlalchemy.sql import select, insert, text

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducible results

# Database setup
DATABASE_URL = "sqlite+aiosqlite:///./dogepal.db"
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False},
)

# Define tables
metadata = MetaData()

spending = Table(
    "spending",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", String, index=True),
    Column("user_type", String),
    Column("department", String),
    Column("project_name", String),
    Column("borough", String),
    Column("spending_date", DateTime, default=datetime.utcnow),
    Column("vendor", String),
    Column("category", String),
    Column("amount", Float),
    Column("justification", String),
    Column("approval_status", String, default="pending"),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)

recommendation = Table(
    "recommendation",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("spending_id", Integer, nullable=False),
    Column("recommendation_type", String),
    Column("description", String),
    Column("potential_savings", Float),
    Column("status", String, default="pending"),
    Column("priority", String, default="medium"),
    Column("metadata_field", JSON, default=dict),
    Column("created_at", DateTime, default=datetime.utcnow),
    Column("updated_at", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow),
)

# Data generation
class SampleDataGenerator:
    def __init__(self):
        self.fake = Faker()
        Faker.seed(42)  # For reproducible results
        
        # Sample data
        self.boroughs = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
        self.departments = ["education", "transportation", "parks", "sanitation", "public_safety"]
        self.categories = ["office_supplies", "technology", "consulting", "travel", "training"]
        self.vendors = [
            "ABC Office Supplies", "Tech Solutions Inc.", "Citywide Consulting",
            "Empire State Services", "Gotham IT", "Metro Office Supply",
            "Urban Development Group", "Five Boroughs Consulting"
        ]
        self.projects = [
            "Citywide Network Upgrade", "Public School Modernization",
            "Parks Renovation", "Infrastructure Maintenance",
            "Community Development", "Public Safety Initiative"
        ]
        self.recommendation_types = ["cost_saving", "budget_optimization", "vendor_consolidation", "spending_anomaly", "policy_violation"]
        self.statuses = ["pending", "in_progress", "completed", "rejected"]
        self.priorities = ["low", "medium", "high"]
    
    async def generate_spending(self, conn, count=100):
        """Generate sample spending records."""
        spendings = []
        for _ in range(count):
            # Create a single datetime for this record to ensure consistency
            record_time = datetime.utcnow()
            spending_date = self.fake.date_time_between(start_date="-1y", end_date="now")
            
            spending = {
                "user_id": f"user_{self.fake.random_int(min=1, max=10)}",
                "user_type": random.choice(["city_official", "department_head", "admin"]),
                "department": random.choice(self.departments),
                "project_name": random.choice(self.projects),
                "borough": random.choice(self.boroughs),
                "spending_date": spending_date.isoformat(" "),
                "vendor": random.choice(self.vendors),
                "category": random.choice(self.categories),
                "amount": round(random.uniform(100, 50000), 2),
                "justification": self.fake.sentence(),
                "approval_status": random.choice(["pending", "approved", "rejected"]),
                "created_at": record_time.isoformat(" "),
                "updated_at": record_time.isoformat(" ")
            }
            result = await conn.execute(insert(spending).returning(spending.c.id), spending)
            spending_id = result.scalar()
            spendings.append(spending_id)
        
        return spendings
    
    async def generate_recommendations(self, conn, spending_ids):
        """Generate sample recommendations for spendings."""
        for spending_id in spending_ids:
            if random.random() < 0.7:  # 70% chance to generate a recommendation
                recommendation = {
                    "spending_id": spending_id,
                    "recommendation_type": random.choice(self.recommendation_types),
                    "description": f"Recommendation for spending ID {spending_id}",
                    "potential_savings": round(random.uniform(100, 10000), 2),
                    "status": random.choice(self.statuses),
                    "priority": random.choice(self.priorities),
                    "metadata_field": json.dumps({
                        "confidence_score": round(random.uniform(0.7, 0.99), 2),
                        "explanation": self.fake.paragraph(),
                        "generated_at": datetime.utcnow().isoformat()
                    }),
                    "created_at": datetime.utcnow().isoformat(" "),
                    "updated_at": datetime.utcnow().isoformat(" ")
                }
                await conn.execute(insert(recommendation), recommendation)

async def main():
    """Main function to generate sample data."""
    print("Starting sample data generation...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)
    
        # Generate data
    async with engine.connect() as conn:
        generator = SampleDataGenerator()
        
        # Generate spendings
        print("Generating spending records...")
        spending_ids = await generator.generate_spending(conn, 100)
        print(f"Generated {len(spending_ids)} spending records")
        
        # Generate recommendations
        print("Generating recommendations...")
        await generator.generate_recommendations(conn, spending_ids)
        
        # Count recommendations
        result = await conn.execute(select([func.count()]).select_from(recommendation))
        rec_count = (await result.first())[0]
        print(f"Generated {rec_count} recommendations")
        
        await conn.commit()
    
    print("Sample data generation completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
