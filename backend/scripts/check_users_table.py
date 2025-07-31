import psycopg2

def check_users_table():
    print("Checking for users table...")
    
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
        
        # Check if users table exists in any schema
        cursor.execute("""
            SELECT table_schema, table_name
            FROM information_schema.tables 
            WHERE table_name = 'users';
        """)
        
        users_tables = cursor.fetchall()
        
        if not users_tables:
            print("\n❌ No 'users' table found in any schema")
            return
            
        print("\nFound 'users' table in the following schemas:")
        for schema, table in users_tables:
            print(f"- {schema}.{table}")
            
            # Get columns for this table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
            """, (schema, table))
            
            columns = cursor.fetchall()
            
            print("\n  Columns:")
            for col in columns:
                col_name, data_type, is_nullable, col_default = col
                print(f"  - {col_name}: {data_type} {'NULL' if is_nullable == 'YES' else 'NOT NULL'}")
                if col_default:
                    print(f"    Default: {col_default}")
            
            # Check if there are any users in the table
            cursor.execute(f'SELECT COUNT(*) FROM \"{schema}\".\"{table}\";')
            user_count = cursor.fetchone()[0]
            print(f"\n  Total users: {user_count}")
            
            if user_count > 0:
                cursor.execute(f'SELECT * FROM \"{schema}\".\"users\" LIMIT 1;')
                user = cursor.fetchone()
                column_names = [desc[0] for desc in cursor.description]
                
                print("\n  Sample user:")
                for name, value in zip(column_names, user):
                    if name.lower() in ['password', 'hashed_password', 'salt']:
                        value = '********' if value else 'NULL'
                    print(f"    {name}: {value}")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Users table check completed")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    check_users_table()
