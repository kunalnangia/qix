import requests

def list_supabase_tables():
    # Supabase configuration
    SUPABASE_URL = "https://lflecyuvttemfoyixngi.supabase.co/rest/v1/"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmbGVjeXV2dHRlbWZveWl4bmdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2Mzg2MTAsImV4cCI6MjA2ODIxNDYxMH0.7OUThn1GxGQJkRS7Si7M7upVchPD5OhH1r7LKE7l8MY"
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    print("Fetching list of all tables from Supabase...")
    
    try:
        # Get database schema information
        response = requests.get(
            f"{SUPABASE_URL}?select=*",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Successfully connected to Supabase!")
            print("\nAvailable tables:")
            
            try:
                tables = response.json()
                if isinstance(tables, list):
                    for i, table in enumerate(tables, 1):
                        table_name = table.get('table_name', 'unknown')
                        print(f"{i}. {table_name}")
                else:
                    print("Unexpected response format. Raw response:")
                    print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
            except Exception as e:
                print(f"Error parsing response: {e}")
                print("Raw response:")
                print(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        else:
            print(f"❌ Failed to fetch tables. Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}..." if len(response.text) > 500 else response.text)
    
    except Exception as e:
        print(f"\n❌ Error connecting to Supabase:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    list_supabase_tables()
