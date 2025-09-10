# ============================================================================
# API ROUTE UPDATES FOR SERVICE INTEGRATION
# ============================================================================

# src/users/api/routes.py (Enhanced for Session 5)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any

from src.core.factories.service_factory import ServiceFactory
from src.users.services.auth_service import AuthService
from src.users.services.user_service import UserService

router = APIRouter()
security = HTTPBearer()

@router.post("/api/auth/register")
async def register_user(request: Dict[str, Any]):
    """Enhanced user registration with proper service management"""
    try:
        email = request.get("email")
        password = request.get("password")
        full_name = request.get("full_name")
        company_name = request.get("company_name", "Default Company")
        user_type = request.get("user_type")  # Get user_type from request
        
        if not all([email, password, full_name]):
            raise HTTPException(
                status_code=400,
                detail="email, password, and full_name are required"
            )
        
        # Map frontend user types to backend enums if user_type is provided
        backend_user_type = None
        if user_type:
            user_type_mapping = {
                "affiliate_marketer": "AFFILIATE_MARKETER",
                "affiliate": "AFFILIATE_MARKETER",
                "content_creator": "CONTENT_CREATOR", 
                "creator": "CONTENT_CREATOR",
                "business_owner": "BUSINESS_OWNER",
                "business": "BUSINESS_OWNER",
            }
            backend_user_type = user_type_mapping.get(user_type, user_type.upper())
        
        async with ServiceFactory.create_transactional_service(AuthService) as auth_service:
            result = await auth_service.register(
                email=email,
                password=password,
                full_name=full_name,
                company_name=company_name,
                user_type=backend_user_type  # Pass user_type to register method
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/auth/login")
async def login_user(request: Dict[str, Any]):
    """Enhanced user login with proper service management"""
    try:
        email = request.get("email")
        password = request.get("password")
        
        if not all([email, password]):
            raise HTTPException(
                status_code=400,
                detail="email and password are required"
            )
        
        async with ServiceFactory.create_service(AuthService) as auth_service:
            result = await auth_service.login(email=email, password=password)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/api/auth/profile")
async def get_user_profile(token: str = Depends(security)):
    """Get user profile with enhanced service management"""
    try:
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            # Map backend user_type to frontend format
            # Since user_type is stored as a string (not enum), we can directly map it
            frontend_user_type = None
            if user.user_type:
                try:
                    # Map to frontend format
                    backend_to_frontend_mapping = {
                        "AFFILIATE_MARKETER": "affiliate_marketer",
                        "CONTENT_CREATOR": "content_creator", 
                        "BUSINESS_OWNER": "business_owner",
                    }
                    
                    frontend_user_type = backend_to_frontend_mapping.get(user.user_type, user.user_type.lower())
                except Exception as e:
                    # Fallback to original value if mapping fails
                    frontend_user_type = user.user_type.lower() if user.user_type else None
                    print(f"Warning: User type mapping failed: {e}")
                    

            return {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role if user.role else "user",  # role is stored as string, not enum
                "user_type": frontend_user_type,
                "is_active": user.is_active,
                "company": {
                    "id": str(user.company.id),
                    "name": user.company.company_name,
                    "subscription_tier": user.company.subscription_tier  # subscription_tier is stored as string, not enum
                } if user.company else None
            }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/user-types/select")
async def select_user_type(request: Dict[str, Any], token: str = Depends(security)):
    """Set user type during onboarding"""
    try:
        from datetime import datetime
        
        user_type = request.get("user_type")
        goals = request.get("goals", [])
        experience_level = request.get("experience_level", "beginner")
        
        if not user_type:
            raise HTTPException(
                status_code=400,
                detail="user_type is required"
            )
        
        # Map frontend user types to backend enums
        user_type_mapping = {
            "affiliate_marketer": "AFFILIATE_MARKETER",
            "affiliate": "AFFILIATE_MARKETER", 
            "content_creator": "CONTENT_CREATOR",
            "creator": "CONTENT_CREATOR",
            "business_owner": "BUSINESS_OWNER", 
            "business": "BUSINESS_OWNER",
        }
        
        # Convert to backend format
        backend_user_type = user_type_mapping.get(user_type, user_type.upper())
        
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            # Use UserService to update user type
            async with ServiceFactory.create_service(UserService) as user_service:
                type_data = {
                    "goals": goals,
                    "experience_level": experience_level,
                    "selected_at": datetime.utcnow().isoformat()
                }
                
                updated_user = await user_service.update_user_type(
                    user.id, 
                    backend_user_type, 
                    type_data
                )
                
                if not updated_user:
                    raise HTTPException(
                        status_code=500,
                        detail="Failed to update user type"
                    )
                
                return {
                    "success": True,
                    "message": "User type selected successfully",
                    "user_profile": {
                        "id": str(updated_user.id),
                        "email": updated_user.email,
                        "full_name": updated_user.full_name,
                        "role": updated_user.role,
                        "user_type": user_type,  # Return original format for frontend
                        "is_active": updated_user.is_active,
                        "onboarding_completed": updated_user.onboarding_completed
                    }
                }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/user-types/complete-onboarding") 
async def complete_user_onboarding(request: Dict[str, Any], token: str = Depends(security)):
    """Complete user onboarding process"""
    try:
        from datetime import datetime
        
        user_type = request.get("user_type")
        goals = request.get("goals", [])
        experience_level = request.get("experience_level", "beginner")
        
        if not user_type:
            raise HTTPException(
                status_code=400,
                detail="user_type is required"
            )
        
        # Map frontend user types to backend enums  
        user_type_mapping = {
            "affiliate_marketer": "AFFILIATE_MARKETER",
            "affiliate": "AFFILIATE_MARKETER",
            "content_creator": "CONTENT_CREATOR", 
            "creator": "CONTENT_CREATOR",
            "business_owner": "BUSINESS_OWNER",
            "business": "BUSINESS_OWNER",
        }
        
        backend_user_type = user_type_mapping.get(user_type, user_type.upper())
        
        async with ServiceFactory.create_service(AuthService) as auth_service:
            user = await auth_service.get_current_user(token.credentials)
            
            if not user:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid or expired token"
                )
            
            async with ServiceFactory.create_service(UserService) as user_service:
                # Update user type
                type_data = {
                    "goals": goals,
                    "experience_level": experience_level,
                    "onboarding_completed_at": datetime.utcnow().isoformat()
                }
                
                updated_user = await user_service.update_user_type(
                    user.id,
                    backend_user_type, 
                    type_data
                )
                
                # Complete onboarding
                if updated_user:
                    updated_user.complete_onboarding(goals, experience_level)
                    await user_service.db.commit()
                    await user_service.db.refresh(updated_user)
                
                return {
                    "success": True,
                    "message": "Onboarding completed successfully",
                    "user_profile": {
                        "id": str(updated_user.id),
                        "email": updated_user.email,
                        "full_name": updated_user.full_name,
                        "role": updated_user.role,
                        "user_type": user_type,
                        "is_active": updated_user.is_active,
                        "onboarding_completed": updated_user.onboarding_completed
                    }
                }
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))