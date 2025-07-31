from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Test App", version="0.1.0")

@app.get("/")
async def read_root():
    return {"message": "Hello, World! This is a test endpoint."}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    port = 8002
    print(f"Starting test FastAPI server on http://127.0.0.1:{port}")
    print("Endpoints:")
    print("  - GET /: Basic test endpoint")
    print("  - GET /health: Health check endpoint")
    uvicorn.run("simple_app:app", host="0.0.0.0", port=port, reload=True)
