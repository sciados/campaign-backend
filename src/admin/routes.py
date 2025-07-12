"""
Admin routes for user and company management
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime, timedelta

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.admin.schemas import (
    UserListResponse, CompanyListResponse, AdminStatsResponse,
    UserUpdateRequest, CompanyUpdateRequest, UserCreateRequest,
    SubscriptionUpdateRequest, AdminUserResponse, AdminCompanyResponse
)
from src.models.base import EnumSerializerMixin
from src.models.user import User
from src.models.company import Company, CompanyMembership, CompanySubscriptionTier
from src.models.campaign import Campaign

# ✅ FIXED: Remove duplicate prefix (main.py already adds /api/admin)
router = APIRouter(tags=["admin"])

async def require_admin(current_user: User = Depends(get_current_user)):
    """Require admin role for admin endpoints"""
    # Only users with 'admin' role can access admin dashboard
    # This ensures only main admins (like you) have full platform access
    if current_user.role != "admin":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Admin access required. Only platform administrators can access this area."
        )
    return current_user

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics"""
    
    # Get current date ranges
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    seven_days_ago = now - timedelta(days=7)
    
    # Total counts
    # total_users = await db.scalar(select(func.count(User.id)))
    result = db.execute(select(func.count(User.id)))
    total_users = result.scalar()
    total_companies = await db.scalar(select(func.count(Company.id)))
    total_campaigns_created = await db.scalar(select(func.count(Campaign.id)))
    
    # Active users (logged in last 30 days)
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    )
    
    # New users this month
    new_users_month = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
    )
    
    # New users this week
    new_users_week = await db.scalar(
        select(func.count(User.id)).where(User.created_at >= seven_days_ago)
    )
    
    # Subscription tier breakdown
    tier_stats = await db.execute(
        select(Company.subscription_tier, func.count(Company.id))
        .group_by(Company.subscription_tier)
    )
    subscription_breakdown = dict(tier_stats.all())
    
    # Monthly recurring revenue estimate
    tier_pricing = {
        "free": 0,
        "starter": 29,
        "professional": 79,
        "agency": 199,
        "enterprise": 499
    }
    
    mrr = sum(tier_pricing.get(tier, 0) * count for tier, count in subscription_breakdown.items())
    
    return AdminStatsResponse(
        total_users=total_users or 0,
        total_companies=total_companies or 0,
        total_campaigns_created=total_campaigns_created or 0,
        active_users=active_users or 0,
        new_users_month=new_users_month or 0,
        new_users_week=new_users_week or 0,
        subscription_breakdown=subscription_breakdown,
        monthly_recurring_revenue=mrr
    )

