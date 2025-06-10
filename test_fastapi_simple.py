"""
Simple test for FastAPI application.
"""
import sys
import logging
from fastapi.testclient import TestClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import the FastAPI app
from backend.app.main import app

def test_read_root():
    """Test the root endpoint."""
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    logger.info("✅ Root endpoint test passed")

def test_health_check():
    """Test the health check endpoint."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    logger.info("✅ Health check test passed")

def main():
    """Run the tests."""
    try:
        logger.info("Starting FastAPI tests...")
        test_read_root()
        test_health_check()
        logger.info("✅ All FastAPI tests passed!")
        return True
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
