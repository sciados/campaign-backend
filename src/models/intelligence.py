# src/models/intelligence.py - FIXED WITH PROPER FOREIGN KEYS
"""
Intelligence models - COMPLETELY REWRITTEN for new optimized database schema
FIXED: Added missing ForeignKey constraints and proper relationships
"""
import json
import uuid
from sqlalchemy import Column, String, Text, Float, Boolean, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel, Field
from typing import List, Optional, Dict, Any, Literal

# FIXED: Consistent imports with proper paths
try:
    from .base import BaseModel, EnumSerializerMixin
except ImportError:
    # Fallback for different import structures
    try:
        from src.models.base import BaseModel, EnumSerializerMixin
    except ImportError:
        # Basic fallback
        from sqlalchemy.ext.declarative import declarative_base
        BaseModel = declarative_base()
        
        class EnumSerializerMixin:
            def _serialize_enum_field(self, field_value):
                if field_value is None:
                    return {}
                if isinstance(field_value, str):
                    try:
                        return json.loads(field_value)
                    except:
                        return {}
                return field_value or {}

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

# NEW OPTIMIZED SCHEMA MODELS
class IntelligenceCore(BaseModel, EnumSerializerMixin):
    """Core intelligence table - replaces campaign intelligence"""
    __tablename__ = "intelligence_core"
    
    # Core fields - matches BaseModel pattern with updated_at
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name = Column(Text, nullable=False)
    source_url = Column(Text, nullable=False)
    confidence_score = Column(Float)
    analysis_method = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships to normalized data
    product_data = relationship("ProductData", back_populates="intelligence_core", uselist=False, cascade="all, delete-orphan")
    market_data = relationship("MarketData", back_populates="intelligence_core", uselist=False, cascade="all, delete-orphan")
    research_links = relationship("IntelligenceResearch", back_populates="intelligence", cascade="all, delete-orphan")
    generated_content = relationship("GeneratedContent", back_populates="intelligence_source")
    
    def get_complete_intelligence(self) -> Dict[str, Any]:
        """Reconstruct complete intelligence data from normalized tables"""
        intelligence = {
            "analysis_id": str(self.id),
            "product_name": self.product_name,
            "source_url": self.source_url,
            "confidence_score": self.confidence_score,
            "analysis_method": self.analysis_method,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            
            # Reconstruct offer intelligence from product_data
            "offer_intelligence": {},
            
            # Reconstruct competitive intelligence from market_data  
            "competitive_intelligence": {},
            
            # Reconstruct psychology intelligence from market_data
            "psychology_intelligence": {},
            
            # Basic content and brand intelligence
            "content_intelligence": {
                "analysis_method": self.analysis_method,
                "source_type": "normalized_intelligence"
            },
            "brand_intelligence": {
                "product_name": self.product_name,
                "brand_positioning": ""
            }
        }
        
        # Add product data if available
        if self.product_data:
            intelligence["offer_intelligence"] = {
                "products": [self.product_name],
                "key_features": self.product_data.features or [],
                "primary_benefits": self.product_data.benefits or [],
                "ingredients_list": self.product_data.ingredients or [],
                "target_conditions": self.product_data.conditions or [],
                "usage_instructions": self.product_data.usage_instructions or [],
                "value_propositions": [f"Primary product: {self.product_name}"],
                "unique_selling_points": [],
                "guarantees": [],
                "insights": []
            }
        
        # Add market data if available
        if self.market_data:
            intelligence["competitive_intelligence"] = {
                "market_category": self.market_data.category or "",
                "market_positioning": self.market_data.positioning or "",
                "competitive_advantages": self.market_data.competitive_advantages or [],
                "differentiation_factors": [],
                "target_market_gaps": [],
                "competitor_weaknesses": [],
                "market_trends": []
            }
            
            intelligence["psychology_intelligence"] = {
                "target_audience": self.market_data.target_audience or "",
                "emotional_triggers": [],
                "pain_points": [],
                "persuasion_techniques": [],
                "psychological_appeals": [],
                "motivation_factors": []
            }
            
            # Update brand intelligence with market data
            intelligence["brand_intelligence"]["brand_positioning"] = self.market_data.positioning or ""
        
        # Add research context if available
        if self.research_links:
            research_info = []
            for link in self.research_links:
                if link.research:
                    research_info.append({
                        "research_type": link.research.research_type,
                        "relevance_score": link.relevance_score,
                        "content_preview": (link.research.content or "")[:100] + "..."
                    })
            
            intelligence["research_enhanced"] = len(research_info) > 0
            intelligence["research_links"] = research_info
        
        return intelligence
    
    def get_content_generation_stats(self) -> Dict[str, Any]:
        """Get statistics about content generated from this intelligence source"""
        if not self.generated_content:
            return {
                "total_content_generated": 0,
                "content_types": [],
                "average_user_rating": 0.0,
                "published_content_count": 0,
                "total_views": 0
            }
        
        content_items = self.generated_content
        total_content = len(content_items)
        content_types = list(set(item.content_type for item in content_items))
        
        # Calculate ratings
        ratings = [item.user_rating for item in content_items if item.user_rating is not None]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        # Count published content
        published_count = sum(1 for item in content_items if item.is_published)
        
        # Sum total views
        total_views = sum(item.view_count or 0 for item in content_items)
        
        return {
            "total_content_generated": total_content,
            "content_types": content_types,
            "average_user_rating": round(avg_rating, 2),
            "published_content_count": published_count,
            "total_views": total_views,
            "content_success_rate": round((published_count / total_content * 100), 1) if total_content > 0 else 0.0
        }

