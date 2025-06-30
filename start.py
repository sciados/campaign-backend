import os
import sys
import uvicorn
from pathlib import Path

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting CampaignForge AI Backend on port {port}")
    print(f"📍 Environment: {'Production' if os.getenv('RAILWAY_PUBLIC_DOMAIN') else 'Development'}")
    print(f"🔐 JWT Secret configured: {'Yes' if os.getenv('JWT_SECRET_KEY') else 'No (using default)'}")
    print(f"💾 Database: {'Connected' if os.getenv('DATABASE_URL') else 'Not configured'}")
    print(f"🐍 Python paths: {sys.path[:3]}...")  # Debug info
    
    try:
        # Test critical imports before starting
        print("🔍 Testing critical imports...")
        import aiohttp
        import bs4
        import lxml
        print("✅ All web scraping dependencies imported successfully")
        
        # Import main app
        from src.main import app
        print("✅ Main app imported successfully")
        
        uvicorn.run(
            app,  # Pass app object directly instead of string
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False
        )
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print(f"🐍 Current Python path: {sys.path}")
        print(f"📁 Current working directory: {os.getcwd()}")
        print(f"📂 Project root: {project_root}")
        print(f"📂 Src path: {src_path}")
        raise
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        raise