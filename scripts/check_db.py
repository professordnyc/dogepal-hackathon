"""Script to check database schema and data."""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import inspect, select
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Import models
from app.models.spending import Spending, Recommendation
from app.db.session import Base, engine

async def check_database():
    print("🔍 Checking database schema...")
    
    # Create async engine and session
    async with engine.begin() as conn:
        # Check if tables exist
        result = await conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in result]
        print(f"\n📋 Database tables: {tables}")
        
        # Check spending table structure
        if 'spending' in tables:
            # Get table info
            result = await conn.execute("PRAGMA table_info(spending)")
            columns = await result.fetchall()
            
            print("\n📊 Spending table columns:")
            for column in columns:
                print(f"  - {column[1]}: {column[2]} (nullable: {not column[3]})")
            
            # Count records
            result = await conn.execute("SELECT COUNT(*) FROM spending")
            count = (await result.fetchone())[0]
            print(f"\n📈 Number of spending records: {count}")
            
            # Show first few records if they exist
            if count > 0:
                result = await conn.execute("SELECT * FROM spending LIMIT 3")
                print("\n📝 Sample spending records:")
                for row in await result.fetchall():
                    print(f"  - {row[0]}: {row[7]} - ${row[9]}")
        
        # Check recommendations table
        if 'recommendations' in tables:
            # Get table info
            result = await conn.execute("PRAGMA table_info(recommendations)")
            columns = await result.fetchall()
            
            print("\n📊 Recommendations table columns:")
            for column in columns:
                print(f"  - {column[1]}: {column[2]} (nullable: {not column[3]})")
            
            # Count records
            result = await conn.execute("SELECT COUNT(*) FROM recommendations")
            count = (await result.fetchone())[0]
            print(f"\n📈 Number of recommendation records: {count}")

async def main():
    try:
        await check_database()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
