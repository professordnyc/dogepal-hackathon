#!/usr/bin/env python3
"""
Main entry point for the DOGEPAL application.

This script initializes the database, loads sample data, and starts the FastAPI server.
"""
import asyncio
import os
import sys
import uvicorn
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

# Set environment variables
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite+aiosqlite:///./dogepal.db"
os.environ["DEBUG"] = "True"

# Import FastAPI app
from backend.app.main import app
from backend.app.db.session import init_db, create_tables, drop_tables, get_engine
from backend.app.db.init_db import create_sample_data

async def initialize_database():
    """Initialize the database with sample data."""
    print("Initializing database...")
    
    # Initialize database engine and session factory
    await init_db()
    
    # Drop and recreate all tables
    await drop_tables()
    await create_tables()
    
    # Create sample data
    print("Creating sample data...")
    await create_sample_data()
    print("✅ Database initialized with sample data")

if __name__ == "__main__":
    # Initialize the database
    asyncio.run(initialize_database())
    
    # Start the FastAPI server
    print("\nStarting FastAPI server...")
    print("Access the API documentation at: http://localhost:8000/docs\n")
    
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
