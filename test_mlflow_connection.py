"""
Test script to verify MLflow connection to HP AI Studio.
"""
import os
import mlflow
from dotenv import load_dotenv
from models.hp_ai_studio_config import HP_AI_STUDIO, HP_AI_STUDIO_TRACKING_URI

# Load environment variables
load_dotenv()

def test_mlflow_connection():
    """Test connection to MLflow tracking server."""
    try:
        # Set the tracking URI
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
        print(f"Attempting to connect to MLflow at: {tracking_uri}")
        mlflow.set_tracking_uri(tracking_uri)
        
        # Test connection by listing experiments
        print("Listing experiments:")
        experiments = mlflow.search_experiments()
        for exp in experiments:
            print(f"- {exp.name} (ID: {exp.experiment_id})")
        
        # Test experiment creation
        experiment_name = HP_AI_STUDIO["experiment_name"]
        print(f"\nChecking experiment: {experiment_name}")
        
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            print("Experiment not found, creating...")
            experiment_id = mlflow.create_experiment(experiment_name)
            print(f"Created new experiment with ID: {experiment_id}")
        else:
            print(f"Using existing experiment: {experiment.experiment_id}")
        
        # Start a test run
        print("\nStarting a test run...")
        with mlflow.start_run(experiment_id=experiment.experiment_id if experiment else None):
            mlflow.log_param("test_param", "test_value")
            mlflow.log_metric("test_metric", 1.0)
            print("Successfully logged test parameter and metric")
            
    except Exception as e:
        print(f"Error connecting to MLflow: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure the MLFLOW_TRACKING_URI is set correctly in your .env file")
        print("2. Verify you have network access to the MLflow server")
        print("3. Check if the MLflow server is running")
        raise

if __name__ == "__main__":
    test_mlflow_connection()
