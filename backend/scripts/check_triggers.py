import psycopg2

def check_triggers():
    print("Checking triggers on auth.users...")
    
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
        
        # Get triggers on auth.users
        cursor.execute("""
            SELECT 
                trigger_name, 
                event_manipulation,
                action_statement,
                action_timing
            FROM information_schema.triggers
            WHERE event_object_schema = 'auth' 
            AND event_object_table = 'users';
        """)
        
        triggers = cursor.fetchall()
        
        if not triggers:
            print("\n❌ No triggers found on auth.users")
            return
            
        print("\nTriggers on auth.users:")
        for trigger in triggers:
            print(f"\nName: {trigger[0]}")
            print(f"Event: {trigger[1]}")
            print(f"Timing: {trigger[3]}")
            print(f"Action: {trigger[2]}")
        
        # Get function definitions for the triggers
        cursor.execute("""
            SELECT 
                p.proname AS function_name,
                pg_get_functiondef(p.oid) AS function_definition
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname = 'auth';
        """)
        
        functions = cursor.fetchall()
        
        if functions:
            print("\nFunctions in auth schema:")
            for func in functions:
                print(f"\nFunction: {func[0]}")
                print(f"Definition: {func[1][:500]}...")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Trigger check completed")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    check_triggers()