class ProductData(BaseModel, EnumSerializerMixin):
    """Focused product data - normalized from offer_intelligence"""
    __tablename__ = "product_data"
    
    intelligence_id = Column(UUID(as_uuid=True), ForeignKey("intelligence_core.id"), primary_key=True)
    features = Column(ARRAY(Text))
    benefits = Column(ARRAY(Text))
    ingredients = Column(ARRAY(Text))
    conditions = Column(ARRAY(Text))
    usage_instructions = Column(ARRAY(Text))
    
    # Relationships
    intelligence_core = relationship("IntelligenceCore", back_populates="product_data")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with null handling"""
        return {
            "features": self.features or [],
            "benefits": self.benefits or [],
            "ingredients": self.ingredients or [],
            "conditions": self.conditions or [],
            "usage_instructions": self.usage_instructions or []
        }

class MarketData(BaseModel, EnumSerializerMixin):
    """Market insights - normalized from competitive_intelligence and psychology_intelligence"""
    __tablename__ = "market_data"
    
    intelligence_id = Column(UUID(as_uuid=True), ForeignKey("intelligence_core.id"), primary_key=True)
    category = Column(Text)
    positioning = Column(Text)
    competitive_advantages = Column(ARRAY(Text))
    target_audience = Column(Text)
    
    # Relationships
    intelligence_core = relationship("IntelligenceCore", back_populates="market_data")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with null handling"""
        return {
            "category": self.category or "",
            "positioning": self.positioning or "",
            "competitive_advantages": self.competitive_advantages or [],
            "target_audience": self.target_audience or ""
        }

class KnowledgeBase(BaseModel, EnumSerializerMixin):
    """Centralized research knowledge"""
    __tablename__ = "knowledge_base"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_hash = Column(Text, unique=True, nullable=False)
    content = Column(Text, nullable=False)
    research_type = Column(Text)  # 'clinical', 'market', 'ingredient'
    source_metadata = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    intelligence_links = relationship("IntelligenceResearch", back_populates="research")
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get metadata with proper serialization"""
        return self._serialize_enum_field(self.source_metadata) if self.source_metadata else {}
    
    def get_content_preview(self, length: int = 200) -> str:
        """Get content preview"""
        if not self.content:
            return ""
        return self.content[:length] + "..." if len(self.content) > length else self.content

class IntelligenceResearch(BaseModel, EnumSerializerMixin):
    """Link intelligence to research"""
    __tablename__ = "intelligence_research"
    
    intelligence_id = Column(UUID(as_uuid=True), ForeignKey("intelligence_core.id"), primary_key=True)
    research_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_base.id"), primary_key=True)
    relevance_score = Column(Float)
    
    # Relationships
    intelligence = relationship("IntelligenceCore", back_populates="research_links")
    research = relationship("KnowledgeBase", back_populates="intelligence_links")

class ScrapedContent(BaseModel, EnumSerializerMixin):
    """Content cache (deduplicated)"""
    __tablename__ = "scraped_content"
    
    url_hash = Column(Text, primary_key=True)
    url = Column(Text)
    content = Column(Text)
    title = Column(Text)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

class GeneratedContent(BaseModel, EnumSerializerMixin):
    """
    Generated content - FIXED with proper foreign key constraints
    """
    __tablename__ = "generated_content"
    
    # UUID PRIMARY KEY
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # CORE CONTENT FIELDS
    content_type = Column(String(50), nullable=False)
    content_title = Column(String(500))
    content_body = Column(Text, nullable=False)
    content_metadata = Column(JSONB, default={})
    
    # GENERATION TRACKING
    generation_settings = Column(JSONB, default={})
    intelligence_used = Column(JSONB, default={})
    performance_data = Column(JSONB, default={})
    
    # USER INTERACTION
    user_rating = Column(Integer)  # 1-5 rating from users
    is_published = Column(Boolean, default=False)
    
    # TIMESTAMPS
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # PERFORMANCE METRICS
    performance_score = Column(Float)
    view_count = Column(Integer, default=0)
    
    # FOREIGN KEYS - FIXED to match database_models.py exactly
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"))
    
    # Link to new intelligence schema
    intelligence_id = Column(UUID(as_uuid=True), ForeignKey("intelligence_core.id", ondelete="SET NULL"))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # RELATIONSHIPS - PROPERLY DEFINED with back_populates
    user = relationship("User", back_populates="generated_content")
    company = relationship("Company", back_populates="generated_content")
    campaign = relationship("Campaign", back_populates="generated_content")
    intelligence_source = relationship("IntelligenceCore", back_populates="generated_content")
    
    def get_generation_metadata(self) -> Dict[str, Any]:
        """Get generation metadata with proper serialization"""
        return {
            "generation_settings": self._serialize_enum_field(self.generation_settings),
            "intelligence_used": self._serialize_enum_field(self.intelligence_used),
            "content_metadata": self._serialize_enum_field(self.content_metadata)
        }
    
    def get_intelligence_source_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary of the intelligence source that generated this content"""
        if not self.intelligence_source:
            return None
        
        source = self.intelligence_source
        return {
            "source_id": str(source.id),
            "product_name": source.product_name,
            "source_url": source.source_url,
            "confidence_score": source.confidence_score,
            "analysis_method": source.analysis_method,
            "created_at": source.created_at.isoformat() if source.created_at else None
        }
    
    def get_source_attribution(self) -> str:
        """Get user-friendly source attribution text"""
        if not self.intelligence_source:
            return "Generated from campaign intelligence"
        
        source = self.intelligence_source
        attribution = f"Generated from: {source.product_name}"
        
        if source.confidence_score:
            attribution += f" ({int(source.confidence_score * 100)}% confidence)"
        
        return attribution

