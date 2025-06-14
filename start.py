import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"🚀 Starting CampaignForge AI Backend on port {port}")
    
    try:
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        raise