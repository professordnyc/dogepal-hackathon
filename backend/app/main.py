import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, Base, init_db, async_session
from app.core.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Custom exception handler
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

# Custom 500 error handler
async def server_error_handler(request, exc):
    logger.error(f"Server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="""
        ## DOGEPAL API
        
        AI-powered spending analysis and optimization for local governments.
        
        ### Features:
        - Vendor consolidation recommendations
        - Budget monitoring and alerts
        - Spending pattern analysis
        - Transparent AI explanations
        """,
        routes=app.routes,
    )
    
    # Add custom error responses
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            responses = method.get("responses", {})
            if "400" not in responses:
                responses["400"] = {"description": "Bad Request"}
            if "401" not in responses:
                responses["401"] = {"description": "Unauthorized"}
            if "422" not in responses:
                responses["422"] = {"description": "Validation Error"}
            if "500" not in responses:
                responses["500"] = {"description": "Internal Server Error"}
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Custom docs endpoints functions (will be attached to app later)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{settings.PROJECT_NAME} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    # Startup
    logger.info("Starting application...")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        await init_db()
        logger.info("Database initialized successfully")
        
        # Add any other startup tasks here
        
        yield
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down application...")
        # Add any cleanup tasks here

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## DOGEPAL - AI-Powered Spending Optimization
    
    A local-first spending analysis and optimization platform for government agencies.
    
    **Key Features:**
    - Vendor consolidation recommendations
    - Budget monitoring and alerts
    - Spending pattern analysis
    - Transparent AI explanations
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=None,  # Disable default docs to use custom
    redoc_url=None,  # Disable default redoc to use custom
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(500, server_error_handler)

# Add custom docs routes
app.get("/docs", include_in_schema=False)(custom_swagger_ui_html)
app.get("/redoc", include_in_schema=False)(redoc_html)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount static files for docs (only if directory exists)
static_dir = Path("static")
if static_dir.exists() and static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info("Static files mounted at /static")
else:
    logger.warning(f"Static directory {static_dir.absolute()} not found. Documentation UI may not work properly.")

# Health check endpoint with detailed status
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API is running and healthy",
    response_description="API health status",
    tags=["System"]
)
async def health_check():
    """
    Check the health of the API service.
    
    Returns:
        dict: Status of the API including name, version, and status.
    """
    return {
        "status": "healthy",
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
    }

# Root endpoint with API documentation links
@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    include_in_schema=False
)
async def root():
    """Root endpoint with API documentation links."""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "health": "/health"
    }

# Set custom OpenAPI schema
app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    
    # Run with auto-reload in development
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug",
        workers=1  # SQLite doesn't work well with multiple workers
    )
