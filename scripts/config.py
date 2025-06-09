"""Configuration for database initialization script."""
import os

# Set environment variables
os.environ["SQLALCHEMY_DATABASE_URI"] = "sqlite+aiosqlite:///./dogepal.db"
os.environ["DEBUG"] = "True"

# Add any other required environment variables here
