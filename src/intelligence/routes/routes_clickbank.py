# clickbank_module/routes_clickbank.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from src.intelligence.services import clickbank_service
from src.core.database.connection import get_async_db
from src.users.services.auth_service import AuthService

router = APIRouter(prefix="/clickbank", tags=["ClickBank"])
security = HTTPBearer()

async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
) -> str:
    """Get current user ID from token"""
    auth_service = AuthService(db)
    user = await auth_service.get_current_user(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return str(user.id)

class ConnectRequest(BaseModel):
    nickname: str
    api_key: str

@router.post("/connect")
async def connect_clickbank(
    body: ConnectRequest,
    user_id: str = Depends(get_current_user_id)
):
    print(f"DEBUG: ClickBank connect endpoint called by user_id={user_id}")
    print(f"DEBUG: Request body - nickname={body.nickname}, api_key=***")

    try:
        # Call the async database function directly instead of sync wrapper
        from src.core.database.clickbank_repo import save_clickbank_creds

        await save_clickbank_creds(
            user_id=user_id,
            nickname=body.nickname,
            api_key=body.api_key
        )

        result = {"status": "success", "message": "ClickBank account connected."}
        print(f"DEBUG: ClickBank save_credentials returned: {result}")
        return result
    except Exception as e:
        print(f"ERROR: ClickBank connect failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sales")
async def get_sales(
    days: int = 30,
    user_id: str = Depends(get_current_user_id)
):
    try:
        return clickbank_service.fetch_sales(int(user_id), days)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
