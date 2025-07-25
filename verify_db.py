import psycopg2
import sys

def get_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres.lflecyuvttemfoyixngi",
            password="Ayeshaayesha12@",
            host="aws-0-ap-southeast-1.pooler.supabase.com",
            port=5432,
            sslmode="require"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        sys.exit(1)

def get_tables(conn):
    """Return list of tables in the public schema."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        return [row[0] for row in cur.fetchall()]

def get_table_info(conn, table_name):
    """Get column information for a specific table."""
    with conn.cursor() as cur:
        # Get column info
        cur.execute("""
            SELECT 
                column_name, 
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position;
        """, (table_name,))
        
        columns = []
        for name, data_type, is_nullable, default_val in cur.fetchall():
            columns.append({
                'name': name,
                'type': data_type,
                'nullable': is_nullable == 'YES',
                'default': default_val
            })
        
        # Get primary key
        cur.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid 
                AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass
            AND i.indisprimary;
        """, (table_name,))
        
        primary_keys = [row[0] for row in cur.fetchall()]
        
        # Get foreign keys
        cur.execute("""
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
        """, (table_name,))
        
        foreign_keys = [{
            'column': row[0],
            'references': f"{row[1]}({row[2]})"
        } for row in cur.fetchall()]
        
        return {
            'name': table_name,
            'columns': columns,
            'primary_key': primary_keys,
            'foreign_keys': foreign_keys
        }

def print_table_info(table_info):
    """Print formatted table information."""
    print(f"\nTable: {table_info['name']}")
    print("-" * 60)
    
    # Print columns
    print("\nColumns:")
    print(f"{'Name':<30} {'Type':<20} {'Nullable':<10} {'Default'}")
    print("-" * 60)
    
    for col in table_info['columns']:
        print(f"{col['name']:<30} {col['type']:<20} {str(col['nullable']):<10} {col['default'] or ''}")
    
    # Print primary key
    if table_info['primary_key']:
        print(f"\nPrimary Key: {', '.join(table_info['primary_key'])}")
    
    # Print foreign keys
    if table_info['foreign_keys']:
        print("\nForeign Keys:")
        for fk in table_info['foreign_keys']:
            print(f"  {fk['column']} -> {fk['references']}")
    
    print("\n" + "=" * 60)

def main():
    print("Connecting to database...")
    conn = get_connection()
    
    try:
        print("Fetching tables...")
        tables = get_tables(conn)
        
        if not tables:
            print("No tables found in the database.")
            return
        
        print(f"\nFound {len(tables)} tables in the database:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
        # Get and print info for each table
        for table in tables:
            print(f"\nFetching info for table: {table}")
            table_info = get_table_info(conn, table)
            print_table_info(table_info)
        
        print("\nDatabase schema verification complete!")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
