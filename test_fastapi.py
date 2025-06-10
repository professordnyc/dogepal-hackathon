"""
Test the FastAPI application with database initialization.
"""
import asyncio
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Set environment variables
import os
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite+aiosqlite:///./test_dogepal.db"
os.environ["DEBUG"] = "True"

# Import FastAPI app and models
from backend.app.main import app
from backend.app.db.session import init_db, drop_tables, create_tables, get_async_session_factory
from backend.app.models.spending import Spending, Recommendation

async def init_test_db():
    """Initialize the database with test data."""
    logger.info("Initializing test database...")
    
    # Initialize the database connection
    await init_db()
    
    # Drop and recreate all tables
    await drop_tables()
    await create_tables()
    
    logger.info("✅ Test database initialized")

async def test_endpoints():
    """Test API endpoints."""
    import httpx
    
    base_url = "http://test"  # Using test client, so host doesn't matter
    
    async with httpx.AsyncClient(app=app, base_url=base_url) as client:
        # Test health check
        logger.info("\nTesting health check...")
        response = await client.get("/health")
        logger.info(f"Health check status: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        assert response.status_code == 200, "Health check failed"
        
        # Test root endpoint
        logger.info("\nTesting root endpoint...")
        response = await client.get("/")
        logger.info(f"Root status: {response.status_code}")
        logger.info(f"Response: {response.json()}")
        assert response.status_code == 200, "Root endpoint failed"
        
        # Test recommendations endpoint
        print("\nTesting recommendations endpoint...")
        response = await client.get("/api/v1/recommendations/")
        print(f"Recommendations status: {response.status_code}")
        print(f"Response: {response.json()}")

async def main():
    """Main test function."""
    try:
        # Initialize the test database
        await init_test_db()
        
        # Test endpoints
        await test_endpoints()
        
        logger.info("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        logger.exception("Test failure details:")
        return False
        
    finally:
        # Clean up resources if needed
        pass

if __name__ == "__main__":
    asyncio.run(main())
