# =====================================
# File: src/intelligence/routes/product_creator_dashboard_routes.py
# =====================================

"""
Product Creator Dashboard API routes for specialized interface.

Provides endpoints for the limited product creator dashboard with
focused tools for URL submission and tracking.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel, HttpUrl, Field

from src.core.database import get_async_db
from src.core.auth.dependencies import get_current_user, require_admin_or_product_creator
from src.core.shared.responses import StandardResponse
from src.intelligence.services.product_creator_dashboard_service import ProductCreatorDashboardService
from src.intelligence.services.admin_intelligence_service import AdminIntelligenceService

router = APIRouter(prefix="/product-creator", tags=["Product Creator Dashboard"])


class SubmitURLsRequest(BaseModel):
    """Request model for product creator URL submissions."""
    product_name: str = Field(..., description="Name of your product")
    category: str = Field(..., description="Product category")
    urls: List[HttpUrl] = Field(..., description="Sales page URLs to analyze", max_items=20)
    launch_date: str = Field(None, description="Expected launch date")
    notes: str = Field(None, description="Additional notes about your product")


@router.get("/dashboard", response_model=StandardResponse[Dict[str, Any]])
async def get_product_creator_dashboard(
    current_user: dict = Depends(require_admin_or_product_creator),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    🎯 Get Product Creator Dashboard Overview.

    **Product Creator Interface**: Specialized dashboard with limited tools
    focused on URL submission and analysis tracking.

    **Features:**
    - URL submission quota tracking
    - Submission status monitoring
    - Analysis results viewing
    - Account restrictions display
    """
    try:
        # Simplified dashboard data for immediate functionality
        dashboard_data = {
            "account_type": "product_creator",
            "user_id": current_user["id"],
            "user_email": current_user["email"],
            "user_type": current_user.get("user_type", "PRODUCT_CREATOR"),
            "restrictions": {
                "max_url_submissions": 50,
                "submission_cooldown_hours": 0,
                "analysis_only": True,
                "content_library_access": True
            },
            "submission_stats": {
                "total_submitted": 0,
                "pending_analysis": 0,
                "completed_analysis": 0,
                "remaining_quota": 50
            },
            "recent_submissions": [],
            "available_tools": [
                {
                    "id": "url_submission",
                    "name": "URL Submission",
                    "description": "Submit sales page URLs for AI analysis",
                    "enabled": True
                },
                {
                    "id": "content_library",
                    "name": "Content Library",
                    "description": "Generate promotional content for affiliates",
                    "enabled": True
                },
                {
                    "id": "submission_tracking",
                    "name": "Submission Tracking",
                    "description": "Monitor your submission status and results",
                    "enabled": True
                }
            ],
            "dashboard_config": {
                "dashboard_type": "product_creator",
                "show_billing": False,
                "show_analytics": False,
                "show_campaign_creation": False,
                "focus_mode": "analysis_only"
            }
        }

        return StandardResponse(
            success=True,
            data=dashboard_data,
            message="Product creator dashboard loaded successfully"
        )

    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load dashboard: {str(e)}")


