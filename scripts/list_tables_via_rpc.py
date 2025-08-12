import requests
import json

def list_tables_via_rpc():
    # Supabase configuration
    SUPABASE_URL = "https://lflecyuvttemfoyixngi.supabase.co/rest/v1/rpc/"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmbGVjeXV2dHRlbWZveWl4bmdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2Mzg2MTAsImV4cCI6MjA2ODIxNDYxMH0.7OUThn1GxGQJkRS7Si7M7upVchPD5OhH1r7LKE7l8MY"
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'params=single-object'
    }
    
    print("Attempting to list tables using RPC...")
    
    try:
        # Try to get tables from information_schema
        response = requests.post(
            f"{SUPABASE_URL}get_tables",
            headers=headers,
            data=json.dumps({
                "schema_name": "public"
            })
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully retrieved tables:")
            try:
                tables = response.json()
                if isinstance(tables, list):
                    for i, table in enumerate(tables, 1):
                        print(f"{i}. {table}")
                else:
                    print("Unexpected response format. Raw response:")
                    print(json.dumps(tables, indent=2)[:1000] + "...")
            except Exception as e:
                print(f"Error parsing response: {e}")
                print("Raw response:")
                print(response.text[:1000] + "...")
        else:
            print(f"❌ Failed to fetch tables. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            # If RPC function doesn't exist, try to create it
            if response.status_code == 404:
                print("\nRPC function 'get_tables' not found. Creating it...")
                create_rpc_function()
                
    except Exception as e:
        print(f"\n❌ Error:")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {str(e)}")

def create_rpc_function():
    # This function would contain SQL to create an RPC function
    # that lists all tables, but requires direct database access
    print("""
To list all tables, you need to create a PostgreSQL function in your database.

1. Go to the Supabase SQL Editor (https://app.supabase.com/project/YOUR_PROJECT_REF/sql)
2. Run this SQL to create the function:

CREATE OR REPLACE FUNCTION get_tables(schema_name text DEFAULT 'public')
RETURNS TABLE (table_name text) AS $$
BEGIN
    RETURN QUERY
    SELECT tablename::text
    FROM pg_tables
    WHERE schemaname = schema_name;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

3. Then run this script again to list the tables.
""")

if __name__ == "__main__":
    list_tables_via_rpc()
