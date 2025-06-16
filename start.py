import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting CampaignForge AI Backend on port {port}")
    print(f"📍 Environment: {'Production' if os.getenv('RAILWAY_PUBLIC_DOMAIN') else 'Development'}")
    print(f"🔐 JWT Secret configured: {'Yes' if os.getenv('JWT_SECRET_KEY') else 'No (using default)'}")
    print(f"💾 Database: {'Connected' if os.getenv('DATABASE_URL') else 'Not configured'}")
    
    try:
        uvicorn.run(
            "main:app",  # Updated to reference main.py directly
            host="0.0.0.0",
            port=port,
            log_level="info",
            reload=False  # Disable reload in production
        )
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        raise