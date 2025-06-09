"""
Script to train and save the spending recommendation model.
This script prepares the model for deployment with HP AI Studio.
"""
import os
import joblib
from datetime import datetime
from .spending_recommender import SpendingRecommender

def train_and_save_model(output_dir: str = "../model_artifacts"):
    """
    Train the model and save it along with necessary artifacts.
    
    Args:
        output_dir: Directory to save the model artifacts
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize and train the model
    print("🔄 Training spending recommendation model...")
    model = SpendingRecommender(confidence_threshold=0.7)
    
    # In a real implementation, we would train the model here
    # For this example, we're using a rule-based model that doesn't require training
    
    # Save the model
    model_path = os.path.join(output_dir, "spending_recommender.joblib")
    model.save(model_path)
    
    # Create model card
    model_card = {
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
            "explanation": "str",
            "metadata": "dict"
        },
        "metrics": {
            "confidence_threshold": model.confidence_threshold
        },
        "categories": model.categories,
        "vendors": model.vendors,
        "departments": model.departments
    }
    
    # Save model card
    model_card_path = os.path.join(output_dir, "model_card.json")
    with open(model_card_path, 'w') as f:
        import json
        json.dump(model_card, f, indent=2)
    
    print(f"✅ Model saved to {model_path}")
    print(f"📄 Model card saved to {model_card_path}")
    
    return model_path, model_card_path

if __name__ == "__main__":
    train_and_save_model()
