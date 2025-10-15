"""
PyFSD GenAI - Database Configuration

This module provides database configuration and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator

# Create base class for models
Base = declarative_base()

# Database engine (will be configured in conftest.py for tests)
engine = None
SessionLocal = None

def get_db() -> Generator:
    """Get database session."""
    if SessionLocal is None:
        raise RuntimeError("Database not initialized")
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database(database_url: str):
    """Initialize database connection."""
    global engine, SessionLocal
    
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)

