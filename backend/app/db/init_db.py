import asyncio
import logging
from pathlib import Path
import sys

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from app.db.session import engine, Base
from app.models.spending import Spending, Recommendation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_models():
    """Initialize database tables."""
    try:
        # Create all tables
        async with engine.begin() as conn:
            logger.info("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully!")
            
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    print("Initializing database...")
    asyncio.run(init_models())
    print("Database initialization complete!")
