"""
MLflow configuration for DOGEPAL project.
Loads settings from environment variables with fallback to defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).parent.parent

# MLflow settings - with environment variable fallbacks
TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "dogepal_spending")

# Model settings
MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "spending_recommender")
MODEL_VERSION = os.getenv("MLFLOW_MODEL_VERSION", "1.0.0")

# Paths
MODEL_ARTIFACT_PATH = str(BASE_DIR / "models" / "artifacts")
DATA_DIR = str(BASE_DIR / "data")

# Create directories if they don't exist
os.makedirs(MODEL_ARTIFACT_PATH, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
