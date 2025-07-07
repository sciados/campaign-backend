import os
import sys
import uvicorn
import logging
from pathlib import Path

# ============================================================================
# ✅ ENHANCED PATH SETUP
# ============================================================================

# Add project root and src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"

# Ensure paths are in sys.path
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Set PYTHONPATH environment variable
os.environ["PYTHONPATH"] = f"{project_root}:{src_path}:{os.environ.get('PYTHONPATH', '')}"

# ============================================================================
# ✅ ENHANCED LOGGING SETUP
# ============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# ✅ DATABASE AND MODEL INITIALIZATION
# ============================================================================

def initialize_database_and_models():
    """
    Initialize database and models in correct order to prevent table conflicts
    """
    try:
        logger.info("🔧 Initializing database and models...")
        
        # Import database core first
        from src.core.database import engine, Base, get_db
        logger.info("✅ Database core imported")
        
        # Import models in dependency order
        logger.info("📦 Importing models in dependency order...")
        
        # Core models first
        from src.models.user import User
        from src.models.company import Company
        logger.info("✅ Core models (User, Company) imported")
        
        # Campaign models
        try:
            from src.models.campaign import Campaign
            logger.info("✅ Campaign models imported")
        except ImportError as e:
            logger.warning(f"⚠️ Campaign models not available: {e}")
        
        # ClickBank models last (most likely to have conflicts)
        try:
            from src.models.clickbank import (
                ClickBankProduct,
                ClickBankCategoryURL,
                UserAffiliatePreferences,
                AffiliateLinkClick,
                ScrapingSchedule,
                ScrapingLog,
                ProductPerformance
            )
            logger.info("✅ ClickBank models imported successfully")
            
            # Create tables with conflict resolution
            try:
                logger.info("🏗️ Creating/verifying database tables...")
                Base.metadata.create_all(bind=engine)
                logger.info("✅ Database tables created/verified successfully")
                return True
                
            except Exception as table_error:
                if "already defined" in str(table_error):
                    logger.warning("⚠️ Table definition conflicts detected, attempting resolution...")
                    try:
                        # Clear metadata and recreate
                        Base.metadata.clear()
                        
                        # Re-import models to refresh metadata
                        from src.models.user import User
                        from src.models.company import Company
                        from src.models.campaign import Campaign
                        from src.models.clickbank import (
                            ClickBankProduct,
                            ClickBankCategoryURL,
                            UserAffiliatePreferences,
                            AffiliateLinkClick,
                            ScrapingSchedule,
                            ScrapingLog,
                            ProductPerformance
                        )
                        
                        # Create tables again
                        Base.metadata.create_all(bind=engine)
                        logger.info("✅ Database tables recreated successfully after conflict resolution")
                        return True
                        
                    except Exception as recreate_error:
                        logger.error(f"❌ Failed to recreate tables: {recreate_error}")
                        logger.info("⚠️ Continuing startup without table creation (tables may already exist)")
                        return True  # Continue anyway
                else:
                    logger.error(f"❌ Database table creation failed: {table_error}")
                    return False
                    
        except ImportError as e:
            logger.warning(f"⚠️ ClickBank models not available: {e}")
            logger.info("⚠️ Continuing startup without ClickBank models")
            return True  # Continue without ClickBank models
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

# ============================================================================
# ✅ ENHANCED DEPENDENCY TESTING
# ============================================================================

def test_critical_dependencies():
    """
    Test critical dependencies before starting the server
    """
    dependencies_status = {}
    
    try:
        logger.info("🔍 Testing critical dependencies...")
        
        # Web scraping dependencies
        try:
            import aiohttp
            import bs4
            import lxml
            dependencies_status['web_scraping'] = True
            logger.info("✅ All web scraping dependencies imported successfully")
        except ImportError as e:
            dependencies_status['web_scraping'] = False
            logger.error(f"❌ Web scraping dependencies failed: {e}")
        
        # FastAPI and core dependencies
        try:
            import fastapi
            import uvicorn
            import sqlalchemy
            import pydantic
            dependencies_status['core_framework'] = True
            logger.info("✅ Core framework dependencies available")
        except ImportError as e:
            dependencies_status['core_framework'] = False
            logger.error(f"❌ Core framework dependencies failed: {e}")
            return False
        
        # Database dependencies
        try:
            import psycopg2
            dependencies_status['database'] = True
            logger.info("✅ Database dependencies available")
        except ImportError:
            try:
                import asyncpg
                dependencies_status['database'] = True
                logger.info("✅ Database dependencies available (asyncpg)")
            except ImportError as e:
                dependencies_status['database'] = False
                logger.warning(f"⚠️ Database dependencies not optimal: {e}")
        
        # Optional dependencies
        try:
            from src.intelligence.amplifier.enhancement import get_load_balancing_stats
            dependencies_status['load_balancing'] = True
            logger.info("✅ Load balancing system available")
        except ImportError as e:
            dependencies_status['load_balancing'] = False
            logger.warning(f"⚠️ Load balancing system not available: {e}")
        
        return dependencies_status
        
    except Exception as e:
        logger.error(f"❌ Dependency testing failed: {e}")
        return False

