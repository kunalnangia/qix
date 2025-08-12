import os
import sys
import subprocess
import time

def main():
    # Set the working directory to the backend directory
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    os.chdir(backend_dir)
    
    # Set up environment
    env = os.environ.copy()
    env['PYTHONPATH'] = os.path.dirname(os.path.abspath(__file__))
    
    print("Starting backend server...")
    print(f"Python path: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # Start the backend server using the Python interpreter
    cmd = [
        sys.executable,
        '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', '8001',
        '--reload',
        '--log-level', 'debug'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(
            cmd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Print output in real-time
        print("\nServer output:")
        print("-" * 80)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Wait for the process to complete and get the exit code
        return_code = process.wait()
        print(f"\nProcess exited with return code: {return_code}")
        
    except KeyboardInterrupt:
        print("\nStopping backend server...")
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Backend server stopped.")
    except Exception as e:
        print(f"Error starting backend server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
