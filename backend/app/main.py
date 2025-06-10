import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.api.v1.api import api_router
from app.db.session import engine, Base, init_db

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Handle application startup and shutdown events.
    
    This context manager ensures proper initialization and cleanup of resources.
    """
    # Startup
    logger.info("Starting application...")
    
    try:
        # Initialize database connection pool and session factory
        logger.info("Initializing database connection...")
        from app.db.session import init_db, get_engine
        await init_db()
        
        # Verify database is accessible
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            
        logger.info("Database connection established successfully")
        
        # Add any other startup tasks here
        
        # Yield control to the application
        yield
        
    except Exception as e:
        logger.critical(f"Failed to start application: {e}", exc_info=True)
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down application...")
        if 'engine' in locals():
            await engine.dispose()
            logger.info("Database connection pool closed")

# Create FastAPI app with lifespan
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## DOGEPAL - AI-Powered Government Spending Analysis
    
    A local-first spending analysis and optimization platform for government agencies.
    
    **Key Features:**
    - Vendor consolidation recommendations
    - Budget monitoring and alerts
    - Spending pattern analysis
    - Transparent AI explanations
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    # Disable automatic trailing slashes
    redirect_slashes=False
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors()},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception occurred")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# API endpoints
@app.get("/health")
async def health_check():
    """
    Check the health of the API service.
    
    Returns:
        dict: Status of the API including name, version, and status.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "healthy",
        "database": "connected" if engine is not None else "disconnected"
    }

@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information."""
    return f"""
    <html>
        <head>
            <title>{settings.PROJECT_NAME} API</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .card {{ 
                    background: #f9f9f9; 
                    padding: 20px; 
                    border-radius: 5px; 
                    margin: 10px 0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                a {{ color: #007bff; text-decoration: none; }}
                a:hover {{ text-decoration: underline; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to {settings.PROJECT_NAME} API</h1>
                <p>Version: {settings.VERSION}</p>
                
                <div class="card">
                    <h2>API Documentation</h2>
                    <ul>
                        <li><a href="/docs">Interactive API Docs (Swagger UI)</a></li>
                        <li><a href="/redoc">ReDoc Documentation</a></li>
                        <li><a href="/openapi.json">OpenAPI Schema</a></li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>API Endpoints</h2>
                    <ul>
                        <li><strong>Health Check:</strong> <a href="/health">/health</a></li>
                        <li><strong>API v1:</strong> <a href="/api/v1">/api/v1</a></li>
                    </ul>
                </div>
                
                <div class="card">
                    <h2>About</h2>
                    <p>This is a local-first spending analysis and optimization platform for government agencies.</p>
                </div>
            </div>
        </body>
    </html>
    """

# Custom OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description="""
        DOGEPAL - AI-Powered Government Spending Analysis
        
        This API provides endpoints for analyzing and optimizing government spending
        with AI-powered recommendations.
        """,
        routes=app.routes,
    )
    
    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Development server"},
    ]
    
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

# Set the custom OpenAPI schema
app.openapi = custom_openapi

# Mount static files for docs (only if directory exists)
static_dir = Path("static")
if static_dir.exists() and static_dir.is_dir():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static files mounted at /static")
else:
    logger.warning(f"Static directory {static_dir.absolute()} not found. Documentation UI may not work properly.")

if __name__ == "__main__":
    import uvicorn
    
    # Run the application using uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning",
        workers=1  # SQLite doesn't work well with multiple workers
    )
