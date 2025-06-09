from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
import numpy as np
from datetime import datetime, timedelta

from app.db.session import get_db
from app.models.spending import Spending as SpendingModel, Recommendation as RecommendationModel
from app.schemas.recommendation import (
    Recommendation, RecommendationCreate, RecommendationUpdate,
    RecommendationWithSpending, RecommendationStats, RecommendationStatus, RecommendationType
)
from app.schemas.spending import Category, Department

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
    This is where the AI/ML magic happens!
    """
    # Get all spending data for analysis
    result = await db.execute(select(SpendingModel))
    all_spending = result.scalars().all()
    
    if not all_spending:
        return []
    
    # Convert to list of dicts for easier processing
    spending_data = [
        {
            "id": s.id,
            "amount": s.amount,
            "category": s.category,
            "vendor": s.vendor,
            "date": s.date,
            "department": s.department
        }
        for s in all_spending
    ]
    
    # Group spending by category for analysis
    categories = {}
    for item in spending_data:
        if item["category"] not in categories:
            categories[item["category"]] = []
        categories[item["category"]].append(item["amount"])
    
    # Calculate statistics for each category
    category_stats = {}
    for category, amounts in categories.items():
        if not amounts:
            continue
            
        amounts = np.array(amounts)
        category_stats[category] = {
            "mean": float(np.mean(amounts)),
            "median": float(np.median(amounts)),
            "std": float(np.std(amounts)) if len(amounts) > 1 else 0,
            "count": len(amounts),
            "total": float(np.sum(amounts))
        }
    
    # Generate recommendations
    new_recommendations = []
    
    # 1. Find unusually large transactions
    for item in spending_data:
        category = item["category"]
        if category not in category_stats:
            continue
            
        stats = category_stats[category]
        if stats["std"] == 0:
            continue
            
        z_score = calculate_zscore(item["amount"], stats["mean"], stats["std"])
        
        # If transaction is more than 2 standard deviations above the mean
        if z_score > 2:
            confidence = min(0.99, z_score / 4)  # Cap confidence at 0.99
            if confidence >= min_confidence:
                recommendation = RecommendationModel(
                    spending_id=item["id"],
                    recommendation_type=RecommendationType.SPENDING_ANOMALY,
                    title=f"Unusually large {category} transaction",
                    description=(
                        f"A {category} transaction of ${item['amount']:,.2f} "
                        f"is {z_score:.1f} standard deviations above the category average "
                        f"of ${stats['mean']:,.2f}."
                    ),
                    potential_savings=item["amount"] - stats["mean"],
                    confidence_score=confidence,
                    explanation=(
                        "This recommendation is based on statistical analysis of spending "
                        f"in the {category} category. The amount significantly exceeds "
                        "the typical transaction value for this category."
                    ),
                    suggested_action=(
                        "Review this transaction for potential errors or opportunities "
                        "for cost savings. Consider negotiating with the vendor or "
                        "finding alternative suppliers."
                    ),
                    status=RecommendationStatus.PENDING
                )
                new_recommendations.append(recommendation)
    
    # 2. Find potential vendor consolidation opportunities
    vendor_spending = {}
    for item in spending_data:
        vendor = item["vendor"].lower().strip()
        if vendor not in vendor_spending:
            vendor_spending[vendor] = 0
        vendor_spending[vendor] += item["amount"]
    
    # Sort vendors by total spending
    sorted_vendors = sorted(vendor_spending.items(), key=lambda x: x[1], reverse=True)
    
    # If there are many small vendors, suggest consolidation
    if len(sorted_vendors) > 5:
        small_vendors = [v for v in sorted_vendors if v[1] < 1000]  # Arbitrary threshold
        if len(small_vendors) > 3:  # If multiple small vendors
            total_small_spend = sum(v[1] for v in small_vendors)
            confidence = min(0.9, len(small_vendors) / 10)  # Scale confidence with number of vendors
            
            if confidence >= min_confidence:
                recommendation = RecommendationModel(
                    spending_id=None,  # Not tied to a specific transaction
                    recommendation_type=RecommendationType.VENDOR_CONSOLIDATION,
                    title="Opportunity for vendor consolidation",
                    description=(
                        f"{len(small_vendors)} vendors account for ${total_small_spend:,.2f} "
                        f"in spending. Consider consolidating with fewer vendors for better pricing."
                    ),
                    potential_savings=total_small_spend * 0.1,  # 10% potential savings estimate
                    confidence_score=confidence,
                    explanation=(
                        "Vendor consolidation can lead to volume discounts, "
                        "reduced administrative overhead, and stronger supplier relationships. "
                        "This recommendation is based on analysis of current vendor spending patterns."
                    ),
                    suggested_action=(
                        "Identify key vendors that can provide a broader range of products/services. "
                        "Negotiate volume discounts with preferred vendors and phase out underperforming "
                        "or redundant suppliers."
                    ),
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
