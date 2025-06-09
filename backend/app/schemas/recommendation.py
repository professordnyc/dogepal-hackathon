from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

# Enums for recommendation types and statuses
class RecommendationType(str, Enum):
    COST_SAVING = "cost_saving"
    BUDGET_OPTIMIZATION = "budget_optimization"
    VENDOR_CONSOLIDATION = "vendor_consolidation"
    SPENDING_ANOMALY = "spending_anomaly"
    POLICY_VIOLATION = "policy_violation"

class RecommendationStatus(str, Enum):
    PENDING = "pending"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"
    ARCHIVED = "archived"

# Base schema with common fields
class RecommendationBase(BaseModel):
    spending_id: int = Field(..., description="ID of the related spending record")
    recommendation_type: RecommendationType = Field(..., description="Type of recommendation")
    title: str = Field(..., max_length=200, description="Short title for the recommendation")
    description: Optional[str] = Field(None, description="Detailed description")
    potential_savings: float = Field(..., ge=0, description="Potential savings amount")
    confidence_score: float = Field(..., ge=0, le=1, description="Confidence level (0-1)")
    explanation: str = Field(..., description="Technical explanation of the recommendation")
    suggested_action: str = Field(..., description="Recommended action to take")
    status: RecommendationStatus = Field(default=RecommendationStatus.PENDING, description="Current status of the recommendation")

# Schema for creating a new recommendation
class RecommendationCreate(RecommendationBase):
    pass

# Schema for updating an existing recommendation
class RecommendationUpdate(BaseModel):
    recommendation_type: Optional[RecommendationType] = None
    title: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    potential_savings: Optional[float] = Field(None, ge=0)
    confidence_score: Optional[float] = Field(None, ge=0, le=1)
    explanation: Optional[str] = None
    suggested_action: Optional[str] = None
    status: Optional[RecommendationStatus] = None

# Base schema for database representation
class RecommendationInDBBase(RecommendationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for returning recommendation data
class Recommendation(RecommendationInDBBase):
    pass

# Schema for recommendation with related spending data
class RecommendationWithSpending(Recommendation):
    spending_amount: float
    spending_category: str
    spending_vendor: str
    spending_date: datetime
    
    class Config:
        from_attributes = True

# Schema for recommendation statistics
class RecommendationStats(BaseModel):
    total_recommendations: int
    total_potential_savings: float
    recommendations_by_type: dict[RecommendationType, int]
    recommendations_by_status: dict[RecommendationStatus, int]
