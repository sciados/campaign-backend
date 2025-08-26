# src/routes/user_type_routes.py
"""
User Type Management API Routes for CampaignForge Multi-User System
🎭 Handles user type selection, configuration, and management
🔧 RESTful API endpoints for user type operations
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from ..core.database import get_db
from ..auth.dependencies import get_current_user
from ..models.user import User, UserType, UserTier, OnboardingStatus
from ..services.user_type_service import UserTypeService

router = APIRouter(tags=["User Types"])

# 📝 Pydantic Models for Request/Response

class UserTypeSelectionRequest(BaseModel):
    user_type: UserType = Field(..., description="Selected user type")
    goals: List[str] = Field(default=[], description="User's stated goals")
    experience_level: str = Field(default="beginner", description="User's experience level")
    current_activities: List[str] = Field(default=[], description="User's current activities")
    interests: List[str] = Field(default=[], description="User's interests")
    description: Optional[str] = Field(None, description="Additional description")

class OnboardingCompleteRequest(BaseModel):
    goals: List[str] = Field(..., description="User's goals")
    experience_level: str = Field(..., description="User's experience level")

class UserTypeDetectionRequest(BaseModel):
    description: str = Field(..., description="Description of user's activities/goals")
    goals: List[str] = Field(default=[], description="User's stated goals")
    current_activities: List[str] = Field(default=[], description="Current activities")
    interests: List[str] = Field(default=[], description="Areas of interest")

class UserTypeMigrationRequest(BaseModel):
    new_user_type: UserType = Field(..., description="New user type to migrate to")
    reason: Optional[str] = Field(None, description="Reason for migration")

class UserSearchRequest(BaseModel):
    user_type: Optional[UserType] = None
    user_tier: Optional[UserTier] = None
    onboarding_status: Optional[OnboardingStatus] = None
    experience_level: Optional[str] = None
    is_active: Optional[bool] = None
    limit: int = Field(default=50, le=500)

# 🎭 User Type Selection & Configuration Endpoints

@router.post("/detect")
async def detect_user_type(
    request: UserTypeDetectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🧠 Intelligent user type detection based on user input
    Analyzes user's description, goals, and activities to suggest best user type
    """
    try:
        service = UserTypeService(db)
        
        user_data = {
            "description": request.description,
            "goals": " ".join(request.goals),
            "current_activities": request.current_activities,
            "interests": " ".join(request.interests)
        }
        
        detected_type = service.detect_user_type_from_data(user_data)
        type_info = service.get_user_type_display_info(detected_type)
        
        return {
            "success": True,
            "detected_type": detected_type.value,
            "type_info": type_info,
            "confidence": "high",  # Could implement confidence scoring
            "all_types": service.get_all_user_types_info(),
            "message": f"Based on your input, we recommend: {type_info.get('title', 'Unknown')}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User type detection failed: {str(e)}")

