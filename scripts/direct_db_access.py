"""Direct database access script to retrieve spending and recommendation data."""
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import os

def format_date(date_obj):
    """Format date objects for display."""
    if isinstance(date_obj, datetime):
        return date_obj.isoformat()
    return str(date_obj)

def dict_factory(cursor, row):
    """Convert SQLite row to dictionary."""
    d = {}
    for idx, col in enumerate(cursor.description):
        value = row[idx]
        # Handle JSON fields
        if col[0] == 'metadata' and value:
            try:
                d[col[0]] = json.loads(value)
            except:
                d[col[0]] = value
        else:
            d[col[0]] = value
    return d

def get_spending_data():
    """Retrieve spending data directly from SQLite."""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dogepal.db')
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found at {db_path}")
        return
    
    print(f"📂 Using database: {db_path}")
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cursor = conn.cursor()
    
    try:
        # Get spending data
        print("\n📊 Retrieving spending data...")
        cursor.execute("SELECT * FROM spending LIMIT 10")
        spending_rows = cursor.fetchall()
        
        if not spending_rows:
            print("❌ No spending records found")
        else:
            print(f"✅ Found {len(spending_rows)} spending records")
            print("\n📝 Sample spending data:")
            for row in spending_rows[:3]:
                # Format the output for better readability
                print(f"  - Transaction: {row['transaction_id']}")
                print(f"    Vendor: {row['vendor']}")
                print(f"    Amount: ${row['amount']}")
                print(f"    Date: {row['spending_date']}")
                print(f"    Department: {row['department']}")
                print(f"    Borough: {row['borough']}")
                print("    ---")
        
        # Get recommendation data
        print("\n📊 Retrieving recommendation data...")
        cursor.execute("SELECT * FROM recommendation LIMIT 10")
        rec_rows = cursor.fetchall()
        
        if not rec_rows:
            print("❌ No recommendation records found")
        else:
            print(f"✅ Found {len(rec_rows)} recommendation records")
            print("\n📝 Sample recommendation data:")
            for row in rec_rows[:3]:
                print(f"  - ID: {row['id']}")
                print(f"    Transaction: {row['transaction_id']}")
                print(f"    Type: {row['recommendation_type']}")
                print(f"    Title: {row['title']}")
                print(f"    Savings: ${row['potential_savings']}")
                print("    ---")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    get_spending_data()
