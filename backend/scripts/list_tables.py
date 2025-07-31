import psycopg2

def list_tables():
    print("Connecting to the database...")
    
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
        
        # Get list of all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        if not tables:
            print("\n❌ No tables found in the database!")
            return
            
        print("\n📋 Found tables:")
        for table in tables:
            print(f"- {table[0]}")
            
            # Get columns for this table
            cursor.execute(f"""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = '{table[0]}'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            for col in columns:
                print(f"  • {col[0]} ({col[1]}, {'NULL' if col[2] == 'YES' else 'NOT NULL'})")
            
            print()  # Add a blank line between tables
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        print("\n✅ Database schema check completed")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    list_tables()
