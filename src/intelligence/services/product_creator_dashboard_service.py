# =====================================
# File: src/intelligence/services/product_creator_dashboard_service.py
# =====================================

"""
Product Creator Dashboard Service for specialized limited interface.

Provides a focused dashboard experience for invited product creators with
limited tools specifically designed for URL submission and analysis tracking.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from src.intelligence.services.product_creator_invite_service import ProductCreatorInviteService
from src.intelligence.models.product_creator_submission import ProductCreatorSubmission
from src.intelligence.repositories.intelligence_repository import IntelligenceRepository

logger = logging.getLogger(__name__)


class ProductCreatorDashboardService:
    """Specialized dashboard service for product creators."""

    def __init__(self):
        self.invite_service = ProductCreatorInviteService()
        self.intelligence_repo = IntelligenceRepository()

    async def get_dashboard_overview(
        self,
        user_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get product creator dashboard overview.

        Args:
            user_id: Product creator user ID
            session: Database session

        Returns:
            Dict with dashboard data
        """
        # Get user restrictions from invite
        restrictions = await self.invite_service.get_user_invite_restrictions(
            user_id=user_id,
            session=session
        )

        if not restrictions:
            raise ValueError("User is not a product creator account")

        # Get submission statistics
        submission_stats = await self._get_submission_statistics(user_id, session)

        # Get usage statistics
        usage_stats = await self._get_usage_statistics(user_id, session)

        # Get recent activity
        recent_activity = await self._get_recent_activity(user_id, session)

        return {
            "account_type": "product_creator",
            "restrictions": restrictions,
            "submission_stats": submission_stats,
            "usage_stats": usage_stats,
            "recent_activity": recent_activity,
            "available_tools": self._get_available_tools(),
            "dashboard_config": self._get_dashboard_config()
        }

    async def _get_submission_statistics(
        self,
        user_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get URL submission statistics."""
        stmt = select(
            func.count(ProductCreatorSubmission.id).label("total_submissions"),
            func.count(ProductCreatorSubmission.id).filter(
                ProductCreatorSubmission.status == "pending_review"
            ).label("pending_submissions"),
            func.count(ProductCreatorSubmission.id).filter(
                ProductCreatorSubmission.status == "completed"
            ).label("completed_submissions"),
            func.count(ProductCreatorSubmission.id).filter(
                ProductCreatorSubmission.status == "rejected"
            ).label("rejected_submissions")
        ).where(ProductCreatorSubmission.submitter_user_id == user_id)

        result = await session.execute(stmt)
        stats = result.first()

        return {
            "total_submissions": stats.total_submissions or 0,
            "pending_submissions": stats.pending_submissions or 0,
            "completed_submissions": stats.completed_submissions or 0,
            "rejected_submissions": stats.rejected_submissions or 0
        }

    async def _get_usage_statistics(
        self,
        user_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get usage statistics for the product creator."""
        # Get user restrictions
        restrictions = await self.invite_service.get_user_invite_restrictions(
            user_id=user_id,
            session=session
        )

        if not restrictions:
            return {}

        # Count total URLs submitted across all submissions
        stmt = select(ProductCreatorSubmission).where(
            ProductCreatorSubmission.submitter_user_id == user_id
        )
        result = await session.execute(stmt)
        submissions = result.scalars().all()

        total_urls_submitted = sum(len(sub.urls) for sub in submissions)
        max_urls = restrictions.get("max_url_submissions", 20)

        return {
            "urls_submitted": total_urls_submitted,
            "max_urls_allowed": max_urls,
            "remaining_urls": max(0, max_urls - total_urls_submitted),
            "usage_percentage": min(100, (total_urls_submitted / max_urls) * 100)
        }

    async def _get_recent_activity(
        self,
        user_id: str,
        session: AsyncSession,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get recent activity for the product creator."""
        stmt = select(ProductCreatorSubmission).where(
            ProductCreatorSubmission.submitter_user_id == user_id
        ).order_by(ProductCreatorSubmission.created_at.desc()).limit(limit)

        result = await session.execute(stmt)
        submissions = result.scalars().all()

        activity = []
        for submission in submissions:
            activity.append({
                "id": submission.id,
                "type": "url_submission",
                "product_name": submission.product_name,
                "status": submission.status,
                "url_count": len(submission.urls),
                "created_at": submission.created_at.isoformat() if submission.created_at else None,
                "processed_at": submission.processed_at.isoformat() if submission.processed_at else None
            })

        return activity

    def _get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of tools available to product creators."""
        return [
            {
                "id": "url_submission",
                "name": "URL Submission",
                "description": "Submit your product sales page URLs for pre-analysis",
                "icon": "link",
                "primary": True,
                "path": "/dashboard/submit-urls"
            },
            {
                "id": "submission_tracking",
                "name": "Submission Tracking",
                "description": "Track the status of your submitted URLs",
                "icon": "list",
                "primary": True,
                "path": "/dashboard/submissions"
            },
            {
                "id": "analysis_results",
                "name": "Analysis Results",
                "description": "View completed intelligence analysis for your products",
                "icon": "chart",
                "primary": False,
                "path": "/dashboard/results"
            },
            {
                "id": "account_settings",
                "name": "Account Settings",
                "description": "Manage your product creator account settings",
                "icon": "settings",
                "primary": False,
                "path": "/dashboard/settings"
            }
        ]

    def _get_dashboard_config(self) -> Dict[str, Any]:
        """Get dashboard configuration for product creators."""
        return {
            "dashboard_type": "product_creator",
            "show_billing": False,  # Free accounts
            "show_analytics": False,  # Limited analytics
            "show_campaigns": False,  # No campaign creation
            "show_content_generation": False,  # No content generation
            "show_intelligence_analysis": False,  # No direct analysis
            "primary_actions": [
                "submit_urls",
                "track_submissions"
            ],
            "restricted_features": [
                "campaign_creation",
                "content_generation",
                "direct_intelligence_analysis",
                "user_management",
                "billing_management"
            ],
            "welcome_message": "Welcome to your Product Creator Dashboard! Submit your sales page URLs for pre-analysis before launch.",
            "help_links": [
                {
                    "title": "How to Submit URLs",
                    "url": "/help/url-submission"
                },
                {
                    "title": "Understanding Analysis Results",
                    "url": "/help/analysis-results"
                },
                {
                    "title": "Contact Support",
                    "url": "/support"
                }
            ]
        }

    async def can_submit_urls(
        self,
        user_id: str,
        url_count: int,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Check if user can submit the requested number of URLs.

        Args:
            user_id: Product creator user ID
            url_count: Number of URLs they want to submit
            session: Database session

        Returns:
            Dict with permission status and details
        """
        # Get current usage
        usage_stats = await self._get_usage_statistics(user_id, session)

        remaining_urls = usage_stats.get("remaining_urls", 0)
        can_submit = url_count <= remaining_urls

        return {
            "can_submit": can_submit,
            "requested_urls": url_count,
            "remaining_urls": remaining_urls,
            "max_allowed": usage_stats.get("max_urls_allowed", 20),
            "currently_used": usage_stats.get("urls_submitted", 0),
            "reason": None if can_submit else f"URL limit exceeded. You can submit {remaining_urls} more URLs."
        }