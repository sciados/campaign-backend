# clickbank_module/routes_clickbank.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src.platforms.clickbank.services import clickbank_service

router = APIRouter(prefix="/clickbank", tags=["ClickBank"])

class ConnectRequest(BaseModel):
    user_id: int
    nickname: str
    clerk_key: str

@router.post("/connect")
def connect_clickbank(body: ConnectRequest):
    try:
        return clickbank_service.save_credentials(
            user_id=body.user_id,
            nickname=body.nickname,
            clerk_key=body.clerk_key
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sales")
def get_sales(user_id: int, days: int = 30):
    try:
        return clickbank_service.fetch_sales(user_id, days)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
