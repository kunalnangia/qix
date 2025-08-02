from fastapi import FastAPI
import uvicorn
import sys
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello, World!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    print("🔄 Starting FastAPI test server...")
    print(f"   Python version: {sys.version}")
    print(f"   Working directory: {os.getcwd()}")
    print("   Endpoints:")
    print("   - http://localhost:8001/")
    print("   - http://localhost:8001/health")
    print("\nPress Ctrl+C to stop the server\n")
    
    try:
        uvicorn.run(app, host="0.0.0.0", port=8001)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("\nTroubleshooting steps:")
        print("1. Make sure port 8001 is not in use")
        print("2. Check if uvicorn is installed: pip install uvicorn")
        print("3. Try a different port: uvicorn test_fastapi:app --port 8001")
