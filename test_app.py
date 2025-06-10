"""
Test the FastAPI application with database initialization.
"""
import asyncio
import sys
from pathlib import Path

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
from backend.app.db.session import engine, Base
from backend.app.models.spending import Spending, Recommendation

async def init_db():
    """Initialize the database with test data."""
    print("\nInitializing database...")
    
    # Drop and recreate all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("✅ Database initialized")

async def test_endpoints():
    """Test API endpoints."""
    import httpx
    
    base_url = "http://localhost:8000"
    
    async with httpx.AsyncClient(app=app, base_url=base_url) as client:
        # Test health check
        print("\nTesting health check...")
        response = await client.get("/health")
        print(f"Health check status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test root endpoint
        print("\nTesting root endpoint...")
        response = await client.get("/")
        print(f"Root status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        # Test recommendations endpoint
        print("\nTesting recommendations endpoint...")
        response = await client.get("/api/v1/recommendations/")
        print(f"Recommendations status: {response.status_code}")
        print(f"Response: {response.json()}")

async def main():
    """Main test function."""
    try:
        # Initialize database
        await init_db()
        
        # Test API endpoints
        await test_endpoints()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    finally:
        # Clean up
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
