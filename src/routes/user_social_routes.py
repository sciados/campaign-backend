# src/routes/user_social_routes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.security import get_current_user
from ..models.user import User
from ..models.user_social_profile import UserSocialProfile
from ..services.platform_config_service import PlatformConfigService

router = APIRouter(prefix="/api/user-social", tags=["user-social"])

@router.get("/recommended-platforms")
async def get_recommended_platforms(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommended platforms for user's type"""
    if not current_user.user_type:
        raise HTTPException(status_code=400, detail="User type not set")
    
    platforms = PlatformConfigService.get_recommended_platforms(current_user.user_type)
    return {"recommended_platforms": platforms}

@router.post("/profiles")
async def add_social_profile(
    platform: str,
    username: str,
    followers: int = 0,
    engagement_rate: float = 0.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add or update a social media profile"""
    
    # Check if profile already exists
    existing = db.query(UserSocialProfile).filter(
        UserSocialProfile.user_id == current_user.id,
        UserSocialProfile.platform == platform
    ).first()
    
    if existing:
        existing.username = username
        existing.followers = followers
        existing.engagement_rate = engagement_rate
        existing.manual_input = True
        profile = existing
    else:
        profile = UserSocialProfile(
            user_id=current_user.id,
            platform=platform,
            username=username,
            followers=followers,
            engagement_rate=engagement_rate,
            manual_input=True
        )
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    
    return {"message": "Profile updated successfully", "profile_id": str(profile.id)}

@router.get("/profiles")
async def get_user_social_profiles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all social profiles for current user"""
    profiles = db.query(UserSocialProfile).filter(
        UserSocialProfile.user_id == current_user.id
    ).all()
    
    return {
        "profiles": [
            {
                "id": str(p.id),
                "platform": p.platform,
                "username": p.username,
                "followers": p.followers,
                "engagement_rate": p.engagement_rate,
                "is_primary": p.is_primary_platform,
                "manual_input": p.manual_input,
                "last_updated": p.updated_at
            }
            for p in profiles
        ]
    }