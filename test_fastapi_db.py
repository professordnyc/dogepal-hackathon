"""
Test FastAPI application with database integration.
"""
import asyncio
import logging
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
from backend.app.db.session import init_db, get_engine
from backend.app.models.spending import Base, Spending, Recommendation

async def setup_test_db():
    """Set up test database with tables."""
    logger.info("Setting up test database...")
    
    # Initialize database
    await init_db()
    engine = get_engine()
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("Test database setup complete")
    return engine

async def test_spending_endpoints():
    """Test spending-related API endpoints."""
    from fastapi.testclient import TestClient
    import json
    
    # Setup test client
    client = TestClient(app)
    
    # Test GET /api/v1/spending/ (empty)
    response = client.get("/api/v1/spending/")
    assert response.status_code == 200
    assert response.json() == []
    
    # Test POST /api/v1/spending/
    test_spending = {
        "transaction_id": "test123",
        "user_id": "test_user",
        "user_type": "test",
        "department": "IT",
        "project_name": "Test Project",
        "borough": "Manhattan",
        "spending_date": "2025-01-01",
        "vendor": "Test Vendor",
        "category": "Software",
        "amount": 100.0,
        "justification": "Test purchase",
        "approval_status": "approved"
    }
    
    response = client.post(
        "/api/v1/spending/",
        json=test_spending
    )
    assert response.status_code == 200
    created_spending = response.json()
    assert created_spending["transaction_id"] == "test123"
    
    # Test GET /api/v1/spending/{transaction_id}
    response = client.get(f"/api/v1/spending/test123")
    assert response.status_code == 200
    assert response.json()["transaction_id"] == "test123"
    
    logger.info("✅ Spending endpoints test passed")
    return True

async def run_tests():
    """Run all tests."""
    try:
        # Setup test database
        engine = await setup_test_db()
        
        # Run tests
        await test_spending_endpoints()
        
        logger.info("✅ All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False
    finally:
        if 'engine' in locals():
            await engine.dispose()
            logger.info("Database engine disposed")

def main():
    """Run the test suite."""
    try:
        # Create and run event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(run_tests())
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return False
    finally:
        # Clean up
        if loop.is_running():
            loop.stop()
        loop.close()
        asyncio.set_event_loop(None)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
