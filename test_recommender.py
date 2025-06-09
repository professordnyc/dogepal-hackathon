"""
Simple test script for the SpendingRecommender model.
"""
import sys
import logging
import traceback
from models.spending_recommender import SpendingRecommender

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_recommender')

def main():
    logger.info("Testing SpendingRecommender model...")
    
    # Create test records with data that will trigger recommendations
    test_records = [
        {
            "transaction_id": "TX0001",
            "user_id": "USER01",
            "department": "technology",  # lowercase to match model expectations
            "borough": "Manhattan",
            "vendor": "Tech Solutions",
            "category": "services",  # lowercase to match model expectations
            "amount": 25000.00,  # Very high amount to trigger cost optimization
            "date": "2025-01-15"
        },
        {
            "transaction_id": "TX0002",
            "user_id": "USER02",
            "department": "hr",  # lowercase to match model expectations
            "borough": "Brooklyn",
            "vendor": "Office Supplies Co",
            "category": "office supplies",  # lowercase to match model expectations
            "amount": 12000.00,  # High amount for office supplies
            "date": "2025-02-20"
        },
        {
            "transaction_id": "TX0003",
            "user_id": "USER03",
            "department": "finance",  # lowercase to match model expectations
            "borough": "Queens",
            "vendor": "Global Tech",
            "category": "hardware",  # lowercase to match model expectations
            "amount": 20000.00,  # Very high amount
            "date": "2025-03-10"
        }
    ]
    
    # Initialize the model
    logger.info("Initializing model...")
    model = SpendingRecommender(confidence_threshold=0.75)
    
    # Debug the model's internal methods
    logger.info("Debugging model internals...")
    
    # Test the _generate_recommendation method directly
    try:
        logger.info("Testing _generate_recommendation method directly...")
        for i, record in enumerate(test_records):
            logger.info(f"Testing record {i+1}: {record['transaction_id']}")
            # Access the private method directly for debugging
            result = model._generate_recommendation(record)
            logger.info(f"Direct _generate_recommendation result: {result}")
    except Exception as e:
        logger.error(f"Error in direct method call: {str(e)}")
        logger.error(traceback.format_exc())
    
    # Generate predictions for each test record
    print("Generating predictions...")
    for i, record in enumerate(test_records):
        print(f"\nTesting record {i+1}: {record['transaction_id']}")
        try:
            prediction = model.predict(record)
            print(f"Prediction type: {type(prediction)}")
            if prediction:
                if isinstance(prediction, list):
                    print(f"Got {len([p for p in prediction if p is not None])} valid recommendations")
                    for j, rec in enumerate([p for p in prediction if p is not None]):
                        print(f"  Recommendation {j+1}:")
                        print(f"    Type: {rec.get('type', 'Unknown')}")
                        print(f"    Title: {rec.get('title', 'No title')}")
                        print(f"    Confidence: {rec.get('confidence_score', 0)}")
                else:
                    print(f"Got a single recommendation:")
                    print(f"  Type: {prediction.get('type', 'Unknown')}")
                    print(f"  Title: {prediction.get('title', 'No title')}")
                    print(f"  Confidence: {prediction.get('confidence_score', 0)}")
            else:
                print("No recommendations generated")
        except Exception as e:
            print(f"Error generating predictions: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
