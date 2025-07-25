from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL
import sys
import os

def get_db_url():
    """Get the database URL from environment or use default."""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres.lflecyuvttemfoyixngi:Ayeshaayesha12@@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    )

def get_table_info(engine, table_name):
    """Get detailed information about a table."""
    inspector = inspect(engine)
    
    print(f"\nTable: {table_name}")
    print("-" * (len(table_name) + 8))
    
    # Get columns
    print("\nColumns:")
    print("-" * 80)
    print(f"{'Name':<30} {'Type':<20} {'Nullable':<10} {'Primary Key':<12} {'Default'}")
    print("-" * 80)
    
    for column in inspector.get_columns(table_name):
        col_type = str(column['type'])
        print(f"{column['name']:<30} {col_type:<20} {str(column['nullable']):<10} {str(column.get('primary_key', False)):<12} {str(column.get('default', ''))}")
    
    # Get primary keys
    pk_constraint = inspector.get_pk_constraint(table_name)
    if pk_constraint and 'constrained_columns' in pk_constraint:
        print(f"\nPrimary Key: {', '.join(pk_constraint['constrained_columns'])}")
    
    # Get foreign keys
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print("\nForeign Keys:")
        for fk in fks:
            print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # Get indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print("\nIndexes:")
        for idx in indexes:
            print(f"  {'UNIQUE ' if idx['unique'] else ''}Index on {idx['column_names']}")

def list_all_tables(engine):
    """List all tables in the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print("\n" + "="*80)
    print("DATABASE SCHEMA INSPECTION")
    print("="*80)
    
    if not tables:
        print("\nNo tables found in the database.")
        return []
    
    print(f"\nFound {len(tables)} tables in the database:")
    for i, table in enumerate(tables, 1):
        print(f"{i}. {table}")
    
    return tables

def main():
    try:
        db_url = get_db_url()
        print(f"Connecting to database: {db_url.split('@')[-1]}")
        
        engine = create_engine(db_url)
        
        # List all tables
        tables = list_all_tables(engine)
        
        if not tables:
            return
        
        # Get detailed info for each table
        for table in tables:
            get_table_info(engine, table)
            print("\n" + "="*80 + "\n")
            
    except Exception as e:
        print(f"\nERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
