"""
MLflow configuration settings for the DOGEPAL project.
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# MLflow settings
TRACKING_URI = "file:./mlruns"  # Local file-based tracking
EXPERIMENT_NAME = "dogepal_spending"

# Model settings
MODEL_NAME = "spending_recommender"
MODEL_VERSION = "1.0.0"

# Paths
MODEL_ARTIFACT_PATH = str(BASE_DIR / "models" / "artifacts")
DATA_DIR = str(BASE_DIR / "data")

# Create directories if they don't exist
os.makedirs(MODEL_ARTIFACT_PATH, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
