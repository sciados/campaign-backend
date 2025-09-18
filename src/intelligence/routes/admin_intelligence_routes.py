# =====================================
# File: src/intelligence/routes/admin_intelligence_routes.py
# =====================================

"""
Admin Intelligence API routes for pre-populating URL cache.

Provides endpoints for admins and product creators to build the
intelligence library before launch.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, HttpUrl, Field

from src.core.database import get_async_db
from src.core.auth.dependencies import get_current_user, require_admin, require_admin_or_product_creator
from src.core.shared.response_models import StandardResponse
from src.intelligence.models.intelligence_models import AnalysisMethod
from src.intelligence.services.admin_intelligence_service import AdminIntelligenceService

router = APIRouter(prefix="/admin/intelligence", tags=["Admin Intelligence"])


class BulkAnalysisRequest(BaseModel):
    """Request model for bulk URL analysis."""
    urls: List[HttpUrl] = Field(..., description="List of URLs to analyze", max_items=100)
    analysis_method: AnalysisMethod = Field(
        default=AnalysisMethod.ENHANCED,
        description="Analysis method to use for all URLs"
    )
    batch_size: int = Field(
        default=5,
        description="Number of URLs to process in parallel per batch",
        ge=1,
        le=10
    )
    delay_between_batches: float = Field(
        default=10.0,
        description="Seconds to wait between batches",
        ge=1.0,
        le=60.0
    )


class ProductCreatorURLSubmission(BaseModel):
    """Model for product creators submitting their URLs."""
    urls: List[HttpUrl] = Field(..., description="Product sales page URLs", max_items=20)
    product_name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    launch_date: Optional[str] = Field(None, description="Expected launch date")
    contact_email: str = Field(..., description="Contact email for updates")
    notes: Optional[str] = Field(None, description="Additional notes about the product")


@router.post("/bulk-analyze")
async def bulk_analyze_urls(
    request: BulkAnalysisRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    🏭 Bulk analyze URLs for pre-populating the affiliate cache.

    **Admin Only**: Pre-analyze high-value URLs before launch so affiliate
    marketers get instant results from day one.

    **Perfect for:**
    - Working with product creators before launch
    - Pre-populating trending product sales pages
    - Building a comprehensive URL intelligence library

    **Processing:**
    - Analyzes URLs in controlled batches
    - Respects API rate limits with delays
    - Uses existing cache when available
    - Provides detailed progress tracking
    """
    try:
        admin_service = AdminIntelligenceService()

        # Convert HttpUrl objects to strings
        url_strings = [str(url) for url in request.urls]

        results = await admin_service.bulk_analyze_urls(
            urls=url_strings,
            admin_user_id=current_user["id"],
            analysis_method=request.analysis_method,
            batch_size=request.batch_size,
            delay_between_batches=request.delay_between_batches,
            session=session
        )

        return StandardResponse(
            success=True,
            data=results,
            message=f"Bulk analysis completed: {results['successful']}/{results['total_urls']} successful"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk analysis failed: {str(e)}")


@router.get("/cache-stats")
async def get_cache_statistics(
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    📊 Get statistics about the current URL cache library.

    **Admin Only**: View comprehensive statistics about:
    - Total unique URLs in cache
    - Analysis coverage and quality
    - Most popular URLs
    - Cache utilization metrics
    """
    try:
        admin_service = AdminIntelligenceService()
        stats = await admin_service.get_cache_statistics(session=session)

        return StandardResponse(
            success=True,
            data=stats,
            message="Cache statistics retrieved successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")


@router.get("/high-value-suggestions")
async def get_high_value_url_suggestions(
    min_confidence: float = 0.8,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[List[Dict[str, Any]]]:
    """
    💎 Get suggestions for high-value URLs to pre-analyze.

    **Admin Only**: Get AI-powered suggestions for URLs that would
    provide maximum value when pre-analyzed for affiliate marketers.
    """
    try:
        admin_service = AdminIntelligenceService()
        suggestions = await admin_service.suggest_high_value_urls(
            min_confidence=min_confidence,
            session=session
        )

        return StandardResponse(
            success=True,
            data=suggestions,
            message=f"Found {len(suggestions)} high-value URL suggestions"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get suggestions: {str(e)}")


@router.post("/product-creator-submission")
async def submit_product_creator_urls(
    request: ProductCreatorURLSubmission,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(require_admin_or_product_creator),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    🎯 Product Creator URL Submission (Public endpoint for special accounts).

    **For Product Creators**: Submit your sales page URLs for pre-analysis
    before launch. This ensures affiliate marketers get instant results
    when analyzing your products.

    **Benefits:**
    - Faster affiliate onboarding
    - Higher quality intelligence
    - Better market penetration
    - Free pre-launch optimization
    """
    try:
        admin_service = AdminIntelligenceService()

        # Create submission record
        submission = await admin_service.create_product_creator_submission(
            urls=[str(url) for url in request.urls],
            product_name=request.product_name,
            category=request.category,
            contact_email=request.contact_email,
            submitter_user_id=current_user.get("id"),
            launch_date=request.launch_date,
            notes=request.notes,
            session=session
        )

        # TODO: Send notification email to admin team
        # TODO: Send confirmation email to product creator

        return StandardResponse(
            success=True,
            data=submission.to_dict(),
            message=f"Product URLs submitted successfully! We'll analyze {len(request.urls)} URLs and notify you at {request.contact_email}. Submission ID: {submission.id}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")


@router.post("/process-creator-submission/{submission_id}")
async def process_product_creator_submission(
    submission_id: str,
    approve: bool = True,
    admin_notes: Optional[str] = None,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    ✅ Process a product creator URL submission.

    **Admin Only**: Approve and process URLs submitted by product creators
    through the special free account system.

    **Approval Process:**
    - Reviews submitted URLs for quality and relevance
    - Runs enhanced analysis on approved URLs
    - Adds results to global affiliate cache
    - Notifies product creator of completion
    """
    try:
        admin_service = AdminIntelligenceService()

        results = await admin_service.process_product_creator_submission(
            submission_id=submission_id,
            approve=approve,
            admin_user_id=current_user["id"],
            admin_notes=admin_notes,
            session=session
        )

        action = "approved and processed" if approve else "rejected"
        message = f"Product creator submission {action} successfully"

        if approve and "bulk_results" in results:
            bulk_results = results["bulk_results"]
            message += f". Analyzed {bulk_results['successful']}/{bulk_results['total_urls']} URLs in {bulk_results['total_duration']:.1f}s"

        # TODO: Send email notification to product creator

        return StandardResponse(
            success=True,
            data=results,
            message=message
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process submission: {str(e)}")


@router.get("/creator-submissions")
async def list_product_creator_submissions(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[List[Dict[str, Any]]]:
    """
    📋 List product creator submissions.

    **Admin Only**: View and manage product creator URL submissions.
    """
    try:
        from sqlalchemy import select
        from src.intelligence.models.product_creator_submission import ProductCreatorSubmission

        stmt = select(ProductCreatorSubmission)

        if status:
            stmt = stmt.where(ProductCreatorSubmission.status == status)

        stmt = stmt.offset(offset).limit(limit).order_by(ProductCreatorSubmission.created_at.desc())

        result = await session.execute(stmt)
        submissions = result.scalars().all()

        return StandardResponse(
            success=True,
            data=[submission.to_dict() for submission in submissions],
            message=f"Found {len(submissions)} product creator submissions"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list submissions: {str(e)}")