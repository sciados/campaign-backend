from fastapi import FastAPI

app = FastAPI(
    title="CampaignForge AI",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/")
def root():
    return {"message": "CampaignForge AI", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}