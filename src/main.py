from fastapi import FastAPI

app = FastAPI(
    title="CampaignForge AI",
    description="Multimedia Campaign Creation Platform API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
async def root():
    return {
        "message": "CampaignForge AI Backend",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}