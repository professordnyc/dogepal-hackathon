"""
Test database operations with proper SQLAlchemy 2.0 async patterns.
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

async def test_database():
    """Test database operations."""
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine
    
    # Create a new engine for testing
    engine = create_async_engine(
        os.environ["SQLALCHEMY_DATABASE_URI"],
        echo=True,
        future=True
    )
    
    try:
        # Test connection
        logger.info("1. Testing database connection...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1
            logger.info("✅ Connection successful")
        
        # Create tables
        logger.info("2. Creating tables...")
        from backend.app.models.spending import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        
        # Verify tables
        logger.info("3. Verifying tables...")
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in result]
            logger.info(f"Found tables: {tables}")
            
            required = {"spending", "recommendation"}
            missing = required - set(tables)
            if missing:
                raise ValueError(f"Missing tables: {missing}")
            
            logger.info("✅ All required tables exist")
        
        logger.info("✅ All tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False
        
    finally:
        await engine.dispose()
        logger.info("Database engine disposed")

def main():
    """Run the test."""
    try:
        # Create and run event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(test_database())
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
