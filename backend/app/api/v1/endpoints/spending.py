from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, or_

from app.db.session import get_db
from app.models.spending import Spending as SpendingModel
from app.schemas.spending import (
    Spending, SpendingCreate, SpendingUpdate, SpendingInDB,
    Category, Department
)

router = APIRouter()

@router.post("/", response_model=Spending, status_code=status.HTTP_201_CREATED)
async def create_spending(
    *,
    db: AsyncSession = Depends(get_db),
    spending_in: SpendingCreate
) -> Spending:
    """
    Create a new spending record.
    """
    # Create new spending instance
    db_spending = SpendingModel(**spending_in.model_dump())
    
    # Add to database
    db.add(db_spending)
    await db.commit()
    await db.refresh(db_spending)
    
    return db_spending

@router.get("/", response_model=List[Spending])
async def read_spendings(
    *,
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[Category] = None,
    department: Optional[Department] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Spending]:
    """
    Retrieve spending records with optional filtering.
    """
    query = select(SpendingModel)
    
    # Apply filters
    if category:
        query = query.where(SpendingModel.category == category)
    if department:
        query = query.where(SpendingModel.department == department)
    if min_amount is not None:
        query = query.where(SpendingModel.amount >= min_amount)
    if max_amount is not None:
        query = query.where(SpendingModel.amount <= max_amount)
    if start_date:
        query = query.where(SpendingModel.date >= start_date)
    if end_date:
        query = query.where(SpendingModel.date <= end_date)
    if search:
        search_filter = or_(
            SpendingModel.vendor.ilike(f"%{search}%"),
            SpendingModel.description.ilike(f"%{search}%")
        )
        query = query.where(search_filter)
    
    # Apply pagination
    query = query.offset(skip).limit(limit).order_by(SpendingModel.date.desc())
    
    # Execute query
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{spending_id}", response_model=Spending)
async def read_spending(
    *,
    db: AsyncSession = Depends(get_db),
    spending_id: int
) -> Spending:
    """
    Get a specific spending record by ID.
    """
    result = await db.execute(
        select(SpendingModel).where(SpendingModel.id == spending_id)
    )
    spending = result.scalars().first()
    
    if not spending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spending record not found"
        )
    
    return spending

@router.put("/{spending_id}", response_model=Spending)
async def update_spending(
    *,
    db: AsyncSession = Depends(get_db),
    spending_id: int,
    spending_in: SpendingUpdate
) -> Spending:
    """
    Update a spending record.
    """
    # Get existing spending
    result = await db.execute(
        select(SpendingModel).where(SpendingModel.id == spending_id)
    )
    db_spending = result.scalars().first()
    
    if not db_spending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spending record not found"
        )
    
    # Update model
    update_data = spending_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_spending, field, value)
    
    # Save changes
    await db.commit()
    await db.refresh(db_spending)
    
    return db_spending

@router.delete("/{spending_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_spending(
    *,
    db: AsyncSession = Depends(get_db),
    spending_id: int
) -> None:
    """
    Delete a spending record.
    """
    # Get spending to delete
    result = await db.execute(
        select(SpendingModel).where(SpendingModel.id == spending_id)
    )
    db_spending = result.scalars().first()
    
    if not db_spending:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spending record not found"
        )
    
    # Delete and commit
    await db.delete(db_spending)
    await db.commit()
    
    return None

@router.get("/stats/summary", response_model=dict)
async def get_spending_summary(
    *,
    db: AsyncSession = Depends(get_db),
    category: Optional[Category] = None,
    department: Optional[Department] = None,
) -> dict:
    """
    Get summary statistics for spending.
    """
    # Base query
    query = select(
        func.count(SpendingModel.id).label("total_transactions"),
        func.sum(SpendingModel.amount).label("total_amount"),
        func.avg(SpendingModel.amount).label("average_amount"),
        func.max(SpendingModel.amount).label("max_amount"),
        func.min(SpendingModel.amount).label("min_amount"),
    )
    
    # Apply filters
    if category:
        query = query.where(SpendingModel.category == category)
    if department:
        query = query.where(SpendingModel.department == department)
    
    result = await db.execute(query)
    stats = result.mappings().first()
    
    # Get category distribution
    category_query = select(
        SpendingModel.category,
        func.count(SpendingModel.id).label("count"),
        func.sum(SpendingModel.amount).label("total")
    )
    
    if department:
        category_query = category_query.where(SpendingModel.department == department)
    
    category_query = category_query.group_by(SpendingModel.category)
    category_result = await db.execute(category_query)
    category_stats = category_result.mappings().all()
    
    return {
        "total_transactions": stats["total_transactions"] or 0,
        "total_amount": float(stats["total_amount"] or 0),
        "average_amount": float(stats["average_amount"] or 0),
        "max_amount": float(stats["max_amount"] or 0),
        "min_amount": float(stats["min_amount"] or 0),
        "category_distribution": [
            {"category": item["category"], "count": item["count"], "total": float(item["total"] or 0)}
            for item in category_stats
        ]
    }
