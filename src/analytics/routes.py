# src/analytics/routes.py
"""
Analytics Routes - Advanced analytics and reporting endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from src.core.database import get_db
from src.auth.dependencies import get_current_user_with_company
from src.models import User, Company, GeneratedContent, Campaign
from src.intelligence.generators.landing_page.analytics.tracker import AnalyticsTracker

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/analytics/top-performing/")
async def get_top_performing_pages(
    db: AsyncSession = Depends(get_db),
    user_data: tuple = Depends(get_current_user_with_company),
    limit: int = 10,
    time_window_days: int = 30
):
    """
    Get top-performing landing pages by conversion rate
    
    Query parameters:
    - limit: Number of pages to return (default: 10)
    - time_window_days: Time window for analytics (default: 30 days)
    """
    
    try:
        user, company = user_data
        
        # Get company's landing pages
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        
        query = select(GeneratedContent).where(
            and_(
                GeneratedContent.company_id == company.id,
                GeneratedContent.content_type == "landing_page",
                GeneratedContent.created_at >= cutoff_date
            )
        ).order_by(desc(GeneratedContent.created_at)).limit(limit * 2)  # Get more to filter
        
        result = await db.execute(query)
        landing_pages = result.scalars().all()
        
        # Get analytics for each page
        tracker = AnalyticsTracker(db)
        performance_data = []
        
        for page in landing_pages:
            analytics = await tracker.get_real_time_analytics(
                content_id=str(page.id),
                time_window_hours=time_window_days * 24
            )
            
            conversion_rate = analytics.get('conversion_metrics', {}).get('conversion_rate', 0)
            page_views = analytics.get('traffic_metrics', {}).get('page_views', 0)
            
            # Only include pages with some traffic
            if page_views > 0:
                performance_data.append({
                    "id": str(page.id),
                    "title": page.title,
                    "campaign_id": str(page.campaign_id) if page.campaign_id else None,
                    "created_at": page.created_at.isoformat(),
                    "conversion_rate": conversion_rate,
                    "page_views": page_views,
                    "conversions": analytics.get('conversion_metrics', {}).get('conversions', 0),
                    "cta_click_rate": analytics.get('engagement_metrics', {}).get('cta_click_rate', 0),
                    "performance_score": analytics.get('conversion_metrics', {}).get('conversion_rate', 0) * 10,
                    "analytics_url": f"/api/landing-pages/{page.id}/analytics/"
                })
        
        # Sort by conversion rate and limit results
        performance_data.sort(key=lambda x: x['conversion_rate'], reverse=True)
        top_performing = performance_data[:limit]
        
        return {
            "success": True,
            "time_window_days": time_window_days,
            "top_performing_pages": top_performing,
            "total_analyzed": len(performance_data),
            "company_analytics_summary": {
                "total_pages": len(landing_pages),
                "avg_conversion_rate": sum(p['conversion_rate'] for p in performance_data) / len(performance_data) if performance_data else 0,
                "total_page_views": sum(p['page_views'] for p in performance_data),
                "total_conversions": sum(p['conversions'] for p in performance_data)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Top performing pages retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Top performing pages retrieval failed: {str(e)}"
        )

@router.get("/analytics/campaign/{campaign_id}/performance/")
async def get_campaign_performance(
    campaign_id: str,
    db: AsyncSession = Depends(get_db),
    user_data: tuple = Depends(get_current_user_with_company),
    time_window_days: int = 30
):
    """
    Get comprehensive performance analytics for a specific campaign
    
    Query parameters:
    - time_window_days: Time window for analytics (default: 30 days)
    """
    
    try:
        user, company = user_data
        
        # Verify campaign ownership
        campaign = await db.get(Campaign, campaign_id)
        if not campaign or campaign.company_id != company.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        # Get all landing pages for this campaign
        query = select(GeneratedContent).where(
            and_(
                GeneratedContent.campaign_id == campaign_id,
                GeneratedContent.content_type == "landing_page"
            )
        ).order_by(desc(GeneratedContent.created_at))
        
        result = await db.execute(query)
        landing_pages = result.scalars().all()
        
        if not landing_pages:
            return {
                "success": True,
                "campaign_info": {
                    "id": campaign_id,
                    "name": campaign.name,
                    "created_at": campaign.created_at.isoformat()
                },
                "message": "No landing pages found for this campaign",
                "landing_pages": []
            }
        
        # Get analytics for each landing page
        tracker = AnalyticsTracker(db)
        campaign_analytics = []
        total_metrics = {
            "page_views": 0,
            "conversions": 0,
            "cta_clicks": 0,
            "unique_sessions": 0
        }
        
        for page in landing_pages:
            analytics = await tracker.get_real_time_analytics(
                content_id=str(page.id),
                time_window_hours=time_window_days * 24
            )
            
            page_analytics = {
                "id": str(page.id),
                "title": page.title,
                "created_at": page.created_at.isoformat(),
                "traffic_metrics": analytics.get('traffic_metrics', {}),
                "engagement_metrics": analytics.get('engagement_metrics', {}),
                "conversion_metrics": analytics.get('conversion_metrics', {}),
                "device_breakdown": analytics.get('device_breakdown', {}),
                "traffic_sources": analytics.get('traffic_sources', {}),
                "performance_score": analytics.get('conversion_metrics', {}).get('conversion_rate', 0) * 10
            }
            
            campaign_analytics.append(page_analytics)
            
            # Aggregate totals
            traffic = analytics.get('traffic_metrics', {})
            conversion = analytics.get('conversion_metrics', {})
            engagement = analytics.get('engagement_metrics', {})
            
            total_metrics["page_views"] += traffic.get('page_views', 0)
            total_metrics["conversions"] += conversion.get('conversions', 0)
            total_metrics["cta_clicks"] += engagement.get('cta_clicks', 0)
            total_metrics["unique_sessions"] += traffic.get('unique_sessions', 0)
        
        # Calculate campaign-level metrics
        campaign_conversion_rate = (total_metrics["conversions"] / total_metrics["page_views"] * 100) if total_metrics["page_views"] > 0 else 0
        campaign_cta_rate = (total_metrics["cta_clicks"] / total_metrics["page_views"] * 100) if total_metrics["page_views"] > 0 else 0
        
        return {
            "success": True,
            "time_window_days": time_window_days,
            "campaign_info": {
                "id": campaign_id,
                "name": campaign.name,
                "description": campaign.description,
                "target_audience": campaign.target_audience,
                "created_at": campaign.created_at.isoformat()
            },
            "campaign_summary": {
                "total_landing_pages": len(landing_pages),
                "total_page_views": total_metrics["page_views"],
                "total_conversions": total_metrics["conversions"],
                "total_cta_clicks": total_metrics["cta_clicks"],
                "unique_sessions": total_metrics["unique_sessions"],
                "campaign_conversion_rate": round(campaign_conversion_rate, 2),
                "campaign_cta_rate": round(campaign_cta_rate, 2),
                "avg_performance_score": sum(p['performance_score'] for p in campaign_analytics) / len(campaign_analytics) if campaign_analytics else 0
            },
            "landing_pages_performance": campaign_analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Campaign performance retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Campaign performance retrieval failed: {str(e)}"
        )

@router.get("/analytics/funnel/{content_id}/")
async def get_conversion_funnel(
    content_id: str,
    db: AsyncSession = Depends(get_db),
    user_data: tuple = Depends(get_current_user_with_company),
    time_window_hours: int = 24
):
    """
    Get conversion funnel analysis for a specific landing page
    
    Query parameters:
    - time_window_hours: Time window for funnel analysis (default: 24 hours)
    """
    
    try:
        user, company = user_data
        
        # Verify content ownership
        content = await db.get(GeneratedContent, content_id)
        if not content or content.company_id != company.id or content.content_type != "landing_page":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Landing page not found"
            )
        
        # Get detailed analytics for funnel analysis
        tracker = AnalyticsTracker(db)
        analytics = await tracker.get_real_time_analytics(
            content_id=content_id,
            time_window_hours=time_window_hours
        )
        
        # Calculate funnel steps
        traffic_metrics = analytics.get('traffic_metrics', {})
        engagement_metrics = analytics.get('engagement_metrics', {})
        conversion_metrics = analytics.get('conversion_metrics', {})
        
        page_views = traffic_metrics.get('page_views', 0)
        cta_clicks = engagement_metrics.get('cta_clicks', 0)
        form_starts = conversion_metrics.get('form_starts', 0)
        form_completions = conversion_metrics.get('form_completions', 0)
        conversions = conversion_metrics.get('conversions', 0)
        
        # Build funnel with drop-off analysis
        funnel_steps = [
            {
                "step": "Page View",
                "count": page_views,
                "percentage": 100.0,
                "drop_off": 0,
                "description": "Users who landed on the page"
            },
            {
                "step": "CTA Click",
                "count": cta_clicks,
                "percentage": (cta_clicks / page_views * 100) if page_views > 0 else 0,
                "drop_off": page_views - cta_clicks,
                "description": "Users who clicked a call-to-action"
            },
            {
                "step": "Form Start",
                "count": form_starts,
                "percentage": (form_starts / page_views * 100) if page_views > 0 else 0,
                "drop_off": cta_clicks - form_starts,
                "description": "Users who started filling a form"
            },
            {
                "step": "Form Complete",
                "count": form_completions,
                "percentage": (form_completions / page_views * 100) if page_views > 0 else 0,
                "drop_off": form_starts - form_completions,
                "description": "Users who completed the form"
            },
            {
                "step": "Conversion",
                "count": conversions,
                "percentage": (conversions / page_views * 100) if page_views > 0 else 0,
                "drop_off": form_completions - conversions,
                "description": "Users who successfully converted"
            }
        ]
        
        # Calculate key insights
        biggest_drop_step = max(funnel_steps[1:], key=lambda x: x['drop_off'])
        conversion_bottleneck = biggest_drop_step['step'] if biggest_drop_step['drop_off'] > 0 else None
        
        return {
            "success": True,
            "content_info": {
                "id": content_id,
                "title": content.title,
                "created_at": content.created_at.isoformat()
            },
            "time_window_hours": time_window_hours,
            "funnel_analysis": {
                "steps": funnel_steps,
                "total_visitors": page_views,
                "total_conversions": conversions,
                "overall_conversion_rate": round((conversions / page_views * 100) if page_views > 0 else 0, 2),
                "conversion_bottleneck": conversion_bottleneck,
                "funnel_efficiency": round((conversions / page_views) if page_views > 0 else 0, 4)
            },
            "optimization_recommendations": [
                {
                    "area": "CTA Optimization",
                    "recommendation": "Improve call-to-action visibility and copy",
                    "priority": "high" if cta_clicks / page_views < 0.15 else "medium"
                },
                {
                    "area": "Form Optimization", 
                    "recommendation": "Simplify form fields and reduce friction",
                    "priority": "high" if form_starts > 0 and form_completions / form_starts < 0.7 else "low"
                },
                {
                    "area": "Page Load Speed",
                    "recommendation": "Optimize page performance for better conversions",
                    "priority": "medium"
                }
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Conversion funnel analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion funnel analysis failed: {str(e)}"
        )

@router.get("/analytics/company/dashboard/")
async def get_company_analytics_dashboard(
    db: AsyncSession = Depends(get_db),
    user_data: tuple = Depends(get_current_user_with_company),
    time_window_days: int = 30
):
    """
    Get comprehensive analytics dashboard for the entire company
    
    Query parameters:
    - time_window_days: Time window for analytics (default: 30 days)
    """
    
    try:
        user, company = user_data
        
        # Get all company landing pages
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        
        query = select(GeneratedContent).where(
            and_(
                GeneratedContent.company_id == company.id,
                GeneratedContent.content_type == "landing_page",
                GeneratedContent.created_at >= cutoff_date
            )
        ).order_by(desc(GeneratedContent.created_at))
        
        result = await db.execute(query)
        landing_pages = result.scalars().all()
        
        if not landing_pages:
            return {
                "success": True,
                "message": "No landing pages found for analytics",
                "dashboard_data": {
                    "summary": {"total_pages": 0, "total_campaigns": 0},
                    "performance": {},
                    "trends": []
                }
            }
        
        # Aggregate analytics across all pages
        tracker = AnalyticsTracker(db)
        
        total_metrics = {
            "page_views": 0,
            "conversions": 0, 
            "cta_clicks": 0,
            "unique_sessions": 0,
            "form_starts": 0,
            "form_completions": 0
        }
        
        device_totals = {"desktop": 0, "mobile": 0, "tablet": 0, "unknown": 0}
        source_totals = {}
        daily_trends = {}
        
        page_performance = []
        
        for page in landing_pages:
            analytics = await tracker.get_real_time_analytics(
                content_id=str(page.id),
                time_window_hours=time_window_days * 24
            )
            
            # Aggregate metrics
            traffic = analytics.get('traffic_metrics', {})
            conversion = analytics.get('conversion_metrics', {})
            engagement = analytics.get('engagement_metrics', {})
            
            page_views = traffic.get('page_views', 0)
            conversions = conversion.get('conversions', 0)
            
            total_metrics["page_views"] += page_views
            total_metrics["conversions"] += conversions
            total_metrics["cta_clicks"] += engagement.get('cta_clicks', 0)
            total_metrics["unique_sessions"] += traffic.get('unique_sessions', 0)
            total_metrics["form_starts"] += conversion.get('form_starts', 0)
            total_metrics["form_completions"] += conversion.get('form_completions', 0)
            
            # Aggregate device data
            devices = analytics.get('device_breakdown', {})
            for device, count in devices.items():
                device_totals[device] = device_totals.get(device, 0) + count
            
            # Aggregate traffic sources
            sources = analytics.get('traffic_sources', {})
            for source, count in sources.items():
                source_totals[source] = source_totals.get(source, 0) + count
            
            # Track page performance
            conversion_rate = (conversions / page_views * 100) if page_views > 0 else 0
            page_performance.append({
                "id": str(page.id),
                "title": page.title,
                "page_views": page_views,
                "conversion_rate": conversion_rate,
                "created_at": page.created_at.isoformat()
            })
        
        # Calculate company-level metrics
        overall_conversion_rate = (total_metrics["conversions"] / total_metrics["page_views"] * 100) if total_metrics["page_views"] > 0 else 0
        overall_cta_rate = (total_metrics["cta_clicks"] / total_metrics["page_views"] * 100) if total_metrics["page_views"] > 0 else 0
        form_completion_rate = (total_metrics["form_completions"] / total_metrics["form_starts"] * 100) if total_metrics["form_starts"] > 0 else 0
        
        # Get unique campaigns
        campaign_ids = set(str(page.campaign_id) for page in landing_pages if page.campaign_id)
        
        return {
            "success": True,
            "time_window_days": time_window_days,
            "company_info": {
                "name": company.company_name,
                "industry": company.industry,
                "subscription_tier": company.subscription_tier
            },
            "dashboard_summary": {
                "total_landing_pages": len(landing_pages),
                "total_campaigns": len(campaign_ids),
                "total_page_views": total_metrics["page_views"],
                "total_conversions": total_metrics["conversions"],
                "total_unique_sessions": total_metrics["unique_sessions"],
                "overall_conversion_rate": round(overall_conversion_rate, 2),
                "overall_cta_rate": round(overall_cta_rate, 2),
                "form_completion_rate": round(form_completion_rate, 2)
            },
            "performance_breakdown": {
                "device_distribution": device_totals,
                "traffic_sources": source_totals,
                "top_performing_pages": sorted(page_performance, key=lambda x: x['conversion_rate'], reverse=True)[:5]
            },
            "insights": {
                "best_performing_page": max(page_performance, key=lambda x: x['conversion_rate']) if page_performance else None,
                "avg_conversion_rate": sum(p['conversion_rate'] for p in page_performance) / len(page_performance) if page_performance else 0,
                "total_revenue_potential": total_metrics["conversions"] * 100  # Placeholder calculation
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Company dashboard retrieval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Company dashboard retrieval failed: {str(e)}"
        )