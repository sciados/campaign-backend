"""
ScrapedImage Model

SQLAlchemy model for scraped product images from sales pages.
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database.base import Base


class ScrapedImage(Base):
    """Scraped product image model"""

    __tablename__ = "scraped_images"

    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Foreign keys
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Storage locations
    r2_path = Column(String, nullable=False)
    cdn_url = Column(String, nullable=False)
    original_url = Column(String, nullable=True)

    # Image properties
    width = Column(Integer, nullable=False)
    height = Column(Integer, nullable=False)
    file_size = Column(Integer, nullable=False)  # bytes
    format = Column(String(10), nullable=False)  # jpg, png, webp

    # Metadata
    alt_text = Column(String, nullable=True)
    context = Column(String, nullable=True)
    quality_score = Column(Float, nullable=False, default=0.0, index=True)

    # Classification flags
    is_hero = Column(Boolean, default=False, nullable=False)
    is_product = Column(Boolean, default=False, nullable=False)
    is_lifestyle = Column(Boolean, default=False, nullable=False)

    # Usage tracking
    times_used = Column(Integer, default=0, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    # Additional metadata (JSONB)
    metadata = Column(JSON, nullable=True)

    # Timestamps
    scraped_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships (optional - uncomment if you want ORM navigation)
    # campaign = relationship("Campaign", back_populates="scraped_images")
    # user = relationship("User", back_populates="scraped_images")

    def __repr__(self):
        return f"<ScrapedImage {self.id} campaign={self.campaign_id} score={self.quality_score}>"

    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": str(self.id),
            "campaign_id": str(self.campaign_id),
            "user_id": str(self.user_id),
            "r2_path": self.r2_path,
            "cdn_url": self.cdn_url,
            "original_url": self.original_url,
            "width": self.width,
            "height": self.height,
            "file_size": self.file_size,
            "format": self.format,
            "alt_text": self.alt_text,
            "context": self.context,
            "quality_score": self.quality_score,
            "is_hero": self.is_hero,
            "is_product": self.is_product,
            "is_lifestyle": self.is_lifestyle,
            "times_used": self.times_used,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "metadata": self.metadata,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
