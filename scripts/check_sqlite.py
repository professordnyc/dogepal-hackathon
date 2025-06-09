"""Script to check SQLite database schema and data."""
import sqlite3
from pathlib import Path

def check_database():
    db_path = Path("dogepal.db")
    if not db_path.exists():
        print("❌ Database file not found!")
        return
    
    print(f"🔍 Checking database: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get list of tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\n📋 Database tables: {tables}")
        
        # Check spending table
        if 'spending' in tables:
            print("\n📊 Spending table structure:")
            cursor.execute("PRAGMA table_info(spending)")
            for column in cursor.fetchall():
                print(f"  - {column[1]}: {column[2]} {'(NOT NULL)' if not column[3] else ''}")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM spending")
            count = cursor.fetchone()[0]
            print(f"\n📈 Number of spending records: {count}")
            
            # Show sample records
            if count > 0:
                cursor.execute("SELECT * FROM spending LIMIT 3")
                print("\n📝 Sample spending records:")
                for row in cursor.fetchall():
                    print(f"  - ID: {row[0]}, Vendor: {row[7]}, Amount: ${row[9]}")
        
        # Check recommendations table
        if 'recommendations' in tables:
            print("\n📊 Recommendations table structure:")
            cursor.execute("PRAGMA table_info(recommendations)")
            for column in cursor.fetchall():
                print(f"  - {column[1]}: {column[2]} {'(NOT NULL)' if not column[3] else ''}")
            
            # Count records
            cursor.execute("SELECT COUNT(*) FROM recommendations")
            count = cursor.fetchone()[0]
            print(f"\n📈 Number of recommendation records: {count}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_database()
