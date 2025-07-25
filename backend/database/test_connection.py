import time
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy import text
from sqlalchemy.orm import Session

# Import database configuration from app
from app.db.session import SessionLocal, engine, get_db
from app.core.config import settings

# Create a db_config dictionary for backward compatibility
db_config = type('DBConfig', (), {
    'db_url': settings.DATABASE_URL,
    'pool_size': settings.POOL_SIZE,
    'max_overflow': settings.MAX_OVERFLOW
})()

def test_connection() -> Dict[str, Any]:
    """Test the database connection and return connection details."""
    result = {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "connection": {
            "url": db_config.db_url.replace(db_config.db_url.split('@')[-1].split('/')[0], '[HIDDEN]'),
            "pool_size": db_config.pool_size,
            "max_overflow": db_config.max_overflow,
        },
        "tests": {}
    }
    
    try:
        # Test basic connection
        start_time = time.time()
        with engine.connect() as conn:
            db_version = conn.execute(text("SELECT version();")).scalar()
            result["tests"]["basic_connection"] = {
                "status": "success",
                "version": db_version,
                "duration": time.time() - start_time
            }
            
        # Test connection pooling
        start_time = time.time()
        connections = []
        try:
            for i in range(db_config.pool_size + db_config.max_overflow + 2):
                conn = engine.connect()
                connections.append(conn)
                result["tests"][f"connection_{i+1}"] = {
                    "status": "success",
                    "connection_id": id(conn)
                }
        except Exception as e:
            result["tests"][f"connection_pool"] = {
                "status": "error",
                "message": str(e),
                "max_connections_reached": len(connections)
            }
        finally:
            for conn in connections:
                conn.close()
                
        # Test concurrent connections
        def query_db(_):
            with SessionLocal() as session:
                return session.execute(text("SELECT 1")).scalar()
                
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(query_db, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
            
        result["tests"]["concurrent_queries"] = {
            "status": "success",
            "results": results,
            "duration": time.time() - start_time
        }
        
        # Test ORM session
        start_time = time.time()
        with SessionLocal() as session:
            count = session.execute(text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")).scalar()
            result["tests"]["orm_session"] = {
                "status": "success",
                "table_count": count,
                "duration": time.time() - start_time
            }
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        
    return result

def print_test_results(results: Dict[str, Any]) -> None:
    """Print the test results in a readable format."""
    print("\n" + "="*80)
    print(f"DATABASE CONNECTION TEST - {results['timestamp']}")
    print("="*80)
    print(f"\nDatabase URL: {results['connection']['url']}")
    print(f"Pool Size: {results['connection']['pool_size']}")
    print(f"Max Overflow: {results['connection']['max_overflow']}")
    
    print("\nTest Results:")
    print("-"*40)
    
    for test_name, test_result in results["tests"].items():
        status = test_result.get("status", "unknown").upper()
        status_color = "\033[92m" if status == "SUCCESS" else "\033[91m"
        print(f"{test_name}: {status_color}{status}\033[0m")
        
        for key, value in test_result.items():
            if key != "status":
                print(f"  {key}: {value}")
    
    if "error" in results:
        print("\n\033[91mERROR:\033[0m", results["error"])
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    results = test_connection()
    print_test_results(results)
