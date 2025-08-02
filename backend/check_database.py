import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import OperationalError, SQLAlchemyError

def print_header(title):
    print("\n" + "="*80)
    print(f" {title.upper()} ")
    print("="*80)

def test_connection():
    try:
        # Add the project root to the Python path
        project_root = Path(__file__).parent
        sys.path.append(str(project_root))
        
        # Load environment variables
        env_path = project_root / '.env'
        load_dotenv(env_path)
        
        # Get database URL from environment variables
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            print("❌ DATABASE_URL not found in environment variables")
            return False
            
        print_header("DATABASE CONNECTION TEST")
        print(f"🔍 Testing connection to: {db_url}")
        
        # Create engine with echo=True for detailed SQL output
        engine = create_engine(db_url, echo=True)
        
        # Test connection with a simple query
        with engine.connect() as conn:
            # Test basic connection
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Connected to PostgreSQL version: {version}")
            
            # Get database name
            db_name = conn.execute(text("SELECT current_database()")).scalar()
            print(f"📊 Database: {db_name}")
            
            # Get current user
            user = conn.execute(text("SELECT current_user")).scalar()
            print(f"👤 Current user: {user}")
            
            # List all schemas
            print("\n📋 Available schemas:")
            schemas = conn.execute(text("SELECT nspname FROM pg_catalog.pg_namespace")).fetchall()
            for schema in schemas:
                print(f"- {schema[0]}")
            
            # List all tables in public schema
            print("\n📋 Tables in public schema:")
            tables = conn.execute(text(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
            )).fetchall()
            
            if tables:
                for table in tables:
                    print(f"- {table[0]}")
            else:
                print("No tables found in public schema.")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting database connection test...")
    success = test_connection()
    if success:
        print("\n✅ Database connection test completed successfully!")
    else:
        print("\n❌ Database connection test failed. Please check the error messages above.")
