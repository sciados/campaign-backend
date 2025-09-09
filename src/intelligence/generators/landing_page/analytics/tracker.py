# src/intelligence/generators/landing_page/analytics/tracker.py
"""
Analytics tracking implementation for landing pages.
Handles real-time event tracking, conversion monitoring, and performance metrics.
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from ..database.models import (
    LandingPageAnalytics, ConversionEvent, GeneratedContent, 
    LandingPageVariant, LandingPageComponent
)
from .events import EventType, ConversionEventData, AnalyticsEventData
from .performance import PerformanceCalculator

logger = logging.getLogger(__name__)

class AnalyticsTracker:
    """
    Real-time analytics tracker for landing pages.
    
    Tracks user behavior, conversions, and performance metrics
    with real-time processing and aggregation.
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.performance_calculator = PerformanceCalculator()
        self._event_queue = asyncio.Queue()
        self._processing_task = None
        
        logger.info("✅ Analytics Tracker initialized")
    
    async def track_event(
        self,
        content_id: str,
        event_type: EventType,
        event_data: Dict[str, Any],
        session_info: Optional[Dict[str, Any]] = None,
        variant_id: Optional[str] = None
    ) -> bool:
        """
        Track a user event on a landing page
        
        Args:
            content_id: ID of the landing page content
            event_type: Type of event being tracked
            event_data: Event-specific data
            session_info: User session information
            variant_id: A/B test variant ID (if applicable)
            
        Returns:
            bool: Success status
        """
        
        try:
            # Create conversion event record
            conversion_event = ConversionEvent(
                content_id=content_id,
                variant_id=variant_id,
                event_type=event_type.value,
                event_data=event_data,
                session_id=session_info.get('session_id') if session_info else None,
                user_fingerprint=session_info.get('user_fingerprint') if session_info else None,
                ip_address=session_info.get('ip_address') if session_info else None,
                user_agent=session_info.get('user_agent') if session_info else None,
                referrer=session_info.get('referrer') if session_info else None,
                landing_url=session_info.get('landing_url') if session_info else None,
                device_info=session_info.get('device_info', {}) if session_info else {},
                page_load_time=event_data.get('page_load_time'),
                timestamp_ms=int(datetime.now().timestamp() * 1000)
            )
            
            self.db.add(conversion_event)
            await self.db.commit()
            
            # Queue for real-time processing
            await self._event_queue.put({
                'content_id': content_id,
                'variant_id': variant_id,
                'event_type': event_type,
                'event_data': event_data,
                'timestamp': datetime.now()
            })
            
            logger.debug(f"✅ Event tracked: {event_type.value} for content {content_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to track event: {str(e)}")
            return False
    
    async def track_page_view(
        self,
        content_id: str,
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None
    ) -> bool:
        """Track a page view event"""
        
        return await self.track_event(
            content_id=content_id,
            event_type=EventType.PAGE_VIEW,
            event_data={
                'timestamp': datetime.now().isoformat(),
                'page_load_time': session_info.get('page_load_time'),
                'screen_resolution': session_info.get('screen_resolution'),
                'viewport_size': session_info.get('viewport_size')
            },
            session_info=session_info,
            variant_id=variant_id
        )
    
    async def track_scroll_depth(
        self,
        content_id: str,
        scroll_percentage: float,
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None
    ) -> bool:
        """Track user scroll depth"""
        
        return await self.track_event(
            content_id=content_id,
            event_type=EventType.SCROLL_DEPTH,
            event_data={
                'scroll_percentage': scroll_percentage,
                'timestamp': datetime.now().isoformat(),
                'time_to_scroll': session_info.get('time_to_scroll')
            },
            session_info=session_info,
            variant_id=variant_id
        )
    
    async def track_cta_click(
        self,
        content_id: str,
        cta_element: str,
        cta_text: str,
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None
    ) -> bool:
        """Track call-to-action button clicks"""
        
        return await self.track_event(
            content_id=content_id,
            event_type=EventType.CTA_CLICK,
            event_data={
                'cta_element': cta_element,
                'cta_text': cta_text,
                'click_timestamp': datetime.now().isoformat(),
                'time_on_page': session_info.get('time_on_page')
            },
            session_info=session_info,
            variant_id=variant_id
        )
    
    async def track_form_interaction(
        self,
        content_id: str,
        form_action: str,
        form_data: Dict[str, Any],
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None
    ) -> bool:
        """Track form interactions (start, field completion, submission)"""
        
        event_type = {
            'start': EventType.FORM_START,
            'complete': EventType.FORM_COMPLETE,
            'submit': EventType.FORM_SUBMIT
        }.get(form_action, EventType.FORM_INTERACTION)
        
        return await self.track_event(
            content_id=content_id,
            event_type=event_type,
            event_data={
                'form_action': form_action,
                'form_fields': form_data.get('fields', []),
                'completion_time': form_data.get('completion_time'),
                'field_errors': form_data.get('errors', []),
                'timestamp': datetime.now().isoformat()
            },
            session_info=session_info,
            variant_id=variant_id
        )
    
    async def track_conversion(
        self,
        content_id: str,
        conversion_type: str,
        conversion_value: Optional[float],
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None
    ) -> bool:
        """Track conversion events"""
        
        return await self.track_event(
            content_id=content_id,
            event_type=EventType.CONVERSION,
            event_data={
                'conversion_type': conversion_type,
                'conversion_value': conversion_value,
                'conversion_timestamp': datetime.now().isoformat(),
                'customer_journey_time': session_info.get('time_on_page')
            },
            session_info=session_info,
            variant_id=variant_id
        )
    
    async def get_real_time_analytics(
        self,
        content_id: str,
        time_window_hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get real-time analytics for a landing page
        
        Args:
            content_id: Landing page content ID
            time_window_hours: Time window for analytics (default 24 hours)
            
        Returns:
            Dict with real-time analytics data
        """
        
        try:
            cutoff_time = datetime.now() - timedelta(hours=time_window_hours)
            
            # Get events within time window
            events = self.db.query(ConversionEvent).filter(
                and_(
                    ConversionEvent.content_id == content_id,
                    ConversionEvent.created_at >= cutoff_time
                )
            ).all()
            
            # Calculate metrics
            page_views = len([e for e in events if e.event_type == EventType.PAGE_VIEW.value])
            cta_clicks = len([e for e in events if e.event_type == EventType.CTA_CLICK.value])
            conversions = len([e for e in events if e.event_type == EventType.CONVERSION.value])
            form_starts = len([e for e in events if e.event_type == EventType.FORM_START.value])
            form_completions = len([e for e in events if e.event_type == EventType.FORM_COMPLETE.value])
            
            # Calculate rates
            conversion_rate = (conversions / page_views * 100) if page_views > 0 else 0
            cta_click_rate = (cta_clicks / page_views * 100) if page_views > 0 else 0
            form_completion_rate = (form_completions / form_starts * 100) if form_starts > 0 else 0
            
            # Get unique sessions
            unique_sessions = len(set(e.session_id for e in events if e.session_id))
            
            # Calculate scroll depth data
            scroll_events = [e for e in events if e.event_type == EventType.SCROLL_DEPTH.value]
            avg_scroll_depth = 0
            if scroll_events:
                scroll_depths = [e.event_data.get('scroll_percentage', 0) for e in scroll_events]
                avg_scroll_depth = sum(scroll_depths) / len(scroll_depths)
            
            return {
                'time_window_hours': time_window_hours,
                'last_updated': datetime.now().isoformat(),
                'traffic_metrics': {
                    'page_views': page_views,
                    'unique_sessions': unique_sessions,
                    'avg_session_duration': self._calculate_avg_session_duration(events)
                },
                'engagement_metrics': {
                    'avg_scroll_depth': round(avg_scroll_depth, 2),
                    'cta_clicks': cta_clicks,
                    'cta_click_rate': round(cta_click_rate, 2),
                    'avg_time_to_cta': self._calculate_avg_time_to_cta(events)
                },
                'conversion_metrics': {
                    'conversions': conversions,
                    'conversion_rate': round(conversion_rate, 2),
                    'form_starts': form_starts,
                    'form_completions': form_completions,
                    'form_completion_rate': round(form_completion_rate, 2)
                },
                'device_breakdown': self._calculate_device_breakdown(events),
                'traffic_sources': self._calculate_traffic_sources(events),
                'hourly_distribution': self._calculate_hourly_distribution(events)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get real-time analytics: {str(e)}")
            return {}
    
    async def aggregate_daily_analytics(self, content_id: str, date: datetime) -> bool:
        """
        Aggregate daily analytics from events
        
        Args:
            content_id: Landing page content ID
            date: Date to aggregate for
            
        Returns:
            bool: Success status
        """
        
        try:
            # Get all events for the date
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            events = self.db.query(ConversionEvent).filter(
                and_(
                    ConversionEvent.content_id == content_id,
                    ConversionEvent.created_at >= start_date,
                    ConversionEvent.created_at < end_date
                )
            ).all()
            
            if not events:
                return True  # No events to aggregate
            
            # Calculate aggregated metrics
            analytics_data = self.performance_calculator.calculate_daily_metrics(events)
            
            # Check if analytics record exists for this date
            existing_analytics = self.db.query(LandingPageAnalytics).filter(
                and_(
                    LandingPageAnalytics.content_id == content_id,
                    LandingPageAnalytics.date_recorded == date.date()
                )
            ).first()
            
            if existing_analytics:
                # Update existing record
                for key, value in analytics_data.items():
                    setattr(existing_analytics, key, value)
                existing_analytics.updated_at = datetime.now()
            else:
                # Create new analytics record
                analytics_record = LandingPageAnalytics(
                    content_id=content_id,
                    date_recorded=date.date(),
                    **analytics_data
                )
                self.db.add(analytics_record)
            
            await self.db.commit()
            logger.info(f"✅ Daily analytics aggregated for {content_id} on {date.date()}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to aggregate daily analytics: {str(e)}")
            return False
    
    def _calculate_avg_session_duration(self, events: List[ConversionEvent]) -> float:
        """Calculate average session duration from events"""
        
        session_durations = {}
        
        for event in events:
            if not event.session_id:
                continue
                
            if event.session_id not in session_durations:
                session_durations[event.session_id] = {
                    'start': event.created_at,
                    'end': event.created_at
                }
            else:
                if event.created_at < session_durations[event.session_id]['start']:
                    session_durations[event.session_id]['start'] = event.created_at
                if event.created_at > session_durations[event.session_id]['end']:
                    session_durations[event.session_id]['end'] = event.created_at
        
        if not session_durations:
            return 0.0
        
        total_duration = sum(
            (session['end'] - session['start']).total_seconds()
            for session in session_durations.values()
        )
        
        return total_duration / len(session_durations)
    
    def _calculate_avg_time_to_cta(self, events: List[ConversionEvent]) -> float:
        """Calculate average time from page view to CTA click"""
        
        session_times = {}
        
        for event in events:
            if not event.session_id:
                continue
                
            if event.session_id not in session_times:
                session_times[event.session_id] = {}
            
            if event.event_type == EventType.PAGE_VIEW.value:
                session_times[event.session_id]['page_view'] = event.created_at
            elif event.event_type == EventType.CTA_CLICK.value:
                session_times[event.session_id]['cta_click'] = event.created_at
        
        # Calculate time differences
        time_to_cta = []
        for session_data in session_times.values():
            if 'page_view' in session_data and 'cta_click' in session_data:
                time_diff = (session_data['cta_click'] - session_data['page_view']).total_seconds()
                time_to_cta.append(time_diff)
        
        return sum(time_to_cta) / len(time_to_cta) if time_to_cta else 0.0
    
    def _calculate_device_breakdown(self, events: List[ConversionEvent]) -> Dict[str, int]:
        """Calculate device type breakdown from events"""
        
        device_counts = {'desktop': 0, 'mobile': 0, 'tablet': 0, 'unknown': 0}
        
        for event in events:
            if event.event_type == EventType.PAGE_VIEW.value and event.device_info:
                device_type = event.device_info.get('device_type', 'unknown').lower()
                if device_type in device_counts:
                    device_counts[device_type] += 1
                else:
                    device_counts['unknown'] += 1
        
        return device_counts
    
    def _calculate_traffic_sources(self, events: List[ConversionEvent]) -> Dict[str, int]:
        """Calculate traffic source breakdown from events"""
        
        source_counts = {}
        
        for event in events:
            if event.event_type == EventType.PAGE_VIEW.value and event.referrer:
                # Parse referrer to determine source
                if 'google' in event.referrer.lower():
                    source = 'google'
                elif 'facebook' in event.referrer.lower():
                    source = 'facebook'
                elif 'twitter' in event.referrer.lower():
                    source = 'twitter'
                elif 'linkedin' in event.referrer.lower():
                    source = 'linkedin'
                else:
                    source = 'other'
                
                source_counts[source] = source_counts.get(source, 0) + 1
            elif event.event_type == EventType.PAGE_VIEW.value:
                source_counts['direct'] = source_counts.get('direct', 0) + 1
        
        return source_counts
    
    def _calculate_hourly_distribution(self, events: List[ConversionEvent]) -> Dict[int, int]:
        """Calculate hourly distribution of page views"""
        
        hourly_counts = {i: 0 for i in range(24)}
        
        for event in events:
            if event.event_type == EventType.PAGE_VIEW.value:
                hour = event.created_at.hour
                hourly_counts[hour] += 1
        
        return hourly_counts

    async def start_processing(self):
        """Start background event processing"""
        if self._processing_task is None:
            self._processing_task = asyncio.create_task(self._process_events())
            logger.info("✅ Analytics event processing started")
    
    async def stop_processing(self):
        """Stop background event processing"""
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            self._processing_task = None
            logger.info("⏹️ Analytics event processing stopped")
    
    async def _process_events(self):
        """Background task to process events from queue"""
        while True:
            try:
                # Wait for events with timeout
                event = await asyncio.wait_for(self._event_queue.get(), timeout=10.0)
                
                # Process the event (could trigger real-time alerts, etc.)
                await self._handle_real_time_event(event)
                
            except asyncio.TimeoutError:
                continue  # No events to process
            except Exception as e:
                logger.error(f"❌ Error processing event: {str(e)}")
    
    async def _handle_real_time_event(self, event: Dict[str, Any]):
        """Handle real-time event processing"""
        
        # This could trigger:
        # - Real-time alerts for low conversion rates
        # - A/B test winner determination
        # - Performance optimization suggestions
        # - Real-time personalization updates
        
        event_type = event['event_type']
        content_id = event['content_id']
        
        if event_type == EventType.CONVERSION:
            logger.info(f"🎯 Conversion tracked for content {content_id}")
            # Could trigger celebration notifications, alerts, etc.
        
        elif event_type == EventType.CTA_CLICK:
            logger.debug(f"👆 CTA clicked for content {content_id}")
            # Could trigger follow-up sequences, retargeting, etc.