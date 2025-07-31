import psycopg2

def get_function_definition():
    print("Getting handle_new_user function definition...")
    
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
        
        # Get the function definition
        cursor.execute("""
            SELECT 
                n.nspname as schema_name,
                p.proname as function_name,
                pg_get_functiondef(p.oid) as function_definition
            FROM 
                pg_proc p
                LEFT JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE 
                p.proname = 'handle_new_user' 
                AND n.nspname = 'auth';
        """)
        
        result = cursor.fetchone()
        
        if not result:
            print("❌ handle_new_user function not found in auth schema")
            return
            
        schema_name, function_name, function_definition = result
        
        print(f"\nFunction: {schema_name}.{function_name}")
        print("-" * 80)
        print(function_definition)
        print("-" * 80)
        
        # Also try to get the function definition in chunks if it's too large
        cursor.execute("""
            SELECT pg_get_functiondef(p.oid) as function_definition
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE p.proname = 'handle_new_user' AND n.nspname = 'auth';
        """)
        
        # Try to get the full function definition in chunks
        cursor.itersize = 1000  # Adjust the chunk size as needed
        full_definition = ""
        for row in cursor:
            full_definition += row[0] if row[0] else ""
        
        if full_definition and len(full_definition) > len(function_definition):
            print("\nFull function definition (chunked):")
            print("-" * 80)
            print(full_definition)
            print("-" * 80)
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Function definition retrieved")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    get_function_definition()
