import asyncio
import logging
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import sys
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import text, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_async_session_factory, get_engine
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
    """
    Initialize database tables.
    
    This function is kept for backward compatibility but is now a no-op
    since table creation is handled by the session module.
    """
    logger.info("Database tables are now managed by the session module")
    return True

async def create_sample_data():
    """
    Generate and insert sample spending and recommendation data.
    
    Returns:
        dict: Dictionary with counts of created records
    """
    logger.info("Generating sample data...")
    
    session_factory = get_async_session_factory()
    async with session_factory() as session:
        # Clear existing data
        await session.execute(text("DELETE FROM recommendation"))
        await session.execute(text("DELETE FROM spending"))
        
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
        
        # Create spending record
        spending = Spending(
            transaction_id=generate_transaction_id(),
            user_id=f"user_{random.randint(1, 20)}",
            user_type=random.choice(USER_TYPES),
            department=random.choice(DEPARTMENTS),
            project_name=random.choice(PROJECTS),
            borough=random.choice(BOROUGHS),
            spending_date=transaction_date,
            vendor=vendor,
            category=category,
            amount=amount,
            justification=random.choice(JUSTIFICATIONS),
            approval_status=random.choice(["pending", "approved", "rejected"]),
            metadata_field={
                "generated_at": datetime.utcnow().isoformat(),
                "source": "sample_data_generator"
            }
        )
        spending_data.append(spending)
    
    return spending_data

async def generate_sample_recommendations(session: AsyncSession) -> List[Recommendation]:
    """
    Generate sample recommendations based on spending data.
    
    Args:
        session: The database session to use
        
    Returns:
        list: List of created Recommendation objects
    """
    logger.info("Generating sample recommendations...")
    
    try:
        # Get all spending records
        result = await session.execute(select(Spending).order_by(Spending.spending_date.desc()))
        spending_records = result.scalars().all()
        
        if not spending_records:
            logger.warning("No spending records found to generate recommendations")
            return []
            
        recommendations = []
        
        # Generate recommendations for each spending record
        for i, spending in enumerate(spending_records):
            # Every 3rd record gets a vendor consolidation recommendation
            if i % 3 == 0:
                rec = create_vendor_consolidation_rec(spending)
                if rec:
                    recommendations.append(rec)
            
            # Every 5th record gets a budget alert
            if i % 5 == 0:
                rec = create_budget_alert_rec(spending)
                if rec:
                    recommendations.append(rec)
            
            # Every 7th record gets a duplicate payment check
            if i % 7 == 0:
                rec = create_duplicate_payment_rec(spending)
                if rec:
                    recommendations.append(rec)
            
            # Add a generic recommendation for variety
            rec = create_generic_recommendation(spending, i)
            if rec:
                recommendations.append(rec)
        
        if recommendations:
            session.add_all(recommendations)
            await session.commit()
            logger.info(f"Generated {len(recommendations)} recommendations")
        else:
            logger.warning("No recommendations were generated")
            
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {e}")
        await session.rollback()
        raise

def create_vendor_consolidation_rec(spending: Spending) -> Recommendation:
    """Create a vendor consolidation recommendation."""
    return Recommendation(
        id=f"REC{random.randint(1000, 9999)}",
        transaction_id=spending.transaction_id,
        recommendation_type="vendor_consolidation",
        title="Vendor Consolidation Opportunity",
        description=f"Consider consolidating {spending.category} services with {spending.vendor} for potential volume discounts.",
        potential_savings=round(spending.amount * 0.15, 2),  # 15% potential savings
        confidence_score=round(random.uniform(0.7, 0.95), 2),
        priority=random.choice(["low", "medium", "high"]),
        explanation=f"You have multiple vendors for {spending.category} services. Consolidating with {spending.vendor} could save ~15% on costs.",
        status="pending",
        metadata_field={
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
        recommendation_type="budget_alert",
        title=f"Budget Alert for {spending.category}",
        description=f"Spending on {spending.category} is 35% over budget for this quarter.",
        potential_savings=round(spending.amount * 0.35, 2),
        confidence_score=round(random.uniform(0.6, 0.9), 2),
        priority="high",
        explanation=f"Your department has spent ${spending.amount * 1.5:,.2f} on {spending.category} this quarter, which is 35% over budget.",
        status="pending",
        metadata_field={
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
        recommendation_type="duplicate_check",
        title="Possible Duplicate Payment",
        description=f"Similar payment to {spending.vendor} detected around the same date.",
        potential_savings=spending.amount,
        confidence_score=round(random.uniform(0.5, 0.8), 2),
        priority="medium",
        explanation=f"A payment of ${spending.amount:,.2f} to {spending.vendor} on {spending.spending_date} may be a duplicate.",
        status="pending",
        metadata_field={
            "recommendation_reason": "possible_duplicate",
            "similar_transactions": [
                {"id": f"TXN{random.randint(10000, 99999)}", "date": spending.spending_date.isoformat(), "amount": spending.amount * 0.9},
                {"id": f"TXN{random.randint(10000, 99999)}", "date": (spending.spending_date - timedelta(days=1)).isoformat(), "amount": spending.amount * 1.1}
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
        recommendation_type=rec["type"],
        title=rec["title"],
        description=rec["description"],
        potential_savings=round(spending.amount * rec["savings_multiplier"], 2),
        confidence_score=round(random.uniform(0.6, 0.85), 2),
        priority=random.choice(["low", "medium"]),
        explanation=rec["explanation"],
        status="pending",
        metadata_field={
            "recommendation_reason": rec["type"],
            "source": "ai_analysis"
        }
    )

async def init():
    """
    Initialize database and load sample data.
    
    This is the main entry point for initializing the database with sample data.
    It ensures the database is properly initialized before creating sample data.
    """
    # Initialize models (tables)
    await init_models()
    
    # Create sample data
    result = await create_sample_data()
    
    logger.info("Database initialization complete!")
    return result

if __name__ == "__main__":
    print("Initializing database...")
    asyncio.run(init())
    print("Database initialization complete!")
