import psycopg2

def check_schema():
    print("Checking database schema...")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host="db.lflecyuvttemfoyixngi.supabase.co",
            database="postgres",
            user="postgres",
            password="Ayeshaayesha12@",
            port="5432"
        )
        
        # Create a cursor
        cursor = conn.cursor()
        
        # Get list of all schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schema_name;
        """)
        
        schemas = [row[0] for row in cursor.fetchall()]
        
        print("\nFound schemas:", schemas)
        
        # For each schema, list tables and columns
        for schema in schemas:
            print(f"\nSchema: {schema}")
            print("-" * 50)
            
            # Get tables in this schema
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = %s
                ORDER BY table_name;
            """, (schema,))
            
            tables = [row[0] for row in cursor.fetchall()]
            
            if not tables:
                print("  No tables found in this schema")
                continue
                
            for table in tables:
                print(f"\n  Table: {schema}.{table}")
                
                # Get columns for this table
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable, column_default
                    FROM information_schema.columns 
                    WHERE table_schema = %s AND table_name = %s
                    ORDER BY ordinal_position;
                """, (schema, table))
                
                columns = cursor.fetchall()
                
                if not columns:
                    print("    No columns found for this table")
                    continue
                    
                for col in columns:
                    col_name, data_type, is_nullable, col_default = col
                    print(f"    - {col_name}: {data_type} {'NULL' if is_nullable == 'YES' else 'NOT NULL'}")
                    if col_default:
                        print(f"      Default: {col_default}")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Schema check completed")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    check_schema()
