"""
Minimal script to check Python environment and basic functionality.
This script avoids any potential encoding issues by using only ASCII characters.
"""

import os
import sys

def main():
    # Create a log file with a unique name
    log_file = f"minimal_check_{os.getpid()}.txt"
    
    try:
        with open(log_file, 'w', encoding='utf-8') as f:
            # Basic environment information
            f.write("=== Python Environment Check ===\n\n")
            f.write(f"Python Version: {sys.version}\n")
            f.write(f"Executable: {sys.executable}\n")
            f.write(f"Current Directory: {os.getcwd()}\n")
            f.write(f"Platform: {sys.platform}\n")
            f.write(f"Default Encoding: {sys.getdefaultencoding()}\n")
            f.write(f"File System Encoding: {sys.getfilesystemencoding()}\n")
            
            # Check for .env file
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
            f.write(f"\n=== Checking for .env file ===\n")
            f.write(f"Looking for .env at: {env_path}\n")
            
            if os.path.exists(env_path):
                f.write("[OK] .env file found\n")
                
                # Check if we can read the .env file
                try:
                    with open(env_path, 'r', encoding='utf-8') as env_file:
                        lines = env_file.readlines()
                        f.write(f"Successfully read {len(lines)} lines from .env\n")
                        
                        # Show first few non-comment lines (masking sensitive data)
                        f.write("\nFirst few non-comment lines (sensitive data masked):\n")
                        count = 0
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('#'):
                                # Mask sensitive data
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    if any(s in key.lower() for s in ['pass', 'secret', 'key', 'token']):
                                        value = '***MASKED***'
                                    line = f"{key}={value}"
                                f.write(f"- {line}\n")
                                count += 1
                                if count >= 3:  # Only show first 3 non-comment lines
                                    break
                except Exception as e:
                    f.write(f"[ERROR] Reading .env file: {str(e)}\n")
            else:
                f.write("[ERROR] .env file not found\n")
                
                # List directory contents
                dir_path = os.path.dirname(env_path)
                if os.path.exists(dir_path):
                    f.write("\nDirectory contents:\n")
                    try:
                        for item in os.listdir(dir_path):
                            item_path = os.path.join(dir_path, item)
                            item_type = "(file)" if os.path.isfile(item_path) else "(dir)"
                            f.write(f"- {item} {item_type}\n")
                    except Exception as e:
                        f.write(f"[ERROR] Listing directory: {str(e)}\n")
            
            # Check for required Python packages
            f.write("\n=== Checking Python Packages ===\n")
            packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2', 'python-dotenv', 'pydantic']
            for pkg in packages:
                try:
                    __import__(pkg.replace('-', '_'))
                    f.write(f"[OK] {pkg} is installed\n")
                except ImportError:
                    f.write(f"[MISSING] {pkg} is not installed\n")
            
            f.write("\n=== Script completed successfully ===\n")
            
    except Exception as e:
        # If we can't write to the log file, try to print to stderr
        print(f"[FATAL] Error in minimal_check.py: {str(e)}", file=sys.stderr)
        return 1
    
    print(f"Check completed. Results written to: {os.path.abspath(log_file)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
