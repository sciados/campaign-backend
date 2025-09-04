# src/models/company.py - FIXED VERSION FOR NEW INTELLIGENCE SCHEMA
"""
Company models and related schemas - FIXED for new intelligence schema
REMOVED: Problematic relationships that referenced non-existent columns
ADDED: Methods to access intelligence through campaigns (correct approach)
"""

from sqlalchemy import Column, String, Text, Integer, ForeignKey, Boolean, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

# Import from our clean base module
from .base import BaseModel, EnumSerializerMixin

class CompanySize(str, enum.Enum):
    STARTUP = "startup"
    SMALL = "small" 
    MEDIUM = "medium"
    ENTERPRISE = "enterprise"

class CompanySubscriptionTier(str, enum.Enum):
    free = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    AGENCY = "agency"
    ENTERPRISE = "enterprise"

class MembershipRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"

class MembershipStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"

class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class Company(BaseModel, EnumSerializerMixin):
    """Company model - FIXED for new intelligence schema"""
    __tablename__ = "companies"
    
    # Company Information
    company_name = Column(String(255), nullable=False)
    company_slug = Column(String(100), unique=True, nullable=False, index=True)
    industry = Column(String(100))
    company_size = Column(String(50), default=CompanySize.STARTUP.value)
    website_url = Column(Text)
    
    # Branding & Settings
    logo_url = Column(Text)
    brand_colors = Column(JSONB, default={})
    brand_guidelines = Column(JSONB, default={})
    
    # Subscription & Billing
    subscription_tier = Column(String(50), default=CompanySubscriptionTier.free.value)
    subscription_status = Column(String(50), default="active")
    billing_email = Column(String(255))
    
    # Usage Tracking
    monthly_credits_used = Column(Integer, default=0)
    monthly_credits_limit = Column(Integer, default=1000)
    total_campaigns_created = Column(Integer, default=0)
    
    # Company Settings
    settings = Column(JSONB, default={})
    
    # FIXED: Updated relationships for new intelligence schema
    users = relationship("User", back_populates="company")
    campaigns = relationship("Campaign", back_populates="company")
    memberships = relationship("CompanyMembership", back_populates="company")
    invitations = relationship("CompanyInvitation", back_populates="company")
    
    # FIXED: Only keep GeneratedContent if it has company_id column
    generated_content = relationship("GeneratedContent", back_populates="company")
    
    # REMOVED: These relationships referenced non-existent columns in new schema
    # intelligence_sources = relationship("IntelligenceCore", foreign_keys="IntelligenceCore.company_id")  # REMOVED - no company_id in IntelligenceCore
    # smart_urls = relationship("SmartURL", back_populates="company")  # REMOVED - SmartURL doesn't exist
    
    # NEW: Methods to access intelligence through campaigns (correct approach for new schema)
    def get_intelligence_data(self, db_session, limit: int = None):
        """Get company's intelligence data through campaigns (new schema approach)"""
        try:
            from .campaign import Campaign
            from .intelligence import IntelligenceCore
            from sqlalchemy.orm import selectinload
            from sqlalchemy import desc
            
            # Get campaigns with intelligence data
            query = db_session.query(Campaign)\
                .filter(Campaign.company_id == self.id)\
                .filter(Campaign.analysis_intelligence_id.isnot(None))\
                .options(selectinload('intelligence_data'))\
                .order_by(desc(Campaign.created_at))
            
            if limit:
                query = query.limit(limit)
                
            campaigns_with_intelligence = query.all()
            
            # Extract intelligence core data
            intelligence_data = []
            for campaign in campaigns_with_intelligence:
                if campaign.analysis_intelligence_id:
                    # Get the actual intelligence record
                    intelligence = db_session.query(IntelligenceCore)\
                        .filter(IntelligenceCore.id == campaign.analysis_intelligence_id)\
                        .first()
                    if intelligence:
                        intelligence_data.append({
                            'campaign_id': str(campaign.id),
                            'campaign_title': campaign.title,
                            'intelligence': intelligence,
                            'confidence_score': campaign.analysis_confidence_score,
                            'created_at': campaign.created_at
                        })
            
            return intelligence_data
            
        except Exception as e:
            # Fallback to just campaigns if intelligence import fails
            campaigns = db_session.query(type(self.campaigns[0]) if self.campaigns else object)\
                .filter_by(company_id=self.id)\
                .filter(getattr(type(self.campaigns[0]), 'analysis_intelligence_id', None).isnot(None))\
                .all() if self.campaigns else []
            return campaigns
    
    def get_intelligence_summary(self, db_session) -> dict:
        """Get summary of company's intelligence data"""
        try:
            intelligence_data = self.get_intelligence_data(db_session)
            
            total_intelligence = len(intelligence_data)
            if total_intelligence == 0:
                return {
                    'total_intelligence_sources': 0,
                    'average_confidence': 0,
                    'most_recent': None,
                    'campaigns_with_intelligence': 0
                }
            
            # Calculate statistics
            confidence_scores = [item.get('confidence_score', 0) for item in intelligence_data if item.get('confidence_score')]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            most_recent = intelligence_data[0] if intelligence_data else None
            
            return {
                'total_intelligence_sources': total_intelligence,
                'average_confidence': round(avg_confidence, 3),
                'most_recent': {
                    'campaign_title': most_recent.get('campaign_title'),
                    'confidence_score': most_recent.get('confidence_score'),
                    'created_at': most_recent.get('created_at').isoformat() if most_recent.get('created_at') else None
                } if most_recent else None,
                'campaigns_with_intelligence': total_intelligence
            }
            
        except Exception:
            return {
                'total_intelligence_sources': 0,
                'average_confidence': 0,
                'most_recent': None,
                'campaigns_with_intelligence': 0,
                'error': 'Unable to calculate intelligence summary'
            }
    
    def get_generated_content_stats(self, db_session) -> dict:
        """Get statistics about content generated for this company"""
        try:
            if not self.generated_content:
                return {
                    'total_content': 0,
                    'content_types': [],
                    'average_rating': 0,
                    'published_content': 0
                }
            
            content_items = self.generated_content
            total_content = len(content_items)
            
            # Get content type distribution
            content_types = {}
            ratings = []
            published_count = 0
            
            for item in content_items:
                content_type = getattr(item, 'content_type', 'unknown')
                content_types[content_type] = content_types.get(content_type, 0) + 1
                
                if hasattr(item, 'user_rating') and item.user_rating:
                    ratings.append(item.user_rating)
                
                if hasattr(item, 'is_published') and item.is_published:
                    published_count += 1
            
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            
            return {
                'total_content': total_content,
                'content_types': content_types,
                'average_rating': round(avg_rating, 2),
                'published_content': published_count,
                'content_performance': {
                    'total_generated': total_content,
                    'published_rate': round((published_count / total_content * 100), 1) if total_content > 0 else 0,
                    'average_rating': round(avg_rating, 2),
                    'rating_count': len(ratings)
                }
            }
            
        except Exception:
            return {
                'total_content': 0,
                'content_types': [],
                'average_rating': 0,
                'published_content': 0,
                'error': 'Unable to calculate content statistics'
            }
    
    def get_branding_settings(self) -> dict:
        """Get branding settings with proper enum serialization"""
        return {
            "brand_colors": self._serialize_enum_field(self.brand_colors),
            "brand_guidelines": self._serialize_enum_field(self.brand_guidelines)
        }
    
    def get_company_settings(self) -> dict:
        """Get company settings with proper enum serialization"""
        return self._serialize_enum_field(self.settings)

