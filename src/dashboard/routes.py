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

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

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

@router.get("/team")
async def get_team_members(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get team members for current user's company"""
    
    # Only owners and admins can see team members
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner or admin permissions required"
        )
    
    team_result = await db.execute(
        select(User).where(User.company_id == current_user.company_id)
        .order_by(User.created_at.desc())
    )
    team_members = team_result.scalars().all()
    
    team_list = []
    for member in team_members:
        team_list.append({
            "id": str(member.id),
            "email": member.email,
            "full_name": member.full_name,
            "role": member.role,
            "is_active": member.is_active,
            "is_verified": member.is_verified,
            "created_at": member.created_at
        })
    
    return {"team_members": team_list}

@router.get("/campaigns")
async def get_company_campaigns(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get campaigns for current user's company"""
    
    campaigns_result = await db.execute(
        select(Campaign).where(Campaign.company_id == current_user.company_id)
        .order_by(Campaign.created_at.desc())
    )
    campaigns = campaigns_result.scalars().all()
    
    campaign_list = []
    for campaign in campaigns:
        campaign_list.append({
            "id": str(campaign.id),
            "title": campaign.title,
            "description": campaign.description,
            "campaign_type": campaign.campaign_type.value if campaign.campaign_type else None,
            "status": campaign.status.value if campaign.status else None,
            "created_at": campaign.created_at,
            "user_id": str(campaign.user_id)
        })
    
    return {"campaigns": campaign_list}