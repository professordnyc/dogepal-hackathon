import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine

# Load environment
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Database URL
db_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dogepal.db")
print(f"Connecting to database: {db_url}")

async def test_connection():
    try:
        engine = create_async_engine(
            db_url,
            echo=True,
            future=True,
            connect_args={"check_same_thread": False},
        )
        async with engine.connect() as conn:
            print("Successfully connected to the database!")
            return True
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_connection())
