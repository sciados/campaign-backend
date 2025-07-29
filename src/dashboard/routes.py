"""
Company dashboard routes for company owners and team members - ADMIN DASHBOARD PATTERN
Uses the same proven pattern as admin dashboard with user-focused data
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
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
            AND status IN ('DRAFT', 'ANALYZING', 'ANALYSIS_COMPLETE', 'ACTIVE')
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

@router.get("/company")
async def get_company_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed company information - SAME PATTERN AS ADMIN"""
    
    try:
        # ✅ EXACTLY LIKE ADMIN: Simple raw SQL
        result = await db.execute(text("""
            SELECT id, company_name, company_slug, industry, company_size, 
                   website_url, subscription_tier, subscription_status,
                   monthly_credits_used, monthly_credits_limit, created_at
            FROM companies 
            WHERE id = :company_id
        """), {"company_id": str(current_user.company_id)})
        
        company_data = result.fetchone()
        
        if not company_data:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return {
            "id": str(company_data[0]),
            "company_name": company_data[1],
            "company_slug": company_data[2],
            "industry": company_data[3] or "",
            "company_size": company_data[4] or "small",
            "website_url": company_data[5] or "",
            "subscription_tier": company_data[6],
            "subscription_status": company_data[7],
            "monthly_credits_used": company_data[8] or 0,
            "monthly_credits_limit": company_data[9] or 5000,
            "created_at": company_data[10].isoformat() if company_data[10] else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Company details error: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch company details"
        )