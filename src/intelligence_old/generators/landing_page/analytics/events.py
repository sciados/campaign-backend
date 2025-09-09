# src/intelligence/generators/landing_page/analytics/events.py
"""
Event definitions and data structures for landing page analytics.
Defines all trackable events and their data schemas.
"""

import enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

class EventType(enum.Enum):
    """Types of events that can be tracked on landing pages"""
    
    # Traffic Events
    PAGE_VIEW = "page_view"
    PAGE_LOAD = "page_load"
    PAGE_EXIT = "page_exit"
    SESSION_START = "session_start"
    SESSION_END = "session_end"
    
    # Engagement Events
    SCROLL_DEPTH = "scroll_depth"
    TIME_ON_PAGE = "time_on_page"
    ELEMENT_HOVER = "element_hover"
    ELEMENT_CLICK = "element_click"
    TEXT_SELECTION = "text_selection"
    
    # Conversion Events
    CTA_CLICK = "cta_click"
    CTA_HOVER = "cta_hover"
    FORM_START = "form_start"
    FORM_FIELD_FOCUS = "form_field_focus"
    FORM_FIELD_COMPLETE = "form_field_complete"
    FORM_VALIDATION_ERROR = "form_validation_error"
    FORM_SUBMIT = "form_submit"
    FORM_COMPLETE = "form_complete"
    CONVERSION = "conversion"
    
    # A/B Testing Events
    VARIANT_VIEW = "variant_view"
    VARIANT_INTERACTION = "variant_interaction"
    
    # Performance Events
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_EVENT = "error_event"
    
    # Custom Events
    CUSTOM_EVENT = "custom_event"
    FORM_INTERACTION = "form_interaction"

class ConversionType(enum.Enum):
    """Types of conversions that can occur"""
    
    LEAD_GENERATION = "lead_generation"
    PURCHASE = "purchase"
    SIGNUP = "signup"
    DOWNLOAD = "download"
    EMAIL_SUBSCRIPTION = "email_subscription"
    PHONE_CALL = "phone_call"
    DEMO_REQUEST = "demo_request"
    CONSULTATION_BOOKING = "consultation_booking"
    TRIAL_START = "trial_start"
    WEBINAR_REGISTRATION = "webinar_registration"

class DeviceType(enum.Enum):
    """Device types for analytics"""
    
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    UNKNOWN = "unknown"

@dataclass
class ConversionEventData:
    """Data structure for conversion events"""
    
    event_type: EventType
    content_id: str
    timestamp: datetime
    session_id: Optional[str] = None
    user_fingerprint: Optional[str] = None
    variant_id: Optional[str] = None
    
    # Event-specific data
    event_data: Dict[str, Any] = None
    
    # Session context
    referrer: Optional[str] = None
    landing_url: Optional[str] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None
    
    # Device information
    device_type: Optional[DeviceType] = None
    screen_resolution: Optional[str] = None
    viewport_size: Optional[str] = None
    
    # Performance data
    page_load_time: Optional[int] = None  # milliseconds
    connection_type: Optional[str] = None
    
    def __post_init__(self):
        if self.event_data is None:
            self.event_data = {}

@dataclass
class AnalyticsEventData:
    """Data structure for analytics aggregation events"""
    
    content_id: str
    date: datetime
    variant_id: Optional[str] = None
    
    # Traffic metrics
    page_views: int = 0
    unique_visitors: int = 0
    returning_visitors: int = 0
    
    # Engagement metrics
    avg_time_on_page: Optional[float] = None  # seconds
    bounce_rate: Optional[float] = None
    exit_rate: Optional[float] = None
    avg_scroll_depth: Optional[float] = None  # percentage
    
    # Conversion metrics
    conversions: int = 0
    conversion_rate: Optional[float] = None
    cta_clicks: int = 0
    cta_click_rate: Optional[float] = None
    form_starts: int = 0
    form_completions: int = 0
    form_completion_rate: Optional[float] = None
    
    # Detailed breakdowns
    device_breakdown: Dict[str, int] = None
    traffic_sources: Dict[str, int] = None
    geographic_data: Dict[str, int] = None
    hourly_distribution: Dict[int, int] = None
    
    def __post_init__(self):
        if self.device_breakdown is None:
            self.device_breakdown = {}
        if self.traffic_sources is None:
            self.traffic_sources = {}
        if self.geographic_data is None:
            self.geographic_data = {}
        if self.hourly_distribution is None:
            self.hourly_distribution = {i: 0 for i in range(24)}

