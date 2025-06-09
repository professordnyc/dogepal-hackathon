"""Script to generate sample data using direct SQLite access."""
import sqlite3
import json
from datetime import datetime, timedelta
import random
from faker import Faker

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducible results

# Database file path
DB_PATH = "dogepal.db"

# Sample data
BOROUGHS = ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"]
DEPARTMENTS = ["education", "transportation", "parks", "sanitation", "public_safety"]
CATEGORIES = ["office_supplies", "technology", "consulting", "travel", "training"]
VENDORS = [
    "ABC Office Supplies", "Tech Solutions Inc.", "Citywide Consulting",
    "Empire State Services", "Gotham IT", "Metro Office Supply",
    "Urban Development Group", "Five Boroughs Consulting"
]
PROJECTS = [
    "Citywide Network Upgrade", "Public School Modernization",
    "Parks Renovation", "Infrastructure Maintenance",
    "Community Development", "Public Safety Initiative"
]
RECOMMENDATION_TYPES = ["cost_saving", "budget_optimization", "vendor_consolidation", "spending_anomaly", "policy_violation"]
STATUSES = ["pending", "in_progress", "completed", "rejected"]
PRIORITIES = ["low", "medium", "high"]

# Create tables
def create_tables(conn):
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute("DROP TABLE IF EXISTS recommendation")
    cursor.execute("DROP TABLE IF EXISTS spending")
    
    # Create spending table
    cursor.execute("""
    CREATE TABLE spending (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        user_type TEXT NOT NULL,
        department TEXT NOT NULL,
        project_name TEXT NOT NULL,
        borough TEXT NOT NULL,
        spending_date TEXT NOT NULL,
        vendor TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        justification TEXT NOT NULL,
        approval_status TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    
    # Create recommendation table
    cursor.execute("""
    CREATE TABLE recommendation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spending_id INTEGER NOT NULL,
        recommendation_type TEXT NOT NULL,
        description TEXT NOT NULL,
        potential_savings REAL NOT NULL,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        metadata_field TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (spending_id) REFERENCES spending (id)
    )
    """)
    
    conn.commit()

def generate_spending_data(count=100):
    """Generate sample spending records."""
    spendings = []
    for _ in range(count):
        record_time = datetime.utcnow()
        spending_date = fake.date_time_between(start_date="-1y", end_date="now")
        
        spending = (
            f"user_{fake.random_int(min=1, max=10)}",  # user_id
            random.choice(["city_official", "department_head", "admin"]),  # user_type
            random.choice(DEPARTMENTS),  # department
            random.choice(PROJECTS),  # project_name
            random.choice(BOROUGHS),  # borough
            spending_date.isoformat(" "),  # spending_date
            random.choice(VENDORS),  # vendor
            random.choice(CATEGORIES),  # category
            round(random.uniform(100, 50000), 2),  # amount
            fake.sentence(),  # justification
            random.choice(["pending", "approved", "rejected"]),  # approval_status
            record_time.isoformat(" "),  # created_at
            record_time.isoformat(" ")  # updated_at
        )
        spendings.append(spending)
    
    return spendings

def generate_recommendations(conn, spending_ids):
    """Generate sample recommendations for spendings."""
    cursor = conn.cursor()
    recommendations = []
    
    for spending_id in spending_ids:
        if random.random() < 0.7:  # 70% chance to generate a recommendation
            metadata = {
                "confidence_score": round(random.uniform(0.7, 0.99), 2),
                "explanation": fake.paragraph(),
                "generated_at": datetime.utcnow().isoformat()
            }
            
            recommendation = (
                spending_id,  # spending_id
                random.choice(RECOMMENDATION_TYPES),  # recommendation_type
                f"Recommendation for spending ID {spending_id}",  # description
                round(random.uniform(100, 10000), 2),  # potential_savings
                random.choice(STATUSES),  # status
                random.choice(PRIORITIES),  # priority
                json.dumps(metadata),  # metadata_field
                datetime.utcnow().isoformat(" "),  # created_at
                datetime.utcnow().isoformat(" ")  # updated_at
            )
            
            cursor.execute("""
                INSERT INTO recommendation 
                (spending_id, recommendation_type, description, potential_savings, 
                 status, priority, metadata_field, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, recommendation)
    
    conn.commit()

def main():
    """Main function to generate sample data."""
    print("Starting sample data generation...")
    
    # Connect to SQLite database
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Create tables
        print("Creating database tables...")
        create_tables(conn)
        
        # Generate and insert spending records
        print("Generating spending records...")
        spendings = generate_spending_data(100)
        cursor = conn.cursor()
        
        cursor.executemany("""
            INSERT INTO spending 
            (user_id, user_type, department, project_name, borough, spending_date, 
             vendor, category, amount, justification, approval_status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, spendings)
        
        # Get the generated spending IDs
        cursor.execute("SELECT id FROM spending")
        spending_ids = [row[0] for row in cursor.fetchall()]
        print(f"Generated {len(spending_ids)} spending records")
        
        # Generate recommendations
        print("Generating recommendations...")
        generate_recommendations(conn, spending_ids)
        
        # Count recommendations
        cursor.execute("SELECT COUNT(*) FROM recommendation")
        rec_count = cursor.fetchone()[0]
        print(f"Generated {rec_count} recommendations")
        
        print("Sample data generation completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
