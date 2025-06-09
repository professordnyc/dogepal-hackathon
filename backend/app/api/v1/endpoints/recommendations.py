from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
import numpy as np
import json
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.spending import Spending as SpendingModel, Recommendation as RecommendationModel
from app.schemas.recommendation import (
    Recommendation, RecommendationCreate, RecommendationUpdate,
    RecommendationWithSpending, RecommendationStats, RecommendationStatus, RecommendationType
)
from app.schemas.spending import CategoryEnum as Category, DepartmentEnum as Department

router = APIRouter()

# Helper function to calculate z-score
def calculate_zscore(value, mean, std):
    if std == 0:
        return 0
    return (value - mean) / std

@router.get("/", response_model=List[RecommendationWithSpending])
async def get_recommendations(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[RecommendationStatus] = None,
    min_confidence: float = 0.5,
    category: Optional[Category] = None,
    department: Optional[Department] = None,
) -> List[RecommendationWithSpending]:
    """
    Get spending recommendations with optional filtering.
    """
    # Build base query with join to spending
    query = (
        select(
            RecommendationModel,
            SpendingModel.amount.label("spending_amount"),
            SpendingModel.category.label("spending_category"),
            SpendingModel.vendor.label("spending_vendor"),
            SpendingModel.date.label("spending_date"),
        )
        .join(SpendingModel, RecommendationModel.spending_id == SpendingModel.id)
        .where(RecommendationModel.confidence_score >= min_confidence)
    )
    
    # Apply filters
    if status:
        query = query.where(RecommendationModel.status == status)
    if category:
        query = query.where(SpendingModel.category == category)
    if department:
        query = query.where(SpendingModel.department == department)
    
    # Apply pagination and ordering
    query = (
        query.order_by(RecommendationModel.confidence_score.desc())
        .offset(skip)
        .limit(limit)
    )
    
    # Execute query
    result = await db.execute(query)
    
    # Convert to Pydantic model
    recommendations = []
    for row in result.mappings().all():
        rec_dict = dict(row["Recommendation"].__dict__)
        rec_dict["spending_amount"] = row["spending_amount"]
        rec_dict["spending_category"] = row["spending_category"]
        rec_dict["spending_vendor"] = row["spending_vendor"]
        rec_dict["spending_date"] = row["spending_date"]
        recommendations.append(RecommendationWithSpending(**rec_dict))
    
    return recommendations

@router.get("/generate", response_model=List[Recommendation])
async def generate_recommendations(
    *,
    db: AsyncSession = Depends(get_db),
    min_confidence: float = 0.7,
) -> List[Recommendation]:
    """
    Generate new spending recommendations based on analysis of spending data.
    Uses the HP AI Studio-integrated SpendingRecommender model for intelligent recommendations.
    """
    # Get all spending data for analysis
    result = await db.execute(select(SpendingModel))
    all_spending = result.scalars().all()
    
    if not all_spending:
        return []
    
    # Import the SpendingRecommender model
    try:
        from models.spending_recommender import SpendingRecommender
    except ImportError:
        # Handle relative import if needed
        import sys
        import os
        from pathlib import Path
        
        # Add the project root to path
        project_root = Path(__file__).parent.parent.parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.append(str(project_root))
        
        try:
            from models.spending_recommender import SpendingRecommender
        except ImportError as e:
            print(f"Failed to import SpendingRecommender: {e}")
            # Fallback to a simple recommendation generator for testing
            class SpendingRecommender:
                def __init__(self):
                    pass
                
                def fit(self, data):
                    return self
                
                def predict(self, data):
                    # Return a simple recommendation for testing
                    return [{
                        'type': 'cost_saving',
                        'title': 'Test Recommendation',
                        'description': 'This is a test recommendation',
                        'confidence_score': 0.8,
                        'priority': 'medium',
                        'explanation': 'Test explanation',
                        'calculation': 'Test calculation',
                        'factors': ['test factor'],
                        'suggested_action': 'Test action'
                    }]
    
    # Convert to list of dicts for easier processing
    spending_data = [
        {
            "transaction_id": str(s.id),
            "amount": s.amount,
            "category": s.category.lower(),  # Model expects lowercase
            "vendor": s.vendor,
            "date": s.date,
            "department": s.department.lower(),  # Model expects lowercase
            "user_id": s.user_id,
            "project_name": s.project_name,
            "borough": s.borough if hasattr(s, 'borough') else None,
            "justification": s.justification if hasattr(s, 'justification') else None
        }
        for s in all_spending
    ]
    
    # Initialize the SpendingRecommender model
    recommender = SpendingRecommender()
    
    # Generate recommendations using the model
    model_recommendations = recommender.predict(spending_data)
    
    # Filter recommendations by confidence score
    filtered_recommendations = [
        rec for rec in model_recommendations 
        if rec and rec.get('confidence_score', 0) >= min_confidence
    ]
    
    # Convert model recommendations to database model instances
    new_recommendations = []
    
    for rec in filtered_recommendations:
        # Find the corresponding spending record
        transaction_id = rec.get('transaction_id')
        if not transaction_id:
            continue
            
        # Check if we already have a recent recommendation for this spending
        try:
            spending_id = int(transaction_id)
        except ValueError:
            # If transaction_id is not a valid integer, try to find by string
            for item in spending_data:
                if item.get('transaction_id') == transaction_id:
                    spending_id = item.get('id')
                    break
            else:
                continue
        
        # Check for existing recommendation
        existing_rec = await db.execute(
            select(RecommendationModel).where(
                RecommendationModel.spending_id == spending_id,
                RecommendationModel.created_at >= datetime.now() - timedelta(days=30)
            )
        )
        if existing_rec.scalars().first():
            continue
        
        # Map recommendation type from model to database enum
        rec_type = rec.get('recommendation_type', 'cost_saving')
        if rec_type == 'spending_anomaly':
            db_rec_type = RecommendationType.SPENDING_ANOMALY
        elif rec_type == 'budget_optimization':
            db_rec_type = RecommendationType.BUDGET_OPTIMIZATION
        elif rec_type == 'vendor_consolidation':
            db_rec_type = RecommendationType.VENDOR_CONSOLIDATION
        elif rec_type == 'policy_violation':
            db_rec_type = RecommendationType.POLICY_VIOLATION
        else:
            db_rec_type = RecommendationType.COST_SAVING
        
        # Map priority based on confidence score
        if rec.get('confidence_score', 0) >= 0.8:
            priority = 'high'
        elif rec.get('confidence_score', 0) >= 0.6:
            priority = 'medium'
        else:
            priority = 'low'
        
        # Create explanation from model data
        explanation = rec.get('explanation', {})
        if isinstance(explanation, dict):
            explanation_text = explanation.get('calculation', '')
            if explanation.get('factors_considered'):
                explanation_text += "\n\nFactors considered:\n" + "\n".join(
                    f"- {factor}" for factor in explanation.get('factors_considered', [])
                )
        else:
            explanation_text = str(explanation)
        
        # Create database model instance
        recommendation = RecommendationModel(
            spending_id=spending_id,
            recommendation_type=db_rec_type,
            title=rec.get('title', 'Spending Recommendation'),
            description=rec.get('description', 'AI-generated spending recommendation'),
            potential_savings=rec.get('potential_savings', 0.0),
            confidence_score=rec.get('confidence_score', 0.5),
            priority=priority,
            explanation=explanation_text,
            suggested_action=rec.get('suggested_action', 
                                   'Review this recommendation and consider implementing the suggested changes.'),
            status=RecommendationStatus.PENDING
        )
        new_recommendations.append(recommendation)
    
    # Save new recommendations to database
    for rec in new_recommendations:
        db.add(rec)
    
    if new_recommendations:
        await db.commit()
        for rec in new_recommendations:
            await db.refresh(rec)
    
    return new_recommendations

