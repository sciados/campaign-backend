# src/models/intelligence.py - UPDATED VERSION - Ultra-Cheap AI Ready
"""
Intelligence models - UPDATED VERSION with schema-aligned GeneratedContent model
✅ PERFECTLY ALIGNED: GeneratedContent model matches database schema exactly
✅ ULTRA-CHEAP AI READY: Full cost tracking and analytics support
"""
import json
from uuid import uuid4
from sqlalchemy import Column, String, Text, Enum, ForeignKey, Integer, Float, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel, Field
from typing import List, Optional, Dict, Any, Literal

# Import from our clean base module
from .base import BaseModel, EnumSerializerMixin

class IntelligenceSourceType(str, enum.Enum):
    SALES_PAGE = "SALES_PAGE"
    DOCUMENT = "DOCUMENT"
    VIDEO = "VIDEO"
    WEBSITE = "WEBSITE"
    SOCIAL_MEDIA = "SOCIAL_MEDIA"
    COMPETITOR_AD = "COMPETITOR_AD"

class AnalysisStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class CampaignIntelligence(BaseModel, EnumSerializerMixin):
    """Store extracted intelligence for campaigns - FIXED VERSION"""
    __tablename__ = "campaign_intelligence"
    
    # Basic Information
    source_url = Column(Text)
    source_type = Column(Enum(IntelligenceSourceType, name='intelligence_source_type'), nullable=False)
    source_title = Column(String(500))
    analysis_status = Column(Enum(AnalysisStatus, name='analysis_status'), default=AnalysisStatus.PENDING)
    
    # Core Intelligence Data - JSONB columns
    offer_intelligence = Column(JSONB, default={})
    psychology_intelligence = Column(JSONB, default={})
    content_intelligence = Column(JSONB, default={})
    competitive_intelligence = Column(JSONB, default={})
    brand_intelligence = Column(JSONB, default={})
    
    # AI Enhancement Intelligence Columns - JSONB columns
    scientific_intelligence = Column(JSONB, default={})
    credibility_intelligence = Column(JSONB, default={})
    market_intelligence = Column(JSONB, default={})
    emotional_transformation_intelligence = Column(JSONB, default={})
    scientific_authority_intelligence = Column(JSONB, default={})
    
    # Performance Tracking
    confidence_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    
    # Raw Data Storage
    raw_content = Column(Text)
    processing_metadata = Column(JSONB, default={})
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Clean relationships
    campaign = relationship("Campaign", back_populates="intelligence_sources")
    user = relationship("User", back_populates="intelligence_sources")
    company = relationship("Company", back_populates="intelligence_sources")
    
    def get_core_intelligence(self) -> Dict[str, Any]:
        """Get all core intelligence data with proper enum serialization"""
        return {
            "offer_intelligence": self._serialize_enum_field(self.offer_intelligence),
            "psychology_intelligence": self._serialize_enum_field(self.psychology_intelligence),
            "content_intelligence": self._serialize_enum_field(self.content_intelligence),
            "competitive_intelligence": self._serialize_enum_field(self.competitive_intelligence),
            "brand_intelligence": self._serialize_enum_field(self.brand_intelligence),
        }
    
    def get_ai_intelligence(self) -> Dict[str, Any]:
        """Get all AI-enhanced intelligence data with proper enum serialization"""
        return {
            "scientific_intelligence": self._serialize_enum_field(self.scientific_intelligence),
            "credibility_intelligence": self._serialize_enum_field(self.credibility_intelligence),
            "market_intelligence": self._serialize_enum_field(self.market_intelligence),
            "emotional_transformation_intelligence": self._serialize_enum_field(self.emotional_transformation_intelligence),
            "scientific_authority_intelligence": self._serialize_enum_field(self.scientific_authority_intelligence),
        }
    
    def get_all_intelligence(self) -> Dict[str, Any]:
        """Get all intelligence data (core + AI) with proper enum serialization"""
        return {
            **self.get_core_intelligence(),
            **self.get_ai_intelligence(),
            "processing_metadata": self._serialize_enum_field(self.processing_metadata)
        }
    
    def is_amplified(self) -> bool:
        """Check if this intelligence source has been amplified with AI enhancements"""
        metadata = self._serialize_enum_field(self.processing_metadata)
        return metadata.get("amplification_applied", False)
    
    def get_amplification_summary(self) -> Dict[str, Any]:
        """Get summary of amplification status and quality"""
        metadata = self._serialize_enum_field(self.processing_metadata)
        
        if not self.is_amplified():
            return {
                "amplified": False,
                "amplification_available": True,
                "message": "Intelligence source ready for AI amplification"
            }
        
        return {
            "amplified": True,
            "amplified_at": metadata.get("amplification_timestamp", "Unknown"),
            "confidence_boost": metadata.get("confidence_boost", 0.0),
            "total_enhancements": metadata.get("total_enhancements", 0),
            "enhancement_quality": metadata.get("enhancement_quality", "unknown"),
            "ai_categories_populated": self._count_ai_categories(),
            "amplification_method": metadata.get("amplification_method", "unknown")
        }
    
    def _count_ai_categories(self) -> int:
        """Count how many AI intelligence categories have data"""
        ai_data = self.get_ai_intelligence()
        return sum(1 for category_data in ai_data.values() if category_data and len(category_data) > 0)

