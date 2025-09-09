"""
Landing Page Storage Operations
Handles database operations for landing page components and analytics.
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from .models import (
    LandingPageComponent,
    LandingPageTemplate, 
    LandingPageVariant,
    LandingPageAnalytics,
    ConversionEvent,
    GeneratedContent
)

logger = logging.getLogger(__name__)

class LandingPageStorage:
    """Handles all database operations for landing page system"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    # Component Operations
    def save_page_components(
        self, 
        content_id: UUID, 
        components: List[Dict[str, Any]]
    ) -> List[LandingPageComponent]:
        """Save landing page components to database"""
        
        try:
            saved_components = []
            
            for component_data in components:
                component = LandingPageComponent(
                    generated_content_id=content_id,
                    component_type=component_data['type'],
                    component_order=component_data['order'],
                    component_data=component_data['data'],
                    styling_data=component_data.get('styling', {}),
                    conversion_elements=component_data.get('conversion_elements', {}),
                    is_active=True
                )
                
                self.db.add(component)
                saved_components.append(component)
            
            self.db.commit()
            logger.info(f"✅ Saved {len(saved_components)} components for content {content_id}")
            return saved_components
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save components: {str(e)}")
            raise
    
    def get_page_components(self, content_id: UUID) -> List[LandingPageComponent]:
        """Get all components for a landing page"""
        
        return self.db.query(LandingPageComponent)\
            .filter(LandingPageComponent.generated_content_id == content_id)\
            .filter(LandingPageComponent.is_active == True)\
            .order_by(LandingPageComponent.component_order)\
            .all()
    
    # Template Operations
    def save_template(self, template_data: Dict[str, Any]) -> LandingPageTemplate:
        """Save a new template"""
        
        try:
            template = LandingPageTemplate(
                template_name=template_data['name'],
                template_type=template_data['type'],
                industry_niche=template_data.get('niche'),
                template_structure=template_data['structure'],
                default_styling=template_data.get('styling', {}),
                conversion_elements=template_data.get('conversion_elements', {}),
                is_premium=template_data.get('is_premium', False),
                created_by=template_data.get('created_by', 'system')
            )
            
            self.db.add(template)
            self.db.commit()
            
            logger.info(f"✅ Saved template: {template.template_name}")
            return template
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save template: {str(e)}")
            raise
    
    def get_templates_by_type(self, template_type: str, niche: Optional[str] = None) -> List[LandingPageTemplate]:
        """Get templates by type and optionally by niche"""
        
        query = self.db.query(LandingPageTemplate)\
            .filter(LandingPageTemplate.template_type == template_type)
        
        if niche:
            query = query.filter(
                or_(
                    LandingPageTemplate.industry_niche == niche,
                    LandingPageTemplate.industry_niche == 'generic'
                )
            )
        
        return query.order_by(desc(LandingPageTemplate.usage_count)).all()
    
    def get_best_performing_template(self, template_type: str, niche: str) -> Optional[LandingPageTemplate]:
        """Get the best performing template for a type and niche"""
        
        return self.db.query(LandingPageTemplate)\
            .filter(LandingPageTemplate.template_type == template_type)\
            .filter(
                or_(
                    LandingPageTemplate.industry_niche == niche,
                    LandingPageTemplate.industry_niche == 'generic'
                )
            )\
            .order_by(desc(LandingPageTemplate.usage_count))\
            .first()
    
    # Variant Operations
    def save_page_variants(
        self, 
        parent_content_id: UUID, 
        variants: List[Dict[str, Any]]
    ) -> List[LandingPageVariant]:
        """Save A/B test variants"""
        
        try:
            saved_variants = []
            variant_group_id = uuid4()
            
            for variant_data in variants:
                variant = LandingPageVariant(
                    parent_content_id=parent_content_id,
                    variant_group_id=variant_group_id,
                    variant_name=variant_data['name'],
                    variant_type=variant_data['type'],
                    html_content=variant_data['html_content'],
                    test_hypothesis=variant_data.get('test_hypothesis'),
                    expected_improvement=variant_data.get('expected_improvement'),
                    test_configuration=variant_data.get('test_config', {}),
                    is_active=True
                )
                
                self.db.add(variant)
                saved_variants.append(variant)
            
            self.db.commit()
            logger.info(f"✅ Saved {len(saved_variants)} variants for content {parent_content_id}")
            return saved_variants
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save variants: {str(e)}")
            raise
    
    def get_page_variants(self, parent_content_id: UUID) -> List[LandingPageVariant]:
        """Get all variants for a landing page"""
        
        return self.db.query(LandingPageVariant)\
            .filter(LandingPageVariant.parent_content_id == parent_content_id)\
            .filter(LandingPageVariant.is_active == True)\
            .order_by(LandingPageVariant.created_at)\
            .all()
    
    def update_variant_performance(
        self, 
        variant_id: UUID, 
        performance_data: Dict[str, Any]
    ) -> bool:
        """Update variant performance data"""
        
        try:
            variant = self.db.query(LandingPageVariant)\
                .filter(LandingPageVariant.id == variant_id)\
                .first()
            
            if variant:
                variant.performance_data = performance_data
                self.db.commit()
                return True
            return False
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update variant performance: {str(e)}")
            return False
    
    # Analytics Operations
    def save_analytics_data(
        self, 
        content_id: UUID, 
        analytics_data: Dict[str, Any],
        variant_id: Optional[UUID] = None
    ) -> LandingPageAnalytics:
        """Save analytics data for a landing page"""
        
        try:
            analytics = LandingPageAnalytics(
                content_id=content_id,
                variant_id=variant_id,
                page_views=analytics_data.get('page_views', 0),
                unique_visitors=analytics_data.get('unique_visitors', 0),
                returning_visitors=analytics_data.get('returning_visitors', 0),
                avg_time_on_page=analytics_data.get('avg_time_on_page'),
                bounce_rate=analytics_data.get('bounce_rate'),
                scroll_depth_avg=analytics_data.get('scroll_depth_avg'),
                exit_rate=analytics_data.get('exit_rate'),
                conversions=analytics_data.get('conversions', 0),
                conversion_rate=analytics_data.get('conversion_rate'),
                cta_clicks=analytics_data.get('cta_clicks', 0),
                form_starts=analytics_data.get('form_starts', 0),
                form_completions=analytics_data.get('form_completions', 0),
                device_breakdown=analytics_data.get('device_breakdown', {}),
                traffic_sources=analytics_data.get('traffic_sources', {}),
                geographic_data=analytics_data.get('geographic_data', {}),
                conversion_events=analytics_data.get('conversion_events', {}),
                user_behavior_data=analytics_data.get('user_behavior_data', {})
            )
            
            self.db.add(analytics)
            self.db.commit()
            
            logger.info(f"✅ Saved analytics for content {content_id}")
            return analytics
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save analytics: {str(e)}")
            raise
    
    def get_analytics_summary(
        self, 
        content_id: UUID, 
        days: int = 30
    ) -> Dict[str, Any]:
        """Get analytics summary for a landing page"""
        
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        analytics = self.db.query(LandingPageAnalytics)\
            .filter(LandingPageAnalytics.content_id == content_id)\
            .filter(LandingPageAnalytics.created_at >= cutoff_date)\
            .all()
        
        if not analytics:
            return {}
        
        # Aggregate analytics data
        total_views = sum(a.page_views for a in analytics)
        total_conversions = sum(a.conversions for a in analytics)
        avg_conversion_rate = (total_conversions / total_views * 100) if total_views > 0 else 0
        
        return {
            'total_page_views': total_views,
            'total_conversions': total_conversions,
            'conversion_rate': round(avg_conversion_rate, 2),
            'avg_time_on_page': sum(a.avg_time_on_page or 0 for a in analytics) / len(analytics),
            'bounce_rate': sum(a.bounce_rate or 0 for a in analytics) / len(analytics),
            'total_cta_clicks': sum(a.cta_clicks for a in analytics),
            'form_completion_rate': self._calculate_form_completion_rate(analytics),
            'period_days': days,
            'last_updated': max(a.created_at for a in analytics)
        }
    
    def _calculate_form_completion_rate(self, analytics: List[LandingPageAnalytics]) -> float:
        """Calculate form completion rate from analytics data"""
        
        total_starts = sum(a.form_starts for a in analytics)
        total_completions = sum(a.form_completions for a in analytics)
        
        if total_starts > 0:
            return round((total_completions / total_starts) * 100, 2)
        return 0.0
    
    # Conversion Event Operations
    def save_conversion_event(
        self, 
        content_id: UUID, 
        event_data: Dict[str, Any],
        variant_id: Optional[UUID] = None
    ) -> ConversionEvent:
        """Save individual conversion event"""
        
        try:
            event = ConversionEvent(
                content_id=content_id,
                variant_id=variant_id,
                event_type=event_data['event_type'],
                event_data=event_data.get('data', {}),
                session_id=event_data.get('session_id'),
                user_fingerprint=event_data.get('user_fingerprint'),
                ip_address=event_data.get('ip_address'),
                user_agent=event_data.get('user_agent'),
                referrer=event_data.get('referrer'),
                landing_url=event_data.get('landing_url'),
                device_info=event_data.get('device_info', {}),
                page_load_time=event_data.get('page_load_time'),
                timestamp_ms=event_data.get('timestamp_ms')
            )
            
            self.db.add(event)
            self.db.commit()
            
            return event
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save conversion event: {str(e)}")
            raise
    
    def get_conversion_events(
        self, 
        content_id: UUID, 
        event_types: Optional[List[str]] = None,
        hours: int = 24
    ) -> List[ConversionEvent]:
        """Get conversion events for analysis"""
        
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        query = self.db.query(ConversionEvent)\
            .filter(ConversionEvent.content_id == content_id)\
            .filter(ConversionEvent.created_at >= cutoff_time)
        
        if event_types:
            query = query.filter(ConversionEvent.event_type.in_(event_types))
        
        return query.order_by(desc(ConversionEvent.created_at)).all()