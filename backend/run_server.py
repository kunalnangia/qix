import uvicorn
import sys
import os
from multiprocessing import freeze_support

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run():
    try:
        from app.main import app
        
        print("✅ Successfully imported the FastAPI application!")
        print(f"App title: {app.title}")
        print(f"App version: {app.version}")
        
        # Start the server
        print("\nStarting FastAPI server on http://127.0.0.1:8001")
        print("Press Ctrl+C to stop the server\n")
        
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8001,
            reload=True,
            log_level="info"
        )
    
    except ImportError as e:
        print(f"❌ Error importing application: {e}")
        print("\nMake sure you're running this script from the backend directory and all dependencies are installed.")
        print("Try running: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    freeze_support()
    run()
