import sys
import os
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Import required modules
try:
    from sqlalchemy import create_engine, text
    from app.core.config import settings
    logger.info("Imported required modules successfully")
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    raise

def test_connection():
    """Test database connection with current settings"""
    try:
        logger.info(f"Testing connection to database: {settings.DATABASE_URI}")
        
        # Create engine with current settings
        engine = create_engine(
            settings.DATABASE_URI,
            echo=True
        )
        
        # Test connection
        with engine.connect() as conn:
            # Get database version
            result = conn.execute(text("SELECT version();"))
            version = result.scalar()
            logger.info(f"✅ Successfully connected to database!")
            logger.info(f"Database version: {version}")
            
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            
            tables = result.fetchall()
            if tables:
                logger.info("\nTables in the database:")
                for table in sorted(tables):
                    logger.info(f"- {table[0]}")
            else:
                logger.warning("No tables found in the database")
                
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("=== Starting Database Connection Test ===")
    if test_connection():
        logger.info("✅ Database connection test completed successfully!")
    else:
        logger.error("❌ Database connection test failed")
        sys.exit(1)
