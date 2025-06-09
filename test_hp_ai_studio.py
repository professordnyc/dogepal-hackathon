"""
Test script for HP AI Studio integration with the DOGEPAL Spending Recommender.

This script tests the end-to-end workflow:
1. Training the model with MLflow tracking
2. Registering the model in the model registry
3. Loading the model for inference
"""
import os
import sys
import argparse
import logging
import mlflow
import pandas as pd
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.hp_ai_studio_config import get_mlflow_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def test_model_inference(model_uri):
    """Test model inference with sample data."""
    logger.info("Testing model inference...")
    
    # Sample test data
    test_data = [
        {
            "transaction_id": "TXN1001",
            "amount": 1500.00,
            "category": "office supplies",
            "vendor": "OfficeMax",
            "department": "Finance",
            "project_name": "Office Upgrade 2025",
            "borough": "Manhattan"
        },
        {
            "transaction_id": "TXN2001",
            "amount": 35000.00,
            "category": "services",
            "vendor": "Tech Solutions",
            "department": "IT",
            "project_name": "Network Upgrade",
            "borough": "Brooklyn"
        }
    ]
    
    # Load the model
    model = mlflow.pyfunc.load_model(model_uri)
    
    # Make predictions
    predictions = model.predict(test_data)
    
    # Display results
    logger.info("\nTest Results:")
    logger.info("-" * 50)
    for i, (input_data, prediction) in enumerate(zip(test_data, predictions)):
        logger.info(f"Test Case {i+1}:")
        logger.info(f"  Input: {input_data}")
        logger.info(f"  Prediction: {prediction}")
        logger.info("-" * 50)

def main():
    """Main function to test HP AI Studio integration."""
    parser = argparse.ArgumentParser(description="Test HP AI Studio integration")
    parser.add_argument(
        "--model-uri",
        type=str,
        help="URI of the model to test (e.g., 'models:/dogepal_spending_recommender/Production')",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Train and register a new model before testing"
    )
    
    args = parser.parse_args()
    
    # Get MLflow config
    mlflow_config = get_mlflow_config()
    mlflow.set_tracking_uri(mlflow_config["tracking_uri"])
    
    # Train and register a new model if requested
    if args.train:
        logger.info("Training and registering a new model...")
        import subprocess
        subprocess.run([
            sys.executable, "train_hp_ai_studio.py",
            "--confidence-threshold", "0.7",
            "--register-model"
        ], check=True)
        
        # Use the newly registered model
        model_uri = f"models:/{mlflow_config['registered_model_name']}/{mlflow_config['model_stage'] or 'None'}"
    else:
        model_uri = args.model_uri or f"models:/{mlflow_config['registered_model_name']}/latest"
    
    # Test the model
    test_model_inference(model_uri)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        raise
