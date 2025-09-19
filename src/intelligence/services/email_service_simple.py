# Simple email service without f-strings
import smtplib
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import os
import asyncio

try:
    import resend
    RESEND_SDK_AVAILABLE = True
except ImportError:
    RESEND_SDK_AVAILABLE = False

logger = logging.getLogger(__name__)

class EmailService:
    """Simple email service for product creator invitations without f-string issues."""

    def __init__(self):
        self.resend_api_key = os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@rodgersdigital.com")
        self.from_name = os.getenv("FROM_NAME", "CampaignForge")
        self.frontend_url = os.getenv("FRONTEND_URL", "https://www.rodgersdigital.com")

        self.use_resend_sdk = bool(self.resend_api_key) and RESEND_SDK_AVAILABLE
        self.is_configured = self.use_resend_sdk

        if self.use_resend_sdk:
            resend.api_key = self.resend_api_key
            logger.info("Email service configured with Resend Python SDK")
        else:
            logger.warning("Email service not configured - emails will be logged instead of sent")

    async def send_product_creator_invitation(
        self,
        invite_data: Dict[str, Any],
        admin_name: Optional[str] = None
    ) -> bool:
        """Send invitation email to product creator."""
        try:
            invitee_email = invite_data.get("invitee_email")
            invitee_name = invite_data.get("invitee_name", "")
            company_name = invite_data.get("company_name", "")
            invite_token = invite_data.get("invite_token")
            max_url_submissions = invite_data.get("max_url_submissions", 20)
            expires_at = invite_data.get("expires_at")

            registration_url = self.frontend_url + "/register?invite_token=" + invite_token
            display_name = invitee_name or invitee_email.split('@')[0]
            admin_display_name = admin_name or "CampaignForge Team"

            subject = "🎯 You're Invited: Exclusive Product Creator Access - CampaignForge"

            # Debug logging to see what we're getting
            logger.info(f"DEBUG - Invitee email: {invitee_email}")
            logger.info(f"DEBUG - Invitee name from data: {invitee_name}")
            logger.info(f"DEBUG - Display name calculated: {display_name}")
            logger.info(f"DEBUG - Admin name passed: {admin_name}")
            logger.info(f"DEBUG - Admin display name: {admin_display_name}")

            # Simple HTML content using string replacement
            html_content = """
            <h1>🎯 You're Invited!</h1>
            <h2>Hi INVITEE_NAME!</h2>
            <p>You've been personally invited by <strong>ADMIN_NAME</strong> to join CampaignForge as a Product Creator.</p>
            <p><strong>Registration URL:</strong> <a href="REG_URL">Click here to register</a></p>
            <p><strong>Submit up to MAX_URLS sales page URLs</strong></p>
            <p>Best regards,<br>The CampaignForge Team</p>
            """

            # Replace placeholders
            html_content = html_content.replace("INVITEE_NAME", display_name)
            html_content = html_content.replace("ADMIN_NAME", admin_display_name)
            html_content = html_content.replace("REG_URL", registration_url)
            html_content = html_content.replace("MAX_URLS", str(max_url_submissions))

            text_content = """
            You're Invited: Exclusive Product Creator Access

            Hi INVITEE_NAME!

            You've been personally invited by ADMIN_NAME to join CampaignForge as a Product Creator.

            Registration URL: REG_URL

            Submit up to MAX_URLS sales page URLs

            Best regards,
            The CampaignForge Team
            """

            # Replace placeholders
            text_content = text_content.replace("INVITEE_NAME", display_name)
            text_content = text_content.replace("ADMIN_NAME", admin_display_name)
            text_content = text_content.replace("REG_URL", registration_url)
            text_content = text_content.replace("MAX_URLS", str(max_url_submissions))

            if not self.is_configured:
                logger.info("📧 EMAIL (NOT SENT - NO CONFIG): " + invitee_email)
                logger.info("Subject: " + subject)
                logger.info("Content: " + text_content[:200] + "...")
                return True

            # Use Resend SDK
            params = {
                "from": self.from_name + " <" + self.from_email + ">",
                "to": [invitee_email],
                "subject": subject,
                "html": html_content,
                "text": text_content
            }

            email_result = await asyncio.to_thread(resend.Emails.send, params)

            if email_result and email_result.get('id'):
                logger.info("📧 EMAIL SENT (Resend SDK): " + invitee_email + " - ID: " + email_result['id'])
                return True
            else:
                logger.error("Resend SDK error: No email ID returned")
                return False

        except Exception as e:
            logger.error("Failed to send invitation email to " + invitee_email + ": " + str(e))
            return False

# Global email service instance
email_service = EmailService()