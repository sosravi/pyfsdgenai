"""
PyFSD GenAI - Database Migration Script

This script creates the initial database migration for all models.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from alembic.config import Config
from alembic import command
from src.core.database import Base
from src.models.database_models import *  # Import all models

def create_initial_migration():
    """Create the initial database migration."""
    
    # Set up Alembic configuration
    alembic_cfg = Config("alembic.ini")
    
    # Create the migration
    command.revision(
        alembic_cfg,
        message="Initial migration - create all tables",
        autogenerate=True
    )
    
    print("✅ Initial migration created successfully!")
    print("📝 Review the migration file in alembic/versions/")
    print("🚀 Run 'alembic upgrade head' to apply the migration")

if __name__ == "__main__":
    create_initial_migration()
