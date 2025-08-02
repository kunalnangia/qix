import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def test_db_connection():
    # Load environment variables
    load_dotenv()
    
    # Get database URL from environment
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return
    
    print(f"🔗 Testing connection to: {db_url.split('@')[-1]}")
    
    try:
        # Create database engine
        engine = create_engine(db_url)
        
        # Test connection
        with engine.connect() as connection:
            # Get database version
            result = connection.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Successfully connected to database!")
            print(f"   Database version: {version}")
            
            # List tables in the database
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📋 Available tables ({len(tables)}):")
            for table in sorted(tables):
                print(f"   - {table}")
            
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")

if __name__ == "__main__":
    test_db_connection()
