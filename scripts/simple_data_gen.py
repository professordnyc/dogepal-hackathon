"""Simplified data generation script."""
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
import random
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum, JSON, ForeignKey

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

# Create session factory
async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Enums
class CategoryEnum(str, Enum):
    OFFICE_SUPPLIES = "office_supplies"
    TECHNOLOGY = "technology"
    CONSULTING = "consulting"
    TRAVEL = "travel"
    TRAINING = "training"

class DepartmentEnum(str, Enum):
    EDUCATION = "education"
    TRANSPORTATION = "transportation"
    PARKS = "parks"
    SANITATION = "sanitation"
    PUBLIC_SAFETY = "public_safety"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class RecommendationType(str, Enum):
    COST_SAVING = "cost_saving"
    BUDGET_OPTIMIZATION = "budget_optimization"
    VENDOR_CONSOLIDATION = "vendor_consolidation"
    SPENDING_ANOMALY = "spending_anomaly"
    POLICY_VIOLATION = "policy_violation"

class RecommendationStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# Models
class Spending(Base):
    __tablename__ = "spending"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    user_type = Column(String)
    department = Column(Enum(DepartmentEnum))
    project_name = Column(String)
    borough = Column(String)
    spending_date = Column(DateTime, default=datetime.utcnow)
    vendor = Column(String)
    category = Column(Enum(CategoryEnum))
    amount = Column(Float)
    justification = Column(String)
    approval_status = Column(Enum(ApprovalStatus), default=ApprovalStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendation"
    
    id = Column(Integer, primary_key=True, index=True)
    spending_id = Column(Integer, ForeignKey("spending.id"))
    recommendation_type = Column(Enum(RecommendationType))
    description = Column(String)
    potential_savings = Column(Float)
    status = Column(Enum(RecommendationStatus), default=RecommendationStatus.PENDING)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    metadata_field = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Data generation
class SampleDataGenerator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.fake = Faker()
        Faker.seed(42)  # For reproducible results
        
        # NYC boroughs
        self.boroughs = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
        
        # Common NYC government vendors
        self.vendors = [
            "ABC Office Supplies", "Tech Solutions Inc.", "Citywide Consulting",
            "Empire State Services", "Gotham IT", "Metro Office Supply",
            "Urban Development Group", "Five Boroughs Consulting"
        ]
        
        # Project names
        self.projects = [
            "Citywide Network Upgrade", "Public School Modernization",
            "Parks Renovation", "Infrastructure Maintenance",
            "Community Development", "Public Safety Initiative"
        ]
    
    async def generate_spending(self, count: int = 50):
        """Generate sample spending records."""
        spendings = []
        for _ in range(count):
            spending = Spending(
                user_id=f"user_{self.fake.random_int(min=1, max=10)}",
                user_type=random.choice(["city_official", "department_head", "admin"]),
                department=random.choice(list(DepartmentEnum)),
                project_name=random.choice(self.projects),
                borough=random.choice(self.boroughs),
                spending_date=self.fake.date_time_between(start_date="-1y", end_date="now"),
                vendor=random.choice(self.vendors),
                category=random.choice(list(CategoryEnum)),
                amount=round(random.uniform(100, 50000), 2),
                justification=self.fake.sentence(),
                approval_status=random.choice(list(ApprovalStatus)),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(spending)
            spendings.append(spending)
        
        await self.db.commit()
        return spendings
    
    async def generate_recommendations(self, spendings: list):
        """Generate sample recommendations for spendings."""
        recommendations = []
        
        # Generate 1-2 recommendations for each spending
        for spending in spendings:
            if random.random() < 0.7:  # 70% chance to generate a recommendation
                recommendation = Recommendation(
                    spending_id=spending.id,
                    recommendation_type=random.choice(list(RecommendationType)),
                    description=f"Recommendation for {spending.vendor} spending",
                    potential_savings=round(spending.amount * random.uniform(0.05, 0.2), 2),
                    status=random.choice(list(RecommendationStatus)),
                    priority=random.choice(list(Priority)),
                    metadata_field={
                        "confidence_score": round(random.uniform(0.7, 0.99), 2),
                        "explanation": self.fake.paragraph(),
                        "generated_at": datetime.utcnow().isoformat()
                    },
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                self.db.add(recommendation)
                recommendations.append(recommendation)
        
        await self.db.commit()
        return recommendations

async def main():
    """Main function to generate sample data."""
    print("Starting sample data generation...")
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Generate data
    async with async_session_factory() as db:
        generator = SampleDataGenerator(db)
        
        # Generate spendings
        print("Generating spending records...")
        spendings = await generator.generate_spending(100)
        print(f"Generated {len(spendings)} spending records")
        
        # Generate recommendations
        print("Generating recommendations...")
        recommendations = await generator.generate_recommendations(spendings)
        print(f"Generated {len(recommendations)} recommendations")
        
        print("Sample data generation completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
