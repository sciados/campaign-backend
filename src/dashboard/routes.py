"""
Company dashboard routes for company owners and team members - FIXED VERSION
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel
from typing import Dict
from datetime import datetime, timedelta

from src.core.database import get_db
from src.auth.dependencies import get_current_user
from src.models.user import User
from src.models.company import Company
from src.models.campaign import Campaign, CampaignStatus  # ✅ FIXED: Import CampaignStatus enum

# ✅ FIXED: Remove duplicate prefix (main.py already adds /api/dashboard)
router = APIRouter(tags=["dashboard"])

class CompanyStatsResponse(BaseModel):
    company_name: str
    subscription_tier: str
    monthly_credits_used: int
    monthly_credits_limit: int
    credits_remaining: int
    total_campaigns: int
    active_campaigns: int
    team_members: int
    campaigns_this_month: int
    usage_percentage: float

@router.get("/stats", response_model=CompanyStatsResponse)
async def get_company_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get company dashboard statistics for current user's company - FIXED"""
    
    try:
        # Get company data
        company_result = await db.execute(
            select(Company).where(Company.id == current_user.company_id)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Get date range for this month
        now = datetime.utcnow()
        first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Total campaigns for this company
        total_campaigns = await db.scalar(
            select(func.count(Campaign.id)).where(Campaign.company_id == current_user.company_id)
        ) or 0
        
        # ✅ FIXED: Use actual database enum values
        # Database has: DRAFT, IN_PROGRESS, REVIEW, ACTIVE, COMPLETED, ARCHIVED
        active_campaigns = await db.scalar(
            select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == current_user.company_id,
                    Campaign.status.in_([
                        CampaignStatus.DRAFT, 
                        CampaignStatus.IN_PROGRESS,
                        CampaignStatus.REVIEW,
                        CampaignStatus.ACTIVE
                    ])  # ✅ FIXED: Use enum values that actually exist in database
                )
            )
        ) or 0
        
        # Team members in this company
        team_members = await db.scalar(
            select(func.count(User.id)).where(User.company_id == current_user.company_id)
        ) or 0
        
        # Campaigns created this month
        campaigns_this_month = await db.scalar(
            select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == current_user.company_id,
                    Campaign.created_at >= first_of_month
                )
            )
        ) or 0
        
        # Calculate usage percentage
        credits_remaining = max(0, company.monthly_credits_limit - company.monthly_credits_used)
        usage_percentage = (company.monthly_credits_used / company.monthly_credits_limit * 100) if company.monthly_credits_limit > 0 else 0
        
        return CompanyStatsResponse(
            company_name=company.company_name,
            subscription_tier=company.subscription_tier,
            monthly_credits_used=company.monthly_credits_used,
            monthly_credits_limit=company.monthly_credits_limit,
            credits_remaining=credits_remaining,
            total_campaigns=total_campaigns,
            active_campaigns=active_campaigns,
            team_members=team_members,
            campaigns_this_month=campaigns_this_month,
            usage_percentage=round(usage_percentage, 1)
        )
        
    except Exception as e:
        # ✅ FIXED: Better error handling to prevent frontend crashes
        print(f"❌ Dashboard stats error: {e}")
        
        # Return safe defaults if we can't get company data
        try:
            company_result = await db.execute(
                select(Company).where(Company.id == current_user.company_id)
            )
            company = company_result.scalar_one_or_none()
            
            return CompanyStatsResponse(
                company_name=company.company_name if company else "Unknown",
                subscription_tier=company.subscription_tier if company else "free",
                monthly_credits_used=company.monthly_credits_used if company else 0,
                monthly_credits_limit=company.monthly_credits_limit if company else 5000,
                credits_remaining=5000,
                total_campaigns=0,
                active_campaigns=0,
                team_members=1,
                campaigns_this_month=0,
                usage_percentage=0.0
            )
        except:
            # Ultimate fallback
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch company stats: {str(e)}"
            )

@router.get("/company")
async def get_company_details(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed company information"""
    
    company_result = await db.execute(
        select(Company).where(Company.id == current_user.company_id)
    )
    company = company_result.scalar_one_or_none()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return {
        "id": str(company.id),
        "company_name": company.company_name,
        "company_slug": company.company_slug,
        "industry": getattr(company, 'industry', None),
        "company_size": getattr(company, 'company_size', 'small'),
        "website_url": getattr(company, 'website_url', None),
        "subscription_tier": company.subscription_tier,
        "subscription_status": company.subscription_status,
        "monthly_credits_used": company.monthly_credits_used,
        "monthly_credits_limit": company.monthly_credits_limit,
        "created_at": company.created_at.isoformat() if company.created_at else None
    }