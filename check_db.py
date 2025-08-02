import os
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

def check_database():
    # Load environment variables
    load_dotenv()
    db_url = os.getenv('DATABASE_URL')
    print(f"Connecting to database: {db_url}")
    
    try:
        # Create engine and connect
        engine = create_engine(db_url)
        connection = engine.connect()
        print("Successfully connected to the database!")
        
        # List all tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print("\nTables in database:")
        for table in tables:
            print(f"- {table}")
            
        # Check if users table exists and count rows
        if 'users' in tables:
            result = connection.execute("SELECT COUNT(*) FROM users")
            count = result.scalar()
            print(f"\nNumber of users in database: {count}")
            
            # List first few users if any exist
            if count > 0:
                print("\nFirst 5 users:")
                result = connection.execute("SELECT id, email, is_active FROM users LIMIT 5")
                for row in result:
                    print(f"ID: {row[0]}, Email: {row[1]}, Active: {row[2]}")
        
        connection.close()
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")

if __name__ == "__main__":
    check_database()
