"""
Company dashboard routes for company owners and team members
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
from src.models.campaign import Campaign

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
    """Get company dashboard statistics for current user's company"""
    
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
        
        # Active campaigns (not archived/completed)
        active_campaigns = await db.scalar(
            select(func.count(Campaign.id)).where(
                and_(
                    Campaign.company_id == current_user.company_id,
                    Campaign.status.in_(["draft", "in_progress", "active"])
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
        "industry": company.industry,
        "company_size": company.company_size,
        "website_url": company.website_url,
        "subscription_tier": company.subscription_tier,
        "subscription_status": company.subscription_status,
        "monthly_credits_used": company.monthly_credits_used,
        "monthly_credits_limit": company.monthly_credits_limit,
        "created_at": company.created_at
    }