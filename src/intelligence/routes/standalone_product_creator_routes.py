# =====================================
# File: src/intelligence/routes/standalone_product_creator_routes.py
# =====================================

"""
Standalone Product Creator Invite API routes.
Isolated to avoid import conflicts with admin routes.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, EmailStr, Field
import logging

from src.core.database import get_async_db
from src.core.auth.dependencies import require_admin, get_current_user
from src.core.shared.responses import StandardResponse
from src.intelligence.services.product_creator_invite_service import ProductCreatorInviteService
from src.intelligence.models.product_creator_invite import InviteStatus

admin_router = APIRouter(prefix="/admin/product-creator-invites", tags=["Admin Product Creator Invites"])
public_router = APIRouter(prefix="/product-creator-invites", tags=["Product Creator Invites Public"])
logger = logging.getLogger(__name__)


class CreateInviteRequest(BaseModel):
    """Request model for creating product creator invites."""
    invitee_email: EmailStr = Field(..., description="Email of the product creator to invite")
    invitee_name: Optional[str] = Field(None, description="Name of the product creator")
    company_name: Optional[str] = Field(None, description="Product creator's company name")
    admin_notes: Optional[str] = Field(None, description="Admin notes about this invite")
    days_valid: int = Field(30, description="Number of days invite is valid", ge=1, le=365)
    max_url_submissions: int = Field(20, description="Maximum URLs they can submit", ge=1, le=100)
    usage_restrictions: Optional[str] = Field(None, description="Special usage restrictions")


class ValidateInviteRequest(BaseModel):
    """Request model for validating invite tokens."""
    invite_token: str = Field(..., description="Invite token to validate")


@admin_router.post("/create", response_model=StandardResponse[Dict[str, Any]])
async def create_product_creator_invite(
    request: CreateInviteRequest,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    🎯 Create a new product creator invite (Admin Only).

    **Private Invite System**: Generate secure invitations for select product creators
    to access special free accounts for URL pre-analysis submissions.
    """
    try:
        invite_service = ProductCreatorInviteService()

        invite = await invite_service.create_invite(
            invitee_email=request.invitee_email,
            invited_by_admin_id=current_user["id"],
            invitee_name=request.invitee_name,
            company_name=request.company_name,
            admin_notes=request.admin_notes,
            days_valid=request.days_valid,
            max_url_submissions=request.max_url_submissions,
            usage_restrictions=request.usage_restrictions,
            session=session
        )

        # TODO: Send invitation email to product creator
        # TODO: Send confirmation email to admin
        email_sent = True  # Placeholder

        # Include sensitive data for admin
        invite_data = invite.to_dict(include_sensitive=True)

        # Add registration URL for easy sharing
        invite_data["registration_url"] = f"/register?invite_token={invite.invite_token}"
        invite_data["email_sent"] = email_sent

        return StandardResponse(
            success=True,
            data=invite_data,
            message=f"Product creator invite created for {request.invitee_email}. Valid for {request.days_valid} days. Email {'sent' if email_sent else 'logged (no SMTP config)'}."
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create invite: {str(e)}")


@admin_router.get("/list", response_model=StandardResponse[List[Dict[str, Any]]])
async def list_product_creator_invites(
    status: Optional[str] = Query(None, description="Filter by invite status"),
    admin_id: Optional[str] = Query(None, description="Filter by inviting admin"),
    limit: int = Query(50, description="Maximum results to return", ge=1, le=100),
    offset: int = Query(0, description="Number of results to skip", ge=0),
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[List[Dict[str, Any]]]:
    """
    📋 List product creator invites (Admin Only).

    **Admin Dashboard**: View and manage all product creator invitations with
    filtering and pagination capabilities.
    """
    try:
        invite_service = ProductCreatorInviteService()

        # Convert string status to enum if provided
        status_filter = None
        if status:
            try:
                status_filter = InviteStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        invites = await invite_service.list_invites(
            status=status_filter,
            admin_id=admin_id,
            limit=limit,
            offset=offset,
            session=session
        )

        invite_data = [invite.to_dict(include_sensitive=True) for invite in invites]

        return StandardResponse(
            success=True,
            data=invite_data,
            message=f"Found {len(invite_data)} product creator invites"
        )

    except Exception as e:
        logger.error(f"Failed to list invites: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to list invites: {str(e)}")


@public_router.post("/validate", response_model=StandardResponse[Dict[str, Any]])
async def validate_invite_token(
    request: ValidateInviteRequest,
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    ✅ Validate a product creator invite token.

    **Public Endpoint**: Used during registration to validate invite tokens.
    Returns invite details if valid for account creation.
    """
    try:
        invite_service = ProductCreatorInviteService()

        validation_result = await invite_service.validate_invite_token(
            invite_token=request.invite_token,
            session=session
        )

        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["reason"])

        return StandardResponse(
            success=True,
            data=validation_result,
            message="Invite token is valid"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate invite: {str(e)}")


@admin_router.post("/revoke/{invite_id}", response_model=StandardResponse[Dict[str, Any]])
async def revoke_product_creator_invite(
    invite_id: str,
    current_user: dict = Depends(require_admin),
    session: AsyncSession = Depends(get_async_db)
) -> StandardResponse[Dict[str, Any]]:
    """
    🚫 Revoke a product creator invite (Admin Only).

    **Admin Control**: Revoke unused invitations to prevent registration.
    Cannot revoke invites that have already been accepted.
    """
    try:
        invite_service = ProductCreatorInviteService()

        success = await invite_service.revoke_invite(
            invite_id=invite_id,
            admin_id=current_user["id"],
            session=session
        )

        if not success:
            raise HTTPException(status_code=400, detail="Cannot revoke invite (not found or already used)")

        return StandardResponse(
            success=True,
            data={"invite_id": invite_id, "revoked_by": current_user["id"]},
            message="Product creator invite revoked successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revoke invite: {str(e)}")