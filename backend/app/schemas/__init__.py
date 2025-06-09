# Import all schemas to make them available when importing from app.schemas
from app.schemas.spending import SpendingCreate, SpendingUpdate, SpendingInDB, Spending
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationUpdate,
    RecommendationInDB,
    Recommendation,
    RecommendationWithSpending
)

# Make these available when importing from app.schemas
__all__ = [
    'SpendingCreate',
    'SpendingUpdate',
    'SpendingInDB',
    'Spending',
    'RecommendationCreate',
    'RecommendationUpdate',
    'RecommendationInDB',
    'Recommendation',
    'RecommendationWithSpending'
]
