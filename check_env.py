import sys
import os

def check_python_version():
    """Check Python version"""
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")

def check_imports():
    """Check if required packages are installed"""
    packages = [
        'fastapi',
        'sqlalchemy',
        'pydantic',
        'python-jose',
        'passlib',
        'python-dotenv',
        'psycopg2-binary',
        'alembic',
    ]
    
    print("\nChecking required packages:")
    for package in packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is NOT installed")

def check_project_structure():
    """Check if project structure is correct"""
    print("\nChecking project structure:")
    
    # Check if backend directory exists
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'backend'))
    print(f"Backend directory: {backend_dir}")
    print(f"Exists: {os.path.exists(backend_dir)}")
    
    if os.path.exists(backend_dir):
        # List contents of backend directory
        print("\nContents of backend directory:")
        for item in os.listdir(backend_dir):
            item_path = os.path.join(backend_dir, item)
            item_type = "directory" if os.path.isdir(item_path) else "file"
            print(f"- {item} ({item_type})")
    
    # Check if app directory exists
    app_dir = os.path.join(backend_dir, 'app')
    print(f"\nApp directory: {app_dir}")
    print(f"Exists: {os.path.exists(app_dir)}")
    
    if os.path.exists(app_dir):
        # List contents of app directory
        print("\nContents of app directory:")
        for item in os.listdir(app_dir):
            item_path = os.path.join(app_dir, item)
            item_type = "directory" if os.path.isdir(item_path) else "file"
            print(f"- {item} ({item_type})")

def main():
    print("=== Environment Check ===\n")
    check_python_version()
    check_imports()
    check_project_structure()

if __name__ == "__main__":
    main()
