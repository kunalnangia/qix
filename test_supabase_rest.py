import requests
import json

def test_supabase_rest():
    # Supabase configuration
    SUPABASE_URL = "https://lflecyuvttemfoyixngi.supabase.co/rest/v1/"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmbGVjeXV2dHRlbWZveWl4bmdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2Mzg2MTAsImV4cCI6MjA2ODIxNDYxMH0.7OUThn1GxGQJkRS7Si7M7upVchPD5OhH1r7LKE7l8MY"
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    print("Testing Supabase REST API connection...")
    print(f"Supabase URL: {SUPABASE_URL}")
    
    try:
        # Try to list all tables first
        print("\nAttempting to list tables...")
        response = requests.get(
            f"{SUPABASE_URL}?select=*&limit=1",
            headers=headers
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully connected to Supabase REST API!")
            try:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            except:
                print(f"Response: {response.text}")
            
            # Try to get a list of all tables
            print("\nAttempting to get table information...")
            tables_response = requests.get(
                "https://lflecyuvttemfoyixngi.supabase.co/rest/v1/?select=table_name&limit=10",
                headers=headers
            )
            
            if tables_response.status_code == 200:
                tables = tables_response.json()
                print(f"\nFound {len(tables)} tables:")
                for i, table in enumerate(tables, 1):
                    print(f"{i}. {table.get('table_name', 'Unknown')}")
            
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to get more detailed error information
            if response.status_code == 401:
                print("\n🔑 Authentication failed. Please check your Supabase API key.")
            elif response.status_code == 404:
                print("\n🔍 Endpoint not found. The REST API might be disabled or the URL is incorrect.")
    
    except Exception as e:
        print(f"\n❌ Error connecting to Supabase:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_supabase_rest()
