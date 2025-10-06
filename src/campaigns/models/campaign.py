# src/campaigns/models/campaign.py

from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid
import enum

from src.core.database.base import Base

class CampaignStatusEnum(str, enum.Enum):
    """Campaign status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CampaignTypeEnum(str, enum.Enum):
    """Campaign type enumeration"""
    EMAIL_SEQUENCE = "email_sequence"
    SOCIAL_MEDIA = "social_media"
    CONTENT_MARKETING = "content_marketing"
    AFFILIATE_PROMOTION = "affiliate_promotion"
    PRODUCT_LAUNCH = "product_launch"

class Campaign(Base):
    """Campaign model for marketing campaigns"""
    __tablename__ = "campaigns"

    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Campaign classification - use strings to match database enum values exactly
    campaign_type = Column(String(50), nullable=False)
    status = Column(String(20), default="draft")
    
    # Ownership
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Campaign configuration
    target_audience = Column(Text, nullable=True)
    goals = Column(JSONB, nullable=True)  # JSON array of goals
    settings = Column(JSONB, nullable=True)  # Campaign-specific settings
    messaging_focus = Column(Text, nullable=True)  # Messaging focus for landing page generation
    
    # Intelligence integration
    intelligence_id = Column(UUID(as_uuid=True), nullable=True)  # Link to intelligence data
    intelligence_status = Column(String(50), default="pending")  # pending, processing, completed, failed
    
    # Workflow tracking
    workflow_step = Column(String(50), default="INITIAL")
    workflow_data = Column(JSONB, nullable=True)
    is_workflow_complete = Column(Boolean, default=False)
    
    # Campaign content tracking
    sources_count = Column(Integer, default=0)  # Number of input sources
    intelligence_count = Column(Integer, default=0)  # Number of intelligence analyses
    generated_content_count = Column(Integer, default=0)  # Number of generated content pieces

    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Integer, default=0)  # In cents
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    launched_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="campaigns")
    company = relationship("Company", back_populates="campaigns")
    storage_files = relationship("UserStorageUsage", back_populates="campaign", cascade="all, delete-orphan")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get campaign performance metrics"""
        ctr = (self.clicks / self.impressions * 100) if self.impressions > 0 else 0
        conversion_rate = (self.conversions / self.clicks * 100) if self.clicks > 0 else 0
        
        return {
            "impressions": self.impressions,
            "clicks": self.clicks,
            "conversions": self.conversions,
            "revenue": self.revenue / 100,  # Convert cents to dollars
            "ctr": round(ctr, 2),
            "conversion_rate": round(conversion_rate, 2),
            "roas": round(self.revenue / 100, 2) if self.revenue > 0 else 0
        }
    
    def update_workflow_step(self, step: str, step_data: Optional[Dict[str, Any]] = None):
        """Update workflow progress"""
        self.workflow_step = step
        
        if step_data:
            current_data = self.workflow_data or {}
            current_data.update({f"step_{step}": step_data})
            self.workflow_data = current_data
            
        self.updated_at = datetime.now(timezone.utc)
    
    def mark_workflow_complete(self):
        """Mark workflow as complete"""
        self.is_workflow_complete = True
        self.workflow_step = "COMPLETE"
        self.updated_at = datetime.now(timezone.utc)
    
    def launch_campaign(self):
        """Launch the campaign"""
        self.status = "active"
        self.launched_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def pause_campaign(self):
        """Pause the campaign"""
        self.status = "paused"
        self.updated_at = datetime.now(timezone.utc)
    
    def complete_campaign(self):
        """Complete the campaign"""
        self.status = "completed"
        self.completed_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert campaign to dictionary"""
        return {
            "id": str(self.id),
            "title": self.name,  # Required by CampaignResponse
            "name": self.name,   # Legacy field
            "display_name": self.name,  # Required by CampaignResponse
            "description": self.description,
            "campaign_type": self.campaign_type,  # Already a string now
            "status": self.status,  # Already a string now
            "user_id": str(self.user_id),
            "company_id": str(self.company_id),
            "target_audience": self.target_audience,
            "goals": self.goals or [],
            "intelligence_status": self.intelligence_status,
            
            # Required workflow object
            "workflow": {
                "current_step": 0 if not self.workflow_step or self.workflow_step == "INITIAL" else 1,
                "current_state": self.workflow_step or "INITIAL",
                "completion_percentage": self.completion_percentage if hasattr(self, 'completion_percentage') else 0,
                "is_complete": self.is_workflow_complete,
                "auto_analysis_status": "PENDING"
            },
            
            # Required counters object
            "counters": {
                "sources": 0,
                "intelligence": 1 if self.intelligence_id else 0,
                "content": 0
            },
            
            # Required performance object
            "performance": self.get_performance_metrics(),
            
            # Timestamps as strings
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "launched_at": self.launched_at.isoformat() if self.launched_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def __repr__(self):
        return f"<Campaign(name='{self.name}', type='{self.campaign_type}', status='{self.status}')>"