from fastapi import APIRouter

from app.api.v1.endpoints import spending, recommendations

api_router = APIRouter()

# Include endpoints
api_router.include_router(
    spending.router,
    prefix="/spending",
    tags=["spending"]
)

api_router.include_router(
    recommendations.router,
    prefix="/recommendations",
    tags=["recommendations"]
)
