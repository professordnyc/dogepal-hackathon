"""Simple test for SpendingRecommender with clean output."""
from models.spending_recommender import SpendingRecommender

def test_spending_recommender():
    print("Testing SpendingRecommender...")
    
    # Initialize model
    model = SpendingRecommender(confidence_threshold=0.5)
    
    # Test cases
    test_cases = [
        {
            "transaction_id": "TXN1001",
            "amount": 1500.00,
            "category": "office supplies",
            "vendor": "OfficeMax",
            "department": "Finance"
        },
        {
            "transaction_id": "TXN2001",
            "amount": 500.00,
            "category": "office supplies",
            "vendor": "OfficeMax",
            "department": "Finance"
        },
        {
            "transaction_id": "TXN3001",
            "amount": 25000.00,
            "category": "services",
            "vendor": "Tech Corp",
            "department": "IT"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print(f"- Amount: ${test_case['amount']:,.2f}")
        print(f"- Category: {test_case['category']}")
        print(f"- Department: {test_case['department']}")
        
        # Get recommendation
        rec = model.predict([test_case])
        
        if rec and len(rec) > 0:
            rec = rec[0]  # Get first recommendation
            print(f"✅ Recommendation: {rec.get('title', 'N/A')}")
            print(f"   Type: {rec.get('recommendation_type', 'N/A').title()}")
            print(f"   Potential Savings: ${rec.get('potential_savings', 0):,.2f}")
        else:
            print("ℹ️  No recommendation (spending within normal ranges)")

if __name__ == "__main__":
    test_spending_recommender()
