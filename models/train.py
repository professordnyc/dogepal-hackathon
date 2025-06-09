"""
Script to train, track, and save the spending recommendation model.
This script includes MLflow integration for experiment tracking and model registry.
"""
import os
import json
import joblib
import argparse
from datetime import datetime
import mlflow
from mlflow.models.signature import infer_signature

# Import local modules
from .spending_recommender import SpendingRecommender
from .mlflow_config import (
    TRACKING_URI,
    EXPERIMENT_NAME,
    MODEL_ARTIFACT_PATH,
    MODEL_NAME,
    DATA_DIR
)

def setup_mlflow():
    """Set up MLflow tracking and experiment."""
    # Configure MLflow
    mlflow.set_tracking_uri(TRACKING_URI)
    mlflow.set_experiment(EXPERIMENT_NAME)
    
    # Start a new run
    run = mlflow.start_run()
    return run

def create_model_card(model):
    """Create a model card with metadata."""
    return {
        "model_name": "DOGEPAL Spending Recommender",
        "version": "1.0.0",
        "description": "A rule-based model for generating cost-saving recommendations for government spending.",
        "author": "DOGEPAL Team",
        "created_at": datetime.utcnow().isoformat(),
        "input_schema": {
            "transaction_id": "str",
            "amount": "float",
            "category": "str",
            "vendor": "str",
            "department": "str",
            "project_name": "str",
            "borough": "str"
        },
        "output_schema": {
            "transaction_id": "str",
            "recommendation_type": "str",
            "title": "str",
            "description": "str",
            "potential_savings": "float",
            "confidence_score": "float",
            "priority": "str",
            "explanation": "dict",
            "metadata": "dict"
        },
        "metrics": {
            "confidence_threshold": model.confidence_threshold
        },
        "categories": model.categories,
        "vendors": model.vendors,
        "departments": model.departments
    }

def train_and_save_model():
    """
    Train the model, track with MLflow, and save artifacts.
    """
    # Set up MLflow
    run = setup_mlflow()
    
    try:
        # Log parameters
        params = {
            "confidence_threshold": 0.7,
            "model_type": "rule_based",
            "version": "1.0.0"
        }
        
        # Initialize the model
        print("🔄 Initializing spending recommendation model...")
        model = SpendingRecommender(confidence_threshold=params["confidence_threshold"])
        
        # Log model parameters
        mlflow.log_params(params)
        
        # Log model metrics (example metrics - in a real scenario, these would come from validation)
        metrics = {
            "training_accuracy": 0.0,  # Placeholder for actual metric
            "precision": 0.0,          # Placeholder for actual metric
            "recall": 0.0              # Placeholder for actual metric
        }
        mlflow.log_metrics(metrics)
        
        # Create model card
        model_card = create_model_card(model)
        
        # Log model card as artifact
        model_card_path = os.path.join(MODEL_ARTIFACT_PATH, "model_card.json")
        with open(model_card_path, 'w') as f:
            json.dump(model_card, f, indent=2)
        
        # Log model with MLflow
        print("📊 Logging model with MLflow...")
        
        # Create a sample input for model signature
        sample_input = {
            "transaction_id": "TXN1001",
            "amount": 1000.0,
            "category": "office supplies",
            "vendor": "OfficeMax",
            "department": "Finance",
            "project_name": "Office Upgrade",
            "borough": "Manhattan"
        }
        
        # Infer model signature
        signature = infer_signature(
            model_input=[sample_input],
            model_output=model.predict([sample_input])
        )
        
        # Log the model
        mlflow.pyfunc.log_model(
            artifact_path=MODEL_NAME,
            python_model=model,
            artifacts={"model_card": model_card_path},
            signature=signature,
            registered_model_name=MODEL_NAME
        )
        
        # Log artifacts
        mlflow.log_artifact(model_card_path)
        
        print(f"✅ Model training and logging complete!")
        print(f"   MLflow run ID: {run.info.run_id}")
        print(f"   Model artifacts: {MODEL_ARTIFACT_PATH}")
        
    except Exception as e:
        print(f"❌ Error during model training: {str(e)}")
        raise
    finally:
        # End the MLflow run
        mlflow.end_run()
    
    return model_path, model_card_path

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Train and log the spending recommendation model with MLflow')
    parser.add_argument('--tracking-uri', type=str, default=TRACKING_URI,
                      help='MLflow tracking URI')
    args = parser.parse_args()
    
    # Ensure the output directory exists
    os.makedirs(MODEL_ARTIFACT_PATH, exist_ok=True)
    
    print(f"🚀 Starting model training with MLflow tracking at: {args.tracking_uri}")
    train_and_save_model()
    print("✨ Training completed successfully!")