@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    subscription_tier: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None)
):
    """Get paginated list of all users with filtering"""
    
    # Build query
    query = select(User).options(selectinload(User.company))
    
    # Apply filters
    conditions = []
    if search:
        conditions.append(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                Company.company_name.ilike(f"%{search}%")
            )
        )
    
    if subscription_tier:
        conditions.append(Company.subscription_tier == subscription_tier)
    
    if is_active is not None:
        conditions.append(User.is_active == is_active)
    
    if conditions:
        query = query.join(Company).where(and_(*conditions))
    else:
        query = query.join(Company)
    
    # Get total count
    total_query = select(func.count(User.id))
    if conditions:
        total_query = total_query.join(Company).where(and_(*conditions))
    else:
        total_query = total_query.join(Company)
    
    total = await db.scalar(total_query) or 0
    
    # Apply pagination
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    users = result.scalars().all()
    
    # Convert to response format
    user_list = []
    for user in users:
        user_list.append(AdminUserResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at,
            company_id=user.company_id,
            company_name=user.company.company_name,
            subscription_tier=user.company.subscription_tier,
            monthly_credits_used=user.company.monthly_credits_used,
            monthly_credits_limit=user.company.monthly_credits_limit
        ))
    
    return UserListResponse(
        users=user_list,
        total=total,
        page=page,
        limit=limit,
        pages=((total - 1) // limit + 1) if total > 0 else 0
    )

@router.get("/companies", response_model=CompanyListResponse)
async def get_all_companies(
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    subscription_tier: Optional[str] = Query(None)
):
    """Get paginated list of all companies"""
    
    try:
        # Build query - start simple without complex relationships
        query = select(Company)
        
        # Apply filters
        conditions = []
        if search:
            conditions.append(
                or_(
                    Company.company_name.ilike(f"%{search}%"),
                    Company.industry.ilike(f"%{search}%")
                )
            )
        
        if subscription_tier:
            conditions.append(Company.subscription_tier == subscription_tier)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Get total count
        total_query = select(func.count(Company.id))
        if conditions:
            total_query = total_query.where(and_(*conditions))
        
        total = await db.scalar(total_query) or 0
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit).order_by(Company.created_at.desc())
        
        result = await db.execute(query)
        companies = result.scalars().all()
        
        # Convert to response format
        company_list = []
        for company in companies:
            # Get user count for this company
            user_count_query = select(func.count(User.id)).where(User.company_id == company.id)
            user_count = await db.scalar(user_count_query) or 0
            
            # Get campaign count for this company
            campaign_count_query = select(func.count(Campaign.id)).where(Campaign.company_id == company.id)
            campaign_count = await db.scalar(campaign_count_query) or 0
            
            company_list.append(AdminCompanyResponse(
                id=company.id,
                company_name=company.company_name,
                company_slug=company.company_slug,
                industry=company.industry or "",
                company_size=company.company_size,
                subscription_tier=company.subscription_tier,
                subscription_status=company.subscription_status,
                monthly_credits_used=company.monthly_credits_used,
                monthly_credits_limit=company.monthly_credits_limit,
                total_campaigns_created=company.total_campaigns_created,  # Use the model field directly
                created_at=company.created_at,
                user_count=user_count,
                campaign_count=campaign_count
            ))
        
        return CompanyListResponse(
            companies=company_list,
            total=total,
            page=page,
            limit=limit,
            pages=((total - 1) // limit + 1) if total > 0 else 0
        )
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_all_companies: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch companies: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=AdminUserResponse)
async def get_user_details(
    user_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed user information"""
    
    result = await db.execute(
        select(User).options(selectinload(User.company))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return AdminUserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
        company_id=user.company_id,
        company_name=user.company.company_name,
        subscription_tier=user.company.subscription_tier,
        monthly_credits_used=user.company.monthly_credits_used,
        monthly_credits_limit=user.company.monthly_credits_limit
    )

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    user_update: UserUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user details"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user fields
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.role is not None:
        user.role = user_update.role
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.is_verified is not None:
        user.is_verified = user_update.is_verified
    
    await db.commit()
    
    return {"message": "User updated successfully"}

@router.put("/companies/{company_id}/subscription")
async def update_company_subscription(
    company_id: str,
    subscription_update: SubscriptionUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update company subscription tier and limits"""
    
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update subscription fields
    if subscription_update.subscription_tier is not None:
        company.subscription_tier = subscription_update.subscription_tier
    if subscription_update.monthly_credits_limit is not None:
        company.monthly_credits_limit = subscription_update.monthly_credits_limit
    if subscription_update.subscription_status is not None:
        # Only update if the field exists on the model
        if hasattr(company, 'subscription_status'):
            company.subscription_status = subscription_update.subscription_status
    
    # Reset monthly credits if requested
    if subscription_update.reset_monthly_credits:
        company.monthly_credits_used = 0
    
    await db.commit()
    
    return {"message": "Company subscription updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete user account"""
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow deleting the last owner of a company
    if user.role == "owner":
        owner_count = await db.scalar(
            select(func.count(User.id))
            .where(and_(User.company_id == user.company_id, User.role == "owner"))
        )
        if owner_count <= 1:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last owner of a company"
            )
    
    await db.delete(user)
    await db.commit()
    
    return {"message": "User deleted successfully"}

@router.post("/users/{user_id}/impersonate")
async def impersonate_user(
    user_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Generate impersonation token for user (admin feature)"""
    
    result = await db.execute(
        select(User).options(selectinload(User.company))
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Create impersonation token
    from src.core.security import create_access_token
    
    impersonation_token = create_access_token(data={
        "sub": str(user.id),
        "company_id": str(user.company_id),
        "role": user.role,
        "impersonated_by": str(admin_user.id)
    })
    
    return {
        "message": f"Impersonation token created for {user.email}",
        "access_token": impersonation_token,
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company.company_name
        }
    }

@router.get("/companies/{company_id}", response_model=AdminCompanyResponse)
async def get_company_details(
    company_id: str,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed company information"""
    
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Get user count for this company
    user_count_query = select(func.count(User.id)).where(User.company_id == company.id)
    user_count = await db.scalar(user_count_query) or 0
    
    # Get campaign count for this company
    campaign_count_query = select(func.count(Campaign.id)).where(Campaign.company_id == company.id)
    campaign_count = await db.scalar(campaign_count_query) or 0
    
    return AdminCompanyResponse(
        id=company.id,
        company_name=company.company_name,
        company_slug=company.company_slug,
        industry=company.industry or "",
        company_size=company.company_size,
        subscription_tier=company.subscription_tier,
        subscription_status=company.subscription_status,
        monthly_credits_used=company.monthly_credits_used,
        monthly_credits_limit=company.monthly_credits_limit,
        total_campaigns_created=company.total_campaigns_created,
        created_at=company.created_at,
        user_count=user_count,
        campaign_count=campaign_count
    )

@router.put("/companies/{company_id}")
async def update_company_details(
    company_id: str,
    company_update: CompanyUpdateRequest,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update company details"""
    
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update company fields
    if company_update.company_name is not None:
        company.company_name = company_update.company_name
    if company_update.industry is not None:
        company.industry = company_update.industry
    if company_update.company_size is not None:
        company.company_size = company_update.company_size
    if company_update.website_url is not None:
        # Only update if the field exists on the model
        if hasattr(company, 'website_url'):
            company.website_url = company_update.website_url
    
    await db.commit()
    
    return {"message": "Company details updated successfully"}

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role_data: dict,
    admin_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user role (only main admin can do this)"""
    
    new_role = role_data.get("new_role")
    
    # Only allow main admin (role='admin') to change roles
    if admin_user.role != "admin":
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Only main admin can change user roles"
        )
    
    # Validate role
    valid_roles = ["admin", "owner", "member", "viewer"]
    if new_role not in valid_roles:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {valid_roles}"
        )
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent removing admin role from main admin (yourself)
    if user.role == "admin" and new_role != "admin":
        # Count total admins
        admin_count = await db.scalar(
            select(func.count(User.id)).where(User.role == "admin")
        )
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove admin role from the last admin user"
            )
    
    # Update role
    old_role = user.role
    user.role = new_role
    await db.commit()
    
    return {
        "message": f"User role updated from {old_role} to {new_role}",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "old_role": old_role,
            "new_role": new_role
        }
    }

@router.get("/roles")
async def get_available_roles(
    admin_user: User = Depends(require_admin)
):
    """Get list of available user roles"""
    
    roles = [
        {
            "value": "admin",
            "label": "Admin",
            "description": "Full platform access, can manage all users and companies"
        },
        {
            "value": "owner", 
            "label": "Company Owner",
            "description": "Company owner with full access to their company"
        },
        {
            "value": "member",
            "label": "Member", 
            "description": "Regular user with standard access"
        },
        {
            "value": "viewer",
            "label": "Viewer",
            "description": "Read-only access to company resources"
        }
    ]
    
    return {"roles": roles}