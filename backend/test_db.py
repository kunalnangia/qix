import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

def test_db_connection():
    # Load environment variables
    env_path = os.path.join(os.path.dirname(os.path.absp(__file__)), '..', '.env')
    load_dotenv(env_path)
    
    # Get database URL
    db_url = os.getenv("DATABASE_URL")
    print(f"Testing connection to database: {db_url}")
    
    try:
        # Create engine and test connection
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print("Successfully connected to the database!")
            
            # List all tables
            tables = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            print("\nTables in the database:")
            for table in tables:
                print(f"- {table[0]}")
                
    except Exception as e:
        print(f"Error connecting to database: {e}")

if __name__ == "__main__":
    test_db_connection()
