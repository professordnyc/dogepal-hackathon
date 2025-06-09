#!/usr/bin/env python3
"""
Initialize the database with sample data using the existing init_db module.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Set environment variables
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite+aiosqlite:///./dogepal.db"
os.environ["DEBUG"] = "True"

# Import the init function from the existing module
from app.db.init_db import init

async def main():
    print("Starting database initialization...")
    try:
        await init()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
