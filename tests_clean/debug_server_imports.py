"""Debug import issues in server.py by examining the import statements."""
import os
import sys
import re

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def find_imports(file_path):
    """Find all import statements in a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all import statements
    import_pattern = re.compile(r'^(from\s+(\S+)\s+import|import\s+(\S+))', re.MULTILINE)
    
    print(f"\n=== Import statements in {os.path.basename(file_path)} ===")
    for match in import_pattern.finditer(content):
        print(f"- Line {content[:match.start()].count('\n') + 1}: {match.group(0).strip()}")

def check_database_imports():
    """Check how the database is being imported in server.py."""
    server_path = os.path.join(project_root, 'backend', 'server.py')
    
    if not os.path.exists(server_path):
        print(f"✗ server.py not found at: {server_path}")
        return
    
    # Find all imports in server.py
    find_imports(server_path)
    
    # Check for database-related imports
    with open(server_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for database-related code
    db_related = [
        ('get_db', 'get_db function'),
        ('SessionLocal', 'SessionLocal'),
        ('engine', 'engine'),
        ('Base', 'Base'),
        ('models.Base', 'models.Base'),
        ('database_sqlite', 'database_sqlite module')
    ]
    
    print("\n=== Database-related code in server.py ===")
    for pattern, name in db_related:
        if pattern in content:
            print(f"✓ Found reference to: {name}")
        else:
            print(f"✗ Missing reference to: {name}")

if __name__ == "__main__":
    print("Debugging server.py imports...")
    check_database_imports()
