"""
Simplified database test script.
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

async def main():
    """Main test function."""
    from backend.app.db.session import init_db, get_engine, drop_tables, create_tables
    
    logger.info("Starting database test...")
    
    # Initialize database
    logger.info("1. Initializing database...")
    await init_db()
    engine = get_engine()
    
    try:
        # Test connection
        logger.info("2. Testing connection...")
        async with engine.connect() as conn:
            result = await conn.execute("SELECT 1")
            assert (await result.scalar()) == 1
            logger.info("✅ Connection successful")
        
        # Drop and recreate tables
        logger.info("3. Dropping tables...")
        await drop_tables()
        
        logger.info("4. Creating tables...")
        await create_tables()
        
        # Verify tables
        logger.info("5. Verifying tables...")
        async with engine.connect() as conn:
            result = await conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in await result.fetchall()]
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

if __name__ == "__main__":
    # Create and run the event loop
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    finally:
        if loop.is_running():
            loop.close()
