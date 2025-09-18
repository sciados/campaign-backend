# =====================================
# File: src/intelligence/services/email_service.py
# =====================================

"""
Email service for product creator invite system.

Handles sending invitation emails, confirmation emails, and status updates
for the admin-controlled product creator invitation workflow.
"""

import smtplib
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Optional, Dict, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails related to product creator invitations."""

    def __init__(self):
        # Email configuration from environment variables
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_username)
        self.from_name = os.getenv("FROM_NAME", "CampaignForge")

        # Frontend URL for registration links
        self.frontend_url = os.getenv("FRONTEND_URL", "https://www.rodgersdigital.com")

        # Check if email is configured
        self.is_configured = bool(self.smtp_username and self.smtp_password)

        if not self.is_configured:
            logger.warning("Email service not configured - emails will be logged instead of sent")

    async def send_product_creator_invitation(
        self,
        invite_data: Dict[str, Any],
        admin_name: Optional[str] = None
    ) -> bool:
        """
        Send invitation email to product creator.

        Args:
            invite_data: Dictionary containing invite information
            admin_name: Name of admin who created the invite

        Returns:
            bool: True if email sent successfully
        """
        try:
            # Extract invite information
            invitee_email = invite_data.get("invitee_email")
            invitee_name = invite_data.get("invitee_name", "")
            company_name = invite_data.get("company_name", "")
            invite_token = invite_data.get("invite_token")
            max_url_submissions = invite_data.get("max_url_submissions", 20)
            expires_at = invite_data.get("expires_at")

            # Create registration URL
            registration_url = f"{self.frontend_url}/register?invite_token={invite_token}"

            # Create email content
            subject = "🎯 You're Invited: Exclusive Product Creator Access - CampaignForge"

            # HTML email template
            html_content = self._create_invitation_html_template(
                invitee_name=invitee_name or invitee_email.split('@')[0],
                company_name=company_name,
                registration_url=registration_url,
                max_url_submissions=max_url_submissions,
                expires_at=expires_at,
                admin_name=admin_name or "CampaignForge Team"
            )

            # Plain text version
            text_content = self._create_invitation_text_template(
                invitee_name=invitee_name or invitee_email.split('@')[0],
                company_name=company_name,
                registration_url=registration_url,
                max_url_submissions=max_url_submissions,
                expires_at=expires_at,
                admin_name=admin_name or "CampaignForge Team"
            )

            # Send email
            success = await self._send_email(
                to_email=invitee_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

            if success:
                logger.info(f"📧 INVITE EMAIL SENT: {invitee_email}")

            return success

        except Exception as e:
            logger.error(f"Failed to send invitation email to {invitee_email}: {e}")
            return False

    async def send_admin_confirmation(
        self,
        admin_email: str,
        invite_data: Dict[str, Any],
        admin_name: Optional[str] = None
    ) -> bool:
        """
        Send confirmation email to admin who created the invite.

        Args:
            admin_email: Admin's email address
            invite_data: Dictionary containing invite information
            admin_name: Name of admin

        Returns:
            bool: True if email sent successfully
        """
        try:
            invitee_email = invite_data.get("invitee_email")
            company_name = invite_data.get("company_name", "")
            invite_token = invite_data.get("invite_token")

            subject = f"✅ Product Creator Invite Created: {invitee_email}"

            # HTML content for admin
            html_content = f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2 style="color: #2563eb;">Invite Created Successfully</h2>

                <p>Hi {admin_name or 'Admin'},</p>

                <p>You've successfully created a product creator invitation for:</p>

                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <strong>📧 Invitee:</strong> {invitee_email}<br>
                    {f"<strong>🏢 Company:</strong> {company_name}<br>" if company_name else ""}
                    <strong>🔗 Token:</strong> {invite_token[:12]}...<br>
                    <strong>📅 Status:</strong> Invitation email sent
                </div>

                <p>The product creator has received their invitation email with the registration link.</p>

                <p style="color: #6b7280; font-size: 14px;">
                    This is an automated confirmation from the CampaignForge admin system.
                </p>
            </div>
            """

            # Plain text version
            text_content = f"""
Product Creator Invite Created Successfully

Hi {admin_name or 'Admin'},

You've successfully created a product creator invitation for:
- Invitee: {invitee_email}
{f"- Company: {company_name}" if company_name else ""}
- Token: {invite_token[:12]}...
- Status: Invitation email sent

The product creator has received their invitation email with the registration link.

---
CampaignForge Admin System
            """

            success = await self._send_email(
                to_email=admin_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )

            if success:
                logger.info(f"📧 ADMIN CONFIRMATION SENT: {admin_email}")

            return success

        except Exception as e:
            logger.error(f"Failed to send admin confirmation to {admin_email}: {e}")
            return False

    def _create_invitation_html_template(
        self,
        invitee_name: str,
        company_name: str,
        registration_url: str,
        max_url_submissions: int,
        expires_at: str,
        admin_name: str
    ) -> str:
        """Create HTML email template for product creator invitation."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Product Creator Invitation - CampaignForge</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f9fafb;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">

                <!-- Header -->
                <div style="background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%); color: white; padding: 30px 40px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px; font-weight: bold;">🎯 You're Invited!</h1>
                    <p style="margin: 10px 0 0; font-size: 16px; opacity: 0.9;">Exclusive Product Creator Access</p>
                </div>

                <!-- Content -->
                <div style="padding: 40px;">
                    <h2 style="color: #1f2937; margin-top: 0;">Hi {invitee_name}! 👋</h2>

                    <p style="color: #374151; font-size: 16px;">
                        You've been personally invited by <strong>{admin_name}</strong> to join CampaignForge as a
                        <strong>Product Creator</strong> with special access to our pre-launch URL analysis system.
                    </p>

                    {f'<p style="color: #374151;">We noticed you\'re with <strong>{company_name}</strong> - this invitation is specifically designed for product creators like you who want to get ahead of the game!</p>' if company_name else ''}

                    <!-- Benefits -->
                    <div style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 20px; margin: 25px 0; border-radius: 0 8px 8px 0;">
                        <h3 style="color: #1e40af; margin-top: 0;">🚀 What You Get:</h3>
                        <ul style="color: #1f2937; padding-left: 20px;">
                            <li><strong>Free Pre-Launch Analysis:</strong> Submit up to {max_url_submissions} sales page URLs</li>
                            <li><strong>Instant Affiliate Ready:</strong> Your products get pre-analyzed for affiliate marketers</li>
                            <li><strong>Faster Market Penetration:</strong> Affiliate marketers can promote immediately</li>
                            <li><strong>Zero Cost to You:</strong> Completely free special account</li>
                        </ul>
                    </div>

                    <!-- CTA Button -->
                    <div style="text-align: center; margin: 35px 0;">
                        <a href="{registration_url}"
                           style="display: inline-block; background: #2563eb; color: white; text-decoration: none; padding: 15px 30px; border-radius: 8px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(37, 99, 235, 0.3);">
                            🎯 Claim Your Invite
                        </a>
                    </div>

                    <!-- How It Works -->
                    <div style="background: #f9fafb; padding: 25px; border-radius: 8px; margin: 25px 0;">
                        <h3 style="color: #1f2937; margin-top: 0;">How It Works:</h3>
                        <div style="color: #374151;">
                            <p><strong>1.</strong> Click the button above to register with your invite token</p>
                            <p><strong>2.</strong> Submit your product sales page URLs (up to {max_url_submissions})</p>
                            <p><strong>3.</strong> We analyze them for affiliate marketers before your launch</p>
                            <p><strong>4.</strong> Affiliate marketers get instant access to promote your products</p>
                        </div>
                    </div>

                    <!-- Urgency -->
                    <div style="background: #fef3c7; border: 1px solid #f59e0b; padding: 15px; border-radius: 8px; margin: 25px 0;">
                        <p style="margin: 0; color: #92400e;">
                            ⏰ <strong>This invitation expires on {expires_at.split('T')[0] if expires_at else 'soon'}</strong> - claim your spot today!
                        </p>
                    </div>

                    <p style="color: #6b7280; font-size: 14px; margin-top: 30px;">
                        This is a private invitation. If you have any questions, reply to this email or contact our support team.
                    </p>

                    <p style="color: #6b7280; font-size: 14px;">
                        Best regards,<br>
                        <strong>The CampaignForge Team</strong>
                    </p>
                </div>

                <!-- Footer -->
                <div style="background: #f3f4f6; padding: 20px; text-align: center; border-top: 1px solid #e5e7eb;">
                    <p style="margin: 0; color: #6b7280; font-size: 12px;">
                        CampaignForge - AI-Powered Marketing Platform<br>
                        This email was sent to {invitee_name.split('@')[0] if '@' in invitee_name else invitee_name} because you were invited by {admin_name}
                    </p>
                </div>
            </div>
        </body>
        </html>
        """

    def _create_invitation_text_template(
        self,
        invitee_name: str,
        company_name: str,
        registration_url: str,
        max_url_submissions: int,
        expires_at: str,
        admin_name: str
    ) -> str:
        """Create plain text email template for product creator invitation."""
        return f"""
🎯 You're Invited: Exclusive Product Creator Access - CampaignForge

Hi {invitee_name}!

You've been personally invited by {admin_name} to join CampaignForge as a Product Creator with special access to our pre-launch URL analysis system.

{f"We noticed you're with {company_name} - this invitation is specifically designed for product creators like you who want to get ahead of the game!" if company_name else ""}

🚀 What You Get:
- Free Pre-Launch Analysis: Submit up to {max_url_submissions} sales page URLs
- Instant Affiliate Ready: Your products get pre-analyzed for affiliate marketers
- Faster Market Penetration: Affiliate marketers can promote immediately
- Zero Cost to You: Completely free special account

How It Works:
1. Click the registration link below to claim your invite
2. Submit your product sales page URLs (up to {max_url_submissions})
3. We analyze them for affiliate marketers before your launch
4. Affiliate marketers get instant access to promote your products

Registration Link:
{registration_url}

⏰ This invitation expires on {expires_at.split('T')[0] if expires_at else 'soon'} - claim your spot today!

This is a private invitation. If you have any questions, reply to this email or contact our support team.

Best regards,
The CampaignForge Team

---
CampaignForge - AI-Powered Marketing Platform
This email was sent because you were invited by {admin_name}
        """

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """
        Send email using SMTP.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email content
            text_content: Plain text email content

        Returns:
            bool: True if email sent successfully
        """
        if not self.is_configured:
            # Log email instead of sending if not configured
            logger.info(f"📧 EMAIL (NOT SENT - NO CONFIG): {to_email}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Content: {text_content[:200]}...")
            return True

        try:
            # Create message
            msg = MimeMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Add both plain text and HTML parts
            text_part = MimeText(text_content, 'plain')
            html_part = MimeText(html_content, 'html')

            msg.attach(text_part)
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"📧 EMAIL SENT: {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False


# Global email service instance
email_service = EmailService()