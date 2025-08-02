import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def check_users_schema():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return
    
    try:
        # Create database engine
        engine = create_engine(db_url)
        
        # Connect to the database
        with engine.connect() as connection:
            # Get all columns from users table
            result = connection.execute(text("SELECT * FROM users LIMIT 1"))
            
            # Get column names
            columns = result.keys()
            print("\nUsers table columns:")
            print("-" * 30)
            for col in columns:
                print(f"- {col}")
            
            # Get row count
            count_result = connection.execute(text("SELECT COUNT(*) FROM users"))
            row_count = count_result.scalar()
            print(f"\nTotal users in database: {row_count}")
            
    except Exception as e:
        print(f"❌ Error checking users table: {e}")

if __name__ == "__main__":
    print("🔍 Checking users table structure...")
    check_users_schema()
