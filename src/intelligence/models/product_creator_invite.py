# =====================================
# File: src/intelligence/models/product_creator_invite.py
# =====================================

"""
Product Creator Invite system for admin-controlled special accounts.

Enables admins to create private invites for product creators to access
the special free account system for URL pre-analysis.
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, JSON
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone
import uuid
import secrets
from enum import Enum

from src.core.database.base import Base


class InviteStatus(str, Enum):
    """Status of product creator invite."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ProductCreatorInvite(Base):
    """
    Admin-generated invites for product creator special accounts.

    This table manages private invitations that allow product creators
    to register for special free accounts with URL submission privileges.
    """
    __tablename__ = "product_creator_invites"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Invite details
    invite_token = Column(String, unique=True, nullable=False, index=True)  # Secure token for registration
    invitee_email = Column(String, nullable=False, index=True)  # Email of invited product creator
    invitee_name = Column(String, nullable=True)  # Optional name
    company_name = Column(String, nullable=True)  # Product creator's company

    # Admin details
    invited_by_admin_id = Column(String, nullable=False)  # Admin who created invite
    admin_notes = Column(Text, nullable=True)  # Admin notes about the invite

    # Invite restrictions
    max_url_submissions = Column(Integer, default=20)  # Max URLs they can submit
    expires_at = Column(DateTime(timezone=True), nullable=False)  # Invite expiration

    # Status tracking
    status = Column(String, nullable=False, default=InviteStatus.PENDING.value)
    created_user_id = Column(String, nullable=True)  # User ID when invite is accepted
    accepted_at = Column(DateTime(timezone=True), nullable=True)  # When invite was used

    # Metadata
    usage_restrictions = Column(Text, nullable=True)  # Special restrictions or notes
    special_permissions = Column(JSON, nullable=True)  # Any special permissions granted

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def generate_invite_token(cls) -> str:
        """Generate a secure invite token."""
        return secrets.token_urlsafe(32)

    @classmethod
    def create_invite(
        cls,
        invitee_email: str,
        invited_by_admin_id: str,
        invitee_name: str = None,
        company_name: str = None,
        admin_notes: str = None,
        days_valid: int = 30,
        max_url_submissions: int = 20,
        usage_restrictions: str = None,
        special_permissions: dict = None
    ) -> 'ProductCreatorInvite':
        """
        Create a new product creator invite.

        Args:
            invitee_email: Email of the product creator to invite
            invited_by_admin_id: Admin creating the invite
            invitee_name: Optional name of invitee
            company_name: Optional company name
            admin_notes: Admin notes about this invite
            days_valid: Number of days invite is valid (default 30)
            max_url_submissions: Max URLs they can submit (default 20)
            usage_restrictions: Any special restrictions

        Returns:
            ProductCreatorInvite: New invite instance
        """
        expires_at = datetime.now(timezone.utc) + timedelta(days=days_valid)

        return cls(
            invite_token=cls.generate_invite_token(),
            invitee_email=invitee_email,
            invitee_name=invitee_name,
            company_name=company_name,
            invited_by_admin_id=invited_by_admin_id,
            admin_notes=admin_notes,
            max_url_submissions=max_url_submissions,
            expires_at=expires_at,
            usage_restrictions=usage_restrictions,
            special_permissions=special_permissions,
            status=InviteStatus.PENDING.value
        )

    def is_valid(self) -> bool:
        """Check if invite is still valid."""
        return (
            self.status == InviteStatus.PENDING.value and
            self.expires_at > datetime.now(timezone.utc)
        )

    def accept_invite(self, user_id: str) -> bool:
        """
        Mark invite as accepted.

        Args:
            user_id: ID of the user who accepted the invite

        Returns:
            bool: True if invite was successfully accepted
        """
        if not self.is_valid():
            return False

        self.status = InviteStatus.ACCEPTED.value
        self.created_user_id = user_id
        self.accepted_at = datetime.now(timezone.utc)
        return True

    def revoke_invite(self) -> bool:
        """
        Revoke the invite (admin action).

        Returns:
            bool: True if invite was revoked
        """
        if self.status == InviteStatus.ACCEPTED.value:
            return False  # Cannot revoke accepted invites

        self.status = InviteStatus.REVOKED.value
        return True

    def to_dict(self, include_sensitive: bool = False):
        """Convert to dictionary for API responses."""
        data = {
            "id": self.id,
            "invitee_email": self.invitee_email,
            "invitee_name": self.invitee_name,
            "company_name": self.company_name,
            "invited_by_admin_id": self.invited_by_admin_id,
            "admin_notes": self.admin_notes,
            "max_url_submissions": self.max_url_submissions,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "status": self.status,
            "created_user_id": self.created_user_id,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "usage_restrictions": self.usage_restrictions,
            "special_permissions": self.special_permissions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_valid": self.is_valid()
        }

        # Only include invite token for admin or during registration
        if include_sensitive:
            data["invite_token"] = self.invite_token

        return data