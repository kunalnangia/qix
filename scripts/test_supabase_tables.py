import requests

def test_supabase_tables():
    # Supabase configuration
    SUPABASE_URL = "https://lflecyuvttemfoyixngi.supabase.co/rest/v1/"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmbGVjeXV2dHRlbWZveWl4bmdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2Mzg2MTAsImV4cCI6MjA2ODIxNDYxMH0.7OUThn1GxGQJkRS7Si7M7upVchPD5OhH1r7LKE7l8MY"
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    print("Testing Supabase Tables...")
    
    # List of tables to check
    tables_to_check = [
        'users', 'test_runs', 'test_cases',
        'test_suites', 'test_executions', 'test_results'
    ]
    
    for table in tables_to_check:
        try:
            print(f"\nChecking table: {table}")
            response = requests.get(
                f"{SUPABASE_URL}{table}?select=*&limit=1",
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"✅ Table '{table}' exists and is accessible")
                data = response.json()
                if data:
                    print(f"   First row columns: {', '.join(data[0].keys())}")
            else:
                print(f"❌ Table '{table}' not found or not accessible")
                print(f"   Status code: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error accessing table '{table}': {str(e)}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    test_supabase_tables()
