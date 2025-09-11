#!/usr/bin/env python3
"""
Simple script to create database tables for production deployment.
This script ensures all tables exist before starting the app.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create all tables if they don't exist."""
    try:
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL environment variable is not set")
            return False
            
        logger.info("Connecting to database...")
        engine = create_engine(database_url)
        
        # Import all models to ensure they're registered with Base
        logger.info("Importing models...")
        from src.core.database.base import Base
        from src.users.models.user import User, Company
        from src.campaigns.models.campaign import Campaign
        from src.core.database.models import IntelligenceCore, Waitlist
        
        # Create all tables
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify critical tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result]
            logger.info(f"Tables in database: {tables}")
            
            # Check for required tables
            required_tables = ['users', 'companies', 'campaigns', 'intelligence_core', 'waitlist']
            missing_tables = [t for t in required_tables if t not in tables]
            
            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False
            else:
                logger.info("All required tables exist!")
                return True
                
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)