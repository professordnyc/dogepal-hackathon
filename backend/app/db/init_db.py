import asyncio
import logging
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy.future import select

from app.core.config import settings
from app.db.session import engine, async_session, Base
from app.models.spending import Spending, Recommendation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample data configuration
DEPARTMENTS = ["HR", "Operations", "Planning", "Analytics", "Waste Management", "Technology", "Finance"]
USER_TYPES = ["solopreneur", "startup", "board"]
BOROUGHS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
CATEGORIES = ["software", "hardware", "consulting", "logistics", "analytics", "printing", "training"]
VENDORS = {
    "software": ["DataSense", "CloudServ", "TechSolutions", "AppWorks", "CodeCraft"],
    "hardware": ["TechSupply", "OfficeGear", "CompuPlus", "GadgetPro", "ITDepot"],
    "consulting": ["ConsultPro", "StrategyPartners", "EcoConsult", "UrbanPlan", "BizAdvisors"],
    "logistics": ["QuickShip", "MetroMove", "CityHaul", "RapidTransit", "UrbanLogistics"],
    "analytics": ["DataSense", "AnalyticsPro", "Insight360", "NumberCrunch", "StatMasters"],
    "printing": ["PrintMasters", "CityPress", "BoroPrint", "QuickCopy", "DocuPrint"],
    "training": ["SkillBridge", "LearnTech", "EduPros", "KnowledgeHub", "TrainRight"]
}
PROJECTS = [
    "AI Skills Initiative", 
    "Smart Waste Pilot", 
    "Waterfront Green Initiative",
    "Digital Inclusion Program",
    "Urban Mobility Project",
    "Public Safety Tech Upgrade",
    "Community Development Program"
]
JUSTIFICATIONS = [
    "Annual subscription renewal",
    "New equipment for team",
    "Professional development training",
    "Software license renewal",
    "Office supplies restock",
    "Consulting services for project",
    "Team offsite event"
]

async def init_models():
    """Initialize database tables."""
    try:
        # Create all tables
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def create_sample_data():
    """Generate and insert sample spending and recommendation data."""
    logger.info("Generating sample data...")
    
    async with async_session() as session:
        # Clear existing data
        await session.execute("DELETE FROM recommendations")
        await session.execute("DELETE FROM spending")
        
        # Generate sample spending data
        spending_data = await generate_sample_spending()
        session.add_all(spending_data)
        await session.commit()
        
        # Generate sample recommendations
        recommendations = await generate_sample_recommendations(session)
        session.add_all(recommendations)
        await session.commit()
        
        logger.info(f"Generated {len(spending_data)} spending records and {len(recommendations)} recommendations")

def generate_transaction_id() -> str:
    """Generate a unique transaction ID."""
    return f"TXN{random.randint(10000, 99999)}"

async def generate_sample_spending() -> List[Spending]:
    """Generate sample spending data."""
    spending_data = []
    start_date = datetime.now() - timedelta(days=180)  # 6 months of data
    
    for i in range(200):  # Generate 200 sample transactions
        # Randomize transaction date within the last 6 months
        days_ago = random.randint(0, 180)
        transaction_date = (start_date + timedelta(days=days_ago)).date()
        
        # Randomly select category and corresponding vendor
        category = random.choice(CATEGORIES)
        vendor = random.choice(VENDORS[category])
        
        # Generate realistic amount based on category
        if category in ["software", "hardware"]:
            amount = round(random.uniform(100, 5000), 2)
        elif category == "consulting":
            amount = round(random.uniform(500, 10000), 2)
        else:
            amount = round(random.uniform(20, 1000), 2)
        
        spending = Spending(
            transaction_id=generate_transaction_id(),
            user_id=f"U{random.randint(1000, 9999)}",
            user_type=random.choice(USER_TYPES),
            department=random.choice(DEPARTMENTS),
            project_name=random.choice(PROJECTS),
            borough=random.choice(BOROUGHS),
            date=transaction_date,
            vendor=vendor,
            category=category,
            amount=amount,
            justification=random.choice(JUSTIFICATIONS),
            approval_status=random.choices(
                ["pending", "approved", "rejected"], 
                weights=[0.2, 0.75, 0.05],
                k=1
            )[0],
            metadata_={"source": "sample_data", "generated_at": datetime.utcnow().isoformat()}
        )
        spending_data.append(spending)
    
    return spending_data

async def generate_sample_recommendations(session: Session) -> List[Recommendation]:
    """Generate sample recommendations based on spending data."""
    # Get some recent spending items to base recommendations on
    result = await session.execute(
        select(Spending)
        .order_by(Spending.date.desc())
        .limit(10)
    )
    recent_spending = result.scalars().all()
    
    recommendations = []
    
    # Generate a few different types of recommendations
    for i, spending in enumerate(recent_spending[:5]):  # First 5 spending items get recommendations
        if i == 0:
            # Vendor consolidation
            recommendations.append(create_vendor_consolidation_rec(spending))
        elif i == 1:
            # Budget alert
            recommendations.append(create_budget_alert_rec(spending))
        elif i == 2:
            # Duplicate payment check
            recommendations.append(create_duplicate_payment_rec(spending))
        else:
            # Generic recommendation
            recommendations.append(create_generic_recommendation(spending, i))
    
    return recommendations

