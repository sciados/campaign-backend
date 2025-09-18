# =====================================
# File: src/intelligence/services/product_creator_invite_service.py
# =====================================

"""
Product Creator Invite Service for admin-controlled special accounts.

Manages the complete lifecycle of product creator invitations including
creation, validation, acceptance, and restrictions enforcement.
"""

import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from datetime import datetime, timedelta, timezone

from src.intelligence.models.product_creator_invite import ProductCreatorInvite, InviteStatus

logger = logging.getLogger(__name__)


class ProductCreatorInviteService:
    """Service for managing product creator invitations."""

    async def create_invite(
        self,
        invitee_email: str,
        invited_by_admin_id: str,
        invitee_name: Optional[str] = None,
        company_name: Optional[str] = None,
        admin_notes: Optional[str] = None,
        days_valid: int = 30,
        max_url_submissions: int = 20,
        usage_restrictions: Optional[str] = None,
        session: AsyncSession = None
    ) -> ProductCreatorInvite:
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
            session: Database session

        Returns:
            ProductCreatorInvite: New invite instance
        """
        # Check if user already has a pending invite
        existing_invite = await self.get_invite_by_email(invitee_email, session)
        if existing_invite and existing_invite.is_valid():
            raise ValueError(f"Active invite already exists for {invitee_email}")

        # Create new invite
        invite = ProductCreatorInvite.create_invite(
            invitee_email=invitee_email,
            invited_by_admin_id=invited_by_admin_id,
            invitee_name=invitee_name,
            company_name=company_name,
            admin_notes=admin_notes,
            days_valid=days_valid,
            max_url_submissions=max_url_submissions,
            usage_restrictions=usage_restrictions
        )

        session.add(invite)
        await session.commit()

        logger.info(f"📧 PRODUCT CREATOR INVITE: Created invite for {invitee_email}")
        logger.info(f"   👤 Invited by admin: {invited_by_admin_id}")
        logger.info(f"   🏢 Company: {company_name or 'Not specified'}")
        logger.info(f"   📅 Valid until: {invite.expires_at}")
        logger.info(f"   🔗 Max URLs: {max_url_submissions}")

        return invite

    async def get_invite_by_token(
        self,
        invite_token: str,
        session: AsyncSession
    ) -> Optional[ProductCreatorInvite]:
        """
        Get invite by token for registration validation.

        Args:
            invite_token: The invite token
            session: Database session

        Returns:
            ProductCreatorInvite or None
        """
        stmt = select(ProductCreatorInvite).where(
            ProductCreatorInvite.invite_token == invite_token
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_invite_by_email(
        self,
        email: str,
        session: AsyncSession
    ) -> Optional[ProductCreatorInvite]:
        """
        Get the most recent invite for an email.

        Args:
            email: Email to search for
            session: Database session

        Returns:
            ProductCreatorInvite or None
        """
        stmt = select(ProductCreatorInvite).where(
            ProductCreatorInvite.invitee_email == email
        ).order_by(ProductCreatorInvite.created_at.desc()).limit(1)

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def validate_invite_token(
        self,
        invite_token: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """
        Validate an invite token for registration.

        Args:
            invite_token: The invite token to validate
            session: Database session

        Returns:
            Dict with validation results
        """
        invite = await self.get_invite_by_token(invite_token, session)

        if not invite:
            return {
                "valid": False,
                "reason": "Invalid invite token",
                "invite": None
            }

        if not invite.is_valid():
            if invite.status == InviteStatus.ACCEPTED.value:
                reason = "Invite has already been used"
            elif invite.status == InviteStatus.EXPIRED.value or invite.expires_at <= datetime.now(timezone.utc):
                reason = "Invite has expired"
            elif invite.status == InviteStatus.REVOKED.value:
                reason = "Invite has been revoked"
            else:
                reason = "Invite is no longer valid"

            return {
                "valid": False,
                "reason": reason,
                "invite": invite.to_dict()
            }

        return {
            "valid": True,
            "reason": "Invite is valid",
            "invite": invite.to_dict(include_sensitive=True)
        }

    async def accept_invite(
        self,
        invite_token: str,
        user_id: str,
        session: AsyncSession
    ) -> bool:
        """
        Accept an invite when user registers.

        Args:
            invite_token: The invite token
            user_id: ID of the newly created user
            session: Database session

        Returns:
            bool: True if invite was accepted successfully
        """
        invite = await self.get_invite_by_token(invite_token, session)

        if not invite or not invite.is_valid():
            return False

        success = invite.accept_invite(user_id)
        if success:
            await session.commit()
            logger.info(f"✅ INVITE ACCEPTED: {invite.invitee_email} registered as user {user_id}")

        return success

    async def list_invites(
        self,
        status: Optional[InviteStatus] = None,
        admin_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        session: AsyncSession = None
    ) -> List[ProductCreatorInvite]:
        """
        List product creator invites with filtering.

        Args:
            status: Filter by invite status
            admin_id: Filter by inviting admin
            limit: Maximum results to return
            offset: Number of results to skip
            session: Database session

        Returns:
            List of ProductCreatorInvite objects
        """
        stmt = select(ProductCreatorInvite)

        if status:
            stmt = stmt.where(ProductCreatorInvite.status == status.value)

        if admin_id:
            stmt = stmt.where(ProductCreatorInvite.invited_by_admin_id == admin_id)

        stmt = stmt.offset(offset).limit(limit).order_by(ProductCreatorInvite.created_at.desc())

        result = await session.execute(stmt)
        return result.scalars().all()

    async def revoke_invite(
        self,
        invite_id: str,
        admin_id: str,
        session: AsyncSession
    ) -> bool:
        """
        Revoke an invite (admin action).

        Args:
            invite_id: ID of invite to revoke
            admin_id: Admin performing the action
            session: Database session

        Returns:
            bool: True if invite was revoked
        """
        invite = await session.get(ProductCreatorInvite, invite_id)

        if not invite:
            return False

        success = invite.revoke_invite()
        if success:
            await session.commit()
            logger.info(f"🚫 INVITE REVOKED: {invite.invitee_email} by admin {admin_id}")

        return success

    async def cleanup_expired_invites(
        self,
        session: AsyncSession
    ) -> int:
        """
        Mark expired invites as expired.

        Args:
            session: Database session

        Returns:
            int: Number of invites marked as expired
        """
        stmt = update(ProductCreatorInvite).where(
            ProductCreatorInvite.status == InviteStatus.PENDING.value,
            ProductCreatorInvite.expires_at <= datetime.now(timezone.utc)
        ).values(status=InviteStatus.EXPIRED.value)

        result = await session.execute(stmt)
        await session.commit()

        expired_count = result.rowcount
        if expired_count > 0:
            logger.info(f"🧹 CLEANUP: Marked {expired_count} invites as expired")

        return expired_count

    async def get_user_invite_restrictions(
        self,
        user_id: str,
        session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Get restrictions for a user based on their invite.

        Args:
            user_id: User ID to check
            session: Database session

        Returns:
            Dict with user restrictions or None if not an invited user
        """
        stmt = select(ProductCreatorInvite).where(
            ProductCreatorInvite.created_user_id == user_id,
            ProductCreatorInvite.status == InviteStatus.ACCEPTED.value
        )

        result = await session.execute(stmt)
        invite = result.scalar_one_or_none()

        if not invite:
            return None

        return {
            "max_url_submissions": int(invite.max_url_submissions),
            "usage_restrictions": invite.usage_restrictions,
            "special_permissions": invite.special_permissions,
            "invited_by_admin": invite.invited_by_admin_id,
            "invite_accepted_at": invite.accepted_at,
            "is_product_creator_account": True
        }