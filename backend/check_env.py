import sys
import os
import subprocess

def check_python_version():
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Working Directory: {os.getcwd()}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

def check_installed_packages():
    print("\nChecking installed packages...")
    try:
        import pkg_resources
        required = [
            'fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2-binary', 
            'python-dotenv', 'pydantic', 'requests', 'websockets'
        ]
        for package in required:
            try:
                dist = pkg_resources.get_distribution(package)
                print(f"✓ {dist.key} ({dist.version}) is installed")
            except pkg_resources.DistributionNotFound:
                print(f"✗ {package} is NOT installed")
    except Exception as e:
        print(f"Error checking packages: {e}")

def check_environment_variables():
    print("\nChecking environment variables...")
    required_vars = ['DATABASE_URL']
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✓ {var} is set"
                  f"{' (value hidden)' if 'PASSWORD' in var or 'SECRET' in var else f': {value}'}")
        else:
            print(f"✗ {var} is NOT set")

if __name__ == "__main__":
    print("=== Environment Check ===")
    check_python_version()
    check_environment_variables()
    check_installed_packages()
    print("\nEnvironment check completed.")
