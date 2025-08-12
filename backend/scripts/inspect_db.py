import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

def print_header(title):
    print("\n" + "="*80)
    print(f" {title.upper()} ")
    print("="*80)

def load_environment():
    """Load environment variables from .env file"""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment from: {env_path}")
    else:
        print(f"⚠️  .env file not found at: {env_path}")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        return None
    
    print(f"🔗 Using database URL: {db_url}")
    return db_url

def get_table_info(engine):
    """Get information about all tables in the database"""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print_header("database tables")
    if not tables:
        print("No tables found in the database!")
        return
    
    for table_name in tables:
        print(f"\n📋 Table: {table_name}")
        print("-" * 40)
        
        # Get column info
        columns = inspector.get_columns(table_name)
        print(f"Columns ({len(columns)}):")
        for col in columns:
            print(f"  - {col['name']}: {col['type']} {'(PK)' if col.get('primary_key') else ''}")
        
        # Get row count
        with engine.connect() as conn:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                print(f"Row count: {count}")
                
                # Show sample data if table is not empty
                if count > 0:
                    result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 2"))
                    rows = result.fetchall()
                    print("Sample data:")
                    for row in rows:
                        print(f"  {dict(row._mapping)}")
            except Exception as e:
                print(f"  Error querying table: {e}")

def check_migrations():
    """Check if migrations have been applied"""
    print_header("migration status")
    print("Checking for 'alembic_version' table...")
    
    try:
        db_url = load_environment()
        if not db_url:
            return
            
        engine = create_engine(db_url.replace('asyncpg', 'psycopg2'))
        inspector = inspect(engine)
        
        if 'alembic_version' in inspector.get_table_names():
            with engine.connect() as conn:
                version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar()
                print(f"✅ Migrations applied. Current version: {version}")
        else:
            print("⚠️  No migrations have been applied (alembic_version table not found)")
            print("   Run 'alembic upgrade head' to apply migrations")
            
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")

def main():
    # Load environment and get database URL
    db_url = load_environment()
    if not db_url:
        return
    
    # Create engine
    try:
        sync_db_url = db_url.replace('asyncpg', 'psycopg2')
        engine = create_engine(sync_db_url)
        
        # Get database info
        with engine.connect() as conn:
            # Get database version
            version = conn.execute(text("SELECT version()")).scalar()
            db_name = conn.execute(text("SELECT current_database()")).scalar()
            
            print_header("database information")
            print(f"Version: {version}")
            print(f"Database: {db_name}")
            print(f"Connection URL: {sync_db_url}")
        
        # Get table info
        get_table_info(engine)
        
        # Check migrations
        check_migrations()
        
    except SQLAlchemyError as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    main()