@router.post("/submit-urls", response_model=StandardResponse[Dict[str, Any]])
async def submit_urls_for_analysis(
    request: SubmitURLsRequest,
    current_user: dict = Depends(require_admin_or_product_creator),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    🔗 Submit URLs for Pre-Launch Analysis.

    **Product Creator Tool**: Submit your sales page URLs for comprehensive
    analysis before launch. Results will be cached for affiliate marketers.

    **Quota Management**: Submissions are tracked against your invite limits.
    """
    try:
        dashboard_service = ProductCreatorDashboardService()

        # Check if user can submit these URLs
        permission_check = await dashboard_service.can_submit_urls(
            user_id=current_user["id"],
            url_count=len(request.urls),
            session=session
        )

        if not permission_check["can_submit"]:
            raise HTTPException(status_code=403, detail=permission_check["reason"])

        # Use the existing admin service to create submission
        admin_service = AdminIntelligenceService()

        submission = await admin_service.create_product_creator_submission(
            urls=[str(url) for url in request.urls],
            product_name=request.product_name,
            category=request.category,
            contact_email=current_user["email"],
            submitter_user_id=current_user["id"],
            launch_date=request.launch_date,
            notes=request.notes,
            session=session
        )

        return StandardResponse(
            success=True,
            data={
                "submission_id": submission.id,
                "product_name": submission.product_name,
                "url_count": len(submission.urls),
                "status": submission.status,
                "created_at": submission.created_at.isoformat() if submission.created_at else None,
                "remaining_quota": permission_check["remaining_urls"] - len(request.urls)
            },
            message=f"Successfully submitted {len(request.urls)} URLs for analysis. Submission ID: {submission.id}"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit URLs: {str(e)}")


@router.get("/submissions", response_model=StandardResponse[List[Dict[str, Any]]])
async def get_my_submissions(
    current_user: dict = Depends(require_admin_or_product_creator),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[List[Dict[str, Any]]]:
    """
    📋 Get My URL Submissions.

    **Submission Tracking**: View all your submitted URLs and their analysis status.
    """
    try:
        from sqlalchemy import select
        from src.intelligence.models.product_creator_submission import ProductCreatorSubmission

        stmt = select(ProductCreatorSubmission).where(
            ProductCreatorSubmission.submitter_user_id == current_user["id"]
        ).order_by(ProductCreatorSubmission.created_at.desc())

        result = await session.execute(stmt)
        submissions = result.scalars().all()

        submission_data = []
        for submission in submissions:
            submission_dict = submission.to_dict()
            # Remove sensitive admin data for product creators
            submission_dict.pop("admin_notes", None)
            submission_dict.pop("processed_by_admin_id", None)
            submission_data.append(submission_dict)

        return StandardResponse(
            success=True,
            data=submission_data,
            message=f"Found {len(submission_data)} submissions"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get submissions: {str(e)}")


@router.get("/submission/{submission_id}", response_model=StandardResponse[Dict[str, Any]])
async def get_submission_details(
    submission_id: str,
    current_user: dict = Depends(require_admin_or_product_creator),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    🔍 Get Submission Details.

    **Result Viewing**: View detailed information about a specific submission
    including analysis results if completed.
    """
    try:
        from src.intelligence.models.product_creator_submission import ProductCreatorSubmission

        submission = await session.get(ProductCreatorSubmission, submission_id)

        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")

        # Verify ownership
        if submission.submitter_user_id != current_user["id"]:
            raise HTTPException(status_code=403, detail="Access denied")

        submission_data = submission.to_dict()

        # Remove sensitive admin data
        submission_data.pop("admin_notes", None)
        submission_data.pop("processed_by_admin_id", None)

        # Add analysis results if available
        if submission.intelligence_ids:
            from src.intelligence.repositories.intelligence_repository import IntelligenceRepository
            repo = IntelligenceRepository()

            analysis_results = []
            for intel_id in submission.intelligence_ids:
                intel = await repo.find_by_id(intel_id, session)
                if intel:
                    analysis_results.append({
                        "intelligence_id": intel.id,
                        "product_name": intel.product_name,
                        "confidence_score": intel.confidence_score,
                        "analysis_method": intel.analysis_method,
                        "created_at": intel.created_at.isoformat() if intel.created_at else None
                    })

            submission_data["analysis_results"] = analysis_results

        return StandardResponse(
            success=True,
            data=submission_data,
            message="Submission details retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get submission details: {str(e)}")


@router.get("/quota", response_model=StandardResponse[Dict[str, Any]])
async def get_url_quota(
    current_user: dict = Depends(require_admin_or_product_creator),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    📊 Get URL Submission Quota.

    **Quota Tracking**: Check your remaining URL submission allowance.
    """
    try:
        dashboard_service = ProductCreatorDashboardService()

        usage_stats = await dashboard_service._get_usage_statistics(
            user_id=current_user["id"],
            session=session
        )

        return StandardResponse(
            success=True,
            data=usage_stats,
            message="URL quota information retrieved successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get quota information: {str(e)}")


@router.get("/tools", response_model=StandardResponse[List[Dict[str, Any]]])
async def get_available_tools(
    current_user: dict = Depends(require_admin_or_product_creator)
) -> StandardResponse[List[Dict[str, Any]]]:
    """
    🛠️ Get Available Tools.

    **Tool Discovery**: Get list of tools available in the product creator dashboard.
    """
    try:
        dashboard_service = ProductCreatorDashboardService()
        tools = dashboard_service._get_available_tools()

        return StandardResponse(
            success=True,
            data=tools,
            message="Available tools retrieved successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get available tools: {str(e)}")