# Legacy compatibility models for API
class AnalysisRequest(PydanticBaseModel):
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

class IntelligenceResponse(PydanticBaseModel):
    analysis_id: str = Field(..., description="Unique analysis ID")
    product_name: str = Field(..., description="Extracted product name")
    source_url: str = Field(..., description="Source URL analyzed")
    confidence_score: float = Field(..., description="Analysis confidence score")
    offer_intelligence: Dict[str, Any] = Field(..., description="Product offer intelligence")
    competitive_intelligence: Dict[str, Any] = Field(..., description="Market competitive intelligence")
    psychology_intelligence: Dict[str, Any] = Field(..., description="Target audience psychology")
    content_intelligence: Dict[str, Any] = Field(..., description="Content analysis")
    brand_intelligence: Dict[str, Any] = Field(..., description="Brand positioning intelligence")
    research_enhanced: bool = Field(default=False, description="Whether enhanced with research")
    analysis_method: str = Field(..., description="Analysis method used")

# Utility functions for working with new schema
def create_intelligence_from_analysis(analysis_data: Dict[str, Any]) -> IntelligenceCore:
    """Create IntelligenceCore from analysis data"""
    intelligence = IntelligenceCore(
        product_name=analysis_data.get("product_name", "Unknown Product"),
        source_url=analysis_data.get("source_url", ""),
        confidence_score=analysis_data.get("confidence_score", 0.0),
        analysis_method=analysis_data.get("analysis_method", "standard")
    )
    
    return intelligence

def create_product_data_from_analysis(intelligence_id: str, analysis_data: Dict[str, Any]) -> ProductData:
    """Create ProductData from analysis data"""
    offer_intel = analysis_data.get("offer_intelligence", {})
    
    product_data = ProductData(
        intelligence_id=intelligence_id,
        features=offer_intel.get("key_features", []),
        benefits=offer_intel.get("primary_benefits", []),
        ingredients=offer_intel.get("ingredients_list", []),
        conditions=offer_intel.get("target_conditions", []),
        usage_instructions=offer_intel.get("usage_instructions", [])
    )
    
    return product_data

def create_market_data_from_analysis(intelligence_id: str, analysis_data: Dict[str, Any]) -> MarketData:
    """Create MarketData from analysis data"""
    competitive_intel = analysis_data.get("competitive_intelligence", {})
    psychology_intel = analysis_data.get("psychology_intelligence", {})
    
    market_data = MarketData(
        intelligence_id=intelligence_id,
        category=competitive_intel.get("market_category", ""),
        positioning=competitive_intel.get("market_positioning", ""),
        competitive_advantages=competitive_intel.get("competitive_advantages", []),
        target_audience=psychology_intel.get("target_audience", "")
    )
    
    return market_data

# Export all models for easy imports
__all__ = [
    # New optimized schema models
    'IntelligenceCore',
    'ProductData', 
    'MarketData',
    'KnowledgeBase',
    'IntelligenceResearch',
    'ScrapedContent',
    
    # Updated models
    'GeneratedContent',
    
    # Enums
    'IntelligenceSourceType',
    'AnalysisStatus',
    
    # Pydantic models
    'AnalysisRequest',
    'IntelligenceResponse',
    
    # Utility functions
    'create_intelligence_from_analysis',
    'create_product_data_from_analysis',
    'create_market_data_from_analysis'
]