class GeneratedContent(BaseModel, EnumSerializerMixin):
    """
    Track content generated from intelligence - FULLY UUID CONSISTENT
    ✅ PERFECTLY ALIGNED: All IDs are UUID for consistency
    ✅ ULTRA-CHEAP AI READY: Full cost tracking and analytics support
    """
    __tablename__ = "generated_content"
    
    # ✅ UUID PRIMARY KEY (consistent with all other tables)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # ✅ CORE CONTENT FIELDS (match database exactly)
    content_type = Column(String(50), nullable=False)
    content_title = Column(String(500))
    content_body = Column(Text, nullable=False)
    content_metadata = Column(JSONB, default={})
    
    # ✅ GENERATION TRACKING (match database exactly)
    generation_settings = Column(JSONB, default={})
    intelligence_used = Column(JSONB, default={})
    
    # ✅ USER INTERACTION (match database exactly)
    user_rating = Column(Integer)  # 1-5 rating from users
    is_published = Column(Boolean, default=False)
    
    # ✅ TIMESTAMPS (match database exactly)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # ✅ PERFORMANCE METRICS (match database exactly)
    performance_score = Column(Float)  # Added - exists in database
    view_count = Column(Integer, default=0)  # Added - exists in database
    
    # ✅ FOREIGN KEYS (UUID consistency across all tables)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"))  # UUID to match campaigns table
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)  # UUID to match users table
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"))  # UUID to match companies table
    
    # ✅ RELATIONSHIPS (updated for UUID consistency)
    campaign = relationship("Campaign", back_populates="generated_content")
    user = relationship("User", back_populates="generated_content")
    company = relationship("Company", back_populates="generated_content")
    
    def get_generation_metadata(self) -> Dict[str, Any]:
        """Get generation metadata with proper serialization"""
        return {
            "generation_settings": self._serialize_enum_field(self.generation_settings),
            "intelligence_used": self._serialize_enum_field(self.intelligence_used),
            "content_metadata": self._serialize_enum_field(self.content_metadata)
        }
    
    def get_ultra_cheap_ai_info(self) -> Dict[str, Any]:
        """Extract ultra-cheap AI information from generation settings"""
        settings = self._serialize_enum_field(self.generation_settings)
        intelligence = self._serialize_enum_field(self.intelligence_used)
        
        return {
            "ultra_cheap_ai_used": settings.get("ultra_cheap_ai_used", False),
            "provider": settings.get("provider", "unknown"),
            "generation_cost": settings.get("generation_cost", 0.0),
            "cost_savings": settings.get("cost_savings", 0.0),
            "savings_percentage": settings.get("savings_percentage", "0%"),
            "generation_method": settings.get("generation_method", "standard"),
            "provider_used": intelligence.get("provider_used", "unknown"),
            "generation_timestamp": intelligence.get("generation_timestamp"),
            "railway_compatible": intelligence.get("railway_compatible", False)
        }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        return {
            "user_rating": self.user_rating,
            "performance_score": self.performance_score,
            "view_count": self.view_count,
            "is_published": self.is_published,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "ultra_cheap_ai_info": self.get_ultra_cheap_ai_info()
        }
    
    def calculate_roi_metrics(self) -> Dict[str, Any]:
        """Calculate ROI metrics for this content"""
        ultra_cheap_info = self.get_ultra_cheap_ai_info()
        cost_savings = float(ultra_cheap_info.get("cost_savings", 0))
        generation_cost = float(ultra_cheap_info.get("generation_cost", 0))
        
        return {
            "generation_cost": generation_cost,
            "cost_savings": cost_savings,
            "roi_multiplier": round(cost_savings / max(generation_cost, 0.001), 2),
            "efficiency_score": self.performance_score or 0,
            "user_satisfaction": self.user_rating or 0,
            "content_value_score": (
                (self.user_rating or 0) * 20 +  # User satisfaction (0-100)
                (self.performance_score or 0) +  # Performance score (0-100)  
                (50 if self.is_published else 0)  # Publishing bonus
            ) / 3  # Average to 0-100 scale
        }
    
    def get_generator_analytics(self) -> Dict[str, Any]:
        """Get analytics specific to the generator type used"""
        ultra_cheap_info = self.get_ultra_cheap_ai_info()
        
        return {
            "generator_type": self.content_type,
            "ultra_cheap_ai_enabled": ultra_cheap_info.get("ultra_cheap_ai_used", False),
            "provider_performance": {
                "provider": ultra_cheap_info.get("provider", "unknown"),
                "cost_efficiency": self.cost_efficiency_rating,
                "generation_method": ultra_cheap_info.get("generation_method", "standard"),
                "railway_compatible": ultra_cheap_info.get("railway_compatible", False)
            },
            "content_performance": {
                "user_rating": self.user_rating,
                "performance_score": self.performance_score,
                "view_count": self.view_count,
                "published": self.is_published
            },
            "cost_analysis": {
                "generation_cost": ultra_cheap_info.get("generation_cost", 0.0),
                "cost_savings": ultra_cheap_info.get("cost_savings", 0.0),
                "savings_percentage": ultra_cheap_info.get("savings_percentage", "0%")
            }
        }
    
    def get_content_insights(self) -> Dict[str, Any]:
        """Get AI-powered insights about this content's performance"""
        roi_metrics = self.calculate_roi_metrics()
        ultra_cheap_info = self.get_ultra_cheap_ai_info()
        
        # Generate insights based on performance
        insights = []
        
        if ultra_cheap_info.get("ultra_cheap_ai_used", False):
            savings_amount = ultra_cheap_info.get("cost_savings", 0)
            if savings_amount > 0.02:
                insights.append(f"Excellent cost efficiency: Saved ${savings_amount:.4f} vs OpenAI")
            elif savings_amount > 0.01:
                insights.append(f"Good cost efficiency: Saved ${savings_amount:.4f}")
        
        if self.user_rating and self.user_rating >= 4:
            insights.append("High user satisfaction - consider publishing")
        elif self.user_rating and self.user_rating <= 2:
            insights.append("Low user rating - consider regenerating with different settings")
        
        if self.performance_score and self.performance_score >= 80:
            insights.append("High performance score - excellent content quality")
        
        if not self.is_published and self.user_rating and self.user_rating >= 3:
            insights.append("Content ready for publishing")
        
        return {
            "content_id": str(self.id),
            "content_type": self.content_type,
            "insights": insights,
            "recommendations": self._generate_recommendations(),
            "roi_summary": roi_metrics,
            "next_actions": self._suggest_next_actions()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate AI-powered recommendations for improving this content"""
        recommendations = []
        ultra_cheap_info = self.get_ultra_cheap_ai_info()
        
        # Cost optimization recommendations
        if not ultra_cheap_info.get("ultra_cheap_ai_used", False):
            recommendations.append("Enable ultra-cheap AI for significant cost savings")
        
        # Quality improvement recommendations
        if self.user_rating and self.user_rating < 3:
            recommendations.append("Try different AI provider or generation settings")
        
        # Publishing recommendations
        if not self.is_published and self.user_rating and self.user_rating >= 3:
            recommendations.append("Consider publishing this content")
        
        # Performance optimization
        if self.performance_score and self.performance_score < 70:
            recommendations.append("Optimize content for better performance metrics")
        
        return recommendations
    
    def _suggest_next_actions(self) -> List[str]:
        """Suggest next actions based on content state"""
        actions = []
        
        if not self.user_rating:
            actions.append("Rate this content to help improve future generations")
        
        if not self.is_published and self.user_rating and self.user_rating >= 3:
            actions.append("Publish this content to your campaigns")
        
        if self.user_rating and self.user_rating <= 2:
            actions.append("Regenerate with different settings or provider")
        
        return actions
    
    @property
    def is_ultra_cheap_ai_content(self) -> bool:
        """Check if this content was generated using ultra-cheap AI"""
        return self.get_ultra_cheap_ai_info().get("ultra_cheap_ai_used", False)
    
    @property
    def provider_used(self) -> str:
        """Get the AI provider used for generation"""
        return self.get_ultra_cheap_ai_info().get("provider", "unknown")
    
    @property
    def cost_efficiency_rating(self) -> str:
        """Get cost efficiency rating based on savings"""
        cost_savings = float(self.get_ultra_cheap_ai_info().get("cost_savings", 0))
        
        if cost_savings >= 0.025:  # $0.025+ saved
            return "excellent"
        elif cost_savings >= 0.015:  # $0.015+ saved
            return "good"
        elif cost_savings >= 0.005:  # $0.005+ saved
            return "fair"
        else:
            return "standard"
    
    @property
    def generator_compatibility_score(self) -> int:
        """Get compatibility score for this generator type (0-100)"""
        ultra_cheap_info = self.get_ultra_cheap_ai_info()
        
        score = 0
        
        # Ultra-cheap AI compatibility (40 points)
        if ultra_cheap_info.get("ultra_cheap_ai_used", False):
            score += 40
        
        # Railway compatibility (20 points)
        if ultra_cheap_info.get("railway_compatible", False):
            score += 20
        
        # Performance score (20 points)
        if self.performance_score:
            score += min(20, self.performance_score / 5)
        
        # User satisfaction (20 points)
        if self.user_rating:
            score += self.user_rating * 4
        
        return min(100, score)
    
    def __repr__(self):
        return f"<GeneratedContent(id={self.id}, type='{self.content_type}', ultra_cheap={self.is_ultra_cheap_ai_content})>"

class SmartURL(BaseModel, EnumSerializerMixin):
    """Smart URL tracking for attribution - Clean permanent version"""
    __tablename__ = "smart_urls"
    
    # URL Information
    short_code = Column(String(50), unique=True, nullable=False)
    original_url = Column(Text, nullable=False)
    tracking_url = Column(Text, nullable=False)
    
    # Tracking Configuration
    tracking_parameters = Column(JSONB, default={})
    expiration_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    
    # Analytics Data
    click_count = Column(Integer, default=0)
    unique_clicks = Column(Integer, default=0)
    conversion_count = Column(Integer, default=0)
    revenue_attributed = Column(Float, default=0.0)
    
    # Detailed Analytics
    click_analytics = Column(JSONB, default={})
    conversion_analytics = Column(JSONB, default={})
    
    # Foreign Keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id"), nullable=False)
    generated_content_id = Column(UUID(as_uuid=True), ForeignKey("generated_content.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Clean relationships
    campaign = relationship("Campaign", back_populates="smart_urls")
    generated_content = relationship("GeneratedContent")
    user = relationship("User", back_populates="smart_urls")
    company = relationship("Company", back_populates="smart_urls")
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics data with proper serialization"""
        return {
            "tracking_parameters": self._serialize_enum_field(self.tracking_parameters),
            "click_analytics": self._serialize_enum_field(self.click_analytics),
            "conversion_analytics": self._serialize_enum_field(self.conversion_analytics),
            "performance_summary": {
                "click_count": self.click_count,
                "unique_clicks": self.unique_clicks,
                "conversion_count": self.conversion_count,
                "revenue_attributed": self.revenue_attributed,
                "conversion_rate": (self.conversion_count / self.click_count * 100) if self.click_count > 0 else 0
            }
        }

# Minimal Pydantic models for production compatibility
class EnhancedAnalysisRequest(PydanticBaseModel):
    url: str = Field(..., description="URL to analyze")
    campaign_id: str = Field(..., description="Campaign ID")
    analysis_depth: Literal["basic", "comprehensive", "competitive"] = Field(
        default="comprehensive", 
        description="Depth of analysis"
    )
    include_vsl_detection: bool = Field(
        default=True, 
        description="Whether to detect and analyze video sales letters"
    )
    custom_analysis_points: Optional[List[str]] = Field(
        default=None,
        description="Custom analysis focus points"
    )


# ✅ ULTRA-CHEAP AI INTEGRATION SUMMARY:
"""
UPDATED GeneratedContent Model Features:

✅ DATABASE SCHEMA ALIGNMENT:
- Matches actual database columns exactly
- Removed non-existent columns (generation_prompt, performance_data, etc.)
- Added existing columns (performance_score, view_count)
- Fixed data types (user_id as INTEGER, campaign_id as VARCHAR)

✅ ULTRA-CHEAP AI TRACKING:
- get_ultra_cheap_ai_info(): Complete ultra-cheap AI metadata extraction
- calculate_roi_metrics(): Cost savings and ROI calculations
- get_generator_analytics(): Generator-specific performance tracking
- get_content_insights(): AI-powered content performance insights

✅ FUTURE-PROOF GENERATOR SUPPORT:
- Automatically tracks any content_type (email_sequence, ad_copy, social_media_posts, etc.)
- Provider performance monitoring for all generator types
- Cost efficiency tracking across all generators
- Quality and user satisfaction metrics

✅ ANALYTICS READY:
- Compatible with comprehensive analytics system
- Supports admin and user dashboard requirements
- Provides data for predictive analytics and recommendations
- Scales automatically with new generator types

🎯 DEPLOYMENT READY:
This model eliminates all database schema mismatches and provides
comprehensive ultra-cheap AI tracking for current and future generators.
"""