class CompanyMembership(BaseModel, EnumSerializerMixin):
    """Company membership model for team collaboration"""
    __tablename__ = "company_memberships"
    
    # Relationships
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    
    # Role & Permissions
    role = Column(String(50), nullable=False, default=MembershipRole.MEMBER.value)
    permissions = Column(JSONB, default={})
    
    # Status
    status = Column(String(50), default=MembershipStatus.ACTIVE.value)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    invited_at = Column(DateTime(timezone=True))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Clean relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="company_memberships")
    company = relationship("Company", back_populates="memberships")
    inviter = relationship("User", foreign_keys=[invited_by], back_populates="invited_memberships")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'company_id', name='unique_user_company_membership'),
    )
    
    def get_permissions(self) -> dict:
        """Get permissions with proper enum serialization"""
        return self._serialize_enum_field(self.permissions)

class CompanyInvitation(BaseModel):
    """Company invitation model for team invites"""
    __tablename__ = "company_invitations"
    
    # Invitation Details
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    email = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=MembershipRole.MEMBER.value)
    invited_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Status & Expiry
    status = Column(String(50), default=InvitationStatus.PENDING.value)
    expires_at = Column(DateTime(timezone=True), server_default=func.now() + func.make_interval(0, 0, 0, 7, 0, 0, 0))
    accepted_at = Column(DateTime(timezone=True))
    accepted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    
    # Security (will be populated by backend)
    invitation_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Clean relationships
    company = relationship("Company", back_populates="invitations")
    inviter = relationship("User", foreign_keys=[invited_by], back_populates="sent_invitations")
    accepter = relationship("User", foreign_keys=[accepted_by], back_populates="accepted_invitations")