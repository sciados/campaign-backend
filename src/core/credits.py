# src/core/credits.py
"""
Credit management and tier enforcement system
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException, status
from typing import Dict, Any
from datetime import datetime
import logging

from src.models.user import User
from src.models.company import Company

logger = logging.getLogger(__name__)

# Tier configuration with limits and features
TIER_CONFIG = {
    "free": {
        "monthly_credits_limit": 50,
        "intelligence_analysis_limit": 5,
        "content_generation_limit": 10,
        "document_upload_limit": 3,
        "smart_urls_limit": 10,
        "features": {
            "sales_page_analysis": True,
            "basic_content_generation": True,
            "document_upload": ["pdf"],
            "email_support": False,
            "api_access": False,
            "white_label": False,
            "team_collaboration": False
        },
        "credits_per_operation": {
            "intelligence_analysis": 5,
            "content_generation": 2,
            "document_analysis": 3,
            "smart_url_creation": 1
        }
    },
    "growth": {
        "monthly_credits_limit": 500,
        "intelligence_analysis_limit": 50,
        "content_generation_limit": 100,
        "document_upload_limit": 25,
        "smart_urls_limit": 100,
        "features": {
            "sales_page_analysis": True,
            "advanced_content_generation": True,
            "document_upload": ["pdf", "docx", "pptx", "txt"],
            "psychology_analysis": True,
            "competitor_monitoring": 5,  # 5 competitors
            "email_support": True,
            "api_access": False,
            "white_label": False,
            "team_collaboration": False
        },
        "credits_per_operation": {
            "intelligence_analysis": 5,
            "content_generation": 2,
            "document_analysis": 3,
            "smart_url_creation": 1
        }
    },
    "professional": {
        "monthly_credits_limit": 2000,
        "intelligence_analysis_limit": 200,
        "content_generation_limit": 500,
        "document_upload_limit": 100,
        "smart_urls_limit": 500,
        "features": {
            "sales_page_analysis": True,
            "advanced_content_generation": True,
            "premium_content_types": True,
            "document_upload": ["pdf", "docx", "pptx", "txt", "xlsx", "csv"],
            "psychology_analysis": True,
            "competitor_monitoring": 20,  # 20 competitors
            "performance_predictions": True,
            "a_b_testing": True,
            "priority_support": True,
            "api_access": True,
            "white_label": True,
            "team_collaboration": 5  # 5 team members
        },
        "credits_per_operation": {
            "intelligence_analysis": 4,  # Reduced cost for higher tier
            "content_generation": 1,
            "document_analysis": 2,
            "smart_url_creation": 1
        }
    },
    "agency": {
        "monthly_credits_limit": -1,  # Unlimited
        "intelligence_analysis_limit": -1,  # Unlimited
        "content_generation_limit": -1,  # Unlimited
        "document_upload_limit": -1,  # Unlimited
        "smart_urls_limit": -1,  # Unlimited
        "features": {
            "everything": True,
            "unlimited_access": True,
            "document_upload": ["all"],
            "competitor_monitoring": -1,  # Unlimited
            "white_label_platform": True,
            "client_management": True,
            "custom_integrations": True,
            "dedicated_support": True,
            "api_access": True,
            "team_collaboration": -1,  # Unlimited
            "custom_models": True
        },
        "credits_per_operation": {
            "intelligence_analysis": 3,  # Lowest cost
            "content_generation": 1,
            "document_analysis": 1,
            "smart_url_creation": 0  # Free for agency
        }
    }
}

class CreditManager:
    """Manage credits and tier enforcement"""
    
    @staticmethod
    async def check_and_consume_credits(
        user: User,
        operation: str,
        credits_required: int = None,
        db: AsyncSession = None
    ) -> Dict[str, Any]:
        """Check if user has enough credits and consume them"""
        
        # Get user's company for tier info
        company_result = await db.execute(
            select(Company).where(Company.id == user.company_id)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        # Get tier configuration
        tier_config = TIER_CONFIG.get(company.subscription_tier, TIER_CONFIG["free"])
        
        # Calculate credits needed if not provided
        if credits_required is None:
            credits_required = tier_config["credits_per_operation"].get(operation, 1)
        
        # Check monthly limits for unlimited tiers
        if tier_config["monthly_credits_limit"] == -1:
            # Unlimited tier - just consume credits for tracking
            await CreditManager._consume_credits(company, credits_required, db)
            return {
                "success": True,
                "credits_consumed": credits_required,
                "remaining_credits": "unlimited",
                "tier": company.subscription_tier
            }
        
        # Check if user has enough credits
        if company.monthly_credits_used + credits_required > company.monthly_credits_limit:
            # Check for specific operation limits
            remaining_credits = company.monthly_credits_limit - company.monthly_credits_used
            
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail={
                    "message": f"Insufficient credits for {operation}",
                    "credits_required": credits_required,
                    "credits_remaining": remaining_credits,
                    "current_tier": company.subscription_tier,
                    "upgrade_suggestion": CreditManager._get_upgrade_suggestion(company.subscription_tier)
                }
            )
        
        # Consume credits
        await CreditManager._consume_credits(company, credits_required, db)
        
        return {
            "success": True,
            "credits_consumed": credits_required,
            "remaining_credits": company.monthly_credits_limit - company.monthly_credits_used,
            "tier": company.subscription_tier
        }
    
    @staticmethod
    async def _consume_credits(company: Company, credits: int, db: AsyncSession):
        """Actually consume the credits"""
        
        await db.execute(
            update(Company)
            .where(Company.id == company.id)
            .values(monthly_credits_used=Company.monthly_credits_used + credits)
        )
        await db.commit()
        
        # Update the object for immediate use
        company.monthly_credits_used += credits
    
    @staticmethod
    def _get_upgrade_suggestion(current_tier: str) -> Dict[str, Any]:
        """Get upgrade suggestion for current tier"""
        
        tier_progression = {
            "free": {
                "next_tier": "growth",
                "price": "$39/month",
                "benefits": [
                    "10x more intelligence analyses (50/month)",
                    "10x more content generation (100/month)",
                    "Advanced psychology insights",
                    "Email support"
                ]
            },
            "growth": {
                "next_tier": "professional",
                "price": "$79/month",
                "benefits": [
                    "4x more analyses (200/month)",
                    "5x more content generation (500/month)",
                    "Performance predictions",
                    "API access",
                    "White-label features"
                ]
            },
            "professional": {
                "next_tier": "agency",
                "price": "$199/month",
                "benefits": [
                    "Unlimited everything",
                    "Client management dashboard",
                    "Custom integrations",
                    "Dedicated support"
                ]
            }
        }
        
        return tier_progression.get(current_tier, {})
    
    @staticmethod
    async def check_feature_access(
        user: User,
        feature: str,
        db: AsyncSession
    ) -> bool:
        """Check if user has access to specific feature"""
        
        company_result = await db.execute(
            select(Company).where(Company.id == user.company_id)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            return False
        
        tier_config = TIER_CONFIG.get(company.subscription_tier, TIER_CONFIG["free"])
        
        # Check specific feature
        return tier_config["features"].get(feature, False)
    
    @staticmethod
    async def check_operation_limit(
        user: User,
        operation: str,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """Check operation-specific limits"""
        
        company_result = await db.execute(
            select(Company).where(Company.id == user.company_id)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        tier_config = TIER_CONFIG.get(company.subscription_tier, TIER_CONFIG["free"])
        
        # Get current month's usage for specific operation
        # This would require tracking individual operations in the database
        # For now, return tier limits
        
        limit_key = f"{operation}_limit"
        limit = tier_config.get(limit_key, 0)
        
        return {
            "operation": operation,
            "limit": limit,
            "unlimited": limit == -1,
            "tier": company.subscription_tier
        }
    
    @staticmethod
    async def get_usage_summary(user: User, db: AsyncSession) -> Dict[str, Any]:
        """Get comprehensive usage summary for user's company"""
        
        company_result = await db.execute(
            select(Company).where(Company.id == user.company_id)
        )
        company = company_result.scalar_one_or_none()
        
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        tier_config = TIER_CONFIG.get(company.subscription_tier, TIER_CONFIG["free"])
        
        # Calculate usage percentages
        credit_usage_percentage = 0
        if tier_config["monthly_credits_limit"] > 0:
            credit_usage_percentage = (company.monthly_credits_used / tier_config["monthly_credits_limit"]) * 100
        
        # Determine if upgrade is recommended
        should_upgrade = credit_usage_percentage > 80
        
        return {
            "tier": company.subscription_tier,
            "credits": {
                "used": company.monthly_credits_used,
                "limit": tier_config["monthly_credits_limit"],
                "remaining": max(0, tier_config["monthly_credits_limit"] - company.monthly_credits_used) if tier_config["monthly_credits_limit"] > 0 else "unlimited",
                "usage_percentage": round(credit_usage_percentage, 1)
            },
            "limits": {
                "intelligence_analysis": tier_config["intelligence_analysis_limit"],
                "content_generation": tier_config["content_generation_limit"],
                "document_upload": tier_config["document_upload_limit"],
                "smart_urls": tier_config["smart_urls_limit"]
            },
            "features": tier_config["features"],
            "upgrade_recommendation": {
                "should_upgrade": should_upgrade,
                "reason": "High usage detected" if should_upgrade else None,
                "suggestion": CreditManager._get_upgrade_suggestion(company.subscription_tier) if should_upgrade else None
            }
        }

