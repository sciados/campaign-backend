"""
File: src/intelligence/handlers/content_handler.py
🔧 FIXED: Content Handler - Async Issue Resolution
✅ FIXED: "object NoneType can't be used in 'await' expression" error
✅ FIXED:  content generation function properly async
✅ FIXED: Direct factory usage with proper error handling
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from fastapi import HTTPException

from src.models.user import User
from src.models.campaign import Campaign
from src.models.intelligence import CampaignIntelligence, GeneratedContent
from ..utils.campaign_helpers import update_campaign_counters
from ..utils.enum_serializer import EnumSerializerMixin

logger = logging.getLogger(__name__)

# 🔧 FIXED:  content generation with proper async handling
async def content_generation(
    content_type: str, 
    intelligence_data: Dict[str, Any], 
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    🔧 FIXED:  content generation with ultra-cheap AI and proper async handling
    This function now properly handles async operations and prevents NoneType errors
    """
    
    if preferences is None:
        preferences = {}
    
    logger.info(f"🎯  content generation: {content_type}")
    
    try:
        # Import and use factory directly for reliable generation
        from ..generators.factory import ContentGeneratorFactory
        
        factory = ContentGeneratorFactory()
        
        # 🔧 CRITICAL FIX: Ensure factory method is properly awaited
        result = await factory.generate_content(content_type, intelligence_data, preferences)
        
        # 🔧 CRITICAL FIX: Check for None result
        if result is None:
            raise ValueError(f"Factory returned None for content_type: {content_type}")
        
        # 🔧 CRITICAL FIX: Validate result structure
        if not isinstance(result, dict):
            raise ValueError(f"Factory returned invalid result type: {type(result)}")
        
        logger.info(f"✅  generation successful: {content_type}")
        return result
        
    except Exception as e:
        logger.error(f"❌  generation failed for {content_type}: {str(e)}")
        
        # 🔧 FIXED: Return proper fallback instead of raising
        return await _generate_fallback_content(content_type, intelligence_data, str(e))

async def _generate_fallback_content(
    content_type: str, 
    intelligence_data: Dict[str, Any], 
    error_message: str
) -> Dict[str, Any]:
    """🔧 FIXED: Generate fallback content when primary generation fails"""
    
    # Extract product name safely
    product_name = "PRODUCT"
    try:
        offer_intel = intelligence_data.get("offer_intelligence", {})
        insights = offer_intel.get("insights", [])
        for insight in insights:
            if "called" in str(insight).lower():
                words = str(insight).split()
                for i, word in enumerate(words):
                    if word.lower() == "called" and i + 1 < len(words):
                        product_name = words[i + 1].upper().replace(",", "").replace(".", "")
                        break
    except:
        pass
    
    # Generate content-type specific fallback
    if content_type == "email_sequence":
        fallback_content = {
            "sequence_title": f"Email Sequence for {product_name}",
            "emails": [
                {
                    "email_number": 1,
                    "subject": f"Discover {product_name} Benefits",
                    "body": f"Learn about the natural health benefits of {product_name} and how it can support your wellness journey.",
                    "send_delay": "Day 1",
                    "fallback_generated": True
                }
            ]
        }
    elif content_type == "SOCIAL_POSTS":
        fallback_content = {
            "posts": [
                {
                    "post_number": 1,
                    "platform": "facebook",
                    "content": f"Discover the natural benefits of {product_name} for your wellness journey! 🌿 #health #wellness",
                    "fallback_generated": True
                }
            ]
        }
    elif content_type == "ad_copy":
        fallback_content = {
            "ads": [
                {
                    "ad_number": 1,
                    "platform": "facebook",
                    "headline": f"{product_name} - Natural Health Solution",
                    "body": f"Experience the benefits of {product_name} for natural health optimization.",
                    "fallback_generated": True
                }
            ]
        }
    else:
        fallback_content = {
            "fallback_generated": True,
            "product_name": product_name,
            "note": f"Fallback content for {content_type}"
        }
    
    return {
        "content_type": content_type,
        "title": f"Fallback {content_type.title()} for {product_name}",
        "content": fallback_content,
        "metadata": {
            "generated_by": "enhanced_fallback_generator",
            "product_name": product_name,
            "content_type": content_type,
            "status": "fallback",
            "error": error_message,
            "fallback_generated": True,
            "ultra_cheap_ai_used": False,
            "generation_cost": 0.0,
            "generated_at": datetime.utcnow().isoformat()
        }
    }

