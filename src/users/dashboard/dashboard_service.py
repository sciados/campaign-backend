# src/users/dashboard/dashboard_service.py
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from ..models.user import User
from ..services.user_service import UserService

class DashboardService:
    def __init__(self, db: Session):
        self.db = db
        self.user_service = UserService(db)
    
    async def get_admin_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive admin dashboard data"""
        user_stats = await self.user_service.get_user_stats()
        recent_users = await self.user_service.get_dashboard_users(limit=10)
        
        return {
            "stats": user_stats,
            "recent_users": [user.to_dict() for user in recent_users],
            "charts": {
                "user_growth": await self._get_user_growth_data(),
                "user_activity": await self._get_user_activity_data()
            }
        }
    
    async def get_user_dashboard_data(self, user_id: int) -> Dict[str, Any]:
        """Get user-specific dashboard data"""
        preferences = await self.user_service.get_dashboard_preferences(user_id)
        
        return {
            "preferences": preferences,
            "quick_stats": {
                "campaigns_created": 0,  # Connect to campaigns module later
                "intelligence_generated": 0,  # Connect to intelligence module later
                "last_activity": "Recently active"
            },
            "recent_activity": []  # Connect to activity tracking later
        }
    
    async def _get_user_growth_data(self) -> List[Dict[str, Any]]:
        """Get user growth chart data"""
        # Implement user growth tracking
        return []
    
    async def _get_user_activity_data(self) -> List[Dict[str, Any]]:
        """Get user activity chart data"""
        # Implement user activity tracking
        return []