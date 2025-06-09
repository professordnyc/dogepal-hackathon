"""
Tests for database models in the DOGEPAL application.
"""
import pytest
from datetime import date, datetime
from uuid import uuid4
from sqlalchemy import select

from app.models.spending import Spending, Recommendation

# Test data
TEST_SPENDING = {
    "transaction_id": "TXN12345",
    "user_id": "U1001",
    "user_type": "solopreneur",
    "department": "Technology",
    "project_name": "AI Skills Initiative",
    "borough": "Manhattan",
    "date": date(2023, 6, 15),
    "vendor": "TechSolutions",
    "category": "software",
    "amount": 4999.99,
    "justification": "Annual subscription renewal",
    "approval_status": "approved",
    "metadata_": {"source": "test"}
}

TEST_RECOMMENDATION = {
    "id": "REC1001",
    "transaction_id": "TXN12345",
    "type": "vendor_consolidation",
    "title": "Vendor Consolidation Opportunity",
    "description": "Consolidate software vendors for better pricing",
    "potential_savings": 750.0,
    "confidence_score": 0.85,
    "priority": "high",
    "explanation": "Consolidating with TechSolutions could save ~15% on costs",
    "status": "pending",
    "metadata_": {"savings_percent": 15, "vendor_count": 3}
}

@pytest.mark.asyncio
async def test_create_spending(db_session):
    """Test creating a new spending record."""
    # Create a new spending record
    spending = Spending(**TEST_SPENDING)
    db_session.add(spending)
    await db_session.commit()
    await db_session.refresh(spending)
    
    # Verify the record was created
    assert spending.id is not None
    assert spending.transaction_id == TEST_SPENDING["transaction_id"]
    assert spending.amount == TEST_SPENDING["amount"]
    assert spending.created_at is not None
    assert spending.updated_at is not None

@pytest.mark.asyncio
async def test_create_recommendation(db_session):
    """Test creating a new recommendation."""
    # First create a spending record
    spending = Spending(**TEST_SPENDING)
    db_session.add(spending)
    await db_session.commit()
    
    # Create a recommendation linked to the spending
    recommendation = Recommendation(**TEST_RECOMMENDATION)
    db_session.add(recommendation)
    await db_session.commit()
    await db_session.refresh(recommendation)
    
    # Verify the record was created
    assert recommendation.id == TEST_RECOMMENDATION["id"]
    assert recommendation.transaction_id == TEST_SPENDING["transaction_id"]
    assert recommendation.potential_savings == TEST_RECOMMENDATION["potential_savings"]
    assert recommendation.created_at is not None
    assert recommendation.updated_at is not None

@pytest.mark.asyncio
async def test_spending_relationships(db_session):
    """Test spending relationships with recommendations."""
    # Create a spending record
    spending = Spending(**TEST_SPENDING)
    db_session.add(spending)
    await db_session.commit()
    
    # Create a recommendation linked to the spending
    recommendation = Recommendation(
        **{
            **TEST_RECOMMENDATION,
            "transaction_id": spending.transaction_id
        }
    )
    db_session.add(recommendation)
    await db_session.commit()
    
    # Test the relationship
    result = await db_session.execute(
        select(Spending).where(Spending.transaction_id == TEST_SPENDING["transaction_id"])
    )
    loaded_spending = result.scalars().first()
    
    # Verify the relationship
    assert loaded_spending is not None
    assert len(loaded_spending.recommendations) == 1
    assert loaded_spending.recommendations[0].id == recommendation.id

@pytest.mark.asyncio
async def test_recommendation_metadata(db_session):
    """Test recommendation metadata storage and retrieval."""
    # Create a spending record
    spending = Spending(**TEST_SPENDING)
    db_session.add(spending)
    await db_session.commit()
    
    # Create a recommendation with metadata
    metadata = {"key1": "value1", "count": 5, "nested": {"a": 1, "b": 2}}
    recommendation = Recommendation(
        **{
            **TEST_RECOMMENDATION,
            "transaction_id": spending.transaction_id,
            "metadata_": metadata
        }
    )
    db_session.add(recommendation)
    await db_session.commit()
    
    # Verify metadata was stored and retrieved correctly
    assert recommendation.metadata_ == metadata
    
    # Test updating metadata
    recommendation.metadata_["new_key"] = "new_value"
    await db_session.commit()
    await db_session.refresh(recommendation)
    assert "new_key" in recommendation.metadata_
