"""Debug backend module imports and structure."""
import sys
import os
import importlib.util

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def check_module(module_name):
    """Check if a module can be imported and print its file location."""
    try:
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            print(f"✗ Module not found: {module_name}")
            return False
        
        module = importlib.import_module(module_name)
        print(f"✓ Successfully imported: {module_name}")
        print(f"   Location: {spec.origin}")
        
        # List all attributes of the module
        print("   Attributes:")
        for attr in dir(module):
            if not attr.startswith('_'):
                print(f"   - {attr}")
        
        return True
    except Exception as e:
        print(f"✗ Error importing {module_name}: {str(e)}")
        return False

print("\n=== Debugging Backend Imports ===")
print(f"Python path: {sys.path}\n")

# Check backend module
print("\n--- Checking backend module ---")
check_module("backend")

# Check backend.server
print("\n--- Checking backend.server ---")
check_module("backend.server")

# Check backend.database_sqlite
print("\n--- Checking backend.database_sqlite ---")
check_module("backend.database_sqlite")
