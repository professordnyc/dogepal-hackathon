"""
Test script for MLflow integration with the SpendingRecommender model.
"""
import os
import sys
import mlflow
import pandas as pd
from models.mlflow_config import (
    TRACKING_URI,
    EXPERIMENT_NAME,
    MODEL_ARTIFACT_PATH
)
from models.spending_recommender import SpendingRecommender

def test_mlflow_tracking():
    """Test MLflow tracking and model logging."""
    print("🚀 Testing MLflow integration...")
    
    # Set up MLflow
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    
    # Create a test model
    model = SpendingRecommender(confidence_threshold=0.6)
    
    # Sample data for testing
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
    
    # Start MLflow run
    with mlflow.start_run() as run:
        print(f"🔍 MLflow Run ID: {run.info.run_id}")
        
        # Log parameters
        mlflow.log_param("confidence_threshold", model.confidence_threshold)
        mlflow.log_param("model_type", "rule_based")
        
        # Make predictions
        predictions = model.predict(test_data)
        
        # Log metrics (example metrics - in a real scenario, these would come from validation)
        mlflow.log_metric("num_recommendations", len([p for p in predictions if p]))
        
        # Log the model
        mlflow.pyfunc.log_model(
            artifact_path="spending_recommender",
            python_model=model,
            registered_model_name="spending_recommender"
        )
        
        print("✅ MLflow test completed successfully!")
        print(f"   View run at: {mlflow.get_tracking_uri()}/#/experiments/{mlflow.active_run().info.experiment_id}/runs/{mlflow.active_run().info.run_id}")

def main():
    """Run MLflow tests."""
    print("🔧 Setting up MLflow test environment...")
    
    # Create necessary directories
    os.makedirs(MODEL_ARTIFACT_PATH, exist_ok=True)
    
    # Run tests
    test_mlflow_tracking()
    
    print("\n✨ All tests completed!")

if __name__ == "__main__":
    main()
