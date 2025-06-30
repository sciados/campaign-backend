"""
File: src/intelligence/handlers/content_handler.py
Content Handler - Contains content generation business logic
Extracted from routes.py to improve maintainability
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import CampaignIntelligence, GeneratedContent
from ..utils.campaign_helpers import update_campaign_counters

logger = logging.getLogger(__name__)

class ContentHandler:
    """Handle content generation and management operations"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
    
    async def generate_content(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using intelligence data"""
        logger.info(f"🎯 Content generation request received")
        
        content_type = request_data.get("content_type", "email_sequence")
        campaign_id = request_data.get("campaign_id")
        preferences = request_data.get("preferences", {})
        
        logger.info(f"🎯 Generating {content_type} for campaign {campaign_id}")
        
        # Verify campaign access
        campaign = await self._verify_campaign_access(campaign_id)
        
        # Get intelligence data
        intelligence_data = await self._prepare_intelligence_data(campaign_id, campaign)
        
        # Generate content
        result = await self._generate_content_by_type(content_type, intelligence_data, preferences)
        
        # Save generated content
        content_id = await self._save_generated_content(
            campaign_id, content_type, result, preferences, intelligence_data
        )
        
        # Update campaign counters
        await self._update_campaign_counters(campaign_id)
        
        return {
            "content_id": content_id,
            "content_type": content_type,
            "generated_content": result,
            "smart_url": None,
            "performance_predictions": {},
            "intelligence_sources_used": len(intelligence_data.get("intelligence_sources", [])),
            "generation_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "generator_used": f"{content_type}_generator",
                "fallback_used": False,
                "success": True
            }
        }
    
    async def get_content_list(
        self, campaign_id: str, include_body: bool = False, content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get list of generated content for a campaign"""
        # Verify campaign access
        await self._verify_campaign_access(campaign_id)
        
        # Build query
        query = select(GeneratedContent).where(
            GeneratedContent.campaign_id == campaign_id
        ).order_by(GeneratedContent.created_at.desc())
        
        if content_type:
            query = query.where(GeneratedContent.content_type == content_type)
        
        result = await self.db.execute(query)
        content_items = result.scalars().all()
        
        # Format response
        content_list = []
        for item in content_items:
            content_data = {
                "id": str(item.id),
                "content_type": item.content_type,
                "content_title": item.content_title,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
                "user_rating": item.user_rating,
                "is_published": item.is_published,
                "published_at": item.published_at,
                "performance_data": item.performance_data or {},
                "content_metadata": item.content_metadata or {},
                "generation_settings": item.generation_settings or {},
                "intelligence_used": item.intelligence_used or {}
            }
            
            if include_body:
                content_data["content_body"] = item.content_body
            else:
                content_data["content_preview"] = self._generate_content_preview(item)
            
            content_list.append(content_data)
        
        return {
            "campaign_id": campaign_id,
            "total_content": len(content_list),
            "content_items": content_list
        }
    
    async def get_content_detail(self, campaign_id: str, content_id: str) -> Dict[str, Any]:
        """Get detailed content including full body"""
        # Get content with verification
        content_item = await self._get_content_with_verification(campaign_id, content_id)
        
        # Parse content body
        parsed_content = self._parse_content_body(content_item.content_body)
        
        # Get intelligence source info
        intelligence_info = await self._get_intelligence_source_info(content_item.intelligence_source_id)
        
        return {
            "id": str(content_item.id),
            "campaign_id": campaign_id,
            "content_type": content_item.content_type,
            "content_title": content_item.content_title,
            "content_body": content_item.content_body,
            "parsed_content": parsed_content,
            "content_metadata": content_item.content_metadata or {},
            "generation_settings": content_item.generation_settings or {},
            "intelligence_used": content_item.intelligence_used or {},
            "performance_data": content_item.performance_data or {},
            "user_rating": content_item.user_rating,
            "is_published": content_item.is_published,
            "published_at": content_item.published_at,
            "created_at": content_item.created_at.isoformat() if content_item.created_at else None,
            "updated_at": content_item.updated_at.isoformat() if content_item.updated_at else None,
            "intelligence_source": intelligence_info
        }
    
    async def update_content(
        self, campaign_id: str, content_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update generated content"""
        # Get content with verification
        content_item = await self._get_content_with_verification(campaign_id, content_id)
        
        # Update allowed fields
        allowed_fields = [
            'content_title', 'content_body', 'content_metadata',
            'user_rating', 'is_published', 'published_at', 'performance_data'
        ]
        
        for field, value in update_data.items():
            if field in allowed_fields and hasattr(content_item, field):
                setattr(content_item, field, value)
        
        # Update timestamp
        content_item.updated_at = datetime.utcnow()
        
        await self.db.commit()
        await self.db.refresh(content_item)
        
        return {
            "id": str(content_item.id),
            "message": "Content updated successfully",
            "updated_at": content_item.updated_at.isoformat()
        }
    
    async def delete_content(self, campaign_id: str, content_id: str) -> Dict[str, Any]:
        """Delete generated content"""
        # Get content with verification
        content_item = await self._get_content_with_verification(campaign_id, content_id)
        
        # Delete the content
        await self.db.delete(content_item)
        await self.db.commit()
        
        # Update campaign counters
        await self._update_campaign_counters(campaign_id)
        
        return {"message": "Content deleted successfully"}
    
    # Private helper methods
    
    async def _verify_campaign_access(self, campaign_id: str) -> Campaign:
        """Verify user has access to the campaign"""
        campaign_result = await self.db.execute(
            select(Campaign).where(
                and_(
                    Campaign.id == campaign_id,
                    Campaign.company_id == self.user.company_id
                )
            )
        )
        campaign = campaign_result.scalar_one_or_none()
        if not campaign:
            raise ValueError("Campaign not found or access denied")
        return campaign
    
    async def _prepare_intelligence_data(self, campaign_id: str, campaign: Campaign) -> Dict[str, Any]:
        """Prepare intelligence data for content generation"""
        # Get intelligence sources
        intelligence_result = await self.db.execute(
            select(CampaignIntelligence).where(
                CampaignIntelligence.campaign_id == campaign_id
            )
        )
        intelligence_sources = intelligence_result.scalars().all()
        
        # Prepare intelligence data structure
        intelligence_data = {
            "campaign_id": campaign_id,
            "campaign_name": campaign.title,
            "target_audience": campaign.target_audience or "health-conscious adults",
            "offer_intelligence": {},
            "psychology_intelligence": {},
            "content_intelligence": {},
            "competitive_intelligence": {},
            "brand_intelligence": {},
            "intelligence_sources": []
        }
        
        # Aggregate intelligence data from all sources
        for source in intelligence_sources:
            try:
                source_data = {
                    "id": str(source.id),
                    "source_type": source.source_type.value if source.source_type else "unknown",
                    "source_url": source.source_url,
                    "confidence_score": source.confidence_score or 0.0,
                    "offer_intelligence": source.offer_intelligence or {},
                    "psychology_intelligence": source.psychology_intelligence or {},
                    "content_intelligence": source.content_intelligence or {},
                    "competitive_intelligence": source.competitive_intelligence or {},
                    "brand_intelligence": source.brand_intelligence or {}
                }
                intelligence_data["intelligence_sources"].append(source_data)
                
                # Merge into aggregate intelligence
                for intel_type in ["offer_intelligence", "psychology_intelligence", "content_intelligence", "competitive_intelligence", "brand_intelligence"]:
                    self._merge_intelligence_category(intelligence_data, source_data, intel_type)
                    
            except Exception as source_error:
                logger.warning(f"⚠️ Error processing source {source.id}: {str(source_error)}")
                continue
        
        return intelligence_data
    
    def _merge_intelligence_category(self, target: Dict, source: Dict, category: str):
        """Merge intelligence category from source into target"""
        source_intel = source.get(category, {})
        if not source_intel:
            return
        
        current_intel = target.get(category, {})
        
        for key, value in source_intel.items():
            if key in current_intel:
                if isinstance(value, list) and isinstance(current_intel[key], list):
                    current_intel[key].extend(value)
                elif isinstance(value, str) and isinstance(current_intel[key], str):
                    if value not in current_intel[key]:
                        current_intel[key] += f" {value}"
            else:
                current_intel[key] = value
        
        target[category] = current_intel
    
    async def _generate_content_by_type(
        self, content_type: str, intelligence_data: Dict[str, Any], preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content using the appropriate generator"""
        if content_type == "email_sequence":
            from src.intelligence.generators.email_generator import EmailSequenceGenerator
            generator = EmailSequenceGenerator()
            return await generator.generate_email_sequence(intelligence_data, preferences)
        
        elif content_type == "SOCIAL_POSTS":
            from src.intelligence.generators.social_media_generator import SocialMediaGenerator
            generator = SocialMediaGenerator()
            return await generator.generate_social_posts(intelligence_data, preferences)
        
        elif content_type == "ad_copy":
            from src.intelligence.generators.ad_copy_generator import AdCopyGenerator
            generator = AdCopyGenerator()
            return await generator.generate_ad_copy(intelligence_data, preferences)
        
        elif content_type == "blog_post":
            from src.intelligence.generators.blog_post_generator import BlogPostGenerator
            generator = BlogPostGenerator()
            return await generator.generate_blog_post(intelligence_data, preferences)
        
        elif content_type == "LANDING_PAGE":
            from src.intelligence.generators.landing_page.core.generator import EnhancedLandingPageGenerator
            generator = EnhancedLandingPageGenerator()
            return await generator.generate_landing_page(intelligence_data, preferences)
        
        elif content_type == "video_script":
            from src.intelligence.generators.video_script_generator import VideoScriptGenerator
            generator = VideoScriptGenerator()
            return await generator.generate_video_script(intelligence_data, preferences)
        
        else:
            raise ValueError(f"Unknown content type: {content_type}")
    
    async def _save_generated_content(
        self, campaign_id: str, content_type: str, result: Dict[str, Any], 
        preferences: Dict[str, Any], intelligence_data: Dict[str, Any]
    ) -> str:
        """Save generated content to database"""
        intelligence_sources = intelligence_data.get("intelligence_sources", [])
        
        generated_content = GeneratedContent(
            campaign_id=campaign_id,
            company_id=self.user.company_id,
            user_id=self.user.id,
            content_type=content_type,
            content_title=result.get("title", f"Generated {content_type.title()}"),
            content_body=json.dumps(result.get("content", {})),
            content_metadata=result.get("metadata", {}),
            generation_settings=preferences,
            intelligence_used={
                "sources_count": len(intelligence_sources),
                "primary_source_id": str(intelligence_sources[0]["id"]) if intelligence_sources else None,
                "generation_timestamp": datetime.utcnow().isoformat(),
                "amplified": any(
                    source.get("processing_metadata", {}).get("amplification_applied", False)
                    for source in intelligence_sources
                )
            },
            intelligence_source_id=intelligence_sources[0]["id"] if intelligence_sources else None,
            is_published=False
        )
        
        self.db.add(generated_content)
        await self.db.commit()
        await self.db.refresh(generated_content)
        
        return str(generated_content.id)
    
    async def _get_content_with_verification(self, campaign_id: str, content_id: str) -> GeneratedContent:
        """Get content item with campaign verification"""
        content_result = await self.db.execute(
            select(GeneratedContent).where(
                and_(
                    GeneratedContent.id == content_id,
                    GeneratedContent.campaign_id == campaign_id,
                    GeneratedContent.company_id == self.user.company_id
                )
            )
        )
        content_item = content_result.scalar_one_or_none()
        if not content_item:
            raise ValueError("Content not found or access denied")
        return content_item
    
    def _parse_content_body(self, content_body: str) -> Dict[str, Any]:
        """Parse content body JSON safely"""
        try:
            if content_body:
                return json.loads(content_body)
        except json.JSONDecodeError:
            return {"raw_content": content_body}
        return {}
    
    def _generate_content_preview(self, item: GeneratedContent) -> str:
        """Generate a preview of the content"""
        try:
            parsed_body = json.loads(item.content_body) if item.content_body else {}
            if isinstance(parsed_body, dict):
                if "emails" in parsed_body and parsed_body["emails"]:
                    return f"{len(parsed_body['emails'])} emails"
                elif "posts" in parsed_body and parsed_body["posts"]:
                    return f"{len(parsed_body['posts'])} posts"
                elif "ads" in parsed_body and parsed_body["ads"]:
                    return f"{len(parsed_body['ads'])} ads"
                elif "title" in parsed_body:
                    return parsed_body["title"][:100] + "..."
                else:
                    return "Generated content"
            else:
                return str(parsed_body)[:100] + "..."
        except:
            return "Content available"
    
    async def _get_intelligence_source_info(self, intelligence_source_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Get intelligence source information if available"""
        if not intelligence_source_id:
            return None
        
        intel_result = await self.db.execute(
            select(CampaignIntelligence).where(
                CampaignIntelligence.id == intelligence_source_id
            )
        )
        intelligence_source = intel_result.scalar_one_or_none()
        
        if not intelligence_source:
            return None
        
        return {
            "id": str(intelligence_source.id),
            "source_title": intelligence_source.source_title,
            "source_url": intelligence_source.source_url,
            "confidence_score": intelligence_source.confidence_score,
            "source_type": intelligence_source.source_type.value if intelligence_source.source_type else None
        }
    
    async def _update_campaign_counters(self, campaign_id: str):
        """Update campaign counters (non-critical)"""
        try:
            await update_campaign_counters(campaign_id, self.db)
            await self.db.commit()
        except Exception as counter_error:
            logger.warning(f"⚠️ Campaign counter update failed (non-critical): {str(counter_error)}")