import os
import sys
from pathlib import Path
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
env_path = str(Path(__file__).parent / '.env')
load_dotenv(env_path)

def print_header(title):
    print("\n" + "="*80)
    print(f" {title.upper()} ")
    print("="*80)

def get_database_url():
    """Get database URL from environment variables"""
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        sys.exit(1)
    return db_url

def list_all_tables(engine):
    """List all tables in the database"""
    print("\n📋 Listing all tables in the database:")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("❌ No tables found in the database")
        return []
    
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    return tables

def check_table_columns(engine, table_name):
    """Check columns in a specific table"""
    print(f"\n🔍 Checking columns in table: {table_name}")
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    
    if not columns:
        print(f"❌ No columns found in table: {table_name}")
        return []
    
    print(f"\n📋 Columns in {table_name}:")
    for col in columns:
        print(f"- {col['name']} ({col['type']})" + 
              (" [PRIMARY KEY]" if col.get('primary_key') else "") +
              (" [NULLABLE]" if col.get('nullable') else " [NOT NULL]"))
    
    return columns

def check_foreign_keys(engine, table_name):
    """Check foreign key constraints for a table"""
    print(f"\n🔍 Checking foreign keys for table: {table_name}")
    inspector = inspect(engine)
    fks = inspector.get_foreign_keys(table_name)
    
    if not fks:
        print("No foreign key constraints found")
        return []
    
    print(f"\n🔗 Foreign keys in {table_name}:")
    for fk in fks:
        print(f"- {fk['constrained_columns']} references {fk['referred_table']}({fk['referred_columns']})")
    
    return fks

def check_table_data(engine, table_name, limit=5):
    """Check sample data in a table"""
    print(f"\n📊 Sample data from {table_name} (first {limit} rows):")
    with engine.connect() as conn:
        try:
            result = conn.execute(text(f"SELECT * FROM \"{table_name}\" LIMIT {limit}"))
            rows = result.fetchall()
            
            if not rows:
                print("No data found")
                return []
            
            # Print column headers
            columns = result.keys()
            print(" | ".join(columns))
            print("-" * 80)
            
            # Print rows
            for row in rows:
                print(" | ".join(str(cell) for cell in row))
            
            return rows
            
        except Exception as e:
            print(f"❌ Error reading data: {str(e)}")
            return []

def check_expected_tables(engine, expected_tables):
    """Check if expected tables exist and have the right structure"""
    print_header("checking expected tables")
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    
    print("\n🔍 Checking for expected tables:")
    missing_tables = []
    for table in expected_tables:
        if table in existing_tables:
            print(f"✅ {table} (exists)")
        else:
            print(f"❌ {table} (missing)")
            missing_tables.append(table)
    
    if missing_tables:
        print(f"\n❌ Missing {len(missing_tables)} tables: {', '.join(missing_tables)}")
    else:
        print("\n✅ All expected tables exist")
    
    return missing_tables

def main():
    try:
        # Get database URL and create engine
        db_url = get_database_url()
        engine = create_engine(db_url)
        
        # List all tables
        print_header("database tables")
        tables = list_all_tables(engine)
        
        if not tables:
            print("\n❌ No tables found in the database")
            return 1
        
        # Check expected tables
        expected_tables = [
            'users', 'projects', 'test_cases', 'test_steps',
            'test_plans', 'test_executions', 'comments', 'teams',
            'team_members', 'environments', 'attachments',
            'activity_logs', 'test_plan_test_cases'
        ]
        
        missing_tables = check_expected_tables(engine, expected_tables)
        
        # If we have tables but not all expected ones, show details
        if tables and len(tables) < len(expected_tables):
            print(f"\n⚠️  Only {len(tables)} out of {len(expected_tables)} expected tables found")
            
            # Show details of existing tables
            for table in tables:
                print(f"\n{'='*40} {table.upper()} {'='*(40-len(table))}")
                check_table_columns(engine, table)
                check_foreign_keys(engine, table)
                check_table_data(engine, table)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        if 'engine' in locals():
            engine.dispose()

if __name__ == "__main__":
    sys.exit(main())
