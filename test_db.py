"""
Simple script to test database initialization and table creation.
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
    """Test database initialization and table creation."""
    from backend.app.db.session import init_db, get_engine, drop_tables, create_tables
    
    engine = None
    try:
        logger.info("1. Initializing database...")
        await init_db()
        engine = get_engine()
        
        logger.info("2. Testing connection...")
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            assert (await result.scalar()) == 1
            logger.info("✅ Connection successful")
        
        logger.info("3. Dropping existing tables...")
        await drop_tables()
        
        logger.info("4. Creating tables...")
        await create_tables()
        
        logger.info("5. Verifying tables...")
        async with engine.connect() as conn:
            # Check if tables exist
            result = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in await result.fetchall()]
            logger.info(f"Found tables: {tables}")
            
            required_tables = {"spending", "recommendation"}
            missing_tables = required_tables - set(tables)
            
            if missing_tables:
                raise ValueError(f"Missing required tables: {missing_tables}")
            
            logger.info("✅ All required tables exist")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False
        
    finally:
        if engine:
            await engine.dispose()
            logger.info("Database engine disposed")

def main():
    """Run the test."""
    try:
        # Create a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the test
        success = loop.run_until_complete(test_database())
        return 0 if success else 1
        
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1
        
    finally:
        # Clean up
        if loop.is_running():
            loop.stop()
        loop.close()
        asyncio.set_event_loop(None)

if __name__ == "__main__":
    sys.exit(main())
