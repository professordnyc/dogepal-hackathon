"""Test script to verify model creation."""
import asyncio
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Add backend to path
import sys
sys.path.append(str(Path(__file__).parent.parent / "backend"))

# Import SQLAlchemy components
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    from sqlalchemy.orm import declarative_base
    from app.models.spending import Spending, Recommendation
    from app.schemas.spending import CategoryEnum, DepartmentEnum, ApprovalStatus
    from app.schemas.recommendation import RecommendationType, RecommendationStatus, Priority
    
    print("All imports successful!")
    
except Exception as e:
    print(f"Error during imports: {e}")
    raise

# Test model creation
async def test_models():
    try:
        # Create a test spending record
        spending = Spending(
            user_id="test_user_1",
            user_type="city_official",
            department=DepartmentEnum.EDUCATION,
            project_name="Test Project",
            borough="Manhattan",
            spending_date=datetime.utcnow(),
            vendor="Test Vendor",
            category=CategoryEnum.OFFICE_SUPPLIES,
            amount=1000.0,
            justification="Test justification",
            approval_status=ApprovalStatus.APPROVED,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        print("Successfully created Spending model!")
        
        # Create a test recommendation
        recommendation = Recommendation(
            spending_id=1,  # This would normally be the ID of an existing spending record
            recommendation_type=RecommendationType.COST_SAVING,
            description="Test recommendation",
            potential_savings=100.0,
            status=RecommendationStatus.PENDING,
            priority=Priority.MEDIUM,
            metadata_field={"test": "data"},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        print("Successfully created Recommendation model!")
        
        return True
        
    except Exception as e:
        print(f"Error creating models: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_models())