@router.get("/stats", response_model=RecommendationStats)
async def get_recommendation_stats(
    *,
    db: AsyncSession = Depends(get_db),
) -> RecommendationStats:
    """
    Get statistics about recommendations.
    """
    # Total recommendations and potential savings
    stats_query = select(
        func.count(RecommendationModel.id).label("total"),
        func.sum(RecommendationModel.potential_savings).label("total_savings")
    )
    stats_result = await db.execute(stats_query)
    stats = stats_result.mappings().first()
    
    # Count by recommendation type
    type_query = (
        select(
            RecommendationModel.recommendation_type,
            func.count(RecommendationModel.id).label("count")
        )
        .group_by(RecommendationModel.recommendation_type)
    )
    type_result = await db.execute(type_query)
    type_counts = {row["recommendation_type"]: row["count"] for row in type_result.mappings()}
    
    # Count by status
    status_query = (
        select(
            RecommendationModel.status,
            func.count(RecommendationModel.id).label("count")
        )
        .group_by(RecommendationModel.status)
    )
    status_result = await db.execute(status_query)
    status_counts = {row["status"]: row["count"] for row in status_result.mappings()}
    
    return RecommendationStats(
        total_recommendations=stats["total"] or 0,
        total_potential_savings=float(stats["total_savings"] or 0),
        recommendations_by_type=type_counts,
        recommendations_by_status=status_counts
    )

@router.put("/{recommendation_id}", response_model=Recommendation)
async def update_recommendation(
    *,
    db: AsyncSession = Depends(get_db),
    recommendation_id: int,
    recommendation_in: RecommendationUpdate
) -> Recommendation:
    """
    Update a recommendation (e.g., change status).
    """
    # Get existing recommendation
    result = await db.execute(
        select(RecommendationModel).where(RecommendationModel.id == recommendation_id)
    )
    db_recommendation = result.scalars().first()
    
    if not db_recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Update fields
    update_data = recommendation_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_recommendation, field, value)
    
    # Save changes
    await db.commit()
    await db.refresh(db_recommendation)
    
    return db_recommendation

@router.delete("/{recommendation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation(
    *,
    db: AsyncSession = Depends(get_db),
    recommendation_id: int
) -> None:
    """
    Delete a recommendation.
    """
    # Get recommendation to delete
    result = await db.execute(
        select(RecommendationModel).where(RecommendationModel.id == recommendation_id)
    )
    db_recommendation = result.scalars().first()
    
    if not db_recommendation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recommendation not found"
        )
    
    # Delete and commit
    await db.delete(db_recommendation)
    await db.commit()
    
    return None