def create_vendor_consolidation_rec(spending: Spending) -> Recommendation:
    """Create a vendor consolidation recommendation."""
    return Recommendation(
        id=f"REC{random.randint(1000, 9999)}",
        transaction_id=spending.transaction_id,
        type="vendor_consolidation",
        title="Vendor Consolidation Opportunity",
        description=f"Consider consolidating {spending.category} services with {spending.vendor} for potential volume discounts.",
        potential_savings=round(spending.amount * 0.15, 2),  # 15% potential savings
        confidence_score=round(random.uniform(0.7, 0.95), 2),
        priority=random.choice(["low", "medium", "high"]),
        explanation=f"You have multiple vendors for {spending.category} services. Consolidating with {spending.vendor} could save ~15% on costs.",
        status="pending",
        metadata_={
            "recommendation_reason": "multiple_vendors",
            "vendor_count": random.randint(3, 8),
            "potential_savings_percent": 15
        }
    )

def create_budget_alert_rec(spending: Spending) -> Recommendation:
    """Create a budget alert recommendation."""
    return Recommendation(
        id=f"REC{random.randint(1000, 9999)}",
        transaction_id=spending.transaction_id,
        type="budget_alert",
        title=f"Budget Alert for {spending.category}",
        description=f"Spending on {spending.category} is 35% over budget for this quarter.",
        potential_savings=round(spending.amount * 0.35, 2),
        confidence_score=round(random.uniform(0.6, 0.9), 2),
        priority="high",
        explanation=f"Your department has spent ${spending.amount * 1.5:,.2f} on {spending.category} this quarter, which is 35% over budget.",
        status="pending",
        metadata_={
            "recommendation_reason": "budget_exceeded",
            "budget_amount": round(spending.amount * 1.5 * 0.65, 2),
            "current_spend": round(spending.amount * 1.5, 2),
            "variance_percent": 35
        }
    )

def create_duplicate_payment_rec(spending: Spending) -> Recommendation:
    """Create a duplicate payment check recommendation."""
    return Recommendation(
        id=f"REC{random.randint(1000, 9999)}",
        transaction_id=spending.transaction_id,
        type="duplicate_check",
        title="Possible Duplicate Payment",
        description=f"Similar payment to {spending.vendor} detected around the same date.",
        potential_savings=spending.amount,
        confidence_score=round(random.uniform(0.5, 0.8), 2),
        priority="medium",
        explanation=f"A payment of ${spending.amount:,.2f} to {spending.vendor} on {spending.date} may be a duplicate.",
        status="pending",
        metadata_={
            "recommendation_reason": "possible_duplicate",
            "similar_transactions": [
                {"id": f"TXN{random.randint(10000, 99999)}", "date": spending.date.isoformat(), "amount": spending.amount * 0.9},
                {"id": f"TXN{random.randint(10000, 99999)}", "date": (spending.date - timedelta(days=1)).isoformat(), "amount": spending.amount * 1.1}
            ]
        }
    )

def create_generic_recommendation(spending: Spending, index: int) -> Recommendation:
    """Create a generic recommendation based on spending."""
    rec_types = [
        {
            "type": "contract_renewal",
            "title": "Upcoming Contract Renewal",
            "description": f"Contract with {spending.vendor} for {spending.category} is up for renewal soon.",
            "explanation": f"Your contract with {spending.vendor} will expire in 30 days. Consider reviewing terms and negotiating pricing.",
            "savings_multiplier": 0.1
        },
        {
            "type": "bulk_discount",
            "title": "Bulk Purchase Opportunity",
            "description": f"You may qualify for bulk discounts on {spending.category} purchases.",
            "explanation": f"Consolidating {spending.category} purchases could qualify you for volume discounts of 10-15%.",
            "savings_multiplier": 0.12
        },
        {
            "type": "alternative_vendor",
            "title": "Alternative Vendor Available",
            "description": f"Consider alternative vendors for {spending.category} that may offer better pricing.",
            "explanation": f"Other vendors offer similar {spending.category} services at 10-20% lower costs.",
            "savings_multiplier": 0.15
        }
    ]
    
    rec = rec_types[index % len(rec_types)]
    return Recommendation(
        id=f"REC{random.randint(1000, 9999)}",
        transaction_id=spending.transaction_id,
        type=rec["type"],
        title=rec["title"],
        description=rec["description"],
        potential_savings=round(spending.amount * rec["savings_multiplier"], 2),
        confidence_score=round(random.uniform(0.6, 0.85), 2),
        priority=random.choice(["low", "medium"]),
        explanation=rec["explanation"],
        status="pending",
        metadata_={
            "recommendation_reason": rec["type"],
            "source": "ai_analysis"
        }
    )

async def init():
    """Initialize database and load sample data."""
    await init_models()
    await create_sample_data()

if __name__ == "__main__":
    print("Initializing database...")
    asyncio.run(init())
    print("Database initialization complete!")
