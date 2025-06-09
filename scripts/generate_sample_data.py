"""
Sample Data Generator for DOGEPAL

This script generates realistic sample data for the DOGEPAL application,
including NYC government spending records and AI-generated recommendations.
"""
import asyncio
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
from faker import Faker
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Add project root to Python path
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add the backend directory to the Python path
backend_dir = str(Path(__file__).parent.parent / "backend")
sys.path.append(backend_dir)

# Import SQLAlchemy components
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Create a minimal settings class
class Settings:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dogepal.db")

# Create database engine
engine = create_async_engine(
    Settings.SQLALCHEMY_DATABASE_URI,
    echo=True,
    future=True,
    connect_args={"check_same_thread": False},
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base class for models
Base = declarative_base()

# Import models after Base is defined
from app.models.spending import Spending as SpendingModel, Recommendation as RecommendationModel
from app.schemas.spending import SpendingCreate, CategoryEnum, DepartmentEnum, ApprovalStatus
from app.schemas.recommendation import (
    RecommendationCreate, RecommendationType, RecommendationStatus, Priority
)

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducible results
random.seed(42)

# NYC-specific data
NYC_BOROUGHS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
NYC_AGENCIES = [
    "Department of Education",
    "Department of Sanitation",
    "Department of Transportation",
    "NYC Housing Authority",
    "Parks Department",
    "Police Department",
    "Fire Department",
    "Health Department",
    "Human Resources Administration",
]

# Common NYC vendors and their categories
VENDORS = {
    "Office Supplies": ["Staples", "Office Depot", "Amazon Business", "W.B. Mason"],
    "Construction": ["Turner Construction", "AECOM", "Skanska", "Lendlease"],
    "Technology": ["Dell", "CDW-G", "SHI", "Connection"],
    "Professional Services": ["Deloitte", "PwC", "EY", "KPMG"],
    "Facilities": ["ABM Industries", "Cushman & Wakefield", "JLL"],
}

# Project names by department
PROJECT_NAMES = {
    "Department of Education": [
        "School Modernization Initiative",
        "Digital Learning Tools",
        "Facility Upgrades FY2025",
    ],
    "Department of Sanitation": [
        "Waste Management Optimization",
        "Recycling Program Expansion",
    ],
    "Department of Transportation": [
        "Street Resurfacing Program",
        "Bridge Maintenance FY2025",
    ],
    "NYC Housing Authority": [
        "Public Housing Repairs",
        "Energy Efficiency Upgrades",
    ],
    "default": [
        "Infrastructure Modernization",
        "Technology Upgrade Program",
        "Facility Maintenance",
    ],
}

# AI explanation templates
AI_EXPLANATIONS = {
    "vendor_consolidation": (
        "Identified multiple vendors providing similar services. Consolidating to {vendor} "
        "could reduce administrative overhead and potentially secure volume discounts."
    ),
    "cost_saving": (
        "Potential cost savings identified by comparing with market rates and similar purchases. "
        "Negotiating prices or exploring alternative vendors could reduce costs by ~{savings_pct}%."
    ),
    "budget_optimization": (
        "This expense represents {pct_of_budget}% of the total budget for {category}. "
        "Reviewing and optimizing these costs could free up resources for other priorities."
    ),
    "spending_anomaly": (
        "This transaction is {std_devs} standard deviations above the average for {category} "
        "in {borough}. Further investigation recommended."
    ),
    "policy_violation": (
        "This transaction may violate procurement policy {policy_reference}. "
        "Review required by {department} compliance team."
    ),
}

class SampleDataGenerator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.vendor_cache = {}
        self.project_cache = {}
        
    async def get_or_create_vendor(self, category: str, department: str) -> str:
        """Get or create a vendor for the given category and department."""
        cache_key = f"{category}_{department}"
        if cache_key not in self.vendor_cache:
            vendors = VENDORS.get(category, ["Vendor Corp"])
            self.vendor_cache[cache_key] = random.choice(vendors)
        return self.vendor_cache[cache_key]
    
    def get_project_name(self, department: str) -> str:
        """Get a project name for the given department."""
        if department not in self.project_cache:
            projects = PROJECT_NAMES.get(department, []) + PROJECT_NAMES["default"]
            self.project_cache[department] = random.choice(projects)
        return self.project_cache[department]
    
    def generate_ai_explanation(self, rec_type: str, **kwargs) -> Dict[str, Any]:
        """Generate AI explanation metadata."""
        template = AI_EXPLANATIONS.get(rec_type, "")
        explanation = template.format(**kwargs)
        
        return {
            "explanation": explanation,
            "confidence": round(random.uniform(0.7, 0.95), 2),
            "factors_considered": ["historical_data", "market_rates", "department_budget"],
            "last_updated": datetime.utcnow().isoformat(),
            "model_version": "1.0.0",
            **kwargs
        }
    
    async def generate_spending(
        self, 
        count: int = 100,
        start_date: str = "2024-01-01",
        end_date: str = "2025-06-09"
    ) -> List[SpendingModel]:
        """Generate sample spending records."""
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        delta = end_dt - start_dt
        
        categories = list(CategoryEnum)
        departments = list(DepartmentEnum)
        statuses = list(ApprovalStatus)
        
        spendings = []
        for _ in range(count):
            # Random date within range
            random_days = random.randrange(delta.days)
            spending_date = start_dt + timedelta(days=random_days)
            
            # Random category and department
            category = random.choice(categories)
            department = random.choice(departments)
            
            # Generate realistic amounts (skewed toward smaller purchases)
            amount = abs(np.random.normal(5000, 10000))
            amount = max(100, min(amount, 100000))  # Cap between $100 and $100,000
            
            # Get vendor and project
            vendor = await self.get_or_create_vendor(category, department.value)
            project_name = self.get_project_name(department.value)
            
            # Create spending record
            spending = SpendingModel(
                user_id=f"user_{random.randint(1, 10)}",
                user_type="city_official",
                department=department,
                project_name=project_name,
                borough=random.choice(NYC_BOROUGHS),
                spending_date=spending_date,
                vendor=vendor,
                category=category,
                amount=round(amount, 2),
                justification=fake.sentence(),
                approval_status=random.choices(
                    statuses, 
                    weights=[0.7, 0.25, 0.05]  # 70% approved, 25% pending, 5% rejected
                )[0],
                created_at=spending_date,
                updated_at=spending_date,
            )
            spendings.append(spending)
        
        # Add to database
        self.db.add_all(spendings)
        await self.db.commit()
        
        # Refresh to get IDs
        for spending in spendings:
            await self.db.refresh(spending)
        
        return spendings
    
    async def generate_recommendations(
        self, 
        spendings: List[SpendingModel],
        recs_per_spending: float = 0.3  # 30% of spendings get recommendations
    ) -> List[RecommendationModel]:
        """Generate sample recommendations based on spending data."""
        if not spendings:
            return []
            
        # Filter spendings that will get recommendations
        selected_spendings = [s for s in spendings if random.random() < recs_per_spending]
        
        recommendations = []
        for spending in selected_spendings:
            # Determine recommendation type
            rec_type = random.choice(list(RecommendationType))
            
            # Generate explanation
            explanation_data = {
                "vendor": random.choice(VENDORS.get(spending.category.value, ["Alternative Vendor"])),
                "savings_pct": random.randint(5, 25),
                "pct_of_budget": round(random.uniform(0.1, 5.0), 1),
                "category": spending.category.value,
                "borough": spending.borough,
                "std_devs": round(random.uniform(1.5, 3.5), 1),
                "policy_reference": f"PROC-{random.randint(1000, 9999)}",
                "department": spending.department.value,
            }
            
            metadata = self.generate_ai_explanation(rec_type.value, **explanation_data)
            
            # Calculate potential savings (5-25% of amount)
            savings_pct = random.uniform(0.05, 0.25)
            potential_savings = round(spending.amount * savings_pct, 2)
            
            # Create recommendation
            recommendation = RecommendationModel(
                spending_id=spending.transaction_id,
                recommendation_type=rec_type,
                description=f"Recommendation to optimize spending on {spending.category.value}",
                potential_savings=potential_savings,
                status=random.choice(list(RecommendationStatus)),
                priority=random.choice(list(Priority)),
                metadata_field=metadata,
                created_at=spending.spending_date + timedelta(days=random.randint(1, 30)),
                updated_at=spending.spending_date + timedelta(days=random.randint(31, 90)),
            )
            recommendations.append(recommendation)
        
        # Add to database
        self.db.add_all(recommendations)
        await self.db.commit()
        
        return recommendations

async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def main():
    """Main function to generate sample data."""
    print("Starting sample data generation...")
    
    # Initialize database
    await init_db()
    
    async with async_session_factory() as db:
        generator = SampleDataGenerator(db)
        
        # Clear existing data
        print("Clearing existing data...")
        await db.execute("DELETE FROM recommendations")
        await db.execute("DELETE FROM spending")
        await db.commit()
        
        # Generate spending data
        print("Generating spending data...")
        spendings = await generator.generate_spending(count=200)
        print(f"Generated {len(spendings)} spending records")
        
        # Generate recommendations
        print("Generating recommendations...")
        recommendations = await generator.generate_recommendations(spendings)
        print(f"Generated {len(recommendations)} recommendations")
        
        print("Sample data generation complete!")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
