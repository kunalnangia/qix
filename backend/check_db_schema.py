import os
import sys
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("Error: DATABASE_URL not found in environment variables")
    sys.exit(1)

print(f"Connecting to database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

# Create engine and inspect
try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # Get list of tables
    tables = inspector.get_table_names()
    print("\n=== Database Tables ===")
    for table in tables:
        print(f"\nTable: {table}")
        print("Columns:")
        for column in inspector.get_columns(table):
            print(f"  - {column['name']}: {column['type']}")
            
        # Print foreign keys
        fks = inspector.get_foreign_keys(table)
        if fks:
            print("\n  Foreign Keys:")
            for fk in fks:
                print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    print("\n=== Schema Check Complete ===")
    
except Exception as e:
    print(f"\nError checking database schema: {str(e)}")
    sys.exit(1)
