import psycopg2

def check_handle_new_user():
    print("Checking handle_new_user function in auth schema...")
    
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
            SELECT pg_get_functiondef(oid) AS function_definition
            FROM pg_proc
            WHERE proname = 'handle_new_user';
        """)
        
        result = cursor.fetchone()
        
        if not result:
            print("❌ handle_new_user function not found")
            return
            
        function_definition = result[0]
        
        print("\nFunction definition for handle_new_user:")
        print("-" * 80)
        print(function_definition)
        print("-" * 80)
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Function check completed")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    check_handle_new_user()
