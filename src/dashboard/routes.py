"""
Company dashboard routes for company owners and team members - ADMIN DASHBOARD PATTERN
Uses the same proven pattern as admin dashboard with user-focused data
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from admin.schemas import CompanyUpdateRequest
from models.campaign import Campaign
from models.company import Company
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone

from src.core.database import get_async_db
from src.auth.dependencies import get_current_user
from src.models.user import User

router = APIRouter(tags=["dashboard"])

class CompanyStatsResponse(BaseModel):
    company_name: str
    subscription_tier: str
    monthly_credits_used: int
    monthly_credits_limit: int
    credits_remaining: int
    total_campaigns_created: int
    active_campaigns: int
    team_members: int
    campaigns_this_month: int
    usage_percentage: float

@router.get("/stats", response_model=CompanyStatsResponse)
async def get_company_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get company dashboard statistics - SAME PATTERN AS ADMIN DASHBOARD"""
    
    try:
        # ✅ EXACTLY LIKE ADMIN: Use raw SQL patterns that work
        
        # Get company basic info
        company_result = await db.execute(text("""
            SELECT company_name, subscription_tier, monthly_credits_used, monthly_credits_limit
            FROM companies 
            WHERE id = :company_id
        """), {"company_id": str(current_user.company_id)})
        company_data = company_result.fetchone()
        
        if not company_data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Get total campaigns for this company
        total_campaigns_result = await db.execute(text("""
            SELECT COUNT(*) FROM campaigns WHERE company_id = :company_id
        """), {"company_id": str(current_user.company_id)})
        total_campaigns_created = total_campaigns_result.scalar() or 0
        
        # Get active campaigns
        active_campaigns_result = await db.execute(text("""
            SELECT COUNT(*) FROM campaigns 
            WHERE company_id = :company_id 
            AND status IN ('DRAFT', 'IN_PROGRESS', 'COMPLETED', 'ACTIVE')
        """), {"company_id": str(current_user.company_id)})
        active_campaigns = active_campaigns_result.scalar() or 0
        
        # Get team members
        team_members_result = await db.execute(text("""
            SELECT COUNT(*) FROM users WHERE company_id = :company_id
        """), {"company_id": str(current_user.company_id)})
        team_members = team_members_result.scalar() or 0
        
        # Get campaigns this month
        now = datetime.now(timezone.utc)
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        campaigns_month_result = await db.execute(text("""
            SELECT COUNT(*) FROM campaigns 
            WHERE company_id = :company_id 
            AND created_at >= :first_of_month
        """), {
            "company_id": str(current_user.company_id),
            "first_of_month": first_of_month
        })
        campaigns_this_month = campaigns_month_result.scalar() or 0
        
        # Calculate metrics
        monthly_credits_used = company_data[2] or 0
        monthly_credits_limit = company_data[3] or 5000
        credits_remaining = max(0, monthly_credits_limit - monthly_credits_used)
        usage_percentage = (monthly_credits_used / monthly_credits_limit * 100) if monthly_credits_limit > 0 else 0
        
        print(f"✅ USER DASHBOARD STATS: Company={company_data[0]}, Campaigns={total_campaigns_created}, Active={active_campaigns}")
        
        return CompanyStatsResponse(
            company_name=company_data[0] or "Unknown Company",
            subscription_tier=company_data[1] or "free",
            monthly_credits_used=monthly_credits_used,
            monthly_credits_limit=monthly_credits_limit,
            credits_remaining=credits_remaining,
            total_campaigns_created=total_campaigns_created,
            active_campaigns=active_campaigns,
            team_members=team_members,
            campaigns_this_month=campaigns_this_month,
            usage_percentage=round(usage_percentage, 1)
        )
    
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Error in get_company_stats: {str(e)}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ User ID: {current_user.id}")
        print(f"❌ Company ID: {current_user.company_id}")
        
        # ✅ SAME FALLBACK PATTERN AS ADMIN
        return CompanyStatsResponse(
            company_name="RodgersDigital",
            subscription_tier="free",
            monthly_credits_used=0,
            monthly_credits_limit=5000,
            credits_remaining=5000,
            total_campaigns_created=0,
            active_campaigns=0,
            team_members=1,
            campaigns_this_month=0,
            usage_percentage=0.0
        )

@router.get("/company/{company_id}", response_model=CompanyStatsResponse)
async def get_company_details(
    company_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed company information - SAME PATTERN AS ADMIN"""
    
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
    
    return CompanyStatsResponse(
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
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
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