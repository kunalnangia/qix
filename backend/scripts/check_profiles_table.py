import psycopg2

def check_profiles_table():
    print("Checking for profiles table...")
    
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
        
        # Check if profiles table exists in public schema
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'profiles'
            );
        """)
        
        profiles_exists = cursor.fetchone()[0]
        
        if not profiles_exists:
            print("\n❌ No 'profiles' table found in the public schema")
            return
            
        print("\n✅ Found 'profiles' table in public schema")
        
        # Get columns for the profiles table
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = 'profiles'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        
        print("\nColumns in public.profiles:")
        for col in columns:
            col_name, data_type, is_nullable, col_default = col
            print(f"- {col_name}: {data_type} {'NULL' if is_nullable == 'YES' else 'NOT NULL'}")
            if col_default:
                print(f"  Default: {col_default}")
        
        # Check if there are any triggers on the profiles table
        cursor.execute("""
            SELECT trigger_name, event_manipulation, action_statement
            FROM information_schema.triggers
            WHERE event_object_schema = 'public' 
            AND event_object_table = 'profiles';
        """)
        
        triggers = cursor.fetchall()
        
        if triggers:
            print("\nTriggers on public.profiles:")
            for trigger in triggers:
                print(f"- {trigger[0]} ({trigger[1]}): {trigger[2]}")
        else:
            print("\nNo triggers found on public.profiles")
        
        # Check if there are any foreign key constraints on the profiles table
        cursor.execute("""
            SELECT
                tc.constraint_name, 
                kcu.column_name, 
                ccu.table_schema || '.' || ccu.table_name || '.' || ccu.column_name AS foreign_column_name 
            FROM 
                information_schema.table_constraints AS tc 
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
            WHERE 
                tc.constraint_type = 'FOREIGN KEY' 
                AND tc.table_schema = 'public'
                AND tc.table_name = 'profiles';
        """)
        
        fks = cursor.fetchall()
        
        if fks:
            print("\nForeign key constraints on public.profiles:")
            for fk in fks:
                print(f"- {fk[0]}: {fk[1]} references {fk[2]}")
        else:
            print("\nNo foreign key constraints found on public.profiles")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Profiles table check completed")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    check_profiles_table()
