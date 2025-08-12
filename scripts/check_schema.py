import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any

def get_db_connection():
    """Create a database connection."""
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres.lflecyuvttemfoyixngi",
        password="Ayeshaayesha12@",
        host="aws-0-ap-southeast-1.pooler.supabase.com",
        port=5432,
        sslmode="require"
    )
    return conn

def get_tables(conn) -> List[Dict[str, Any]]:
    """Get list of all tables in the public schema."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        return [{'name': row[0], 'type': row[1]} for row in cur.fetchall()]

def get_table_columns(conn, table_name: str) -> List[Dict[str, Any]]:
    """Get column details for a specific table."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                column_name, 
                data_type,
                is_nullable,
                column_default,
                character_maximum_length,
                numeric_precision,
                numeric_scale
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = %s
            ORDER BY ordinal_position;
        
        """, (table_name,))
        
        columns = []
        for row in cur.fetchall():
            col_type = row[1]
            if row[4]:  # character_maximum_length
                col_type = f"{col_type}({row[4]})"
            elif row[5]:  # numeric_precision
                if row[6]:  # numeric_scale
                    col_type = f"{col_type}({row[5]},{row[6]})"
                else:
                    col_type = f"{col_type}({row[5]})"
            
            columns.append({
                'name': row[0],
                'type': col_type,
                'nullable': row[2] == 'YES',
                'default': row[3]
            })
        
        return columns

def get_primary_keys(conn, table_name: str) -> List[str]:
    """Get primary key columns for a table."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid 
                AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass
            AND i.indisprimary;
        """, (table_name,))
        return [row[0] for row in cur.fetchall()]

def get_foreign_keys(conn, table_name: str) -> List[Dict[str, Any]]:
    """Get foreign key constraints for a table."""
    with conn.cursor() as cur:
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
        
        return [{
            'column': row[0],
            'references': f"{row[1]}.{row[2]}"
        } for row in cur.fetchall()]

def print_schema():
    """Print the database schema in a readable format."""
    try:
        conn = get_db_connection()
        
        print("\n" + "="*80)
        print("DATABASE SCHEMA INSPECTION")
        print("="*80)
        
        # Get all tables
        tables = get_tables(conn)
        if not tables:
            print("\nNo tables found in the database.")
            return
        
        print(f"\nFound {len(tables)} tables in the database:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table['name']} ({table['type']})")
        
        # Get details for each table
        for table in tables:
            table_name = table['name']
            
            print("\n" + "="*80)
            print(f"TABLE: {table_name}")
            print("="*80)
            
            # Get columns
            columns = get_table_columns(conn, table_name)
            print("\nCOLUMNS:")
            print("-" * 80)
            print(f"{'Name':<30} {'Type':<25} {'Nullable':<10} {'Default'}")
            print("-" * 80)
            
            for col in columns:
                nullable = "YES" if col['nullable'] else "NO"
                default = col['default'] or ""
                print(f"{col['name']:<30} {col['type']:<25} {nullable:<10} {default}")
            
            # Get primary keys
            pks = get_primary_keys(conn, table_name)
            if pks:
                print(f"\nPRIMARY KEY: {', '.join(pks)}")
            
            # Get foreign keys
            fks = get_foreign_keys(conn, table_name)
            if fks:
                print("\nFOREIGN KEYS:")
                for fk in fks:
                    print(f"  {fk['column']} -> {fk['references']}")
            
            print("\n" + "-" * 80)
        
        print("\nSchema inspection complete!")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Inspecting database schema...")
    print_schema()
