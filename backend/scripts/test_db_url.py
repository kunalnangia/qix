import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('test_db_url')

def test_get_supabase_db_url():
    """Test the get_supabase_db_url function"""
    logger.info("\n=== Starting tests for get_supabase_db_url() ===")
    
    # Test with a valid postgres:// URL
    test_url = 'postgres://user:pass@host:5432/dbname'
    os.environ['DATABASE_URL'] = test_url
    logger.info(f"\nTest 1: Converting postgres:// to postgresql+asyncpg://")
    logger.info(f"Input URL: {test_url}")
    
    # Import here to ensure we get the latest version
    if 'update_db_urls' in sys.modules:
        import importlib
        importlib.reload(sys.modules['update_db_urls'])
    from update_db_urls import get_supabase_db_url
    
    # Test conversion from postgres:// to postgresql+asyncpg://
    result = get_supabase_db_url()
    expected = 'postgresql+asyncpg://user:pass@host:5432/dbname'
    logger.info(f"Expected: {expected}")
    logger.info(f"Got:      {result}")
    assert result == expected, f"Expected postgresql+asyncpg URL, got {result}"
    
    # Test with already correct URL
    test_url = 'postgresql+asyncpg://user:pass@host:5432/dbname'
    os.environ['DATABASE_URL'] = test_url
    logger.info(f"\nTest 2: Already correct URL format")
    logger.info(f"Input URL: {test_url}")
    
    result = get_supabase_db_url()
    expected = 'postgresql+asyncpg://user:pass@host:5432/dbname'
    logger.info(f"Expected: {expected}")
    logger.info(f"Got:      {result}")
    assert result == expected, f"Expected same URL, got {result}"
    
    # Test with invalid URL
    test_url = 'invalid-url'
    os.environ['DATABASE_URL'] = test_url
    logger.info(f"\nTest 3: Invalid URL format")
    logger.info(f"Input URL: {test_url}")
    
    result = get_supabase_db_url()
    logger.info(f"Expected: None")
    logger.info(f"Got:      {result}")
    assert result is None, f"Expected None for invalid URL, got {result}"
    
    # Test with empty URL
    test_url = ''
    os.environ['DATABASE_URL'] = test_url
    logger.info(f"\nTest 4: Empty URL")
    logger.info(f"Input URL: (empty string)")
    
    result = get_supabase_db_url()
    logger.info(f"Expected: None")
    logger.info(f"Got:      {result}")
    assert result is None, f"Expected None for empty URL, got {result}"
    
    logger.info("\n✅ All tests passed!")

if __name__ == "__main__":
    test_get_supabase_db_url()
