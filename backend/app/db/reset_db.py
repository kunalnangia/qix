import sys
import logging
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .session import engine, Base
from ..models.db_models import (
    User, Project, TestCase, TestStep, TestPlan, 
    TestExecution, Comment, Team, TeamMember, 
    Environment, Attachment, TestPlanTestCase, ActivityLog
)

def reset_database():
    """
    Reset the database by dropping all tables and recreating them.
    """
    try:
        with engine.connect() as conn:
            # Disable foreign key constraints
            logger.info("Disabling foreign key constraints...")
            conn.execute(text('SET session_replication_role = "replica";'))
            conn.commit()
            
            # Get all tables in the database
            result = conn.execute(text(
                """
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public' 
                ORDER BY tablename;
                """
            ))
            all_tables = [row[0] for row in result]
            
            # Drop all tables in the correct order
            logger.info("Dropping existing tables...")
            for table_name in all_tables:
                try:
                    logger.info(f"Dropping table: {table_name}")
                    conn.execute(text(f'DROP TABLE IF EXISTS \"{table_name}\" CASCADE;'))
                    conn.commit()
                    logger.info(f"Dropped table: {table_name}")
                except Exception as e:
                    logger.error(f"Error dropping table {table_name}: {str(e)}")
                    conn.rollback()
                    raise
            
            # Re-enable foreign key constraints
            logger.info("Re-enabling foreign key constraints...")
            conn.execute(text('SET session_replication_role = "origin";'))
            conn.commit()
            
            # Create all tables
            logger.info("Creating all tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("All tables created successfully!")
            
            return True
            
    except SQLAlchemyError as e:
        logger.error(f"Database error occurred: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting database reset...")
    if reset_database():
        logger.info("Database reset completed successfully!")
        sys.exit(0)
    else:
        logger.error("Database reset failed!")
        sys.exit(1)