@router.post("/select")
async def select_user_type(
    request: UserTypeSelectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🎯 Set user type and initialize type-specific configuration
    """
    try:
        service = UserTypeService(db)
        
        # Prepare type-specific data
        type_data = {
            "goals": request.goals,
            "experience_level": request.experience_level,
            "current_activities": request.current_activities,
            "interests": request.interests,
            "description": request.description,
            "selection_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Set user type
        updated_user = service.set_user_type(
            str(current_user.id), 
            request.user_type, 
            type_data
        )
        
        # Get dashboard configuration
        dashboard_config = service.get_dashboard_config(str(current_user.id))
        
        return {
            "success": True,
            "user_profile": updated_user.get_user_profile(),
            "dashboard_config": dashboard_config,
            "message": f"User type set to {updated_user.get_user_type_display()}",
            "next_step": "complete_onboarding"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User type selection failed: {str(e)}")

@router.post("/complete-onboarding")
async def complete_onboarding(
    request: OnboardingCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Complete user onboarding process
    """
    try:
        service = UserTypeService(db)
        
        updated_user = service.complete_user_onboarding(
            str(current_user.id),
            request.goals,
            request.experience_level
        )
        
        # Get recommendations for new user
        recommendations = service.get_user_recommendations(str(current_user.id))
        welcome_message = service.get_personalized_welcome_message(str(current_user.id))
        
        return {
            "success": True,
            "user_profile": updated_user.get_user_profile(),
            "welcome_message": welcome_message,
            "recommendations": recommendations,
            "dashboard_route": updated_user.get_dashboard_route(),
            "message": "Onboarding completed successfully!"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Onboarding completion failed: {str(e)}")

# 📊 User Information & Configuration Endpoints

@router.get("/current")
async def get_current_user_type(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📋 Get current user's type information and configuration
    """
    try:
        service = UserTypeService(db)
        
        user_profile = current_user.get_user_profile()
        dashboard_config = service.get_dashboard_config(str(current_user.id))
        
        return {
            "success": True,
            "user_profile": user_profile,
            "dashboard_config": dashboard_config,
            "onboarding_complete": current_user.onboarding_status == OnboardingStatus.COMPLETED
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user type info: {str(e)}")

@router.get("/dashboard-config")
async def get_dashboard_config(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🎨 Get user-specific dashboard configuration
    """
    try:
        service = UserTypeService(db)
        config = service.get_dashboard_config(str(current_user.id))
        
        return {
            "success": True,
            "config": config
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard config: {str(e)}")

@router.get("/recommendations")
async def get_user_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🎯 Get personalized recommendations for the user
    """
    try:
        service = UserTypeService(db)
        recommendations = service.get_user_recommendations(str(current_user.id))
        
        return {
            "success": True,
            "recommendations": recommendations,
            "user_type": current_user.user_type.value if current_user.user_type else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")

@router.get("/usage-summary")
async def get_usage_summary(
    current_user: User = Depends(get_current_user)
):
    """
    📈 Get current user's usage summary
    """
    try:
        usage_summary = current_user.get_usage_summary()
        
        return {
            "success": True,
            "usage": usage_summary,
            "user_type": current_user.user_type.value if current_user.user_type else None,
            "tier": current_user.user_tier.value if current_user.user_tier else "free"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get usage summary: {str(e)}")

@router.get("/upgrade-check")
async def check_upgrade_eligibility(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🚀 Check if user can/should upgrade their tier
    """
    try:
        service = UserTypeService(db)
        upgrade_info = service.can_user_upgrade_tier(str(current_user.id))
        
        return {
            "success": True,
            "upgrade_info": upgrade_info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check upgrade eligibility: {str(e)}")

# 📊 Analytics & Admin Endpoints

@router.get("/stats")
async def get_user_type_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📊 Get user type statistics (admin only)
    """
    # Add admin permission check here if needed
    try:
        service = UserTypeService(db)
        stats = service.get_user_type_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user type stats: {str(e)}")

@router.post("/search")
async def search_users_by_type(
    request: UserSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔍 Search users by type and other filters (admin only)
    """
    # Add admin permission check here if needed
    try:
        service = UserTypeService(db)
        filters = request.dict(exclude_unset=True)
        users = service.search_users(filters)
        
        return {
            "success": True,
            "users": [
                {
                    "id": str(user.id),
                    "email": user.email,
                    "full_name": user.full_name,
                    "user_type": user.user_type.value if user.user_type else None,
                    "user_tier": user.user_tier.value if user.user_tier else "free",
                    "onboarding_status": user.onboarding_status.value if user.onboarding_status else "incomplete",
                    "total_campaigns": user.total_campaigns_created,
                    "last_active": user.last_active_at.isoformat() if user.last_active_at else None
                }
                for user in users
            ],
            "total": len(users)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User search failed: {str(e)}")

@router.get("/activity/{user_id}")
async def get_user_activity_summary(
    user_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    📈 Get user activity summary for specified user (admin only)
    """
    # Add admin permission check here if needed
    try:
        service = UserTypeService(db)
        activity = service.get_user_activity_summary(user_id, days)
        
        return {
            "success": True,
            "activity": activity
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user activity: {str(e)}")

# 🔄 User Type Migration

@router.post("/migrate")
async def migrate_user_type(
    request: UserTypeMigrationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    🔄 Migrate user to a different user type
    """
    try:
        service = UserTypeService(db)
        
        updated_user = service.migrate_user_type(
            str(current_user.id),
            request.new_user_type,
            request.reason
        )
        
        # Get new dashboard configuration
        dashboard_config = service.get_dashboard_config(str(current_user.id))
        recommendations = service.get_user_recommendations(str(current_user.id))
        
        return {
            "success": True,
            "user_profile": updated_user.get_user_profile(),
            "dashboard_config": dashboard_config,
            "recommendations": recommendations,
            "message": f"Successfully migrated to {updated_user.get_user_type_display()}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"User type migration failed: {str(e)}")

# 📋 Utility Endpoints

@router.get("/types")
async def get_all_user_types():
    """
    📋 Get information about all available user types
    """
    try:
        service = UserTypeService()
        types_info = service.get_all_user_types_info()
        
        return {
            "success": True,
            "user_types": types_info
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user types: {str(e)}")

@router.get("/welcome-message")
async def get_welcome_message(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    👋 Get personalized welcome message for current user
    """
    try:
        service = UserTypeService(db)
        message = service.get_personalized_welcome_message(str(current_user.id))
        
        return {
            "success": True,
            "welcome_message": message,
            "user_type": current_user.user_type.value if current_user.user_type else None
        }
    
    except Exception as e:
        return {
            "success": True,
            "welcome_message": "Welcome to CampaignForge!",
            "user_type": None
        }