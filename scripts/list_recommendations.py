"""List all recommendations in the database."""
import sqlite3
import os
from pathlib import Path

def list_recommendations():
    """List all recommendations with their IDs."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dogepal.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all recommendations
        cursor.execute("SELECT id, transaction_id, recommendation_type, title FROM recommendation")
        recommendations = cursor.fetchall()
        
        if not recommendations:
            print("❌ No recommendations found in the database")
            return
        
        print("\n📋 Available Recommendations:")
        print("ID\t\t\tTransaction ID\tType\t\t\tTitle")
        print("-" * 80)
        for rec in recommendations:
            print(f"{rec[0]}\t{rec[1]}\t{rec[2]}\t{rec[3]}")
        
        # Show example URLs
        if recommendations:
            print("\n🌐 Example URLs:")
            print(f"http://localhost:8080/api/v1/recommendations/{recommendations[0][0]}")
            print(f"http://localhost:8080/api/v1/spending/{recommendations[0][1]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    list_recommendations()