@dataclass
class FormInteractionEvent:
    """Specific event data for form interactions"""
    
    form_id: str
    field_name: str
    interaction_type: str  # focus, blur, input, error, submit
    field_value_length: Optional[int] = None
    validation_error: Optional[str] = None
    time_spent: Optional[float] = None  # seconds
    keystroke_count: Optional[int] = None
    field_order: Optional[int] = None

@dataclass
class CTAInteractionEvent:
    """Specific event data for CTA interactions"""
    
    cta_id: str
    cta_text: str
    cta_type: str  # button, link, image
    cta_position: str  # hero, sidebar, footer, etc.
    hover_time: Optional[float] = None  # seconds
    click_coordinates: Optional[Dict[str, int]] = None  # x, y
    time_to_click: Optional[float] = None  # seconds from page load

@dataclass
class ScrollDepthEvent:
    """Specific event data for scroll tracking"""
    
    scroll_percentage: float
    scroll_direction: str  # up, down
    scroll_speed: Optional[float] = None  # pixels per second
    time_to_scroll: Optional[float] = None  # seconds from page load
    section_reached: Optional[str] = None  # hero, benefits, cta, footer

@dataclass
class PerformanceEvent:
    """Specific event data for performance metrics"""
    
    metric_name: str
    metric_value: float
    metric_unit: str  # ms, seconds, percentage, etc.
    browser_info: Optional[Dict[str, str]] = None
    connection_info: Optional[Dict[str, str]] = None

