# src/models/email_subject_templates.py
"""
Database model for storing proven email subject line templates
These serve as AI reference patterns, not fallbacks
"""

import re
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum
from src.models.base import Base

class SubjectLineCategory(enum.Enum):
    """Psychology-based subject line categories"""
    CURIOSITY_GAP = "curiosity_gap"
    URGENCY_SCARCITY = "urgency_scarcity" 
    SOCIAL_PROOF = "social_proof"
    PERSONAL_BENEFIT = "personal_benefit"
    QUESTION_HOOKS = "question_hooks"
    VALUE_PROMISE = "value_promise"
    TRANSFORMATION = "transformation"
    AUTHORITY_SCIENTIFIC = "authority_scientific"
    EMOTIONAL_TRIGGERS = "emotional_triggers"
    INSIDER_SECRET = "insider_secret"

class PerformanceLevel(enum.Enum):
    """Performance level of subject line templates"""
    EXPERIMENTAL = "experimental"  # New/untested
    GOOD = "good"                 # Decent performance
    HIGH_PERFORMING = "high_performing"  # Proven performers
    TOP_TIER = "top_tier"         # Best of the best

class EmailSubjectTemplate(Base):
    """
    Stores proven email subject line templates for AI reference
    These are used as patterns, not direct fallbacks
    """
    __tablename__ = "email_subject_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template details
    template_text = Column(String(200), nullable=False, index=True)
    category = Column(SQLEnum(SubjectLineCategory), nullable=False, index=True)
    performance_level = Column(SQLEnum(PerformanceLevel), nullable=False, default=PerformanceLevel.EXPERIMENTAL)
    
    # Performance metrics
    avg_open_rate = Column(Float, default=0.0)  # Average open rate for this template
    total_uses = Column(Integer, default=0)     # How many times used
    total_opens = Column(Integer, default=0)    # Total opens achieved
    
    # Template metadata
    psychology_triggers = Column(JSONB)  # List of psychology triggers used
    keywords = Column(JSONB)             # Key words/phrases in template
    character_count = Column(Integer)    # Length for mobile optimization
    
    # Classification
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Manually verified as good
    source = Column(String(100))  # Where this template came from
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_used_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<EmailSubjectTemplate('{self.template_text[:50]}...', {self.category.value})>"

class EmailSubjectPerformance(Base):
    """
    Tracks performance of generated subject lines for learning
    """
    __tablename__ = "email_subject_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Reference to template used (if any)
    template_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Actual subject line used
    subject_line = Column(String(200), nullable=False)
    product_name = Column(String(100), nullable=False)
    category_used = Column(SQLEnum(SubjectLineCategory), nullable=False)
    
    # Performance data
    emails_sent = Column(Integer, default=0)
    emails_opened = Column(Integer, default=0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    
    # Generation details
    was_ai_generated = Column(Boolean, default=True)
    ai_provider_used = Column(String(50))
    generation_method = Column(String(100))  # "ai_with_template_reference", "pure_ai", "fallback"
    
    # Campaign context
    campaign_id = Column(UUID(as_uuid=True), index=True)
    email_number_in_sequence = Column(Integer)
    strategic_angle = Column(String(50))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    performance_updated_at = Column(DateTime(timezone=True))
    
    def calculate_open_rate(self):
        """Calculate and update open rate"""
        if self.emails_sent > 0:
            self.open_rate = (self.emails_opened / self.emails_sent) * 100
        return self.open_rate