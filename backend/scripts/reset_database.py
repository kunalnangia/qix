import asyncio
import logging
import os
import sys
from sqlalchemy import text

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine as sync_engine
from app.models.db_models import (
    User, Project, TestCase, TestStep, TestPlan, TestExecution,
    Comment, Team, TeamMember, Environment, Attachment, TestPlanTestCase, ActivityLog
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def reset_database():
    """
    Drops and recreates all tables in the database.
    """
    try:
        logger.info("Starting database reset...")

        tables = [
            User.__table__,
            Team.__table__,
            Project.__table__,
            Environment.__table__,
            TestCase.__table__,
            TestStep.__table__,
            TestPlan.__table__,
            TestPlanTestCase.__table__,
            TestExecution.__table__,
            Comment.__table__,
            TeamMember.__table__,
            Attachment.__table__,
            ActivityLog.__table__
        ]

        with sync_engine.connect() as conn:
            logger.info("Disabling foreign key constraints...")
            conn.execute(text('SET session_replication_role = "replica";'))

            logger.info("Dropping all tables...")
            for table in reversed(tables):
                try:
                    logger.info(f"Dropping table: {table.name}")
                    table.drop(conn, checkfirst=True)
                except Exception as e:
                    logger.warning(f"Could not drop table {table.name}: {e}")

            logger.info("Creating all tables...")
            for table in tables:
                try:
                    logger.info(f"Creating table: {table.name}")
                    table.create(conn, checkfirst=True)
                except Exception as e:
                    logger.error(f"Could not create table {table.name}: {e}")
                    raise

            logger.info("Enabling foreign key constraints...")
            conn.execute(text('SET session_replication_role = "origin";'))

        logger.info("Database reset successfully.")

    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(reset_database())