class EventDataFactory:
    """Factory class for creating event data objects"""
    
    @staticmethod
    def create_page_view_event(
        content_id: str,
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None
    ) -> ConversionEventData:
        """Create a page view event"""
        
        return ConversionEventData(
            event_type=EventType.PAGE_VIEW,
            content_id=content_id,
            timestamp=datetime.now(),
            session_id=session_info.get('session_id'),
            user_fingerprint=session_info.get('user_fingerprint'),
            variant_id=variant_id,
            referrer=session_info.get('referrer'),
            landing_url=session_info.get('landing_url'),
            user_agent=session_info.get('user_agent'),
            ip_address=session_info.get('ip_address'),
            device_type=DeviceType(session_info.get('device_type', 'unknown')),
            screen_resolution=session_info.get('screen_resolution'),
            viewport_size=session_info.get('viewport_size'),
            page_load_time=session_info.get('page_load_time'),
            connection_type=session_info.get('connection_type'),
            event_data={
                'page_title': session_info.get('page_title'),
                'landing_page_type': session_info.get('landing_page_type'),
                'utm_source': session_info.get('utm_source'),
                'utm_medium': session_info.get('utm_medium'),
                'utm_campaign': session_info.get('utm_campaign')
            }
        )
    
    @staticmethod
    def create_cta_click_event(
        content_id: str,
        cta_data: CTAInteractionEvent,
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None
    ) -> ConversionEventData:
        """Create a CTA click event"""
        
        return ConversionEventData(
            event_type=EventType.CTA_CLICK,
            content_id=content_id,
            timestamp=datetime.now(),
            session_id=session_info.get('session_id'),
            user_fingerprint=session_info.get('user_fingerprint'),
            variant_id=variant_id,
            event_data={
                'cta_id': cta_data.cta_id,
                'cta_text': cta_data.cta_text,
                'cta_type': cta_data.cta_type,
                'cta_position': cta_data.cta_position,
                'hover_time': cta_data.hover_time,
                'click_coordinates': cta_data.click_coordinates,
                'time_to_click': cta_data.time_to_click
            }
        )
    
    @staticmethod
    def create_form_interaction_event(
        content_id: str,
        form_data: FormInteractionEvent,
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None
    ) -> ConversionEventData:
        """Create a form interaction event"""
        
        event_type_mapping = {
            'focus': EventType.FORM_FIELD_FOCUS,
            'blur': EventType.FORM_FIELD_COMPLETE,
            'input': EventType.FORM_INTERACTION,
            'error': EventType.FORM_VALIDATION_ERROR,
            'submit': EventType.FORM_SUBMIT
        }
        
        event_type = event_type_mapping.get(form_data.interaction_type, EventType.FORM_INTERACTION)
        
        return ConversionEventData(
            event_type=event_type,
            content_id=content_id,
            timestamp=datetime.now(),
            session_id=session_info.get('session_id'),
            user_fingerprint=session_info.get('user_fingerprint'),
            variant_id=variant_id,
            event_data={
                'form_id': form_data.form_id,
                'field_name': form_data.field_name,
                'interaction_type': form_data.interaction_type,
                'field_value_length': form_data.field_value_length,
                'validation_error': form_data.validation_error,
                'time_spent': form_data.time_spent,
                'keystroke_count': form_data.keystroke_count,
                'field_order': form_data.field_order
            }
        )
    
    @staticmethod
    def create_scroll_depth_event(
        content_id: str,
        scroll_data: ScrollDepthEvent,
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None
    ) -> ConversionEventData:
        """Create a scroll depth event"""
        
        return ConversionEventData(
            event_type=EventType.SCROLL_DEPTH,
            content_id=content_id,
            timestamp=datetime.now(),
            session_id=session_info.get('session_id'),
            user_fingerprint=session_info.get('user_fingerprint'),
            variant_id=variant_id,
            event_data={
                'scroll_percentage': scroll_data.scroll_percentage,
                'scroll_direction': scroll_data.scroll_direction,
                'scroll_speed': scroll_data.scroll_speed,
                'time_to_scroll': scroll_data.time_to_scroll,
                'section_reached': scroll_data.section_reached
            }
        )
    
    @staticmethod
    def create_conversion_event(
        content_id: str,
        conversion_type: ConversionType,
        conversion_value: Optional[float],
        session_info: Dict[str, Any],
        variant_id: Optional[str] = None,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> ConversionEventData:
        """Create a conversion event"""
        
        event_data = {
            'conversion_type': conversion_type.value,
            'conversion_value': conversion_value,
            'conversion_timestamp': datetime.now().isoformat()
        }
        
        if additional_data:
            event_data.update(additional_data)
        
        return ConversionEventData(
            event_type=EventType.CONVERSION,
            content_id=content_id,
            timestamp=datetime.now(),
            session_id=session_info.get('session_id'),
            user_fingerprint=session_info.get('user_fingerprint'),
            variant_id=variant_id,
            event_data=event_data
        )
    
    @staticmethod
    def create_performance_event(
        content_id: str,
        performance_data: PerformanceEvent,
        session_info: Dict[str, Any]
    ) -> ConversionEventData:
        """Create a performance metrics event"""
        
        return ConversionEventData(
            event_type=EventType.PERFORMANCE_METRIC,
            content_id=content_id,
            timestamp=datetime.now(),
            session_id=session_info.get('session_id'),
            user_fingerprint=session_info.get('user_fingerprint'),
            event_data={
                'metric_name': performance_data.metric_name,
                'metric_value': performance_data.metric_value,
                'metric_unit': performance_data.metric_unit,
                'browser_info': performance_data.browser_info,
                'connection_info': performance_data.connection_info
            }
        )

class EventValidator:
    """Validates event data before processing"""
    
    @staticmethod
    def validate_event_data(event_data: ConversionEventData) -> bool:
        """Validate event data structure and required fields"""
        
        # Check required fields
        if not event_data.content_id:
            return False
        
        if not isinstance(event_data.event_type, EventType):
            return False
        
        if not event_data.timestamp:
            return False
        
        # Validate event-specific data
        if event_data.event_type == EventType.CTA_CLICK:
            return EventValidator._validate_cta_event(event_data)
        elif event_data.event_type in [EventType.FORM_START, EventType.FORM_SUBMIT, EventType.FORM_COMPLETE]:
            return EventValidator._validate_form_event(event_data)
        elif event_data.event_type == EventType.SCROLL_DEPTH:
            return EventValidator._validate_scroll_event(event_data)
        elif event_data.event_type == EventType.CONVERSION:
            return EventValidator._validate_conversion_event(event_data)
        
        return True
    
    @staticmethod
    def _validate_cta_event(event_data: ConversionEventData) -> bool:
        """Validate CTA-specific event data"""
        
        required_fields = ['cta_id', 'cta_text', 'cta_type']
        
        for field in required_fields:
            if field not in event_data.event_data:
                return False
        
        return True
    
    @staticmethod
    def _validate_form_event(event_data: ConversionEventData) -> bool:
        """Validate form-specific event data"""
        
        if 'form_id' not in event_data.event_data:
            return False
        
        return True
    
    @staticmethod
    def _validate_scroll_event(event_data: ConversionEventData) -> bool:
        """Validate scroll-specific event data"""
        
        if 'scroll_percentage' not in event_data.event_data:
            return False
        
        scroll_percentage = event_data.event_data['scroll_percentage']
        if not isinstance(scroll_percentage, (int, float)) or scroll_percentage < 0 or scroll_percentage > 100:
            return False
        
        return True
    
    @staticmethod
    def _validate_conversion_event(event_data: ConversionEventData) -> bool:
        """Validate conversion-specific event data"""
        
        required_fields = ['conversion_type', 'conversion_timestamp']
        
        for field in required_fields:
            if field not in event_data.event_data:
                return False
        
        return True

class EventAggregator:
    """Aggregates events for analytics reporting"""
    
    @staticmethod
    def aggregate_events_by_hour(events: List[ConversionEventData]) -> Dict[int, Dict[str, int]]:
        """Aggregate events by hour of day"""
        
        hourly_data = {i: {} for i in range(24)}
        
        for event in events:
            hour = event.timestamp.hour
            event_type = event.event_type.value
            
            if event_type not in hourly_data[hour]:
                hourly_data[hour][event_type] = 0
            
            hourly_data[hour][event_type] += 1
        
        return hourly_data
    
    @staticmethod
    def aggregate_events_by_device(events: List[ConversionEventData]) -> Dict[str, Dict[str, int]]:
        """Aggregate events by device type"""
        
        device_data = {}
        
        for event in events:
            device_type = event.device_type.value if event.device_type else 'unknown'
            event_type = event.event_type.value
            
            if device_type not in device_data:
                device_data[device_type] = {}
            
            if event_type not in device_data[device_type]:
                device_data[device_type][event_type] = 0
            
            device_data[device_type][event_type] += 1
        
        return device_data
    
    @staticmethod
    def calculate_conversion_funnel(events: List[ConversionEventData]) -> Dict[str, int]:
        """Calculate conversion funnel metrics"""
        
        funnel_steps = {
            'page_views': 0,
            'engaged_users': 0,  # scrolled > 25%
            'interested_users': 0,  # scrolled > 50% or spent > 30s
            'intent_users': 0,  # clicked CTA or started form
            'conversions': 0
        }
        
        session_data = {}
        
        # Group events by session
        for event in events:
            session_id = event.session_id or event.user_fingerprint or 'anonymous'
            
            if session_id not in session_data:
                session_data[session_id] = []
            
            session_data[session_id].append(event)
        
        # Analyze each session
        for session_events in session_data.values():
            has_page_view = False
            max_scroll = 0
            has_cta_click = False
            has_form_start = False
            has_conversion = False
            
            for event in session_events:
                if event.event_type == EventType.PAGE_VIEW:
                    has_page_view = True
                elif event.event_type == EventType.SCROLL_DEPTH:
                    scroll_pct = event.event_data.get('scroll_percentage', 0)
                    max_scroll = max(max_scroll, scroll_pct)
                elif event.event_type == EventType.CTA_CLICK:
                    has_cta_click = True
                elif event.event_type == EventType.FORM_START:
                    has_form_start = True
                elif event.event_type == EventType.CONVERSION:
                    has_conversion = True
            
            # Count funnel progression
            if has_page_view:
                funnel_steps['page_views'] += 1
                
                if max_scroll > 25:
                    funnel_steps['engaged_users'] += 1
                    
                    if max_scroll > 50:
                        funnel_steps['interested_users'] += 1
                        
                        if has_cta_click or has_form_start:
                            funnel_steps['intent_users'] += 1
                            
                            if has_conversion:
                                funnel_steps['conversions'] += 1
        
        return funnel_steps

# Export all classes and enums
__all__ = [
    'EventType',
    'ConversionType', 
    'DeviceType',
    'ConversionEventData',
    'AnalyticsEventData',
    'FormInteractionEvent',
    'CTAInteractionEvent',
    'ScrollDepthEvent',
    'PerformanceEvent',
    'EventDataFactory',
    'EventValidator',
    'EventAggregator'
]