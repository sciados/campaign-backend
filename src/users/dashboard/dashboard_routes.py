# src/users/dashboard/dashboard_routes.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from .dashboard_service import DashboardService
from ..services.auth_service import AuthService
from src.core.database.connection import get_db

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
security = HTTPBearer()

@router.get("/admin", response_model=Dict[str, Any])
async def get_admin_dashboard(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get admin dashboard data"""
    # Verify admin permissions
    auth_service = AuthService(db)
    current_user = await auth_service.get_current_user(credentials.credentials)
    
    if not current_user or not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_admin_dashboard_data()

@router.get("/user", response_model=Dict[str, Any])
async def get_user_dashboard(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user dashboard data"""
    auth_service = AuthService(db)
    current_user = await auth_service.get_current_user(credentials.credentials)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    dashboard_service = DashboardService(db)
    return await dashboard_service.get_user_dashboard_data(current_user.id)