import os
import sys
import logging
import sqlalchemy
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('supabase_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_connection(db_url):
    """Test database connection with the provided URL"""
    try:
        logger.info("Testing database connection...")
        
        # Create engine with connection pooling
        engine = create_engine(
            db_url,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=5,
            max_overflow=10,
            connect_args={
                'connect_timeout': 10,
                'keepalives': 1,
                'keepalives_idle': 30,
                'keepalives_interval': 10,
                'keepalives_count': 5
            }
        )
        
        # Test connection
        with engine.connect() as conn:
            # Get database version
            version = conn.execute(text("SELECT version();")).scalar()
            logger.info(f"✅ Successfully connected to database!")
            logger.info(f"Database version: {version}")
            
            # List all tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """))
            
            tables = [row[0] for row in result.fetchall()]
            if tables:
                logger.info("\nTables in the database:")
                for table in sorted(tables):
                    logger.info(f"- {table}")
            else:
                logger.warning("No tables found in the database")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {str(e)}")
        return False

if __name__ == "__main__":
    # Use the provided database URL
    db_url = "postgresql://postgres:Ayeshaayesha12%40@db.lflecyuvttemfoyixngi.supabase.co:5432/postgres"
    
    # Test the connection
    logger.info("=" * 80)
    logger.info("TESTING SUPABASE DATABASE CONNECTION")
    logger.info("=" * 80)
    
    if test_connection(db_url):
        logger.info("\n✅ Database connection test completed successfully!")
    else:
        logger.error("\n❌ Database connection test failed")
    
    logger.info("\n" + "=" * 80)
    logger.info("TEST COMPLETED")
    logger.info("=" * 80)
