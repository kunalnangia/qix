from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create a minimal FastAPI app
app = FastAPI(title="Minimal Test API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health check endpoint
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Minimal FastAPI server is running",
        "version": "0.1.0"
    }

# Simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Simple test endpoint that doesn't require database
@app.get("/api/test")
async def test_endpoint():
    return {
        "message": "This is a test endpoint that doesn't require database access",
        "data": {
            "test": "success",
            "timestamp": "2023-01-01T00:00:00Z"
        }
    }

if __name__ == "__main__":
    print("Starting minimal FastAPI server...")
    print("Endpoints:")
    print("  - GET /: Health check")
    print("  - GET /health: Health check")
    print("  - GET /api/test: Test endpoint")
    
    uvicorn.run(
        "minimal_app:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="debug"
    )
