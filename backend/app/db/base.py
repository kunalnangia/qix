"""
Base model definition for SQLAlchemy models.
This file contains the declarative base class that all models should inherit from.
"""
from sqlalchemy.ext.declarative import declarative_base

# Create a base class for all database models
Base = declarative_base()

# This allows us to import Base without causing circular imports
__all__ = ['Base']
