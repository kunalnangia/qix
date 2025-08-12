import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def test_sqlalchemy_connection():
    # Load environment variables from the same .env file as the backend
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    load_dotenv(env_path)
    
    # Get the connection string from environment variables
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        print("❌ Error: DATABASE_URL not found in environment variables")
        return False
    
    print(f"🔍 Testing SQLAlchemy connection to: {DATABASE_URL}")
    
    try:
        # Create engine with the same settings as in database_postgres.py
        engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            pool_recycle=300,
            pool_timeout=30,
            connect_args={
                'connect_timeout': 10,
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5
            }
        )
        
        # Test the connection
        print("\n🔌 Attempting to connect to the database using SQLAlchemy...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Successfully connected to database!")
            print(f"📊 Database version: {version}")
            
            # List all tables
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"\n📋 Found {len(tables)} tables in the database:")
            for table in tables:
                print(f"  • {table}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed!")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {str(e)}")
        
        # Provide specific troubleshooting tips based on error
        if "Connection refused" in str(e):
            print("\n🔧 Troubleshooting:")
            print("1. Check if the database server is running")
            print("2. Verify the hostname and port are correct")
            print("3. Check if your IP is whitelisted in the database firewall")
            
        elif "authentication failed" in str(e).lower():
            print("\n🔧 Troubleshooting:")
            print("1. Verify the username and password are correct")
            print("2. Check if the user has permission to access the database")
            
        elif "does not exist" in str(e).lower():
            print("\n🔧 Troubleshooting:")
            print("1. Verify the database name is correct")
            print("2. The database may need to be created")
        
        return False

if __name__ == "__main__":
    success = test_sqlalchemy_connection()
    if not success:
        print("\n❌ SQLAlchemy connection test failed. Please check the error message above.")
        sys.exit(1)
    else:
        print("\n✅ SQLAlchemy connection test completed successfully!")
