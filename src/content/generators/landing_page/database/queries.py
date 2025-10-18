"""
Common Database Queries
Predefined queries for landing page analytics and reporting.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_, String

from .models import (
    LandingPageComponent,
    LandingPageTemplate,
    LandingPageVariant,
    LandingPageAnalytics,
    ConversionEvent,
    GeneratedContent,
    Campaign
)

logger = logging.getLogger(__name__)

class LandingPageQueries:
    """Common database queries for landing page system"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_top_performing_pages(
        self, 
        company_id: UUID, 
        limit: int = 10,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get top performing landing pages by conversion rate"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        results = self.db.query(
            GeneratedContent.id,
            GeneratedContent.content_title,
            func.avg(LandingPageAnalytics.conversion_rate).label('avg_conversion_rate'),
            func.sum(LandingPageAnalytics.page_views).label('total_views'),
            func.sum(LandingPageAnalytics.conversions).label('total_conversions')
        )\
        .join(LandingPageAnalytics, GeneratedContent.id == LandingPageAnalytics.content_id)\
        .filter(GeneratedContent.company_id == company_id)\
        .filter(LandingPageAnalytics.created_at >= cutoff_date)\
        .group_by(GeneratedContent.id, GeneratedContent.content_title)\
        .order_by(desc('avg_conversion_rate'))\
        .limit(limit)\
        .all()
        
        return [
            {
                'content_id': str(result.id),
                'title': result.content_title,
                'conversion_rate': float(result.avg_conversion_rate or 0),
                'total_views': result.total_views or 0,
                'total_conversions': result.total_conversions or 0
            }
            for result in results
        ]
    
    def get_variant_performance_comparison(
        self, 
        parent_content_id: UUID,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Compare performance of all variants for a landing page"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get control (original) performance
        control_analytics = self.db.query(LandingPageAnalytics)\
            .filter(LandingPageAnalytics.content_id == parent_content_id)\
            .filter(LandingPageAnalytics.variant_id.is_(None))\
            .filter(LandingPageAnalytics.created_at >= cutoff_date)\
            .all()
        
        control_performance = self._aggregate_analytics(control_analytics)
        control_performance['variant_name'] = 'Control (Original)'
        control_performance['variant_id'] = None
        
        # Get variant performances
        variants = self.db.query(LandingPageVariant)\
            .filter(LandingPageVariant.parent_content_id == parent_content_id)\
            .filter(LandingPageVariant.is_active == True)\
            .all()
        
        variant_performances = [control_performance]
        
        for variant in variants:
            variant_analytics = self.db.query(LandingPageAnalytics)\
                .filter(LandingPageAnalytics.variant_id == variant.id)\
                .filter(LandingPageAnalytics.created_at >= cutoff_date)\
                .all()
            
            performance = self._aggregate_analytics(variant_analytics)
            performance['variant_name'] = variant.variant_name
            performance['variant_id'] = str(variant.id)
            performance['variant_type'] = variant.variant_type
            performance['test_hypothesis'] = variant.test_hypothesis
            
            variant_performances.append(performance)
        
        return variant_performances
    
    def get_conversion_funnel_analysis(
        self, 
        content_id: UUID,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Analyze conversion funnel for a landing page"""
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Get conversion events
        events = self.db.query(ConversionEvent)\
            .filter(ConversionEvent.content_id == content_id)\
            .filter(ConversionEvent.created_at >= cutoff_time)\
            .all()
        
        # Analyze funnel steps
        funnel_data = {
            'page_loads': 0,
            'scroll_25': 0,
            'scroll_50': 0,
            'scroll_75': 0,
            'cta_clicks': 0,
            'form_starts': 0,
            'form_completions': 0,
            'total_sessions': 0
        }
        
        sessions = set()
        
        for event in events:
            if event.session_id:
                sessions.add(event.session_id)
            
            event_type = event.event_type.lower() if event.event_type else ''
            
            if event_type in ['page_view', 'page_load']:
                funnel_data['page_loads'] += 1
            elif event_type == 'scroll_depth' and event.event_data:
                depth = event.event_data.get('scroll_percentage', 0)
                if depth >= 75:
                    funnel_data['scroll_75'] += 1
                elif depth >= 50:
                    funnel_data['scroll_50'] += 1
                elif depth >= 25:
                    funnel_data['scroll_25'] += 1
            elif event_type == 'cta_click':
                funnel_data['cta_clicks'] += 1
            elif event_type == 'form_start':
                funnel_data['form_starts'] += 1
            elif event_type in ['form_submit', 'form_complete']:
                funnel_data['form_completions'] += 1
        
        funnel_data['total_sessions'] = len(sessions)
        
        # Calculate conversion rates
        funnel_rates = {}
        if funnel_data['page_loads'] > 0:
            funnel_rates['scroll_25_rate'] = (funnel_data['scroll_25'] / funnel_data['page_loads']) * 100
            funnel_rates['scroll_50_rate'] = (funnel_data['scroll_50'] / funnel_data['page_loads']) * 100
            funnel_rates['scroll_75_rate'] = (funnel_data['scroll_75'] / funnel_data['page_loads']) * 100
            funnel_rates['cta_click_rate'] = (funnel_data['cta_clicks'] / funnel_data['page_loads']) * 100
        
        if funnel_data['form_starts'] > 0:
            funnel_rates['form_completion_rate'] = (funnel_data['form_completions'] / funnel_data['form_starts']) * 100
        
        return {
            'funnel_data': funnel_data,
            'conversion_rates': funnel_rates,
            'analysis_period_hours': hours,
            'last_updated': datetime.now()
        }
    
    def get_campaign_landing_page_performance(
        self, 
        campaign_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance summary for all landing pages in a campaign"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get all landing pages for the campaign
        landing_pages = self.db.query(GeneratedContent)\
            .filter(GeneratedContent.campaign_id == campaign_id)\
            .filter(GeneratedContent.content_type == 'LANDING_PAGE')\
            .all()
        
        if not landing_pages:
            return {
                'total_pages': 0,
                'total_views': 0,
                'total_conversions': 0,
                'avg_conversion_rate': 0,
                'best_performing_page': None,
                'page_performances': []
            }
        
        campaign_performance = {
            'total_pages': len(landing_pages),
            'total_views': 0,
            'total_conversions': 0,
            'avg_conversion_rate': 0,
            'best_performing_page': None,
            'page_performances': []
        }
        
        page_performances = []
        
        for page in landing_pages:
            analytics = self.db.query(LandingPageAnalytics)\
                .filter(LandingPageAnalytics.content_id == page.id)\
                .filter(LandingPageAnalytics.created_at >= cutoff_date)\
                .all()
            
            performance = self._aggregate_analytics(analytics)
            performance['page_id'] = str(page.id)
            performance['page_title'] = page.content_title
            
            page_performances.append(performance)
            
            campaign_performance['total_views'] += performance['total_views']
            campaign_performance['total_conversions'] += performance['total_conversions']
        
        # Calculate overall conversion rate
        if campaign_performance['total_views'] > 0:
            campaign_performance['avg_conversion_rate'] = (
                campaign_performance['total_conversions'] / 
                campaign_performance['total_views']
            ) * 100
        
        # Find best performing page
        if page_performances:
            best_page = max(page_performances, key=lambda x: x['conversion_rate'])
            campaign_performance['best_performing_page'] = best_page
        
        campaign_performance['page_performances'] = page_performances
        
        return campaign_performance
    
    def get_template_usage_stats(self, company_id: Optional[UUID] = None) -> List[Dict[str, Any]]:
        """Get template usage statistics"""
        
        query = self.db.query(
            LandingPageTemplate.id,
            LandingPageTemplate.template_name,
            LandingPageTemplate.template_type,
            LandingPageTemplate.industry_niche,
            LandingPageTemplate.usage_count,
            func.avg(LandingPageAnalytics.conversion_rate).label('avg_conversion_rate')
        )\
        .outerjoin(
            GeneratedContent, 
            GeneratedContent.landing_page_metadata['template_id'].astext == func.cast(LandingPageTemplate.id, String)
        )\
        .outerjoin(LandingPageAnalytics, LandingPageAnalytics.content_id == GeneratedContent.id)
        
        if company_id:
            query = query.filter(GeneratedContent.company_id == company_id)
        
        results = query.group_by(
            LandingPageTemplate.id,
            LandingPageTemplate.template_name,
            LandingPageTemplate.template_type,
            LandingPageTemplate.industry_niche,
            LandingPageTemplate.usage_count
        )\
        .order_by(desc(LandingPageTemplate.usage_count))\
        .all()
        
        return [
            {
                'template_id': str(result.id),
                'template_name': result.template_name,
                'template_type': result.template_type,
                'industry_niche': result.industry_niche,
                'usage_count': result.usage_count,
                'avg_conversion_rate': float(result.avg_conversion_rate or 0)
            }
            for result in results
        ]
    
    def get_real_time_events(
        self,
        content_id: UUID,
        minutes: int = 60
    ) -> List[Dict[str, Any]]:
        """Get recent conversion events for real-time monitoring"""
        
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        events = self.db.query(ConversionEvent)\
            .filter(ConversionEvent.content_id == content_id)\
            .filter(ConversionEvent.created_at >= cutoff_time)\
            .order_by(desc(ConversionEvent.created_at))\
            .limit(100)\
            .all()
        
        return [
            {
                'event_id': str(event.id),
                'event_type': event.event_type,
                'event_data': event.event_data,
                'session_id': event.session_id,
                'created_at': event.created_at.isoformat(),
                'device_info': event.device_info
            }
            for event in events
        ]
    
    def get_top_exit_points(
        self,
        content_id: UUID,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Identify where users are exiting the page most frequently"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get scroll depth events to identify exit points
        scroll_events = self.db.query(ConversionEvent)\
            .filter(ConversionEvent.content_id == content_id)\
            .filter(ConversionEvent.event_type == 'scroll_depth')\
            .filter(ConversionEvent.created_at >= cutoff_date)\
            .all()
        
        # Group by scroll percentage ranges
        exit_ranges = {
            '0-25%': 0,
            '25-50%': 0,
            '50-75%': 0,
            '75-100%': 0
        }
        
        for event in scroll_events:
            if event.event_data and 'scroll_percentage' in event.event_data:
                percentage = event.event_data['scroll_percentage']
                
                if percentage < 25:
                    exit_ranges['0-25%'] += 1
                elif percentage < 50:
                    exit_ranges['25-50%'] += 1
                elif percentage < 75:
                    exit_ranges['50-75%'] += 1
                else:
                    exit_ranges['75-100%'] += 1
        
        # Convert to list and sort by frequency
        exit_points = [
            {'range': range_name, 'exits': count}
            for range_name, count in exit_ranges.items()
        ]
        
        exit_points.sort(key=lambda x: x['exits'], reverse=True)
        
        return exit_points
    
    def get_device_performance_breakdown(
        self,
        content_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance breakdown by device type"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        analytics = self.db.query(LandingPageAnalytics)\
            .filter(LandingPageAnalytics.content_id == content_id)\
            .filter(LandingPageAnalytics.created_at >= cutoff_date)\
            .all()
        
        device_breakdown = {}
        
        for record in analytics:
            if record.device_breakdown:
                for device_type, count in record.device_breakdown.items():
                    if device_type not in device_breakdown:
                        device_breakdown[device_type] = {
                            'views': 0,
                            'conversions': 0,
                            'conversion_rate': 0
                        }
                    
                    device_breakdown[device_type]['views'] += count
                    
                    # Estimate conversions by device (simplified)
                    device_conversion_rate = record.conversion_rate or 0
                    device_conversions = (count * device_conversion_rate / 100)
                    device_breakdown[device_type]['conversions'] += device_conversions
        
        # Calculate conversion rates for each device
        for device_type, data in device_breakdown.items():
            if data['views'] > 0:
                data['conversion_rate'] = (data['conversions'] / data['views']) * 100
            else:
                data['conversion_rate'] = 0
        
        return device_breakdown
    
    def get_traffic_source_performance(
        self,
        content_id: UUID,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get performance breakdown by traffic source"""
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        analytics = self.db.query(LandingPageAnalytics)\
            .filter(LandingPageAnalytics.content_id == content_id)\
            .filter(LandingPageAnalytics.created_at >= cutoff_date)\
            .all()
        
        source_breakdown = {}
        
        for record in analytics:
            if record.traffic_sources:
                for source, count in record.traffic_sources.items():
                    if source not in source_breakdown:
                        source_breakdown[source] = {
                            'views': 0,
                            'conversions': 0,
                            'conversion_rate': 0
                        }
                    
                    source_breakdown[source]['views'] += count
                    
                    # Estimate conversions by source (simplified)
                    source_conversion_rate = record.conversion_rate or 0
                    source_conversions = (count * source_conversion_rate / 100)
                    source_breakdown[source]['conversions'] += source_conversions
        
        # Calculate conversion rates for each source
        for source, data in source_breakdown.items():
            if data['views'] > 0:
                data['conversion_rate'] = (data['conversions'] / data['views']) * 100
            else:
                data['conversion_rate'] = 0
        
        return source_breakdown
    
    def _aggregate_analytics(self, analytics: List[LandingPageAnalytics]) -> Dict[str, Any]:
        """Aggregate analytics data from multiple records"""
        
        if not analytics:
            return {
                'total_views': 0,
                'total_conversions': 0,
                'conversion_rate': 0.0,
                'avg_time_on_page': 0,
                'bounce_rate': 0.0,
                'cta_clicks': 0,
                'form_completion_rate': 0.0
            }
        
        total_views = sum(a.page_views for a in analytics)
        total_conversions = sum(a.conversions for a in analytics)
        conversion_rate = (total_conversions / total_views * 100) if total_views > 0 else 0
        
        total_form_starts = sum(a.form_starts for a in analytics)
        total_form_completions = sum(a.form_completions for a in analytics)
        form_completion_rate = (total_form_completions / total_form_starts * 100) if total_form_starts > 0 else 0
        
        return {
            'total_views': total_views,
            'total_conversions': total_conversions,
            'conversion_rate': round(conversion_rate, 2),
            'avg_time_on_page': sum(a.avg_time_on_page or 0 for a in analytics) / len(analytics),
            'bounce_rate': round(sum(a.bounce_rate or 0 for a in analytics) / len(analytics), 2),
            'cta_clicks': sum(a.cta_clicks for a in analytics),
            'form_completion_rate': round(form_completion_rate, 2)
        }

# Additional utility queries

def get_winning_variants(db_session: Session, days: int = 30) -> List[Dict[str, Any]]:
    """Get all variants that are currently winning their A/B tests"""
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    winning_variants = db_session.query(LandingPageVariant)\
        .filter(LandingPageVariant.is_winning_variant == True)\
        .filter(LandingPageVariant.is_active == True)\
        .all()
    
    results = []
    
    for variant in winning_variants:
        # Get performance data
        analytics = db_session.query(LandingPageAnalytics)\
            .filter(LandingPageAnalytics.variant_id == variant.id)\
            .filter(LandingPageAnalytics.created_at >= cutoff_date)\
            .all()
        
        if analytics:
            total_views = sum(a.page_views for a in analytics)
            total_conversions = sum(a.conversions for a in analytics)
            conversion_rate = (total_conversions / total_views * 100) if total_views > 0 else 0
            
            results.append({
                'variant_id': str(variant.id),
                'variant_name': variant.variant_name,
                'variant_type': variant.variant_type,
                'parent_content_id': str(variant.parent_content_id),
                'test_hypothesis': variant.test_hypothesis,
                'expected_improvement': variant.expected_improvement,
                'actual_conversion_rate': round(conversion_rate, 2),
                'total_views': total_views,
                'total_conversions': total_conversions
            })
    
    return results

def get_underperforming_pages(
    db_session: Session, 
    company_id: UUID, 
    threshold_conversion_rate: float = 2.0,
    days: int = 30
) -> List[Dict[str, Any]]:
    """Get landing pages with conversion rates below threshold"""
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    results = db_session.query(
        GeneratedContent.id,
        GeneratedContent.content_title,
        func.avg(LandingPageAnalytics.conversion_rate).label('avg_conversion_rate'),
        func.sum(LandingPageAnalytics.page_views).label('total_views')
    )\
    .join(LandingPageAnalytics, GeneratedContent.id == LandingPageAnalytics.content_id)\
    .filter(GeneratedContent.company_id == company_id)\
    .filter(GeneratedContent.content_type == 'LANDING_PAGE')\
    .filter(LandingPageAnalytics.created_at >= cutoff_date)\
    .group_by(GeneratedContent.id, GeneratedContent.content_title)\
    .having(func.avg(LandingPageAnalytics.conversion_rate) < threshold_conversion_rate)\
    .having(func.sum(LandingPageAnalytics.page_views) >= 100)\
    .order_by('avg_conversion_rate')\
    .all()
    
    return [
        {
            'content_id': str(result.id),
            'title': result.content_title,
            'conversion_rate': float(result.avg_conversion_rate or 0),
            'total_views': result.total_views or 0,
            'needs_optimization': True
        }
        for result in results
    ]

# Export the main class and utility functions
__all__ = [
    'LandingPageQueries',
    'get_winning_variants',
    'get_underperforming_pages'
]