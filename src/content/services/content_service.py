# ============================================================================
# CONTENT SERVICE WITH SESSION MANAGEMENT (Session 5)
# ============================================================================

# src/content/services/content_service.py

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
import logging

logger = logging.getLogger(__name__)

class ContentService:
    """Content Service with proper database session management"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_content(
        self,
        campaign_id: Union[str, UUID],
        content_type: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate content using appropriate generator"""
        try:
            logger.info(f"Generating {content_type} content for campaign {campaign_id}")
            
            # Import generators (dynamic import to avoid circular dependencies)
            from src.content.generators.email_generator import EmailGenerator
            from src.content.generators.social_media_generator import SocialMediaGenerator
            from src.content.generators.blog_content_generator import BlogContentGenerator
            from src.content.generators.ad_copy_generator import AdCopyGenerator
            
            # Route to appropriate generator
            if content_type.lower() in ["email", "email_sequence"]:
                generator = EmailGenerator()
                result = await generator.generate_email_sequence(
                    campaign_id=campaign_id,
                    **preferences or {}
                )
            elif content_type.lower() in ["social_post", "social_media"]:
                generator = SocialMediaGenerator()
                result = await generator.generate_social_content(
                    campaign_id=campaign_id,
                    **preferences or {}
                )
            elif content_type.lower() in ["blog_post", "blog"]:
                generator = BlogContentGenerator()
                result = await generator.generate_blog_post(
                    campaign_id=campaign_id,
                    **preferences or {}
                )
            elif content_type.lower() in ["ad_copy", "advertisement"]:
                generator = AdCopyGenerator()
                result = await generator.generate_ad_copy(
                    campaign_id=campaign_id,
                    **preferences or {}
                )
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Store content in database (implement this when full integration is ready)
            content_record = await self._store_generated_content(
                campaign_id=campaign_id,
                content_type=content_type,
                content_data=result
            )
            
            return {
                "success": True,
                "content_id": content_record["content_id"],
                "content_type": content_type,
                "generated_content": result,
                "generation_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "service_version": "1.0.0"
                }
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_type": content_type,
                "campaign_id": str(campaign_id)
            }
    
    async def _store_generated_content(
        self,
        campaign_id: Union[str, UUID],
        content_type: str,
        content_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store generated content in database"""
        # For now, return a mock content record
        # In full implementation, this would store in the database
        content_id = f"content_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "content_id": content_id,
            "campaign_id": str(campaign_id),
            "content_type": content_type,
            "stored_at": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_campaign_content(
        self,
        campaign_id: Union[str, UUID],
        content_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get generated content for a campaign"""
        try:
            # For now, return mock data
            # In full implementation, query the database
            return [
                {
                    "content_id": "mock_content_1",
                    "campaign_id": str(campaign_id),
                    "content_type": content_type or "email",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
            ]
            
        except Exception as e:
            logger.error(f"Failed to get campaign content: {e}")
            return []