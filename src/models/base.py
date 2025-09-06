# =====================================
# File: src/models/base.py
# =====================================

"""
Base model classes for CampaignForge models.
Provides common functionality and imports for all models.
"""

from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
from datetime import datetime, timezone
import uuid

# Import the actual Base from your database setup
from src.core.database.models import Base


class BaseModel(Base):
    """
    Abstract base model class that provides common functionality.
    All models should inherit from this class.
    """
    __abstract__ = True
    
    # Primary key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Timestamps
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
    
    def __repr__(self):
        """String representation of the model."""
        return f"<{self.__class__.__name__}(id='{self.id}')>"


# Export the Base as well for direct SQLAlchemy usage
__all__ = ["BaseModel", "Base"]