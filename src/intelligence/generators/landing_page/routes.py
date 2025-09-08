# src/intelligence/generators/landing_page/routes.py
"""
Landing Page Routes - With corrected authentication imports
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import logging

# Use existing auth functions
from src.core.database import get_async_db
from src.auth.dependencies import get_current_active_user
from src.models import User, Company, GeneratedContent, Campaign

# Try to import landing page components
try:
    from .core.generator import LandingPageGenerator
    GENERATOR_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Landing page generator not available: {e}")
    GENERATOR_AVAILABLE = False

try:
    from .analytics.tracker import AnalyticsTracker
    from .analytics.events import EventType
    ANALYTICS_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Analytics not available: {e}")
    ANALYTICS_AVAILABLE = False

logger = logging.getLogger(__name__)
router = APIRouter()

# Helper function to get user and company
async def get_user_and_company(
    user: User = Depends(get_current_active_user)
) -> tuple[User, Company]:
    """Get current user and their company"""
    if not user.company:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with a company"
        )
    return user, user.company

@router.get("/landing-pages/status/")
async def landing_page_status():
    """Status check for landing page system"""
    return {
        "status": "ready",
        "message": "Landing page system is operational",
        "path": "src/intelligence/generators/landing_page/",
        "available_features": {
            "generator": GENERATOR_AVAILABLE,
            "analytics": ANALYTICS_AVAILABLE
        },
        "endpoints": [
            "GET /api/landing-pages/status/ - System status",
            "GET /api/landing-pages/ - List pages",
            "POST /api/landing-pages/generate/ - Generate page"
        ]
    }

@router.get("/landing-pages/")
async def list_landing_pages(
    db: AsyncSession = Depends(get_async_db),
    user_data: tuple = Depends(get_user_and_company),
    limit: int = 50,
    offset: int = 0
):
    """List all landing pages for the company"""
    
    try:
        user, company = user_data
        
        # Get landing pages for the company
        from sqlalchemy import select, and_
        
        query = select(GeneratedContent).where(
            and_(
                GeneratedContent.company_id == company.id,
                GeneratedContent.content_type == "LANDING_PAGE"
            )
        ).order_by(GeneratedContent.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        landing_pages = result.scalars().all()
        
        # Format response
        pages_data = []
        for page in landing_pages:
            pages_data.append({
                "id": str(page.id),
                "title": page.title,
                "campaign_id": str(page.campaign_id) if page.campaign_id else None,
                "created_at": page.created_at.isoformat(),
                "updated_at": page.updated_at.isoformat(),
                "metadata": page.metadata,
                "status": page.analysis_status,
                "analytics_url": f"/api/landing-pages/{page.id}/analytics/"
            })
        
        return {
            "success": True,
            "landing_pages": pages_data,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(pages_data)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Landing page listing failed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Landing page listing failed: {str(e)}"
        )

# Only include generator functionality if available
if GENERATOR_AVAILABLE:
    try:
        landing_page_generator = LandingPageGenerator()
        logger.info("✅ Landing page generator initialized")
    except Exception as e:
        logger.warning(f"⚠️ Could not initialize generator: {e}")
        landing_page_generator = None

    @router.post("/landing-pages/generate/")
    async def generate_landing_page(
        request_data: Dict[str, Any],
        db: AsyncSession = Depends(get_async_db),
        user_data: tuple = Depends(get_user_and_company)
    ):
        """Generate an AI-powered landing page from campaign intelligence"""
        
        if not landing_page_generator:
            raise HTTPException(
                status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Landing page generator not available"
            )
        
        try:
            user, company = user_data
            campaign_id = request_data.get("campaign_id")
            
            if not campaign_id:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail="campaign_id is required"
                )
            
            # Get campaign and verify ownership
            campaign = await db.get(Campaign, campaign_id)
            if not campaign or campaign.company_id != company.id:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Campaign not found"
                )
            
            # Extract intelligence data from campaign
            intelligence_data = {
                "campaign_id": campaign_id,
                "campaign_name": campaign.name,
                "campaign_description": campaign.description,
                "target_audience": campaign.target_audience,
                "messaging_focus": campaign.messaging_focus,
                "industry": company.industry,
                "company_info": {
                    "name": company.company_name,
                    "website": company.website_url,
                    "brand_colors": company.brand_colors or {},
                    "brand_guidelines": company.brand_guidelines or {}
                }
            }
            
            # Get user preferences
            preferences = request_data.get("preferences", {})
            
            # Generate the landing page
            logger.info(f"🚀 Generating landing page for campaign {campaign_id}")
            generation_result = await landing_page_generator.generate_landing_page(
                intelligence_data=intelligence_data,
                preferences=preferences
            )
            
            # Save generated content to database
            generated_content = GeneratedContent(
                campaign_id=campaign_id,
                company_id=company.id,
                user_id=user.id,
                content_type="landing_page",
                title=generation_result.title,
                content=generation_result.html_code,
                metadata=generation_result.metadata,
                analysis_status="completed"
            )
            
            db.add(generated_content)
            await db.commit()
            await db.refresh(generated_content)
            
            # Update company campaign counter
            company.total_campaigns_created = (company.total_campaigns_created or 0) + 1
            await db.commit()
            
            logger.info(f"✅ Landing page generated successfully: {generated_content.id}")
            
            return {
                "success": True,
                "content_id": str(generated_content.id),
                "title": generation_result.title,
                "html_code": generation_result.html_code,
                "sections": generation_result.sections,
                "conversion_elements": generation_result.conversion_elements,
                "metadata": generation_result.metadata,
                "variants": generation_result.variants,
                "performance_predictions": generation_result.performance_predictions,
                "analytics_tracking_url": f"/api/landing-pages/{generated_content.id}/track-event/",
                "analytics_dashboard_url": f"/api/landing-pages/{generated_content.id}/analytics/"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Landing page generation failed: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Landing page generation failed: {str(e)}"
            )

else:
    @router.post("/landing-pages/generate/")
    async def generate_landing_page_unavailable():
        """Landing page generation not available"""
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Landing page generation not available - generator not loaded"
        )

# Analytics endpoints (if available)
if ANALYTICS_AVAILABLE:
    
    @router.post("/landing-pages/{content_id}/track-event/")
    async def track_analytics_event(
        content_id: str,
        event_data: Dict[str, Any],
        db: AsyncSession = Depends(get_async_db)
    ):
        """Track user interaction events on a landing page"""
        
        try:
            # Verify content exists
            content = await db.get(GeneratedContent, content_id)
            if not content or content.content_type != "landing_page":
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Landing page not found"
                )
            
            # Initialize analytics tracker
            tracker = AnalyticsTracker(db)
            
            # Extract event information
            event_type_str = event_data.get("event_type", "").upper()
            
            try:
                event_type = EventType[event_type_str]
            except KeyError:
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid event_type: {event_type_str}"
                )
            
            # Track the event
            success = await tracker.track_event(
                content_id=content_id,
                event_type=event_type,
                event_data=event_data.get("event_data", {}),
                session_info=event_data.get("session_info"),
                variant_id=event_data.get("variant_id")
            )
            
            if success:
                logger.debug(f"✅ Event tracked: {event_type.value} for content {content_id}")
                return {"success": True, "message": "Event tracked successfully"}
            else:
                raise HTTPException(
                    status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to track event"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Event tracking failed: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Event tracking failed: {str(e)}"
            )

    @router.get("/landing-pages/{content_id}/analytics/")
    async def get_landing_page_analytics(
        content_id: str,
        time_window_hours: int = 24,
        db: AsyncSession = Depends(get_async_db),
        user_data: tuple = Depends(get_user_and_company)
    ):
        """Get real-time analytics for a landing page"""
        
        try:
            user, company = user_data
            
            # Verify content exists and user has access
            content = await db.get(GeneratedContent, content_id)
            if not content or content.company_id != company.id:
                raise HTTPException(
                    status_code=http_status.HTTP_404_NOT_FOUND,
                    detail="Landing page not found"
                )
            
            # Get analytics data
            tracker = AnalyticsTracker(db)
            analytics_data = await tracker.get_real_time_analytics(
                content_id=content_id,
                time_window_hours=time_window_hours
            )
            
            # Add content metadata
            analytics_data.update({
                "content_info": {
                    "id": content_id,
                    "title": content.title,
                    "created_at": content.created_at.isoformat(),
                    "campaign_id": str(content.campaign_id),
                    "content_type": content.content_type
                }
            })
            
            logger.debug(f"✅ Analytics retrieved for content {content_id}")
            return analytics_data
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Analytics retrieval failed: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analytics retrieval failed: {str(e)}"
            )

@router.get("/landing-pages/{content_id}/")
async def get_landing_page(
    content_id: str,
    db: AsyncSession = Depends(get_async_db),
    user_data: tuple = Depends(get_user_and_company)
):
    """Get a specific landing page by ID"""
    
    try:
        user, company = user_data
        
        # Get the landing page
        content = await db.get(GeneratedContent, content_id)
        if not content or content.company_id != company.id or content.content_type != "landing_page":
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Landing page not found"
            )
        
        return {
            "success": True,
            "id": str(content.id),
            "title": content.title,
            "html_code": content.content,
            "campaign_id": str(content.campaign_id) if content.campaign_id else None,
            "created_at": content.created_at.isoformat(),
            "updated_at": content.updated_at.isoformat(),
            "metadata": content.metadata,
            "status": content.analysis_status,
            "analytics_url": f"/api/landing-pages/{content.id}/analytics/",
            "tracking_url": f"/api/landing-pages/{content.id}/track-event/"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Landing page retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Landing page retrieval failed: {str(e)}"
        )