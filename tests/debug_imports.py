"""Debug Python imports and module resolution."""
import sys
import os
import importlib

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

def check_module_import(module_name):
    """Check if a module can be imported and print its location."""
    try:
        print(f"\n=== Checking import for: {module_name} ===")
        module = importlib.import_module(module_name)
        print(f"✓ Successfully imported: {module_name}")
        print(f"   Location: {module.__file__}")
        return True
    except ImportError as e:
        print(f"✗ Error importing {module_name}: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error importing {module_name}: {e}")
        return False

def check_absolute_import(module_path, full_path):
    """Check if a module can be imported using absolute path."""
    try:
        print(f"\n=== Checking absolute import for: {module_path} ===")
        spec = importlib.util.spec_from_file_location(module_path, full_path)
        if spec is None:
            print(f"✗ Could not create spec for {module_path}")
            return False
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_path] = module
        spec.loader.exec_module(module)
        print(f"✓ Successfully imported: {module_path}")
        print(f"   Location: {module.__file__}")
        return True
    except Exception as e:
        print(f"✗ Error importing {module_path}: {e}")
        return False

if __name__ == "__main__":
    print("\n=== Python Path ===")
    for path in sys.path:
        print(f"- {path}")
    
    # Check database_sqlite import
    db_sqlite_path = os.path.join(project_root, 'backend', 'database_sqlite.py')
    check_absolute_import('database_sqlite', db_sqlite_path)
    
    # Check models import
    models_path = os.path.join(project_root, 'backend', 'models.py')
    if os.path.exists(models_path):
        check_absolute_import('models', models_path)
    else:
        print("\n=== models.py not found at:", models_path)
    
    # Check server.py
    server_path = os.path.join(project_root, 'backend', 'server.py')
    if os.path.exists(server_path):
        print("\n=== server.py exists at:", server_path)
    else:
        print("\n=== server.py not found at:", server_path)
    
    # Try to import database_sqlite directly
    check_module_import('backend.database_sqlite')