class ContentHandler(EnumSerializerMixin):
    """🔧 FIXED: Content Handler with proper async handling and error prevention"""
    
    def __init__(self, db: AsyncSession, user: User):
        self.db = db
        self.user = user
        
        # Validate user for security
        if not user or not user.id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Initialize tracking
        self.ultra_cheap_ai_enabled = True
        self.generation_stats = {
            "total_generations": 0,
            "ultra_cheap_generations": 0,
            "cost_savings": 0.0,
            "fallback_generations": 0
        }
    
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
        """🔧 FIXED: Generate content with proper error handling and async operations"""
        logger.info(f"🎯 Content generation request received")
        
        content_type = request_data.get("content_type", "email_sequence")
        campaign_id = request_data.get("campaign_id")
        preferences = request_data.get("preferences", {})
        
        logger.info(f"🎯 Generating {content_type} for campaign {campaign_id}")
        
        # Track generation attempt
        self.generation_stats["total_generations"] += 1
        
        try:
            # Verify campaign access
            campaign = await self._verify_campaign_access(campaign_id)
            
            # Get intelligence data
            intelligence_data = await self._prepare_intelligence_data(campaign_id, campaign)
            
            # 🔧 FIXED: Use enhanced content generation with proper error handling
            result = await content_generation(content_type, intelligence_data, preferences)
            
            # 🔧 CRITICAL FIX: Ensure result is not None
            if result is None:
                raise ValueError("Content generation returned None")
            
            # Track usage
            metadata = result.get("metadata", {})
            if metadata.get("ultra_cheap_ai_used", False):
                self.generation_stats["ultra_cheap_generations"] += 1
                cost_savings = metadata.get("cost_savings", 0.0)
                self.generation_stats["cost_savings"] += cost_savings
                logger.info(f"💰 Ultra-cheap AI used: ${cost_savings:.4f} saved")
            
            if metadata.get("fallback_generated", False):
                self.generation_stats["fallback_generations"] += 1
                logger.warning(f"⚠️ Fallback generation used for {content_type}")
            
            # Save generated content
            content_id = await self._save_generated_content(
                campaign_id, content_type, result, preferences, intelligence_data
            )
            
            # Update campaign counters
            await self._update_campaign_counters(campaign_id)
            
            # Return response
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
                    "fallback_used": metadata.get("fallback_generated", False),
                    "ultra_cheap_ai_enabled": self.ultra_cheap_ai_enabled,
                    "ultra_cheap_ai_used": metadata.get("ultra_cheap_ai_used", False),
                    "cost_savings": metadata.get("cost_savings", 0.0),
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
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {str(e)}")
            self.generation_stats["fallback_generations"] += 1
            
            # Return error response instead of raising
            return {
                "content_id": None,
                "content_type": content_type,
                "generated_content": None,
                "success": False,
                "error": str(e),
                "generation_metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "generator_used": "error_handler",
                    "fallback_used": True,
                    "ultra_cheap_ai_enabled": self.ultra_cheap_ai_enabled,
                    "ultra_cheap_ai_used": False,
                    "cost_savings": 0.0,
                    "success": False,
                    "error_message": str(e)
                }
            }
    
    async def get_content_list(
        self, campaign_id: str, include_body: bool = False, content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """🔐 SECURE: Get list of generated content with proper user filtering"""
        # Verify campaign access first
        await self._verify_campaign_access(campaign_id)
        
        # Build query with security filters
        query = select(GeneratedContent).where(
            and_(
                GeneratedContent.campaign_id == campaign_id,
                GeneratedContent.company_id == self.user.company_id,
            )
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
                # 🔧 CRITICAL FIX: Safe performance_data access
                "performance_data": getattr(item, 'performance_data', {}) or {},
                "content_metadata": item.content_metadata or {},
                "generation_settings": item.generation_settings or {},
                "intelligence_used": intelligence_used,
                "ultra_cheap_ai_used": ultra_cheap_used,
                "generated_by": item.content_metadata.get("user_email", "unknown") if item.content_metadata else "unknown",
                "user_tier": item.generation_settings.get("user_tier", "standard") if item.generation_settings else "standard"
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
            "ultra_cheap_stats": {
                "ultra_cheap_content_count": ultra_cheap_count,
                "ultra_cheap_percentage": f"{(ultra_cheap_count / max(1, len(content_list))) * 100:.1f}%",
                "cost_efficient_content": ultra_cheap_count
            },
            "user_context": {
                "user_id": str(self.user.id),
                "company_id": str(self.user.company_id) if hasattr(self.user, 'company_id') else None,
                "user_email": self.user.email,
                "access_level": getattr(self.user, 'role', 'user'),
                "user_tier": getattr(self.user, 'tier', 'standard')
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
            "ultra_cheap_info": ultra_cheap_info,
            # 🔧 CRITICAL FIX: Safe performance_data access
            "performance_data": getattr(content_item, 'performance_data', {}) or {},
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
        """🔐 SECURE: Verify user has access to the campaign"""
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
            raise HTTPException(
                status_code=403, 
                detail="Campaign not found or access denied"
            )
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
                    "scientific_intelligence": self._serialize_enum_field(source.scientific_intelligence),
                    "credibility_intelligence": self._serialize_enum_field(source.credibility_intelligence),
                    "market_intelligence": self._serialize_enum_field(source.market_intelligence),
                    "emotional_transformation_intelligence": self._serialize_enum_field(source.emotional_transformation_intelligence),
                    "scientific_authority_intelligence": self._serialize_enum_field(source.scientific_authority_intelligence),
                    "processing_metadata": self._serialize_enum_field(source.processing_metadata),
                }
                intelligence_data["intelligence_sources"].append(source_data)
                
                # Merge into aggregate intelligence
                for intel_type in ["offer_intelligence", "psychology_intelligence", "content_intelligence", "competitive_intelligence", "brand_intelligence"]:
                    self._merge_intelligence_category(intelligence_data, source_data, intel_type)
                    
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
    
    async def _save_generated_content(
        self, campaign_id: str, content_type: str, result: Dict[str, Any], 
        preferences: Dict[str, Any], intelligence_data: Dict[str, Any]
    ) -> str:
        """🔐 SECURE: Save generated content with ultra-cheap AI tracking"""
        intelligence_sources = intelligence_data.get("intelligence_sources", [])
        
        # Check for amplification data
        amplified_sources = []
        for source in intelligence_sources:
            processing_metadata = self._serialize_enum_field(source.get("processing_metadata", {}))
            if processing_metadata.get("amplification_applied", False):
                amplified_sources.append(source["id"])
        
        # Extract ultra-cheap AI metadata
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
                "ultra_cheap_ai_used": ultra_cheap_ai_used,
                "cost_savings": cost_savings,
                "provider_used": provider_used,
                "generation_cost": generation_cost,
                "railway_compatible": True,
                "user_session": str(self.user.id),
                "company_session": str(self.user.company_id) if hasattr(self.user, 'company_id') else None,
                "user_email": self.user.email,
                "user_tier": getattr(self.user, 'tier', 'standard')
            },
            # 🔧 CRITICAL FIX: Populate performance_data to prevent infinite loop
            performance_data={
                "generation_time": metadata.get("generation_time", 0.0),
                "total_tokens": metadata.get("total_tokens", 0),
                "quality_score": metadata.get("quality_score", 80),
                "ultra_cheap_ai_used": ultra_cheap_ai_used,
                "cost_efficiency": cost_savings,
                "provider_performance": provider_used,
                "railway_compatible": True,
                "user_id": str(self.user.id),
                "company_id": str(self.user.company_id) if hasattr(self.user, 'company_id') else None,
                "generated_by": self.user.email,
                "user_tier": getattr(self.user, 'tier', 'standard')
            },
            is_published=False
        )
        
        self.db.add(generated_content)
        await self.db.commit()
        await self.db.refresh(generated_content)
        
        logger.info(f"✅ Content saved for user {self.user.email} with {len(amplified_sources)} amplified sources")
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
        """🔐 SECURE: Get content with full security verification"""
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
            raise HTTPException(
                status_code=403,
                detail="Content not found or access denied"
            )
        return content_item
    
    def _parse_content_body(self, content_body: str) -> Dict[str, Any]:
        """Parse content body JSON safely"""
        try:
            if content_body:
                parsed = json.loads(content_body)
                if isinstance(parsed, dict) and parsed:
                    return parsed
                else:
                    return {"raw_content": content_body, "parsing_issue": "invalid_structure"}
            else:
                return {"parsing_issue": "empty_content"}
        except json.JSONDecodeError as e:
            return {"raw_content": content_body, "parsing_issue": "json_decode_error"}
        except Exception as e:
            return {"raw_content": content_body, "parsing_issue": "unknown_error"}
    
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