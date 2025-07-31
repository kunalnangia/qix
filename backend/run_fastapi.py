import sys
import uvicorn
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_fastapi():
    try:
        logger.info("🚀 Starting FastAPI application...")
        
        # Import the FastAPI app
        from app.main import app
        
        # Configure uvicorn to run the app
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=8001,
            log_level="info",
            reload=True
        )
        
        server = uvicorn.Server(config)
        logger.info("✅ FastAPI app imported successfully")
        
        # List all routes
        logger.info("\n📋 Registered routes:")
        for route in app.routes:
            if hasattr(route, 'path'):
                methods = getattr(route, 'methods', [])
                logger.info(f"- {route.path} [{', '.join(methods) if methods else 'N/A'}]")
        
        # Start the server
        logger.info("\n🌐 Starting FastAPI server...")
        server.run()
        
    except ImportError as e:
        logger.error(f"❌ Import error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(run_fastapi())
