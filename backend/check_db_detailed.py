import os
import sys
import logging
from pathlib import Path
from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def print_header(title):
    print("\n" + "="*80)
    print(f" {title.upper()} ")
    print("="*80)

def check_db_connection():
    try:
        # Load environment variables
        env_path = str(Path(__file__).parent / '.env')
        load_dotenv(env_path)
        
        # Get database URL from environment
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            logger.error("❌ DATABASE_URL not found in environment variables")
            return False
            
        print_header("Database Connection Test")
        logger.info(f"🔍 Connecting to: {db_url}")
        
        # Create engine and test connection
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Test basic connection
            version = conn.execute(text("SELECT version()")).scalar()
            logger.info(f"✅ Connected to: {version}")
            
            # Get database info
            db_name = conn.execute(text("SELECT current_database()")).scalar()
            db_user = conn.execute(text("SELECT current_user")).scalar()
            db_schema = conn.execute(text("SELECT current_schema()")).scalar()
            
            logger.info(f"📊 Database: {db_name}")
            logger.info(f"👤 User: {db_user}")
            logger.info(f"🏷️  Schema: {db_schema}")
            
            # List all schemas
            logger.info("\n📋 Available schemas:")
            schemas = conn.execute(text("""
                SELECT nspname 
                FROM pg_catalog.pg_namespace 
                WHERE nspname NOT LIKE 'pg_%' AND nspname != 'information_schema'
                ORDER BY nspname
            """)).fetchall()
            
            for schema in schemas:
                logger.info(f"  - {schema[0]}")
            
            # List all tables in the current schema
            logger.info("\n📋 Tables in current schema:")
            tables = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = current_schema()
                ORDER BY table_name
            """)).fetchall()
            
            if not tables:
                logger.warning("  No tables found in the current schema!")
            else:
                for table in tables:
                    logger.info(f"  - {table[0]}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error connecting to database: {str(e)}")
        return False

if __name__ == "__main__":
    print_header("Database Check Utility")
    if check_db_connection():
        logger.info("\n✅ Database connection test completed successfully")
    else:
        logger.error("\n❌ Database connection test failed")
