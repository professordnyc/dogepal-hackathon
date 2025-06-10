"""
Test database connection and basic operations.
"""
import asyncio
import sys
import logging
from pathlib import Path
from sqlalchemy import text

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

# Import database components
from backend.app.db.session import init_db, get_engine, drop_tables, create_tables

async def run_tests():
    """Run database tests."""
    engine = None
    try:
        logger.info("Starting database tests...")
        
        # Initialize the database
        logger.info("1. Initializing database...")
        await init_db()
        engine = get_engine()
        
        # Test basic connection
        async with engine.connect() as conn:
            logger.info("2. Testing database connection...")
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1, "Connection test failed"
            logger.info("✅ Database connection successful")
        
        # Test table operations
        logger.info("3. Testing table operations...")
        
        # Drop tables if they exist
        logger.info("   Dropping existing tables...")
        await drop_tables()
        
        # Create tables
        logger.info("   Creating tables...")
        await create_tables()
        
        # Verify tables were created
        async with engine.connect() as conn:
            logger.info("4. Verifying table creation...")
            # Check if spending table exists
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result]
            logger.info(f"   Found tables: {tables}")
            
            assert "spending" in tables, "Spending table not found"
            assert "recommendation" in tables, "Recommendation table not found"
            
        logger.info("✅ All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False
        
    finally:
        if engine:
            await engine.dispose()
            logger.info("Database engine disposed")

def main():
    """Run the tests."""
    # Create and set event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run the async tests
        success = loop.run_until_complete(run_tests())
        return 0 if success else 1
        
    except Exception as e:
        logger.critical(f"Fatal error in test execution: {e}", exc_info=True)
        return 1
        
    finally:
        # Clean up
        if loop.is_running():
            loop.stop()
        loop.close()
        asyncio.set_event_loop(None)

if __name__ == "__main__":
    sys.exit(main())
