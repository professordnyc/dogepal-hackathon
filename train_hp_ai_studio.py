"""
Training script for the DOGEPAL Spending Recommender model with HP AI Studio integration.

This script trains the model and registers it with HP AI Studio's MLflow tracking server.
"""
import os
import sys
import logging
import argparse
import mlflow
import mlflow.sklearn
from pathlib import Path

# Add project root to path
project_root = str(Path(__file__).parent.absolute())
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.spending_recommender import SpendingRecommender
from models.hp_ai_studio_config import get_mlflow_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def train_model(confidence_threshold=0.7, register_model=False):
    """
    Train the spending recommender model and log to MLflow.
    
    Args:
        confidence_threshold: Threshold for recommendation confidence
        register_model: Whether to register the model in the model registry
    """
    # Get MLflow configuration
    mlflow_config = get_mlflow_config()
    
    # Set up MLflow
    mlflow.set_tracking_uri(mlflow_config["tracking_uri"])
    mlflow.set_experiment(mlflow_config["experiment_name"])
    
    # Start MLflow run
    with mlflow.start_run() as run:
        logger.info(f"Starting MLflow run {run.info.run_id}")
        
        # Log parameters
        mlflow.log_param("confidence_threshold", confidence_threshold)
        mlflow.log_param("model_type", "rule_based")
        
        # Initialize and train the model
        logger.info("Initializing model...")
        model = SpendingRecommender(confidence_threshold=confidence_threshold)
        
        # Log model artifacts
        logger.info("Logging model artifacts...")
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=mlflow_config["registered_model_name"] if register_model else None
        )
        
        # Log metrics (example metrics - in a real scenario, these would come from validation)
        mlflow.log_metric("confidence_threshold", confidence_threshold)
        
        # Log the model with pyfunc for better deployment support
        mlflow.pyfunc.log_model(
            "model",
            python_model=model,
            registered_model_name=mlflow_config["registered_model_name"] if register_model else None
        )
        
        # Register the model if requested
        if register_model:
            logger.info("Registering model in MLflow Model Registry...")
            model_uri = f"runs:/{run.info.run_id}/model"
            registered_model = mlflow.register_model(
                model_uri=model_uri,
                name=mlflow_config["registered_model_name"]
            )
            
            # Transition model to specified stage
            if mlflow_config["model_stage"]:
                client = mlflow.tracking.MlflowClient()
                client.transition_model_version_stage(
                    name=mlflow_config["registered_model_name"],
                    version=registered_model.version,
                    stage=mlflow_config["model_stage"]
                )
                logger.info(f"Model registered and transitioned to {mlflow_config['model_stage']} stage")
        
        logger.info("Training completed successfully!")
        logger.info(f"MLflow run: {mlflow.get_tracking_uri()}/#/experiments/{run.info.experiment_id}/runs/{run.info.run_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the DOGEPAL Spending Recommender model")
    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.7,
        help="Confidence threshold for recommendations (0-1)"
    )
    parser.add_argument(
        "--register-model",
        action="store_true",
        help="Register the model in the MLflow Model Registry"
    )
    
    args = parser.parse_args()
    
    try:
        train_model(
            confidence_threshold=args.confidence_threshold,
            register_model=args.register_model
        )
    except Exception as e:
        logger.error(f"Error during training: {str(e)}")
        raise
