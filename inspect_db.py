import psycopg2
import sys
from datetime import datetime

def connect_db():
    """Create a database connection."""
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
        print(f"Error connecting to database: {e}")
        sys.exit(1)

def get_table_info(conn, table_name):
    """Get information about a specific table."""
    with conn.cursor() as cur:
        # Get columns
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
            'columns': columns,
            'primary_key': primary_keys,
            'foreign_keys': foreign_keys
        }

def main():
    print("Connecting to database...")
    conn = connect_db()
    
    try:
        # Get list of tables
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cur.fetchall()]
        
        print(f"\nFound {len(tables)} tables in the database:")
        for i, table in enumerate(tables, 1):
            print(f"{i}. {table}")
        
        # Get info for each table
        schema = {}
        for table in tables:
            print(f"\nProcessing table: {table}")
            schema[table] = get_table_info(conn, table)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"db_schema_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("DATABASE SCHEMA\n")
            f.write("=" * 80 + "\n\n")
            
            for table, info in schema.items():
                f.write(f"TABLE: {table}\n")
                f.write("-" * 80 + "\n")
                
                # Write columns
                f.write("COLUMNS:\n")
                f.write(f"{'Name':<30} {'Type':<20} {'Nullable':<10} {'Default'}\n")
                f.write("-" * 80 + "\n")
                
                for col in info['columns']:
                    f.write(f"{col['name']:<30} {col['type']:<20} {str(col['nullable']):<10} {str(col['default'] or '')}\n")
                
                # Write primary key
                if info['primary_key']:
                    f.write("\nPRIMARY KEY: " + ", ".join(info['primary_key']) + "\n")
                
                # Write foreign keys
                if info['foreign_keys']:
                    f.write("\nFOREIGN KEYS:\n")
                    for fk in info['foreign_keys']:
                        f.write(f"  {fk['column']} -> {fk['references']}\n")
                
                f.write("\n" + "=" * 80 + "\n\n")
        
        print(f"\nSchema saved to {filename}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
