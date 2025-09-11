#!/usr/bin/env python3
"""
Debug deployment issues by testing key components
"""

import os
import sys
import traceback
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all key imports work."""
    try:
        logger.info("Testing imports...")
        
        # Test core imports
        from src.core.database.base import Base
        logger.info("✓ Base import successful")
        
        from src.users.models.user import User, Company
        logger.info("✓ User models import successful")
        
        from src.campaigns.models.campaign import Campaign  
        logger.info("✓ Campaign models import successful")
        
        from src.core.database.models import IntelligenceCore, Waitlist
        logger.info("✓ Core models import successful")
        
        from src.users.api.routes import router
        logger.info("✓ Routes import successful")
        
        return True
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def test_database_connection():
    """Test database connection."""
    try:
        logger.info("Testing database connection...")
        
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            logger.error("DATABASE_URL not set")
            return False
            
        from sqlalchemy import create_engine, text
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info("✓ Database connection successful")
            
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False

def test_environment_variables():
    """Test critical environment variables."""
    logger.info("Testing environment variables...")
    
    critical_vars = [
        'DATABASE_URL',
        'JWT_SECRET_KEY', 
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY'
    ]
    
    missing_vars = []
    for var in critical_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        return False
    else:
        logger.info("✓ All critical environment variables present")
        return True

def main():
    logger.info("=== Deployment Debug Tool ===")
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
        
    # Test environment variables  
    if not test_environment_variables():
        success = False
        
    # Test database connection
    if not test_database_connection():
        success = False
        
    if success:
        logger.info("✅ All tests passed!")
    else:
        logger.error("❌ Some tests failed!")
        
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)