import psycopg2

def check_auth_users():
    print("Checking auth.users table structure...")
    
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
        
        # Get columns for the auth.users table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'auth' AND table_name = 'users'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("\nColumns in auth.users:")
        for col in columns:
            col_name, data_type, is_nullable, col_default = col
            print(f"- {col_name}: {data_type} {'NULL' if is_nullable == 'YES' else 'NOT NULL'}")
            if col_default:
                print(f"  Default: {col_default}")
        
        # Check if there are any users in the table
        cursor.execute("SELECT COUNT(*) FROM auth.users;")
        user_count = cursor.fetchone()[0]
        print(f"\nTotal users in auth.users: {user_count}")
        
        if user_count > 0:
            # Get a sample user (without sensitive data)
            cursor.execute("""
                SELECT id, email, created_at, last_sign_in_at, role 
                FROM auth.users 
                LIMIT 1;
            """)
            
            user = cursor.fetchone()
            column_names = [desc[0] for desc in cursor.description]
            
            print("\nSample user:")
            for name, value in zip(column_names, user):
                print(f"- {name}: {value}")
        
        # Check for any triggers on the auth.users table
        cursor.execute("""
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers
            WHERE event_object_schema = 'auth' 
            AND event_object_table = 'users';
        """)
        
        triggers = cursor.fetchall()
        
        if triggers:
            print("\nTriggers on auth.users:")
            for trigger in triggers:
                print(f"- {trigger[0]} ({trigger[1]}): {trigger[2]}")
        else:
            print("\nNo triggers found on auth.users")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Auth users check completed")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    check_auth_users()
