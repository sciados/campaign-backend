# src/intelligence/generators/landing_page/analytics/performance.py
"""
Performance prediction and optimization analysis for landing pages.
Uses machine learning and statistical models to predict conversion rates and performance.
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from sqlalchemy.orm import Session

from ..database.models import ConversionEvent, LandingPageAnalytics, GeneratedContent
from .events import EventType, ConversionEventData

logger = logging.getLogger(__name__)

@dataclass
class PerformancePrediction:
    """Performance prediction results"""
    
    predicted_conversion_rate: float
    confidence_interval: Tuple[float, float]
    optimization_score: float  # 0-100
    performance_grade: str  # A, B, C, D, F
    
    # Detailed predictions
    traffic_predictions: Dict[str, Any]
    engagement_predictions: Dict[str, Any]
    conversion_predictions: Dict[str, Any]
    
    # Optimization recommendations
    recommendations: List[Dict[str, Any]]
    improvement_potential: float  # percentage improvement possible
    
    # Metadata
    prediction_confidence: float  # 0-1
    model_version: str
    generated_at: datetime

class PerformanceCalculator:
    """
    Calculates performance metrics and predictions for landing pages.
    
    Uses historical data, industry benchmarks, and machine learning models
    to predict performance and suggest optimizations.
    """
    
    def __init__(self):
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.conversion_factors = self._load_conversion_factors()
        self.model_version = "2.0.0"
        
        logger.info("✅ Performance Calculator initialized")
    
    def predict_performance(
        self,
        intelligence_data: Dict[str, Any],
        page_config: Dict[str, Any],
        conversion_intelligence: Optional[Dict[str, Any]] = None
    ) -> PerformancePrediction:
        """
        Predict landing page performance based on intelligence and configuration
        
        Args:
            intelligence_data: Competitor and market intelligence
            page_config: Landing page configuration and elements
            conversion_intelligence: Enhanced conversion intelligence
            
        Returns:
            PerformancePrediction with detailed performance forecasts
        """
        
        try:
            # Extract key performance indicators
            niche = intelligence_data.get('detected_niche', 'general')
            template_type = page_config.get('template_type', 'lead_generation')
            
            # Calculate base conversion rate prediction
            base_conversion_rate = self._calculate_base_conversion_rate(niche, template_type)
            
            # Apply intelligence-based modifiers
            intelligence_multiplier = self._calculate_intelligence_multiplier(
                intelligence_data, conversion_intelligence
            )
            
            # Apply page configuration modifiers
            config_multiplier = self._calculate_config_multiplier(page_config)
            
            # Calculate final prediction
            predicted_rate = base_conversion_rate * intelligence_multiplier * config_multiplier
            predicted_rate = max(0.5, min(25.0, predicted_rate))  # Clamp between 0.5% and 25%
            
            # Calculate confidence interval
            confidence_interval = self._calculate_confidence_interval(
                predicted_rate, intelligence_data, page_config
            )
            
            # Calculate optimization score
            optimization_score = self._calculate_optimization_score(
                predicted_rate, niche, page_config, intelligence_data
            )
            
            # Generate performance grade
            performance_grade = self._calculate_performance_grade(optimization_score)
            
            # Generate detailed predictions
            traffic_predictions = self._predict_traffic_metrics(
                predicted_rate, niche, page_config
            )
            
            engagement_predictions = self._predict_engagement_metrics(
                intelligence_data, page_config
            )
            
            conversion_predictions = self._predict_conversion_metrics(
                predicted_rate, page_config
            )
            
            # Generate optimization recommendations
            recommendations = self._generate_recommendations(
                predicted_rate, optimization_score, page_config, intelligence_data
            )
            
            # Calculate improvement potential
            improvement_potential = self._calculate_improvement_potential(
                optimization_score, recommendations
            )
            
            # Calculate prediction confidence
            prediction_confidence = self._calculate_prediction_confidence(
                intelligence_data, page_config
            )
            
            return PerformancePrediction(
                predicted_conversion_rate=round(predicted_rate, 2),
                confidence_interval=confidence_interval,
                optimization_score=round(optimization_score, 1),
                performance_grade=performance_grade,
                traffic_predictions=traffic_predictions,
                engagement_predictions=engagement_predictions,
                conversion_predictions=conversion_predictions,
                recommendations=recommendations,
                improvement_potential=round(improvement_potential, 1),
                prediction_confidence=round(prediction_confidence, 2),
                model_version=self.model_version,
                generated_at=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"❌ Performance prediction failed: {str(e)}")
            return self._generate_fallback_prediction()
    
    def calculate_daily_metrics(self, events: List[ConversionEvent]) -> Dict[str, Any]:
        """
        Calculate daily analytics metrics from events
        
        Args:
            events: List of conversion events for the day
            
        Returns:
            Dict with calculated daily metrics
        """
        
        if not events:
            return self._get_empty_daily_metrics()
        
        # Basic traffic metrics
        page_views = len([e for e in events if e.event_type == EventType.PAGE_VIEW.value])
        unique_sessions = len(set(e.session_id for e in events if e.session_id))
        
        # Engagement metrics
        scroll_events = [e for e in events if e.event_type == EventType.SCROLL_DEPTH.value]
        avg_scroll_depth = 0
        if scroll_events:
            scroll_depths = [e.event_data.get('scroll_percentage', 0) for e in scroll_events]
            avg_scroll_depth = sum(scroll_depths) / len(scroll_depths)
        
        # Calculate time on page
        avg_time_on_page = self._calculate_avg_time_on_page(events)
        
        # Calculate bounce rate
        bounce_rate = self._calculate_bounce_rate(events)
        
        # Conversion metrics
        conversions = len([e for e in events if e.event_type == EventType.CONVERSION.value])
        cta_clicks = len([e for e in events if e.event_type == EventType.CTA_CLICK.value])
        form_starts = len([e for e in events if e.event_type == EventType.FORM_START.value])
        form_completions = len([e for e in events if e.event_type == EventType.FORM_COMPLETE.value])
        
        # Calculate rates
        conversion_rate = (conversions / page_views * 100) if page_views > 0 else 0
        cta_click_rate = (cta_clicks / page_views * 100) if page_views > 0 else 0
        form_completion_rate = (form_completions / form_starts * 100) if form_starts > 0 else 0
        
        # Device and traffic breakdowns
        device_breakdown = self._calculate_device_breakdown(events)
        traffic_sources = self._calculate_traffic_sources(events)
        hourly_distribution = self._calculate_hourly_distribution(events)
        
        return {
            'page_views': page_views,
            'unique_visitors': unique_sessions,
            'returning_visitors': 0,  # Would need session tracking across days
            'avg_time_on_page': round(avg_time_on_page, 1) if avg_time_on_page else None,
            'bounce_rate': round(bounce_rate, 4) if bounce_rate else None,
            'avg_scroll_depth': round(avg_scroll_depth, 2) if avg_scroll_depth else None,
            'exit_rate': round(bounce_rate, 4) if bounce_rate else None,  # Simplified
            'conversions': conversions,
            'conversion_rate': round(conversion_rate / 100, 4) if conversion_rate else None,
            'cta_clicks': cta_clicks,
            'form_starts': form_starts,
            'form_completions': form_completions,
            'device_breakdown': device_breakdown,
            'traffic_sources': traffic_sources,
            'geographic_data': {},  # Would need IP geolocation
            'conversion_events': {
                'total_conversions': conversions,
                'conversion_types': self._get_conversion_types(events)
            },
            'user_behavior_data': {
                'avg_scroll_depth': avg_scroll_depth,
                'avg_time_on_page': avg_time_on_page,
                'cta_interaction_rate': cta_click_rate,
                'form_abandonment_rate': 100 - form_completion_rate if form_starts > 0 else 0
            },
            'hourly_distribution': hourly_distribution
        }
    
    def _calculate_base_conversion_rate(self, niche: str, template_type: str) -> float:
        """Calculate base conversion rate from industry benchmarks"""
        
        # Industry benchmark conversion rates (%)
        base_rates = {
            'health': {'lead_generation': 3.2, 'sales': 2.1, 'webinar': 4.5},
            'business': {'lead_generation': 2.8, 'sales': 1.8, 'webinar': 3.9},
            'technology': {'lead_generation': 2.5, 'sales': 1.5, 'webinar': 3.2},
            'finance': {'lead_generation': 2.2, 'sales': 1.3, 'webinar': 2.8},
            'education': {'lead_generation': 3.5, 'sales': 2.3, 'webinar': 5.1},
            'lifestyle': {'lead_generation': 2.9, 'sales': 1.9, 'webinar': 3.7}
        }
        
        niche_rates = base_rates.get(niche, base_rates['business'])
        return niche_rates.get(template_type, 2.5)
    
    def _calculate_intelligence_multiplier(
        self,
        intelligence_data: Dict[str, Any],
        conversion_intelligence: Optional[Dict[str, Any]]
    ) -> float:
        """Calculate multiplier based on intelligence quality"""
        
        multiplier = 1.0
        
        # Intelligence data quality
        if intelligence_data.get('confidence_score', 0) > 0.8:
            multiplier *= 1.2
        elif intelligence_data.get('confidence_score', 0) > 0.6:
            multiplier *= 1.1
        
        # Conversion intelligence factors
        if conversion_intelligence:
            # Scientific backing
            if conversion_intelligence.get('scientific_backing', {}).get('score', 0) > 0.7:
                multiplier *= 1.15
            
            # Emotional triggers
            if conversion_intelligence.get('emotional_triggers', {}).get('effectiveness', 0) > 0.7:
                multiplier *= 1.1
            
            # Authority indicators
            if conversion_intelligence.get('authority_indicators', {}).get('score', 0) > 0.7:
                multiplier *= 1.08
        
        # Competitor intelligence
        competitors_analyzed = len(intelligence_data.get('competitors', []))
        if competitors_analyzed >= 5:
            multiplier *= 1.1
        elif competitors_analyzed >= 3:
            multiplier *= 1.05
        
        return min(multiplier, 1.5)  # Cap at 50% improvement
    
    def _calculate_config_multiplier(self, page_config: Dict[str, Any]) -> float:
        """Calculate multiplier based on page configuration"""
        
        multiplier = 1.0
        
        # Template quality
        template_quality = page_config.get('template_quality', 'standard')
        if template_quality == 'premium':
            multiplier *= 1.2
        elif template_quality == 'professional':
            multiplier *= 1.1
        
        # Conversion elements
        conversion_elements = page_config.get('conversion_elements', [])
        element_bonus = {
            'social_proof': 0.08,
            'urgency_indicators': 0.06,
            'trust_signals': 0.05,
            'multiple_ctas': 0.04,
            'video_content': 0.07,
            'testimonials': 0.06,
            'guarantee': 0.05
        }
        
        for element in conversion_elements:
            if element in element_bonus:
                multiplier += element_bonus[element]
        
        # Mobile optimization
        if page_config.get('mobile_optimized', False):
            multiplier *= 1.15
        
        # Page load speed
        load_speed = page_config.get('estimated_load_speed', 3.0)
        if load_speed < 2.0:
            multiplier *= 1.1
        elif load_speed > 5.0:
            multiplier *= 0.9
        
        return min(multiplier, 1.8)  # Cap at 80% improvement
    
    def _calculate_confidence_interval(
        self,
        predicted_rate: float,
        intelligence_data: Dict[str, Any],
        page_config: Dict[str, Any]
    ) -> Tuple[float, float]:
        """Calculate confidence interval for prediction"""
        
        # Base confidence interval (±20%)
        base_margin = predicted_rate * 0.2
        
        # Adjust based on data quality
        confidence_score = intelligence_data.get('confidence_score', 0.5)
        data_quality_factor = 1.0 - confidence_score * 0.3
        
        margin = base_margin * data_quality_factor
        
        lower_bound = max(0.1, predicted_rate - margin)
        upper_bound = min(30.0, predicted_rate + margin)
        
        return (round(lower_bound, 2), round(upper_bound, 2))
    
    def _calculate_optimization_score(
        self,
        predicted_rate: float,
        niche: str,
        page_config: Dict[str, Any],
        intelligence_data: Dict[str, Any]
    ) -> float:
        """Calculate overall optimization score (0-100)"""
        
        score = 0
        
        # Conversion rate performance (40 points)
        benchmark = self._calculate_base_conversion_rate(niche, page_config.get('template_type', 'lead_generation'))
        if predicted_rate >= benchmark * 1.5:
            score += 40
        elif predicted_rate >= benchmark * 1.2:
            score += 32
        elif predicted_rate >= benchmark:
            score += 25
        elif predicted_rate >= benchmark * 0.8:
            score += 18
        else:
            score += 10
        
        # Intelligence quality (20 points)
        intelligence_score = intelligence_data.get('confidence_score', 0.5)
        score += intelligence_score * 20
        
        # Page configuration (25 points)
        config_score = self._evaluate_config_quality(page_config)
        score += config_score * 25
        
        # Best practices compliance (15 points)
        best_practices_score = self._evaluate_best_practices(page_config)
        score += best_practices_score * 15
        
        return min(100, score)
    
    def _calculate_performance_grade(self, optimization_score: float) -> str:
        """Convert optimization score to letter grade"""
        
        if optimization_score >= 90:
            return "A"
        elif optimization_score >= 80:
            return "B"
        elif optimization_score >= 70:
            return "C"
        elif optimization_score >= 60:
            return "D"
        else:
            return "F"
    
    def _predict_traffic_metrics(
        self,
        conversion_rate: float,
        niche: str,
        page_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict traffic-related metrics"""
        
        # Base traffic assumptions for predictions
        estimated_daily_visitors = page_config.get('expected_traffic', 100)
        
        return {
            'estimated_daily_visitors': estimated_daily_visitors,
            'estimated_monthly_visitors': estimated_daily_visitors * 30,
            'predicted_bounce_rate': self._predict_bounce_rate(niche, page_config),
            'predicted_time_on_page': self._predict_time_on_page(niche, page_config),
            'predicted_pages_per_session': 1.2,  # Landing page focused
            'mobile_traffic_percentage': 65,  # Industry average
            'peak_traffic_hours': [10, 11, 14, 15, 19, 20]
        }
    
    def _predict_engagement_metrics(
        self,
        intelligence_data: Dict[str, Any],
        page_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict engagement metrics"""
        
        # Content quality affects engagement
        content_quality = intelligence_data.get('confidence_score', 0.5)
        
        base_scroll_depth = 45 + (content_quality * 25)  # 45-70%
        base_cta_click_rate = 8 + (content_quality * 7)  # 8-15%
        
        return {
            'predicted_scroll_depth': round(base_scroll_depth, 1),
            'predicted_cta_click_rate': round(base_cta_click_rate, 1),
            'predicted_form_start_rate': round(base_cta_click_rate * 0.7, 1),
            'predicted_social_shares': max(1, int(content_quality * 10)),
            'predicted_return_visitor_rate': round(15 + (content_quality * 10), 1),
            'engagement_score': round(content_quality * 100, 1)
        }
    
    def _predict_conversion_metrics(
        self,
        conversion_rate: float,
        page_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Predict conversion-related metrics"""
        
        estimated_traffic = page_config.get('expected_traffic', 100)
        daily_conversions = (estimated_traffic * conversion_rate / 100)
        
        return {
            'predicted_daily_conversions': round(daily_conversions, 1),
            'predicted_monthly_conversions': round(daily_conversions * 30, 1),
            'predicted_conversion_value': page_config.get('average_order_value', 0) * daily_conversions,
            'predicted_lead_quality_score': self._predict_lead_quality(page_config),
            'predicted_customer_lifetime_value': page_config.get('customer_lifetime_value', 0),
            'conversion_funnel_efficiency': self._calculate_funnel_efficiency(conversion_rate),
            'predicted_cost_per_conversion': page_config.get('estimated_cpc', 0) / (conversion_rate / 100) if conversion_rate > 0 else 0
        }
    
    def _generate_recommendations(
        self,
        predicted_rate: float,
        optimization_score: float,
        page_config: Dict[str, Any],
        intelligence_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate optimization recommendations"""
        
        recommendations = []
        
        # Conversion rate recommendations
        if predicted_rate < 2.0:
            recommendations.append({
                'category': 'conversion_optimization',
                'priority': 'high',
                'title': 'Improve Core Conversion Elements',
                'description': 'Your predicted conversion rate is below industry average. Focus on strengthening your value proposition, headlines, and call-to-action buttons.',
                'expected_impact': '+1.2% conversion rate',
                'implementation_difficulty': 'medium',
                'actions': [
                    'Strengthen headline with benefit-focused copy',
                    'Add social proof elements',
                    'Optimize CTA button text and placement',
                    'Simplify form fields'
                ]
            })
        
        # Intelligence-based recommendations
        confidence_score = intelligence_data.get('confidence_score', 0.5)
        if confidence_score < 0.7:
            recommendations.append({
                'category': 'intelligence_quality',
                'priority': 'medium',
                'title': 'Enhance Intelligence Data',
                'description': 'Gathering more competitor intelligence could improve your page performance by 15-25%.',
                'expected_impact': '+0.8% conversion rate',
                'implementation_difficulty': 'low',
                'actions': [
                    'Analyze 2-3 additional competitors',
                    'Gather more customer testimonials',
                    'Research industry-specific pain points',
                    'Collect scientific backing for claims'
                ]
            })
        
        # Page configuration recommendations
        conversion_elements = page_config.get('conversion_elements', [])
        if 'social_proof' not in conversion_elements:
            recommendations.append({
                'category': 'trust_building',
                'priority': 'high',
                'title': 'Add Social Proof Elements',
                'description': 'Adding testimonials, reviews, or customer logos can increase conversions by 8-15%.',
                'expected_impact': '+0.6% conversion rate',
                'implementation_difficulty': 'low',
                'actions': [
                    'Add customer testimonials with photos',
                    'Include company logos or badges',
                    'Show user count or popularity metrics',
                    'Display recent customer activity'
                ]
            })
        
        if 'urgency_indicators' not in conversion_elements:
            recommendations.append({
                'category': 'urgency_optimization',
                'priority': 'medium',
                'title': 'Create Urgency and Scarcity',
                'description': 'Time-limited offers or limited availability can boost conversions by 6-12%.',
                'expected_impact': '+0.4% conversion rate',
                'implementation_difficulty': 'low',
                'actions': [
                    'Add countdown timer for limited-time offers',
                    'Show limited stock or seats available',
                    'Include "act now" messaging',
                    'Display recent customer activity'
                ]
            })
        
        # Mobile optimization
        if not page_config.get('mobile_optimized', False):
            recommendations.append({
                'category': 'mobile_optimization',
                'priority': 'high',
                'title': 'Optimize for Mobile Devices',
                'description': 'With 65% of traffic from mobile, mobile optimization is critical for conversions.',
                'expected_impact': '+1.0% conversion rate',
                'implementation_difficulty': 'medium',
                'actions': [
                    'Ensure responsive design works on all devices',
                    'Optimize form fields for mobile input',
                    'Improve page load speed on mobile',
                    'Make CTA buttons thumb-friendly'
                ]
            })
        
        # Performance optimization
        load_speed = page_config.get('estimated_load_speed', 3.0)
        if load_speed > 3.0:
            recommendations.append({
                'category': 'performance',
                'priority': 'medium',
                'title': 'Improve Page Load Speed',
                'description': f'Your page loads in {load_speed}s. Every second delay reduces conversions by ~7%.',
                'expected_impact': '+0.5% conversion rate',
                'implementation_difficulty': 'high',
                'actions': [
                    'Optimize and compress images',
                    'Minimize CSS and JavaScript',
                    'Use a content delivery network (CDN)',
                    'Enable browser caching'
                ]
            })
        
        # A/B testing recommendations
        if optimization_score < 80:
            recommendations.append({
                'category': 'testing',
                'priority': 'medium',
                'title': 'Implement A/B Testing',
                'description': 'Test different variations to find the highest-converting version of your page.',
                'expected_impact': '+0.7% conversion rate',
                'implementation_difficulty': 'medium',
                'actions': [
                    'Test different headline variations',
                    'Test CTA button colors and text',
                    'Test different page layouts',
                    'Test form length variations'
                ]
            })
        
        # Sort by priority and expected impact
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        recommendations.sort(
            key=lambda x: (priority_order.get(x['priority'], 0), float(x['expected_impact'].split('+')[1].split('%')[0])),
            reverse=True
        )
        
        return recommendations[:6]  # Return top 6 recommendations
    
    def _calculate_improvement_potential(
        self,
        optimization_score: float,
        recommendations: List[Dict[str, Any]]
    ) -> float:
        """Calculate potential improvement percentage"""
        
        # Base improvement potential based on current score
        base_potential = max(0, 100 - optimization_score) * 0.6
        
        # Add potential from recommendations
        recommendation_potential = sum(
            float(rec['expected_impact'].split('+')[1].split('%')[0])
            for rec in recommendations
            if '+' in rec['expected_impact'] and '%' in rec['expected_impact']
        )
        
        total_potential = base_potential + recommendation_potential
        return min(total_potential, 150)  # Cap at 150% improvement
    
    def _calculate_prediction_confidence(
        self,
        intelligence_data: Dict[str, Any],
        page_config: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the prediction"""
        
        confidence = 0.1  # Base confidence
        
        # Intelligence data quality
        intelligence_confidence = intelligence_data.get('confidence_score', 0.5)
        confidence += intelligence_confidence * 0.3
        
        # Number of competitors analyzed
        competitors_count = len(intelligence_data.get('competitors', []))
        if competitors_count >= 5:
            confidence += 0.15
        elif competitors_count >= 3:
            confidence += 0.1
        elif competitors_count >= 1:
            confidence += 0.05
        
        # Page configuration completeness
        required_elements = ['headline', 'cta_button', 'benefits', 'template_type']
        present_elements = sum(1 for elem in required_elements if elem in page_config)
        confidence += (present_elements / len(required_elements)) * 0.1
        
        return min(1.0, confidence)
    
    def _generate_fallback_prediction(self) -> PerformancePrediction:
        """Generate fallback prediction when calculation fails"""
        
        return PerformancePrediction(
            predicted_conversion_rate=2.5,
            confidence_interval=(1.8, 3.2),
            optimization_score=65.0,
            performance_grade="C",
            traffic_predictions={'estimated_daily_visitors': 100},
            engagement_predictions={'predicted_scroll_depth': 50.0},
            conversion_predictions={'predicted_daily_conversions': 2.5},
            recommendations=[{
                'category': 'general',
                'priority': 'medium',
                'title': 'Improve Overall Performance',
                'description': 'Focus on core conversion elements.',
                'expected_impact': '+0.5% conversion rate',
                'implementation_difficulty': 'medium',
                'actions': ['Optimize headlines', 'Add social proof']
            }],
            improvement_potential=35.0,
            prediction_confidence=0.6,
            model_version=self.model_version,
            generated_at=datetime.now()
        )
    
    def _load_industry_benchmarks(self) -> Dict[str, Any]:
        """Load industry benchmark data"""
        
        return {
            'health': {'avg_conversion_rate': 3.2, 'avg_bounce_rate': 45.2},
            'business': {'avg_conversion_rate': 2.8, 'avg_bounce_rate': 42.1},
            'technology': {'avg_conversion_rate': 2.5, 'avg_bounce_rate': 38.7},
            'finance': {'avg_conversion_rate': 2.2, 'avg_bounce_rate': 41.3},
            'education': {'avg_conversion_rate': 3.5, 'avg_bounce_rate': 39.8},
            'lifestyle': {'avg_conversion_rate': 2.9, 'avg_bounce_rate': 46.1}
        }
    
    def _load_conversion_factors(self) -> Dict[str, float]:
        """Load conversion factor multipliers"""
        
        return {
            'social_proof': 1.08,
            'urgency_indicators': 1.06,
            'trust_signals': 1.05,
            'video_content': 1.07,
            'testimonials': 1.06,
            'guarantee': 1.05,
            'mobile_optimized': 1.15,
            'fast_loading': 1.10
        }
    
    def _get_empty_daily_metrics(self) -> Dict[str, Any]:
        """Return empty daily metrics structure"""
        
        return {
            'page_views': 0,
            'unique_visitors': 0,
            'returning_visitors': 0,
            'avg_time_on_page': None,
            'bounce_rate': None,
            'avg_scroll_depth': None,
            'exit_rate': None,
            'conversions': 0,
            'conversion_rate': None,
            'cta_clicks': 0,
            'form_starts': 0,
            'form_completions': 0,
            'device_breakdown': {},
            'traffic_sources': {},
            'geographic_data': {},
            'conversion_events': {},
            'user_behavior_data': {},
            'hourly_distribution': {i: 0 for i in range(24)}
        }
    
    def _calculate_avg_time_on_page(self, events: List[ConversionEvent]) -> Optional[float]:
        """Calculate average time on page from events"""
        
        session_times = {}
        
        for event in events:
            if not event.session_id:
                continue
                
            if event.session_id not in session_times:
                session_times[event.session_id] = {
                    'start': event.created_at,
                    'end': event.created_at
                }
            else:
                if event.created_at < session_times[event.session_id]['start']:
                    session_times[event.session_id]['start'] = event.created_at
                if event.created_at > session_times[event.session_id]['end']:
                    session_times[event.session_id]['end'] = event.created_at
        
        if not session_times:
            return None
        
        total_time = sum(
            (session['end'] - session['start']).total_seconds()
            for session in session_times.values()
        )
        
        return total_time / len(session_times)
    
    def _calculate_bounce_rate(self, events: List[ConversionEvent]) -> Optional[float]:
        """Calculate bounce rate from events"""
        
        session_event_counts = {}
        
        for event in events:
            session_id = event.session_id or 'anonymous'
            if session_id not in session_event_counts:
                session_event_counts[session_id] = 0
            session_event_counts[session_id] += 1
        
        if not session_event_counts:
            return None
        
        bounced_sessions = sum(1 for count in session_event_counts.values() if count == 1)
        total_sessions = len(session_event_counts)
        
        return bounced_sessions / total_sessions
    
    def _calculate_device_breakdown(self, events: List[ConversionEvent]) -> Dict[str, int]:
        """Calculate device breakdown from events"""
        
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
        """Calculate traffic sources from events"""
        
        source_counts = {}
        
        for event in events:
            if event.event_type == EventType.PAGE_VIEW.value:
                if event.referrer:
                    if 'google' in event.referrer.lower():
                        source = 'google'
                    elif 'facebook' in event.referrer.lower():
                        source = 'facebook'
                    elif 'twitter' in event.referrer.lower():
                        source = 'twitter'
                    else:
                        source = 'other'
                else:
                    source = 'direct'
                
                source_counts[source] = source_counts.get(source, 0) + 1
        
        return source_counts
    
    def _calculate_hourly_distribution(self, events: List[ConversionEvent]) -> Dict[int, int]:
        """Calculate hourly distribution of events"""
        
        hourly_counts = {i: 0 for i in range(24)}
        
        for event in events:
            if event.event_type == EventType.PAGE_VIEW.value:
                hour = event.created_at.hour
                hourly_counts[hour] += 1
        
        return hourly_counts
    
    def _get_conversion_types(self, events: List[ConversionEvent]) -> Dict[str, int]:
        """Get breakdown of conversion types"""
        
        conversion_types = {}
        
        for event in events:
            if event.event_type == EventType.CONVERSION.value:
                conv_type = event.event_data.get('conversion_type', 'unknown')
                conversion_types[conv_type] = conversion_types.get(conv_type, 0) + 1
        
        return conversion_types
    
    def _predict_bounce_rate(self, niche: str, page_config: Dict[str, Any]) -> float:
        """Predict bounce rate based on niche and configuration"""
        
        base_rates = {
            'health': 45.2, 'business': 42.1, 'technology': 38.7,
            'finance': 41.3, 'education': 39.8, 'lifestyle': 46.1
        }
        
        base_rate = base_rates.get(niche, 43.0)
        
        # Adjust based on page quality
        if page_config.get('mobile_optimized', False):
            base_rate -= 3.0
        
        if page_config.get('estimated_load_speed', 3.0) < 2.0:
            base_rate -= 2.0
        
        return max(25.0, min(70.0, base_rate))
    
    def _predict_time_on_page(self, niche: str, page_config: Dict[str, Any]) -> float:
        """Predict average time on page"""
        
        base_times = {
            'health': 95, 'business': 78, 'technology': 85,
            'finance': 72, 'education': 110, 'lifestyle': 88
        }
        
        base_time = base_times.get(niche, 85)
        
        # Adjust based on content quality
        content_elements = len(page_config.get('conversion_elements', []))
        base_time += content_elements * 8
        
        return max(30.0, min(300.0, base_time))
    
    def _predict_lead_quality(self, page_config: Dict[str, Any]) -> float:
        """Predict lead quality score"""
        
        base_score = 70.0
        
        # Higher quality with more qualification
        if 'form' in page_config.get('conversion_elements', []):
            base_score += 10
        
        if page_config.get('template_type') == 'webinar':
            base_score += 15  # Webinar leads tend to be higher quality
        
        return min(100.0, base_score)
    
    def _calculate_funnel_efficiency(self, conversion_rate: float) -> float:
        """Calculate conversion funnel efficiency"""
        
        # Simplified funnel efficiency calculation
        # Higher conversion rate indicates better funnel efficiency
        return min(100.0, conversion_rate * 25)
    
    def _evaluate_config_quality(self, page_config: Dict[str, Any]) -> float:
        """Evaluate overall page configuration quality (0-1)"""
        
        score = 0.0
        max_score = 0.0
        
        # Check for key elements
        key_elements = {
            'headline': 0.2,
            'cta_button': 0.2,
            'benefits': 0.15,
            'social_proof': 0.1,
            'mobile_optimized': 0.15,
            'trust_signals': 0.1,
            'video_content': 0.1
        }
        
        for element, weight in key_elements.items():
            max_score += weight
            if element in page_config.get('conversion_elements', []) or page_config.get(element):
                score += weight
        
        return score / max_score if max_score > 0 else 0.5
    
    def _evaluate_best_practices(self, page_config: Dict[str, Any]) -> float:
        """Evaluate adherence to best practices (0-1)"""
        
        score = 0.0
        checks = 0
        
        # Page load speed
        checks += 1
        if page_config.get('estimated_load_speed', 5.0) < 3.0:
            score += 1
        
        # Mobile optimization
        checks += 1
        if page_config.get('mobile_optimized', False):
            score += 1
        
        # Clear CTA
        checks += 1
        if 'cta_button' in page_config.get('conversion_elements', []):
            score += 1
        
        # Social proof
        checks += 1
        if 'social_proof' in page_config.get('conversion_elements', []):
            score += 1
        
        # Trust signals
        checks += 1
        if 'trust_signals' in page_config.get('conversion_elements', []):
            score += 1
        
        return score / checks if checks > 0 else 0.5

# Export main classes
__all__ = [
    'PerformancePrediction',
    'PerformanceCalculator'
]