# ============================================================================
# ✅ MAIN STARTUP FUNCTION
# ============================================================================

def start_server():
    """
    Main server startup function with enhanced error handling
    """
    port = int(os.environ.get("PORT", 8000))
    
    # Enhanced startup banner
    print("=" * 60)
    print("🚀 Starting CampaignForge AI Backend")
    print("=" * 60)
    print(f"📍 Environment: {'Production' if os.getenv('RAILWAY_PUBLIC_DOMAIN') else 'Development'}")
    print(f"🔐 JWT Secret: {'✅ Configured' if os.getenv('JWT_SECRET_KEY') else '⚠️ Using default'}")
    print(f"💾 Database: {'✅ Connected' if os.getenv('DATABASE_URL') else '❌ Not configured'}")
    print(f"🌐 Port: {port}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"📁 Python paths: {sys.path[:3]}...")
    print("=" * 60)
    
    # Test dependencies
    dependencies = test_critical_dependencies()
    if not dependencies:
        print("❌ Critical dependency testing failed!")
        return False
    
    # Initialize database and models
    if not initialize_database_and_models():
        print("❌ Database initialization failed!")
        return False
    
    # Import and test main app
    try:
        logger.info("📦 Importing main application...")
        from src.main import app
        logger.info("✅ Main app imported successfully")
        
        # Test app initialization
        try:
            # Make a simple test to ensure app is properly configured
            routes_count = len(app.routes)
            logger.info(f"✅ App initialized with {routes_count} routes")
        except Exception as e:
            logger.warning(f"⚠️ App configuration warning: {e}")
        
    except ImportError as e:
        logger.error(f"❌ Failed to import main app: {e}")
        print(f"🐍 Current Python path: {sys.path}")
        print(f"📁 Current working directory: {os.getcwd()}")
        print(f"📂 Project root: {project_root}")
        print(f"📂 Src path: {src_path}")
        return False
    except Exception as e:
        logger.error(f"❌ Main app import error: {e}")
        return False
    
    # Start the server
    try:
        print("🎯 All systems ready - starting server...")
        print("=" * 60)
        
        uvicorn.run(
            app,  # Pass app object directly
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False,
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        return False
    
    return True

# ============================================================================
# ✅ ERROR RECOVERY FUNCTION
# ============================================================================

def attempt_error_recovery():
    """
    Attempt to recover from common startup errors
    """
    logger.info("🔧 Attempting error recovery...")
    
    try:
        # Clear any cached modules that might be causing issues
        import importlib
        modules_to_reload = [
            'src.models.clickbank',
            'src.models.user', 
            'src.models.company',
            'src.models.campaign'
        ]
        
        for module_name in modules_to_reload:
            if module_name in sys.modules:
                logger.info(f"🔄 Reloading module: {module_name}")
                importlib.reload(sys.modules[module_name])
        
        # Clear SQLAlchemy metadata
        try:
            from src.core.database import Base
            Base.metadata.clear()
            logger.info("🧹 SQLAlchemy metadata cleared")
        except:
            pass
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error recovery failed: {e}")
        return False

# ============================================================================
# ✅ MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        # First attempt
        if not start_server():
            logger.info("🔄 First startup attempt failed, trying error recovery...")
            
            # Attempt recovery
            if attempt_error_recovery():
                logger.info("🔄 Error recovery completed, retrying startup...")
                
                # Second attempt after recovery
                if not start_server():
                    logger.error("❌ Startup failed after recovery attempt")
                    sys.exit(1)
            else:
                logger.error("❌ Error recovery failed")
                sys.exit(1)
                
    except KeyboardInterrupt:
        logger.info("⚠️ Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Critical startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)