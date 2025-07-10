"""
File: src/intelligence/handlers/content_handler.py
Content Handler - Contains content generation business logic
Extracted from routes.py to improve maintainability
🔥 FIXED: Enum serialization issues resolved
🚀 ENHANCED: Ultra-cheap AI integration with Railway compatibility
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from intelligence.utils.enum_serializer import EnumSerializerMixin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import CampaignIntelligence, GeneratedContent
from ..utils.campaign_helpers import update_campaign_counters

logger = logging.getLogger(__name__)

# 🚀 NEW: Enhanced content generation with ultra-cheap AI
async def enhanced_content_generation(content_type: str, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None):
    """Enhanced content generation with ultra-cheap AI"""
    
    if preferences is None:
        preferences = {}
    
    logger.info(f"🎯 Enhanced content generation: {content_type}")
    
    try:
        # Try ultra-cheap AI generators first
        if content_type == "email_sequence":
            from src.intelligence.generators.email_generator import EmailSequenceGenerator
            generator = EmailSequenceGenerator()
            return await generator.generate_content(intelligence_data, preferences)
            
        elif content_type == "ad_copy":
            from src.intelligence.generators.ad_copy_generator import AdCopyGenerator
            generator = AdCopyGenerator()
            return await generator.generate_content(intelligence_data, preferences)
            
        elif content_type in ["SOCIAL_POSTS", "social_media"]:
            try:
                from src.intelligence.generators.social_media_generator import SocialMediaGenerator
                generator = SocialMediaGenerator()
                return await generator.generate_content(intelligence_data, preferences)
            except ImportError:
                logger.warning("⚠️ Social media generator not available, using Railway compatibility")
        
        elif content_type == "blog_post":
            try:
                from src.intelligence.generators.blog_post_generator import BlogPostGenerator
                generator = BlogPostGenerator()
                return await generator.generate_content(intelligence_data, preferences)
            except ImportError:
                logger.warning("⚠️ Blog post generator not available, using Railway compatibility")
        
        elif content_type == "LANDING_PAGE":
            try:
                from src.intelligence.generators.landing_page.core.generator import EnhancedLandingPageGenerator
                generator = EnhancedLandingPageGenerator()
                return await generator.generate_content(intelligence_data, preferences)
            except ImportError:
                logger.warning("⚠️ Landing page generator not available, using Railway compatibility")
        
        elif content_type == "video_script":
            try:
                from src.intelligence.generators.video_script_generator import VideoScriptGenerator
                generator = VideoScriptGenerator()
                return await generator.generate_content(intelligence_data, preferences)
            except ImportError:
                logger.warning("⚠️ Video script generator not available, using Railway compatibility")
        
        # Fallback to Railway compatibility layer
        from src.intelligence.utils.railway_compatibility import railway_safe_generate_content
        return await railway_safe_generate_content(content_type, intelligence_data, preferences)
        
    except Exception as e:
        logger.error(f"❌ Enhanced generation failed for {content_type}: {str(e)}")
        
        # Final fallback
        from src.intelligence.utils.railway_compatibility import get_railway_compatibility_handler
        handler = get_railway_compatibility_handler()
        return await handler.generate_ultra_cheap_content(content_type, intelligence_data, preferences)


class ContentHandler(EnumSerializerMixin):
    """Handle content generation and management operations"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        
        # 🚀 NEW: Initialize ultra-cheap AI tracking
        self.ultra_cheap_ai_enabled = True
        self.generation_stats = {
            "total_generations": 0,
            "ultra_cheap_generations": 0,
            "cost_savings": 0.0,
            "fallback_generations": 0
        }
    
    # 🔥 CRITICAL FIX: Add enum serialization helper
    def _serialize_enum_field(self, field_value):
        """Serialize enum field to proper format for API response"""
        if field_value is None:
            return {}
        
        if isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except (json.JSONDecodeError, ValueError):
                logger.warning(f"Failed to parse enum field as JSON: {field_value}")
                return {}
        
        if isinstance(field_value, dict):
            return field_value
        
        logger.warning(f"Unexpected enum field type: {type(field_value)}")
        return {}
    
    async def generate_content(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using intelligence data with ultra-cheap AI"""
        logger.info(f"🎯 Content generation request received (Ultra-cheap AI enabled)")
        
        content_type = request_data.get("content_type", "email_sequence")
        campaign_id = request_data.get("campaign_id")
        preferences = request_data.get("preferences", {})
        
        logger.info(f"🎯 Generating {content_type} for campaign {campaign_id}")
        
        # Track generation attempt
        self.generation_stats["total_generations"] += 1
        
        # Verify campaign access
        campaign = await self._verify_campaign_access(campaign_id)
        
        # Get intelligence data
        intelligence_data = await self._prepare_intelligence_data(campaign_id, campaign)
        
        # 🚀 NEW: Use enhanced content generation with ultra-cheap AI
        try:
            result = await enhanced_content_generation(content_type, intelligence_data, preferences)
            
            # Track ultra-cheap AI usage
            metadata = result.get("metadata", {})
            if metadata.get("ultra_cheap_ai_used", False):
                self.generation_stats["ultra_cheap_generations"] += 1
                cost_savings = metadata.get("cost_savings", 0.0)
                self.generation_stats["cost_savings"] += cost_savings
                logger.info(f"💰 Ultra-cheap AI used: ${cost_savings:.4f} saved")
            
            # Check if fallback was used
            if metadata.get("fallback", False):
                self.generation_stats["fallback_generations"] += 1
                logger.warning(f"⚠️ Fallback generation used for {content_type}")
        
        except Exception as e:
            logger.error(f"❌ Enhanced generation failed, using legacy method: {str(e)}")
            # Fallback to legacy generation method
            result = await self._generate_content_by_type(content_type, intelligence_data, preferences)
            self.generation_stats["fallback_generations"] += 1
        
        # Save generated content
        content_id = await self._save_generated_content(
            campaign_id, content_type, result, preferences, intelligence_data
        )
        
        # Update campaign counters
        await self._update_campaign_counters(campaign_id)
        
        # Enhanced response with ultra-cheap AI stats
        response = {
            "content_id": content_id,
            "content_type": content_type,
            "generated_content": result,
            "smart_url": None,
            "performance_predictions": {},
            "intelligence_sources_used": len(intelligence_data.get("intelligence_sources", [])),
            "generation_metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "generator_used": f"{content_type}_generator",
                "fallback_used": result.get("metadata", {}).get("fallback", False),
                "ultra_cheap_ai_enabled": self.ultra_cheap_ai_enabled,
                "ultra_cheap_ai_used": result.get("metadata", {}).get("ultra_cheap_ai_used", False),
                "cost_savings": result.get("metadata", {}).get("cost_savings", 0.0),
                "success": True
            },
            "ultra_cheap_stats": {
                "total_generations": self.generation_stats["total_generations"],
                "ultra_cheap_rate": f"{(self.generation_stats['ultra_cheap_generations'] / max(1, self.generation_stats['total_generations'])) * 100:.1f}%",
                "total_cost_savings": f"${self.generation_stats['cost_savings']:.4f}",
                "fallback_rate": f"{(self.generation_stats['fallback_generations'] / max(1, self.generation_stats['total_generations'])) * 100:.1f}%"
            }
        }
        
        return response
    
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
        ultra_cheap_count = 0
        for item in content_items:
            # Check if content was generated with ultra-cheap AI
            intelligence_used = item.intelligence_used or {}
            ultra_cheap_used = intelligence_used.get("ultra_cheap_ai_used", False)
            if ultra_cheap_used:
                ultra_cheap_count += 1
            
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
                "intelligence_used": intelligence_used,
                "ultra_cheap_ai_used": ultra_cheap_used  # 🚀 NEW: Ultra-cheap AI indicator
            }
            
            if include_body:
                content_data["content_body"] = item.content_body
            else:
                content_data["content_preview"] = self._generate_content_preview(item)
            
            content_list.append(content_data)
        
        return {
            "campaign_id": campaign_id,
            "total_content": len(content_list),
            "content_items": content_list,
            "ultra_cheap_stats": {  # 🚀 NEW: Ultra-cheap AI stats
                "ultra_cheap_content_count": ultra_cheap_count,
                "ultra_cheap_percentage": f"{(ultra_cheap_count / max(1, len(content_list))) * 100:.1f}%",
                "cost_efficient_content": ultra_cheap_count
            }
        }
    
    async def get_content_detail(self, campaign_id: str, content_id: str) -> Dict[str, Any]:
        """Get detailed content including full body"""
        # Get content with verification
        content_item = await self._get_content_with_verification(campaign_id, content_id)
        
        # Parse content body
        parsed_content = self._parse_content_body(content_item.content_body)
        
        # Get intelligence source info
        intelligence_info = await self._get_intelligence_source_info(content_item.intelligence_source_id)
        
        # Extract ultra-cheap AI info
        intelligence_used = content_item.intelligence_used or {}
        ultra_cheap_info = {
            "ultra_cheap_ai_used": intelligence_used.get("ultra_cheap_ai_used", False),
            "cost_savings": intelligence_used.get("cost_savings", 0.0),
            "provider_used": intelligence_used.get("provider_used", "unknown"),
            "generation_cost": intelligence_used.get("generation_cost", 0.0)
        }
        
        return {
            "id": str(content_item.id),
            "campaign_id": campaign_id,
            "content_type": content_item.content_type,
            "content_title": content_item.content_title,
            "content_body": content_item.content_body,
            "parsed_content": parsed_content,
            "content_metadata": content_item.content_metadata or {},
            "generation_settings": content_item.generation_settings or {},
            "intelligence_used": intelligence_used,
            "ultra_cheap_info": ultra_cheap_info,  # 🚀 NEW: Ultra-cheap AI details
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
        """Prepare intelligence data for content generation with enum serialization"""
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
                # 🔥 CRITICAL FIX: Use enum serialization for all intelligence fields
                source_data = {
                    "id": str(source.id),
                    "source_type": source.source_type.value if source.source_type else "unknown",
                    "source_url": source.source_url,
                    "confidence_score": source.confidence_score or 0.0,
                    "offer_intelligence": self._serialize_enum_field(source.offer_intelligence),
                    "psychology_intelligence": self._serialize_enum_field(source.psychology_intelligence),
                    "content_intelligence": self._serialize_enum_field(source.content_intelligence),
                    "competitive_intelligence": self._serialize_enum_field(source.competitive_intelligence),
                    "brand_intelligence": self._serialize_enum_field(source.brand_intelligence),
                    
                    # 🔥 CRITICAL FIX: Also include AI-enhanced categories with enum serialization
                    "scientific_intelligence": self._serialize_enum_field(source.scientific_intelligence),
                    "credibility_intelligence": self._serialize_enum_field(source.credibility_intelligence),
                    "market_intelligence": self._serialize_enum_field(source.market_intelligence),
                    "emotional_transformation_intelligence": self._serialize_enum_field(source.emotional_transformation_intelligence),
                    "scientific_authority_intelligence": self._serialize_enum_field(source.scientific_authority_intelligence),
                    
                    # 🔥 CRITICAL FIX: Processing metadata with enum serialization
                    "processing_metadata": self._serialize_enum_field(source.processing_metadata),
                }
                intelligence_data["intelligence_sources"].append(source_data)
                
                # Merge into aggregate intelligence
                for intel_type in ["offer_intelligence", "psychology_intelligence", "content_intelligence", "competitive_intelligence", "brand_intelligence"]:
                    self._merge_intelligence_category(intelligence_data, source_data, intel_type)
                
                # Debug logging for first source
                if len(intelligence_data["intelligence_sources"]) == 1:
                    logger.info(f"🔍 Content Handler - First source AI categories:")
                    logger.info(f"   scientific_intelligence: {len(source_data['scientific_intelligence'])} items")
                    logger.info(f"   credibility_intelligence: {len(source_data['credibility_intelligence'])} items")
                    logger.info(f"   market_intelligence: {len(source_data['market_intelligence'])} items")
                    logger.info(f"   emotional_transformation_intelligence: {len(source_data['emotional_transformation_intelligence'])} items")
                    logger.info(f"   scientific_authority_intelligence: {len(source_data['scientific_authority_intelligence'])} items")
                    
            except Exception as source_error:
                logger.warning(f"⚠️ Error processing source {source.id}: {str(source_error)}")
                continue
        
        logger.info(f"✅ Content Handler prepared intelligence data: {len(intelligence_data['intelligence_sources'])} sources")
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
        """Generate content using the appropriate generator (legacy method)"""
        logger.warning(f"⚠️ Using legacy content generation for {content_type}")
        
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
        """Save generated content to database with ultra-cheap AI tracking"""
        intelligence_sources = intelligence_data.get("intelligence_sources", [])
        
        # 🔥 CRITICAL FIX: Check for amplification data using enum serialization
        amplified_sources = []
        for source in intelligence_sources:
            processing_metadata = self._serialize_enum_field(source.get("processing_metadata", {}))
            if processing_metadata.get("amplification_applied", False):
                amplified_sources.append(source["id"])
        
        # 🚀 NEW: Extract ultra-cheap AI metadata
        metadata = result.get("metadata", {})
        ultra_cheap_ai_used = metadata.get("ultra_cheap_ai_used", False)
        cost_savings = metadata.get("cost_savings", 0.0)
        provider_used = metadata.get("provider_used", "unknown")
        generation_cost = metadata.get("generation_cost", 0.0)
        
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
                "amplified": bool(amplified_sources),
                "amplified_sources": amplified_sources,
                "ai_categories_available": self._count_ai_categories(intelligence_sources),
                "enum_serialization_applied": True,
                # 🚀 NEW: Ultra-cheap AI tracking
                "ultra_cheap_ai_used": ultra_cheap_ai_used,
                "cost_savings": cost_savings,
                "provider_used": provider_used,
                "generation_cost": generation_cost,
                "railway_compatible": True
            },
            intelligence_source_id=intelligence_sources[0]["id"] if intelligence_sources else None,
            is_published=False
        )
        
        self.db.add(generated_content)
        await self.db.commit()
        await self.db.refresh(generated_content)
        
        logger.info(f"✅ Content saved with {len(amplified_sources)} amplified sources, ultra-cheap AI: {ultra_cheap_ai_used}")
        return str(generated_content.id)
    
    def _count_ai_categories(self, intelligence_sources: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count available AI intelligence categories across all sources"""
        ai_categories = [
            'scientific_intelligence',
            'credibility_intelligence',
            'market_intelligence',
            'emotional_transformation_intelligence',
            'scientific_authority_intelligence'
        ]
        
        category_counts = {}
        for category in ai_categories:
            total_items = 0
            for source in intelligence_sources:
                ai_data = source.get(category, {})
                if isinstance(ai_data, dict) and ai_data:
                    total_items += len(ai_data)
            category_counts[category] = total_items
        
        return category_counts
    
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
        """Get intelligence source information if available with enum serialization"""
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
        
        # 🔥 CRITICAL FIX: Include amplification status with enum serialization
        processing_metadata = self._serialize_enum_field(intelligence_source.processing_metadata)
        amplification_applied = processing_metadata.get("amplification_applied", False)
        
        return {
            "id": str(intelligence_source.id),
            "source_title": intelligence_source.source_title,
            "source_url": intelligence_source.source_url,
            "confidence_score": intelligence_source.confidence_score,
            "source_type": intelligence_source.source_type.value if intelligence_source.source_type else None,
            "amplification_applied": amplification_applied,
            "ai_categories_available": {
                "scientific_intelligence": bool(self._serialize_enum_field(intelligence_source.scientific_intelligence)),
                "credibility_intelligence": bool(self._serialize_enum_field(intelligence_source.credibility_intelligence)),
                "market_intelligence": bool(self._serialize_enum_field(intelligence_source.market_intelligence)),
                "emotional_transformation_intelligence": bool(self._serialize_enum_field(intelligence_source.emotional_transformation_intelligence)),
                "scientific_authority_intelligence": bool(self._serialize_enum_field(intelligence_source.scientific_authority_intelligence))
            }
        }
    
    async def _update_campaign_counters(self, campaign_id: str):
        """Update campaign counters (non-critical)"""
        try:
            await update_campaign_counters(campaign_id, self.db)
            await self.db.commit()
        except Exception as counter_error:
            logger.warning(f"⚠️ Campaign counter update failed (non-critical): {str(counter_error)}")
    
    # 🚀 NEW: Ultra-cheap AI statistics methods
    
    def get_ultra_cheap_stats(self) -> Dict[str, Any]:
        """Get ultra-cheap AI usage statistics"""
        total = self.generation_stats["total_generations"]
        if total == 0:
            return {
                "total_generations": 0,
                "ultra_cheap_rate": "0%",
                "total_cost_savings": "$0.00",
                "fallback_rate": "0%",
                "efficiency_score": "N/A"
            }
        
        ultra_cheap_rate = (self.generation_stats["ultra_cheap_generations"] / total) * 100
        fallback_rate = (self.generation_stats["fallback_generations"] / total) * 100
        efficiency_score = max(0, 100 - fallback_rate)
        
        return {
            "total_generations": total,
            "ultra_cheap_generations": self.generation_stats["ultra_cheap_generations"],
            "ultra_cheap_rate": f"{ultra_cheap_rate:.1f}%",
            "total_cost_savings": f"${self.generation_stats['cost_savings']:.4f}",
            "average_savings_per_generation": f"${self.generation_stats['cost_savings'] / total:.4f}",
            "fallback_generations": self.generation_stats["fallback_generations"],
            "fallback_rate": f"{fallback_rate:.1f}%",
            "efficiency_score": f"{efficiency_score:.1f}%",
            "status": "optimal" if fallback_rate < 10 else "good" if fallback_rate < 25 else "needs_attention"
        }
    
    def reset_ultra_cheap_stats(self):
        """Reset ultra-cheap AI statistics"""
        self.generation_stats = {
            "total_generations": 0,
            "ultra_cheap_generations": 0,
            "cost_savings": 0.0,
            "fallback_generations": 0
        }
        logger.info("🔄 Ultra-cheap AI statistics reset")
    
    async def get_content_handler_status(self) -> Dict[str, Any]:
        """Get comprehensive content handler status"""
        return {
            "handler_info": {
                "version": "2.0.0-ultra-cheap",
                "ultra_cheap_ai_enabled": self.ultra_cheap_ai_enabled,
                "railway_compatible": True,
                "enum_serialization_fixed": True
            },
            "ultra_cheap_stats": self.get_ultra_cheap_stats(),
            "supported_content_types": [
                "email_sequence",
                "ad_copy", 
                "SOCIAL_POSTS",
                "blog_post",
                "LANDING_PAGE",
                "video_script"
            ],
            "enhanced_features": [
                "Ultra-cheap AI integration",
                "Railway compatibility layer",
                "Graceful fallback handling",
                "Cost tracking and optimization",
                "Enhanced error handling",
                "Enum serialization fixes"
            ]
        }