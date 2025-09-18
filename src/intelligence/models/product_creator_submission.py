# =====================================
# File: src/intelligence/models/product_creator_submission.py
# =====================================

"""
Product Creator URL Submission models for pre-launch intelligence gathering.

Enables product creators to submit their sales pages for pre-analysis
before affiliate marketing launch.
"""

from sqlalchemy import Column, String, Text, JSON, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from enum import Enum

from src.core.database.base import Base


class SubmissionStatus(str, Enum):
    """Status of product creator URL submission."""
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ProductCreatorSubmission(Base):
    """
    Product Creator URL submissions for pre-launch intelligence gathering.

    This table stores submissions from product creators who want their
    sales pages pre-analyzed before affiliate marketing launch.
    """
    __tablename__ = "product_creator_submissions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Submission details
    product_name = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False)
    urls = Column(JSON, nullable=False)  # List of URLs to analyze

    # Contact information
    contact_email = Column(String, nullable=False)
    submitter_user_id = Column(String, nullable=True)  # If submitted by logged-in user

    # Optional details
    launch_date = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Processing details
    status = Column(String, nullable=False, default=SubmissionStatus.PENDING_REVIEW.value)
    admin_notes = Column(Text, nullable=True)
    processed_by_admin_id = Column(String, nullable=True)

    # Analysis results (populated after processing)
    intelligence_ids = Column(JSON, nullable=True)  # List of created intelligence IDs
    analysis_summary = Column(JSON, nullable=True)  # Summary of analysis results

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Tracking
    processing_time_seconds = Column(String, nullable=True)
    total_urls_processed = Column(String, nullable=True)

    def to_dict(self):
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "product_name": self.product_name,
            "category": self.category,
            "urls": self.urls,
            "contact_email": self.contact_email,
            "submitter_user_id": self.submitter_user_id,
            "launch_date": self.launch_date,
            "notes": self.notes,
            "status": self.status,
            "admin_notes": self.admin_notes,
            "processed_by_admin_id": self.processed_by_admin_id,
            "intelligence_ids": self.intelligence_ids,
            "analysis_summary": self.analysis_summary,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "processing_time_seconds": self.processing_time_seconds,
            "total_urls_processed": self.total_urls_processed
        }