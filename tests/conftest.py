"""
Pytest configuration and fixtures for testing the DOGEPAL application.
"""
import asyncio
import pytest
from pathlib import Path
import sys
from typing import AsyncGenerator, Dict, Any
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import event

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import after adding to path
from app.core.config import settings
from app.db.session import Base, get_db, async_session
from app.main import app

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Override the database URL for testing
settings.SQLALCHEMY_DATABASE_URI = TEST_DATABASE_URL

# Create test engine and session factory
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    future=True,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Fixture to create the database schema
@pytest.fixture(scope="session")
def event_loop():
    ""
    Create an instance of the default event loop for the test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Fixture to initialize the test database
@pytest.fixture(scope="session", autouse=True)
async def init_test_db():
    """
    Initialize the test database with all tables.
    This runs once per test session.
    """
    async with test_engine.begin() as conn:
        # Drop all tables if they exist
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    # This is a teardown that will run after all tests complete
    yield
    
    # Cleanup: Drop all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Fixture to get a database session
@pytest.fixture
def db_session(init_test_db) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a new database session with a savepoint, and the rollback to it
    after the test completes.
    """
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Begin a nested transaction (using SAVEPOINT).
    nested = await connection.begin_nested()
    
    # If the application code calls session.commit, it will end the nested
    # transaction. Need to start a new one when that happens.
    @event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()
    
    yield session
    
    # Cleanup
    await session.close()
    await transaction.rollback()
    await connection.close()

# Fixture to override the get_db dependency
@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override the get_db dependency for testing."""
    async def _get_db():
        try:
            yield db_session
        finally:
            pass  # Don't close the session here, let the fixture handle it
    
    return _get_db

# Fixture to get a test client
@pytest.fixture
def client(override_get_db):
    """Create a test client that uses the override_get_db fixture."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides = {}

# Fixture for test data
@pytest.fixture
def test_spending_data() -> Dict[str, Any]:
    """Return sample spending data for testing."""
    return {
        "transaction_id": "TXN12345",
        "user_id": "U1001",
        "user_type": "solopreneur",
        "department": "Technology",
        "project_name": "AI Skills Initiative",
        "borough": "Manhattan",
        "date": "2023-06-15",
        "vendor": "TechSolutions",
        "category": "software",
        "amount": 4999.99,
        "justification": "Annual subscription renewal",
        "approval_status": "approved",
    }

@pytest.fixture
def test_recommendation_data() -> Dict[str, Any]:
    """Return sample recommendation data for testing."""
    return {
        "id": "REC1001",
        "transaction_id": "TXN12345",
        "type": "vendor_consolidation",
        "title": "Vendor Consolidation Opportunity",
        "description": "Consolidate software vendors for better pricing",
        "potential_savings": 750.0,
        "confidence_score": 0.85,
        "priority": "high",
        "explanation": "Consolidating with TechSolutions could save ~15% on costs",
        "status": "pending",
        "metadata": {"savings_percent": 15, "vendor_count": 3}
    }
