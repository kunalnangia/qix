import psycopg2

def test_connection():
    print("Testing database connection...")
    
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
        
        # Execute a simple query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print("\n✅ Successfully connected to the database!")
        print(f"Database version: {version[0]}")
        
        # Close the cursor and connection
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error connecting to the database: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
