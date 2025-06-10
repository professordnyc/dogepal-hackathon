from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
import numpy as np
import json
from datetime import datetime, timedelta

from app.db.session import get_async_session
from app.models.spending import Spending as SpendingModel, Recommendation as RecommendationModel
from app.schemas.recommendation import (
    Recommendation, RecommendationCreate, RecommendationUpdate,
    RecommendationWithSpending, RecommendationStats, RecommendationStatus, RecommendationType
)
from app.schemas.spending import CategoryEnum as Category, DepartmentEnum as Department

router = APIRouter(prefix="", include_in_schema=True)

# Helper function to calculate z-score
def calculate_zscore(value, mean, std):
    if std == 0:
        return 0
    return (value - mean) / std

@router.get("/", response_model=List[RecommendationWithSpending])
async def get_recommendations(
    *,
    db: AsyncSession = Depends(get_async_session),
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
    try:
        print("DEBUG: Entering get_recommendations endpoint")
        # Build base query with join to spending
        query = (
            select(
                RecommendationModel,
                SpendingModel.amount.label("spending_amount"),
                SpendingModel.category.label("spending_category"),
                SpendingModel.vendor.label("spending_vendor"),
                SpendingModel.spending_date.label("spending_date"),
            )
            .join(SpendingModel, RecommendationModel.transaction_id == SpendingModel.transaction_id)
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
        
        print(f"DEBUG: Executing query: {query}")
        result = await db.execute(query)
        recommendations_with_spending = result.mappings().all()
        print(f"DEBUG: Found {len(recommendations_with_spending)} recommendations")
        
        # Convert to Pydantic model
        recommendations = []
        for row in recommendations_with_spending:
            rec_dict = dict(row["Recommendation"].__dict__)
            rec_dict["spending_amount"] = row["spending_amount"]
            rec_dict["spending_category"] = row["spending_category"]
            rec_dict["spending_vendor"] = row["spending_vendor"]
            rec_dict["spending_date"] = row["spending_date"]
            recommendations.append(RecommendationWithSpending(**rec_dict))
        
        return recommendations
    except Exception as e:
        print(f"ERROR in get_recommendations: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving recommendations: {str(e)}"
        )
    
    # This code is unreachable due to the try/except block above

@router.get("/generate", response_model=List[Recommendation])
async def generate_recommendations(
    *,
    db: AsyncSession = Depends(get_async_session),
    min_confidence: float = 0.7,
) -> List[Recommendation]:
    """
    Generate new spending recommendations based on analysis of spending data.
    Uses the HP AI Studio-integrated SpendingRecommender model for intelligent recommendations.
    """
    try:
        print("DEBUG: Entering generate_recommendations endpoint")
        # Get all spending data for analysis
        result = await db.execute(select(SpendingModel))
        all_spending = result.scalars().all()
        print(f"DEBUG: Found {len(all_spending)} spending records")
        
        if not all_spending:
            print("DEBUG: No spending records found, returning empty list")
            return []
        
        # Import the SpendingRecommender model
        try:
            print("DEBUG: Attempting to import SpendingRecommender")
            from models.spending_recommender import SpendingRecommender
        except ImportError:
            # Handle relative import if needed
            import sys
            import os
            from pathlib import Path
            
            # Add the project root to path
            project_root = Path(__file__).parent.parent.parent.parent.parent
            print(f"DEBUG: Adding project root to path: {project_root}")
            if str(project_root) not in sys.path:
                sys.path.append(str(project_root))
            
            try:
                from models.spending_recommender import SpendingRecommender
                print("DEBUG: Successfully imported SpendingRecommender after path adjustment")
            except ImportError as e:
                print(f"ERROR: Failed to import SpendingRecommender: {e}")
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
                print("DEBUG: Using fallback SpendingRecommender implementation")
        
        # Convert to list of dicts for easier processing
        print("DEBUG: Converting spending data to dict format for model")
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
        print("DEBUG: Initializing SpendingRecommender model")
        recommender = SpendingRecommender()
        
        # Generate recommendations using the model
        print("DEBUG: Generating recommendations using model")
        model_recommendations = recommender.predict(spending_data)
        print(f"DEBUG: Model returned {len(model_recommendations) if model_recommendations else 0} recommendations")
        
        # Filter recommendations by confidence score
        filtered_recommendations = [
            rec for rec in model_recommendations 
            if rec and rec.get('confidence_score', 0) >= min_confidence
        ]
        print(f"DEBUG: Filtered to {len(filtered_recommendations)} recommendations with confidence >= {min_confidence}")
        
        # Check if we already have these recommendations in the database
        new_recommendations = []
        for rec in filtered_recommendations:
            # Create a new recommendation
            spending_id = None
            
            # Find the spending record this recommendation is for
            if 'transaction_id' in rec:
                # Look up spending by transaction ID
                result = await db.execute(
                    select(SpendingModel).where(SpendingModel.id == rec['transaction_id'])
                )
                spending = result.scalars().first()
                if spending:
                    spending_id = spending.id
            
            # If no specific transaction ID, use the first spending record
            if not spending_id and all_spending:
                spending_id = all_spending[0].id
            
            if not spending_id:
                print(f"DEBUG: Skipping recommendation - no spending ID found for {rec.get('title')}")
                continue
            
            # Check if a similar recommendation already exists
            result = await db.execute(
                select(RecommendationModel).where(
                    RecommendationModel.spending_id == spending_id,
                    RecommendationModel.type == rec.get('type', 'unknown')
                )
            )
            existing_rec = result.scalars().first()
            
            if existing_rec:
                # Skip if we already have this recommendation
                print(f"DEBUG: Skipping recommendation - already exists for spending {spending_id}")
                continue
            
            # Map recommendation type to enum
            rec_type = RecommendationType.unknown
            if rec.get('type') == 'cost_saving':
                rec_type = RecommendationType.cost_saving
            elif rec.get('type') == 'budget_optimization':
                rec_type = RecommendationType.budget_optimization
            elif rec.get('type') == 'vendor_consolidation':
                rec_type = RecommendationType.vendor_consolidation
            elif rec.get('type') == 'spending_anomaly':
                rec_type = RecommendationType.spending_anomaly
            elif rec.get('type') == 'policy_violation':
                rec_type = RecommendationType.policy_violation
            
            # Map confidence score to priority
            priority = "low"
            if rec.get('confidence_score', 0) >= 0.8:
                priority = "high"
            elif rec.get('confidence_score', 0) >= 0.6:
                priority = "medium"
            
            # Create recommendation object
            new_rec = RecommendationModel(
                spending_id=spending_id,
                type=rec_type,
                title=rec.get('title', 'Untitled Recommendation'),
                description=rec.get('description', ''),
                confidence_score=rec.get('confidence_score', 0.0),
                priority=priority,
                status=RecommendationStatus.pending,
                explanation=rec.get('explanation', ''),
                calculation=rec.get('calculation', ''),
                factors=json.dumps(rec.get('factors', [])),
                suggested_action=rec.get('suggested_action', ''),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # Add to database
            db.add(new_rec)
            new_recommendations.append(new_rec)
        
        # Commit changes
        print(f"DEBUG: Committing {len(new_recommendations)} new recommendations to database")
        await db.commit()
        
        # Refresh to get IDs
        for rec in new_recommendations:
            await db.refresh(rec)
        
        # Convert to Pydantic models
        return [Recommendation.from_orm(rec) for rec in new_recommendations]
        
    except Exception as e:
        print(f"ERROR in generate_recommendations: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendations: {str(e)}"
        )

@router.get("/stats", response_model=RecommendationStats)
async def get_recommendation_stats(
    *,
    db: AsyncSession = Depends(get_async_session),
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
    db: AsyncSession = Depends(get_async_session),
    recommendation_id: str,
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
    db: AsyncSession = Depends(get_async_session),
    recommendation_id: str
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
