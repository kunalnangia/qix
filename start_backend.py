import os
import sys
import subprocess
import time
import signal
import logging
from pathlib import Path
from dotenv import load_dotenv

def check_port_in_use(port):
    """Check if a port is in use."""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Kill process running on the specified port."""
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.info['connections'] or []:
                if conn.laddr.port == port:
                    print(f"Killing process {proc.info['pid']} using port {port}")
                    proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def start_backend():
    """Start the FastAPI backend server with proper environment setup."""
    # Load environment variables from .env file
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    load_dotenv(env_path, override=True)
    
    # Ensure we're using the correct database URL with the pooler format
    db_url = "postgresql://postgres.lflecyuvttemfoyixngi:Ayeshaayesha121@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
    os.environ['DATABASE_URL'] = db_url
    
    # Set the working directory to the backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # Set up environment
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    env['DATABASE_URL'] = db_url  # Ensure the correct DB URL is used
    
    # Start the backend server with detailed logging
    cmd = [
        sys.executable,  # Use the same Python interpreter
        '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', '8001',
        '--reload',
        '--log-level', 'debug',
        '--use-colors',
        '--no-access-log'  # Disable access logs for cleaner output
    ]
    
    print(f"Starting backend server with command: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    # Monitor the output
    print("Backend server started. Press Ctrl+C to stop.")
    print("Server output:")
    print("-" * 80)
    
    try:
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
            
            error = process.stderr.readline()
            if error:
                print(f"ERROR: {error.strip()}")
                
    except KeyboardInterrupt:
        print("\nStopping backend server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Backend server stopped.")
    
    return process.returncode

if __name__ == "__main__":
    # Kill any process using port 8001
    if check_port_in_use(8001):
        print("Port 8001 is in use. Attempting to free it...")
        kill_process_on_port(8001)
        time.sleep(2)  # Give it a moment to release the port
    
    # Start the backend
    sys.exit(start_backend())
