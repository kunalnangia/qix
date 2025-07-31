import os
import sys

# Set up simple print-based logging
def log(message):
    print(f"[TEST] {message}")

# Test get_supabase_db_url function
def test_get_supabase_db_url():
    log("Starting tests for get_supabase_db_url()")
    
    # Import the function directly
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from app.db.session import get_supabase_db_url
    
    # Test 1: Convert postgres:// to postgresql+asyncpg://
    test_url = 'postgres://user:pass@host:5432/dbname'
    os.environ['DATABASE_URL'] = test_url
    result = get_supabase_db_url()
    expected = 'postgresql+asyncpg://user:pass@host:5432/dbname'
    log(f"Test 1 - Input: {test_url}")
    log(f"   Expected: {expected}")
    log(f"   Got:      {result}")
    assert result == expected, f"Test 1 failed: Expected {expected}, got {result}"
    
    # Test 2: Already correct URL format
    test_url = 'postgresql+asyncpg://user:pass@host:5432/dbname'
    os.environ['DATABASE_URL'] = test_url
    result = get_supabase_db_url()
    log(f"\nTest 2 - Input: {test_url}")
    log(f"   Expected: {test_url}")
    log(f"   Got:      {result}")
    assert result == test_url, f"Test 2 failed: Expected {test_url}, got {result}"
    
    # Test 3: Invalid URL format
    test_url = 'invalid-url'
    os.environ['DATABASE_URL'] = test_url
    result = get_supabase_db_url()
    log(f"\nTest 3 - Input: {test_url}")
    log(f"   Expected: None")
    log(f"   Got:      {result}")
    assert result is None, f"Test 3 failed: Expected None, got {result}"
    
    # Test 4: Empty URL
    test_url = ''
    os.environ['DATABASE_URL'] = test_url
    result = get_supabase_db_url()
    log(f"\nTest 4 - Input: (empty string)")
    log(f"   Expected: None")
    log(f"   Got:      {result}")
    assert result is None, f"Test 4 failed: Expected None, got {result}"
    
    log("\n✅ All tests passed!")

if __name__ == "__main__":
    test_get_supabase_db_url()
