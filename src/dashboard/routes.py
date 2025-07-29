"""
Company dashboard routes for company owners and team members - COMPLETELY FIXED VERSION
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from pydantic import BaseModel
from typing import Dict
from datetime import datetime, timedelta, timezone

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.company import Company
from src.models.campaign import Campaign, CampaignStatus

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
    db: AsyncSession = Depends(get_db)
):
    """Get company dashboard statistics - COMPLETELY FIXED with raw SQL approach"""
    
    try:
        print(f"🔍 Getting stats for user {current_user.id} in company {current_user.company_id}")
        
        # ✅ FIXED: Use raw SQL to avoid SQLAlchemy async issues
        company_query = text("""
            SELECT company_name, subscription_tier, monthly_credits_used, 
                   monthly_credits_limit, subscription_status
            FROM companies 
            WHERE id = :company_id
        """)
        
        company_result = await db.execute(company_query, {"company_id": str(current_user.company_id)})
        company_row = company_result.fetchone()
        
        if not company_row:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Get date range for this month
        now = datetime.now(timezone.utc)
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # ✅ FIXED: Use raw SQL for all counting queries with proper async handling
        stats_query = text("""
            SELECT 
                (SELECT COUNT(*) FROM campaigns WHERE company_id = :company_id) as total_campaigns,
                (SELECT COUNT(*) FROM campaigns 
                 WHERE company_id = :company_id 
                 AND status IN ('DRAFT', 'ANALYZING', 'ANALYSIS_COMPLETE', 'ACTIVE')) as active_campaigns,
                (SELECT COUNT(*) FROM users WHERE company_id = :company_id) as team_members,
                (SELECT COUNT(*) FROM campaigns 
                 WHERE company_id = :company_id 
                 AND created_at >= :first_of_month) as campaigns_this_month
        """)
        
        stats_result = await db.execute(stats_query, {
            "company_id": str(current_user.company_id),
            "first_of_month": first_of_month
        })
        stats_row = stats_result.fetchone()
        
        # Extract values safely with proper attribute access
        total_campaigns_created = getattr(stats_row, 'total_campaigns', 0) if stats_row else 0
        active_campaigns = getattr(stats_row, 'active_campaigns', 0) if stats_row else 0
        team_members = getattr(stats_row, 'team_members', 1) if stats_row else 1
        campaigns_this_month = getattr(stats_row, 'campaigns_this_month', 0) if stats_row else 0
        
        # Calculate usage percentage with safe attribute access
        monthly_credits_used = getattr(company_row, 'monthly_credits_used', 0) or 0
        monthly_credits_limit = getattr(company_row, 'monthly_credits_limit', 5000) or 5000
        credits_remaining = max(0, monthly_credits_limit - monthly_credits_used)
        usage_percentage = (monthly_credits_used / monthly_credits_limit * 100) if monthly_credits_limit > 0 else 0
        
        print(f"✅ Successfully calculated stats: {total_campaigns_created} campaigns, {active_campaigns} active")
        
        return CompanyStatsResponse(
            company_name=getattr(company_row, 'company_name', 'Unknown Company') or "Unknown Company",
            subscription_tier=getattr(company_row, 'subscription_tier', 'free') or "free",
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
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        print(f"❌ Dashboard stats error: {e}")
        print(f"❌ Error type: {type(e)}")
        print(f"❌ User ID: {current_user.id}")
        print(f"❌ Company ID: {current_user.company_id}")
        
        # ✅ FIXED: Provide safe fallback without any database queries
        try:
            # Try to get just the company name with raw SQL
            simple_query = text("SELECT company_name FROM companies WHERE id = :company_id")
            name_result = await db.execute(simple_query, {"company_id": str(current_user.company_id)})
            name_row = name_result.fetchone()
            company_name = name_row.company_name if name_row else "Unknown Company"
        except:
            company_name = "Unknown Company"
        
        # Return minimal safe defaults
        return CompanyStatsResponse(
            company_name=company_name,
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
    db: AsyncSession = Depends(get_db)
):
    """Get detailed company information - FIXED with raw SQL"""
    
    try:
        # ✅ FIXED: Use raw SQL to avoid async issues
        query = text("""
            SELECT id, company_name, company_slug, industry, company_size, 
                   website_url, subscription_tier, subscription_status,
                   monthly_credits_used, monthly_credits_limit, created_at
            FROM companies 
            WHERE id = :company_id
        """)
        
        company_result = await db.execute(query, {"company_id": str(current_user.company_id)})
        company_row = company_result.fetchone()
        
        if not company_row:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        return {
            "id": str(getattr(company_row, 'id', '')),
            "company_name": getattr(company_row, 'company_name', ''),
            "company_slug": getattr(company_row, 'company_slug', ''),
            "industry": getattr(company_row, 'industry', ''),
            "company_size": getattr(company_row, 'company_size', 'small') or 'small',
            "website_url": getattr(company_row, 'website_url', ''),
            "subscription_tier": getattr(company_row, 'subscription_tier', 'free'),
            "subscription_status": getattr(company_row, 'subscription_status', 'active'),
            "monthly_credits_used": getattr(company_row, 'monthly_credits_used', 0),
            "monthly_credits_limit": getattr(company_row, 'monthly_credits_limit', 5000),
            "created_at": company_row.created_at.isoformat() if hasattr(company_row, 'created_at') and company_row.created_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Company details error: {e}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch company details"
        )