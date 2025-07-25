import requests

def check_supabase_endpoints():
    # Supabase configuration
    SUPABASE_URL = "https://lflecyuvttemfoyixngi.supabase.co/rest/v1/"
    SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmbGVjeXV2dHRlbWZveWl4bmdpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI2Mzg2MTAsImV4cCI6MjA2ODIxNDYxMH0.7OUThn1GxGQJkRS7Si7M7upVchPD5OhH1r7LKE7l8MY"
    
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}'
    }
    
    print("Testing Supabase REST API endpoints...")
    
    # Test the root endpoint
    try:
        print("\nTesting root endpoint...")
        response = requests.get(SUPABASE_URL, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}..." if len(response.text) > 500 else response.text)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test the tables endpoint
    try:
        print("\nTesting tables endpoint...")
        response = requests.get(f"{SUPABASE_URL}?select=*", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}..." if len(response.text) > 500 else response.text)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test the RPC endpoint
    try:
        print("\nTesting RPC endpoint...")
        response = requests.post(
            f"{SUPABASE_URL}rpc/get_tables",
            headers={**headers, 'Content-Type': 'application/json'},
            json={"schema_name": "public"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}..." if len(response.text) > 500 else response.text)
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nTest completed.")

if __name__ == "__main__":
    check_supabase_endpoints()
