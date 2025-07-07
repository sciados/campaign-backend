import os
import sys
import uvicorn
import logging
from pathlib import Path

# ============================================================================
# ✅ PATH SETUP
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
# ✅ LOGGING SETUP
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# ✅ SIMPLIFIED: Just test imports and start server
# ============================================================================

def test_critical_dependencies():
    """Test critical dependencies"""
    try:
        logger.info("🔍 Testing critical dependencies...")
        
        # Web scraping dependencies
        import aiohttp
        import bs4
        import lxml
        logger.info("✅ All web scraping dependencies imported successfully")
        
        # Core framework
        import fastapi
        import uvicorn
        import sqlalchemy
        import pydantic
        logger.info("✅ Core framework dependencies available")
        
        # Optional load balancing check
        try:
            from src.intelligence.amplifier.enhancement import get_load_balancing_stats
            logger.info("✅ Load balancing system available")
        except ImportError as e:
            logger.warning(f"⚠️ Load balancing system not available: {e}")
        
        return True
        
    except ImportError as e:
        logger.error(f"❌ Critical dependency missing: {e}")
        return False

def start_server():
    """Main server startup function"""
    port = int(os.environ.get("PORT", 8000))
    
    # Startup banner
    print("=" * 60)
    print("🚀 Starting CampaignForge AI Backend")
    print("=" * 60)
    print(f"📍 Environment: {'Production' if os.getenv('RAILWAY_PUBLIC_DOMAIN') else 'Development'}")
    print(f"🔐 JWT Secret: {'✅ Configured' if os.getenv('JWT_SECRET_KEY') else '⚠️ Using default'}")
    print(f"💾 Database: {'✅ Connected' if os.getenv('DATABASE_URL') else '❌ Not configured'}")
    print(f"🌐 Port: {port}")
    print(f"🐍 Python version: {sys.version.split()[0]}")
    print("=" * 60)
    
    # Test dependencies
    if not test_critical_dependencies():
        logger.error("❌ Critical dependency testing failed!")
        return False
    
    # Import main app (this will handle all the model imports through main.py)
    try:
        logger.info("📦 Importing main application...")
        from src.main import app
        logger.info("✅ Main app imported successfully")
        
        # Test app initialization
        routes_count = len(app.routes)
        logger.info(f"✅ App initialized with {routes_count} routes")
        
    except Exception as e:
        logger.error(f"❌ Failed to import main app: {e}")
        print(f"🐍 Current Python path: {sys.path[:3]}")
        print(f"📁 Current working directory: {os.getcwd()}")
        return False
    
    # Start the server
    try:
        print("🎯 All systems ready - starting server...")
        print("=" * 60)
        
        uvicorn.run(
            app,
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
# ✅ MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        logger.info("⚠️ Startup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Critical startup error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)