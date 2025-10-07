# =====================================
# File: src/core/database/models.py
# =====================================

"""
Base database models and mixins for CampaignForge

Provides common model patterns and the consolidated intelligence schema.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Float, Boolean, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, List, Optional
import uuid

# Import Base from the main database base module to ensure consistency
from src.core.database.base import Base


class TimestampMixin:
    """Mixin for automatic timestamp management."""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )


class UserMixin:
    """Mixin for user association."""
    
    user_id = Column(String, nullable=False, index=True)
    company_id = Column(String, nullable=True, index=True)


# =====================================
# CONSOLIDATED INTELLIGENCE SCHEMA
# =====================================

class IntelligenceCore(Base, TimestampMixin, UserMixin):
    """
    Core intelligence metadata table with complete analysis data storage.

    This is the main table for intelligence records including the complete
    intelligence data from the 3-stage analysis pipeline.
    """
    __tablename__ = "intelligence_core"

    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PostgreSQLUUID(as_uuid=True), nullable=False, index=True)
    company_id = Column(PostgreSQLUUID(as_uuid=True), nullable=True, index=True)
    product_name = Column(String, nullable=False, index=True)
    salespage_url = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.0, index=True)
    analysis_method = Column(String, nullable=False)  # 'fast', 'deep', 'enhanced'

    # Complete intelligence data storage (thousands of characters)
    full_analysis_data = Column(JSON, nullable=True)  # Complete intelligence from 3-stage pipeline
    
    # Relationships
    product_data = relationship("ProductData", back_populates="intelligence", cascade="all, delete-orphan")
    market_data = relationship("MarketData", back_populates="intelligence", cascade="all, delete-orphan")
    research_links = relationship("IntelligenceResearch", back_populates="intelligence", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_intelligence_user_product', 'user_id', 'product_name'),
        Index('idx_intelligence_confidence', 'confidence_score'),
        Index('idx_intelligence_method', 'analysis_method'),
    )


class ProductData(Base):
    """Normalized product information table."""
    __tablename__ = "product_data"

    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intelligence_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("intelligence_core.id", ondelete="CASCADE"), nullable=False)
    
    # Product attributes as JSON arrays for flexibility
    features = Column(JSON, default=list)  # List of product features
    benefits = Column(JSON, default=list)  # List of benefits
    ingredients = Column(JSON, default=list)  # List of ingredients
    conditions = Column(JSON, default=list)  # List of health conditions
    usage_instructions = Column(JSON, default=list)  # List of usage instructions
    
    # Relationship
    intelligence = relationship("IntelligenceCore", back_populates="product_data")
    
    __table_args__ = (
        Index('idx_product_intelligence', 'intelligence_id'),
    )


class MarketData(Base):
    """Market and positioning data table."""
    __tablename__ = "market_data"

    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intelligence_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("intelligence_core.id", ondelete="CASCADE"), nullable=False)
    
    category = Column(String, nullable=True, index=True)
    positioning = Column(Text, nullable=True)
    competitive_advantages = Column(JSON, default=list)  # List of competitive advantages
    target_audience = Column(Text, nullable=True)
    
    # Relationship
    intelligence = relationship("IntelligenceCore", back_populates="market_data")
    
    __table_args__ = (
        Index('idx_market_intelligence', 'intelligence_id'),
        Index('idx_market_category', 'category'),
    )


class KnowledgeBase(Base, TimestampMixin):
    """Centralized research repository with deduplication."""
    __tablename__ = "knowledge_base"

    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_hash = Column(String, unique=True, nullable=False, index=True)  # For deduplication
    content = Column(Text, nullable=False)
    research_type = Column(String, nullable=False, index=True)  # 'scientific', 'market', 'competitor'
    source_metadata = Column(JSON, default=dict)  # Source information
    
    # Relationships
    intelligence_links = relationship("IntelligenceResearch", back_populates="research", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_knowledge_type', 'research_type'),
        Index('idx_knowledge_hash', 'content_hash'),
    )


class IntelligenceResearch(Base):
    """Many-to-many relationship between intelligence and research."""
    __tablename__ = "intelligence_research"

    id = Column(PostgreSQLUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    intelligence_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("intelligence_core.id", ondelete="CASCADE"), nullable=False)
    research_id = Column(PostgreSQLUUID(as_uuid=True), ForeignKey("knowledge_base.id", ondelete="CASCADE"), nullable=False)
    relevance_score = Column(Float, default=0.0, index=True)
    
    # Relationships
    intelligence = relationship("IntelligenceCore", back_populates="research_links")
    research = relationship("KnowledgeBase", back_populates="intelligence_links")
    
    __table_args__ = (
        Index('idx_intel_research_link', 'intelligence_id', 'research_id'),
        Index('idx_research_relevance', 'relevance_score'),
    )


class ScrapedContent(Base, TimestampMixin):
    """Deduplicated content cache for web scraping."""
    __tablename__ = "scraped_content"
    
    url_hash = Column(String, primary_key=True)  # SHA-256 hash of URL
    url = Column(Text, nullable=False, index=True)
    content = Column(Text, nullable=False)
    title = Column(String, nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_scraped_url', 'url'),
        Index('idx_scraped_date', 'scraped_at'),
    )


class Waitlist(Base, TimestampMixin):
    """Simple waitlist model for tracking signups"""
    __tablename__ = "waitlist"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    referrer = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    is_notified = Column(Boolean, default=False)
    
    __table_args__ = (
        Index('idx_waitlist_email', 'email'),
        Index('idx_waitlist_created', 'created_at'),
    )