import os
import uvicorn

if __name__ == "__main__":
    # Get port from Railway environment (Railway sets this automatically)
    port = int(os.environ.get("PORT", 8000))
    
    # Get other environment settings
    debug = os.environ.get("DEBUG", "False").lower() == "true"
    
    print(f"🚀 Starting CampaignForge AI Backend on port {port}")
    print(f"📊 Debug mode: {debug}")
    print(f"🌐 Environment: {os.environ.get('ENVIRONMENT', 'production')}")
    
    # Start the FastAPI application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=debug,  # Only reload in debug mode
        log_level="info"
    )