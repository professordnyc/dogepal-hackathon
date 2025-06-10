"""
Manual database test script with proper async handling.
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

async def test_db():
    """Test database operations."""
    from backend.app.db.session import init_db, get_engine, drop_tables, create_tables
    from sqlalchemy import text
    
    logger.info("Starting database test...")
    
    try:
        # Initialize database
        logger.info("1. Initializing database...")
        await init_db()
        engine = get_engine()
        
        # Test connection
        logger.info("2. Testing connection...")
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            assert result.scalar() == 1  # No need to await scalar()
            logger.info("✅ Connection successful")
        
        # Drop tables if they exist
        logger.info("3. Dropping existing tables...")
        await drop_tables()
        
        # Create tables
        logger.info("4. Creating tables...")
        await create_tables()
        
        # Verify tables
        logger.info("5. Verifying tables...")
        async with engine.connect() as conn:
            # Get list of tables
            result = await conn.execute(
                text("SELECT name FROM sqlite_master WHERE type='table'")
            )
            tables = [row[0] for row in await result.fetchall()]
            logger.info(f"Found tables: {tables}")
            
            # Check for required tables
            required = {"spending", "recommendation"}
            missing = required - set(tables)
            if missing:
                raise ValueError(f"Missing tables: {missing}")
            
            # Verify table schemas
            for table_name in required:
                result = await conn.execute(
                    text(f"PRAGMA table_info({table_name})")
                )
                columns = [row[1] for row in await result.fetchall()]
                logger.info(f"Table {table_name} columns: {columns}")
                if not columns:
                    raise ValueError(f"Table {table_name} has no columns")
            
            logger.info("✅ All required tables exist with valid schemas")
        
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
    """Run the test."""
    # Create a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Run the test
        success = loop.run_until_complete(test_db())
        return 0 if success else 1
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        return 1
    finally:
        # Clean up
        loop.close()
        asyncio.set_event_loop(None)

if __name__ == "__main__":
    sys.exit(main())
