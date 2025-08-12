import psycopg2
import json
from datetime import datetime

def get_db_connection():
    """Create a database connection."""
    return psycopg2.connect(
        dbname="postgres",
        user="postgres.lflecyuvttemfoyixngi",
        password="Ayeshaayesha12@",
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        port=5432,
        sslmode="require"
    )

def get_schema():
    """Get the complete database schema."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    schema = {
        'timestamp': datetime.utcnow().isoformat(),
        'tables': {}
    }
    
    try:
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            # Get columns
            cursor.execute("""
                SELECT 
                    column_name, 
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = %s
                ORDER BY ordinal_position;
            """, (table,))
            
            columns = []
            for name, data_type, is_nullable, default_val in cursor.fetchall():
                columns.append({
                    'name': name,
                    'type': data_type,
                    'nullable': is_nullable == 'YES',
                    'default': default_val
                })
            
            # Get primary key
            cursor.execute("""
                SELECT a.attname
                FROM pg_index i
                JOIN pg_attribute a ON a.attrelid = i.indrelid 
                    AND a.attnum = ANY(i.indkey)
                WHERE i.indrelid = %s::regclass
                AND i.indisprimary;
            """, (table,))
            
            primary_keys = [row[0] for row in cursor.fetchall()]
            
            # Get foreign keys
            cursor.execute("""
                SELECT
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_name = %s;
            """, (table,))
            
            foreign_keys = [{
                'column': row[0],
                'references': f"{row[1]}({row[2]})"
            } for row in cursor.fetchall()]
            
            schema['tables'][table] = {
                'columns': columns,
                'primary_key': primary_keys,
                'foreign_keys': foreign_keys
            }
            
        return schema
        
    finally:
        cursor.close()
        conn.close()

def save_schema_to_file(schema, filename='database_schema.json'):
    """Save schema to a JSON file."""
    with open(filename, 'w') as f:
        json.dump(schema, f, indent=2)
    print(f"Schema saved to {filename}")

def print_schema_summary(schema):
    """Print a summary of the database schema."""
    print("\n" + "="*80)
    print("DATABASE SCHEMA SUMMARY")
    print("="*80)
    print(f"Generated at: {schema['timestamp']}")
    print(f"Total tables: {len(schema['tables'])}\n")
    
    for table_name, table_info in schema['tables'].items():
        print(f"TABLE: {table_name}")
        print("-" * 80)
        print(f"Columns: {len(table_info['columns'])}")
        print(f"Primary Key: {', '.join(table_info['primary_key']) or 'None'}")
        
        if table_info['foreign_keys']:
            print("Foreign Keys:")
            for fk in table_info['foreign_keys']:
                print(f"  {fk['column']} -> {fk['references']}")
        
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print("Fetching database schema...")
    schema = get_schema()
    save_schema_to_file(schema)
    print_schema_summary(schema)