# Decorator for enforcing credit requirements
def require_credits(operation: str, credits: int = None):
    """Decorator to enforce credit requirements on endpoints"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user and db from function arguments
            user = None
            db = None
            
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            for key, value in kwargs.items():
                if key == 'current_user' and isinstance(value, User):
                    user = value
                elif key == 'db' and hasattr(value, 'execute'):
                    db = value
            
            if not user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Credit enforcement failed - missing user or db"
                )
            
            # Check and consume credits
            await CreditManager.check_and_consume_credits(
                user=user,
                operation=operation,
                credits_required=credits,
                db=db
            )
            
            # Call original function
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Feature access decorator
def require_feature(feature: str):
    """Decorator to enforce feature access requirements"""
    
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user and db
            user = None
            db = None
            
            for arg in args:
                if isinstance(arg, User):
                    user = arg
                    break
            
            for key, value in kwargs.items():
                if key == 'current_user' and isinstance(value, User):
                    user = value
                elif key == 'db' and hasattr(value, 'execute'):
                    db = value
            
            if not user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Feature enforcement failed"
                )
            
            # Check feature access
            has_access = await CreditManager.check_feature_access(user, feature, db)
            
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail={
                        "message": f"Feature '{feature}' not available in your current tier",
                        "current_tier": user.company.subscription_tier if hasattr(user, 'company') else "unknown",
                        "upgrade_suggestion": CreditManager._get_upgrade_suggestion(
                            user.company.subscription_tier if hasattr(user, 'company') else "free"
                        )
                    }
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Convenience function for direct use in routes
async def check_and_consume_credits(
    user: User,
    operation: str,
    credits_required: int = None,
    db: AsyncSession = None
) -> Dict[str, Any]:
    """Direct function call for credit checking and consumption"""
    return await CreditManager.check_and_consume_credits(
        user=user,
        operation=operation,
        credits_required=credits_required,
        db=db
    )