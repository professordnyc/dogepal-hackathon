"""
HP AI Studio configuration for the DOGEPAL project.

This module contains configuration settings for connecting to HP AI Studio's
MLflow tracking server and model registry.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# HP AI Studio MLflow Tracking URI
# Replace with your HP AI Studio MLflow tracking URI
HP_AI_STUDIO_TRACKING_URI = os.getenv(
    "MLFLOW_TRACKING_URI",
    "http://localhost:5000"  # Default to local MLflow for development
)

# HP AI Studio specific settings
HP_AI_STUDIO = {
    "experiment_name": "dogepal_spending",
    "registered_model_name": "dogepal_spending_recommender",
    "model_version": "1.0.0",
    "model_stage": "Staging",  # Options: None, Staging, Production, Archived
}

# Paths
MODEL_ARTIFACT_PATH = str(BASE_DIR / "models" / "artifacts")
DATA_DIR = str(BASE_DIR / "data")

# Create directories if they don't exist
os.makedirs(MODEL_ARTIFACT_PATH, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

def get_mlflow_config():
    """
    Get MLflow configuration for HP AI Studio.
    
    Returns:
        dict: Configuration dictionary with MLflow settings
    """
    return {
        "tracking_uri": HP_AI_STUDIO_TRACKING_URI,
        "experiment_name": HP_AI_STUDIO["experiment_name"],
        "registered_model_name": HP_AI_STUDIO["registered_model_name"],
        "model_version": HP_AI_STUDIO["model_version"],
        "model_stage": HP_AI_STUDIO["model_stage"],
    }
