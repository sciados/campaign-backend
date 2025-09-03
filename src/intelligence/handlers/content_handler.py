"""
File: src/intelligence/handlers/content_handler.py
✅ CRUD MIGRATION: Complete database operation migration to CRUD system
✅ FIXED: ChunkedIteratorResult elimination across all database queries
✅ FIXED: Direct SQLAlchemy queries replaced with CRUD methods
✅ FIXED: Async issue resolution with proper CRUD patterns
✅ NEW: Intelligence backlink support for content provenance and analytics
"""
import json
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from src.models.user import User
from src.models.campaign import Campaign
from src.core.crud.intelligence_crud import intelligence_crud, GeneratedContent

# 🚀 CRUD MIGRATION: Import centralized CRUD system
from src.core.crud import campaign_crud, intelligence_crud

from ..utils.campaign_helpers import update_campaign_counters
from ..utils.enum_serializer import EnumSerializerMixin

# 🔧 CRITICAL FIX: JSON serialization helper for datetime objects
from src.utils.json_utils import json_serial

logger = logging.getLogger(__name__)

# 🔧 FIXED: content generation with proper async handling
async def content_generation(
    content_type: str, 
    intelligence_data: Dict[str, Any], 
    preferences: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    🔧 FIXED: content generation with ultra-cheap AI and proper async handling
    This function now properly handles async operations and prevents NoneType errors
    """
    
    if preferences is None:
        preferences = {}
    
    logger.info(f"🎯 content generation: {content_type}")
    
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
        
        logger.info(f"✅ generation successful: {content_type}")
        return result
        
    except Exception as e:
        logger.error(f"❌ generation failed for {content_type}: {str(e)}")
        
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
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    }

class ContentHandler(EnumSerializerMixin):
    """✅ CRUD MIGRATED: Content Handler with complete CRUD integration and intelligence backlink support"""
    
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
        """✅ CRUD MIGRATED: Generate content with complete CRUD integration and intelligence attribution"""
        logger.info(f"🎯 Content generation request received")
        
        content_type = request_data.get("content_type", "email_sequence")
        campaign_id = request_data.get("campaign_id")
        preferences = request_data.get("preferences", {})
        
        logger.info(f"🎯 Generating {content_type} for campaign {campaign_id}")
        
        # Track generation attempt
        self.generation_stats["total_generations"] += 1
        
        try:
            # Verify campaign access - CRUD MIGRATED
            logger.info(f"🔍 Verifying campaign access for {campaign_id}")
            campaign = await self._verify_campaign_access(campaign_id)
            logger.info(f"✅ Campaign access verified")
            
            # Get intelligence data - CRUD MIGRATED
            logger.info(f"📊 Preparing intelligence data")
            intelligence_data = await self._prepare_intelligence_data(campaign_id, campaign)
            logger.info(f"✅ Intelligence data prepared: {len(intelligence_data.get('intelligence_sources', []))} sources")
            
            # 🔧 FIXED: Use enhanced content generation with proper error handling
            logger.info(f"🤖 Starting content generation for {content_type}")
            result = await content_generation(content_type, intelligence_data, preferences)
            logger.info(f"✅ Content generation completed")
            
            # 🔧 CRITICAL FIX: Ensure result is valid
            if result is None:
                logger.error("❌ Content generation returned None")
                raise ValueError("Content generation returned None")
            
            if not isinstance(result, dict):
                logger.error(f"❌ Content generation returned invalid type: {type(result)}")
                raise ValueError(f"Content generation returned invalid type: {type(result)}")
            
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
            
            # Save generated content - CRUD MIGRATED with intelligence attribution
            logger.info(f"💾 Saving generated content to database with intelligence attribution")
            try:
                content_id = await self._save_generated_content(
                    campaign_id, content_type, result, preferences, intelligence_data
                )
                logger.info(f"✅ Content saved with ID: {content_id}")
            except Exception as save_error:
                logger.error(f"❌ Failed to save content: {str(save_error)}")
                # Continue with response even if saving fails
                content_id = None
                logger.warning("⚠️ Continuing with response despite save failure")
            
            # Update campaign counters
            logger.info(f"📊 Updating campaign counters")
            try:
                await self._update_campaign_counters(campaign_id)
                logger.info(f"✅ Campaign counters updated")
            except Exception as counter_error:
                logger.warning(f"⚠️ Campaign counter update failed: {str(counter_error)}")
            
            # Return response
            response = {
                "content_id": content_id,
                "content_type": content_type,
                "generated_content": result,
                "smart_url": None,
                "performance_predictions": {},
                "intelligence_sources_used": len(intelligence_data.get("intelligence_sources", [])),
                "generation_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "generator_used": f"{content_type}_generator",
                    "fallback_used": metadata.get("fallback_generated", False),
                    "ultra_cheap_ai_enabled": self.ultra_cheap_ai_enabled,
                    "ultra_cheap_ai_used": metadata.get("ultra_cheap_ai_used", False),
                    "cost_savings": metadata.get("cost_savings", 0.0),
                    "success": True,
                    "content_saved": content_id is not None,
                    "intelligence_attribution": bool(intelligence_data.get("intelligence_sources"))
                },
                "ultra_cheap_stats": {
                    "total_generations": self.generation_stats["total_generations"],
                    "ultra_cheap_rate": f"{(self.generation_stats['ultra_cheap_generations'] / max(1, self.generation_stats['total_generations'])) * 100:.1f}%",
                    "total_cost_savings": f"${self.generation_stats['cost_savings']:.4f}",
                    "fallback_rate": f"{(self.generation_stats['fallback_generations'] / max(1, self.generation_stats['total_generations'])) * 100:.1f}%"
                }
            }
            
            logger.info(f"✅ Content generation response prepared successfully")
            return response
        
        except Exception as e:
            logger.error(f"❌ Content generation failed: {str(e)}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            
            self.generation_stats["fallback_generations"] += 1
            
            # Return error response instead of raising
            error_response = {
                "content_id": None,
                "content_type": content_type,
                "generated_content": None,
                "success": False,
                "error": str(e),
                "generation_metadata": {
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "generator_used": "error_handler",
                    "fallback_used": True,
                    "ultra_cheap_ai_enabled": self.ultra_cheap_ai_enabled,
                    "ultra_cheap_ai_used": False,
                    "cost_savings": 0.0,
                    "success": False,
                    "error_message": str(e)
                }
            }
            
            logger.info(f"❌ Returning error response: {error_response}")
            return error_response
    
    async def get_content_list(
        self, campaign_id: str, include_body: bool = False, content_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """✅ CRUD MIGRATED: Get list of generated content with CRUD patterns and intelligence attribution"""
        # Verify campaign access first - CRUD MIGRATED
        await self._verify_campaign_access(campaign_id)
        
        # ✅ CRUD MIGRATION: Use intelligence_crud for content queries with intelligence attribution
        content_items = await intelligence_crud.get_generated_content(
            db=self.db,
            campaign_id=campaign_id,
            company_id=str(self.user.company_id),
            content_type=content_type,
            include_intelligence_source=True  # ✅ NEW: Include intelligence source info
        )
        
        # Format response
        content_list = []
        ultra_cheap_count = 0
        attributed_count = 0
        
        for item in content_items:
            # Check if content was generated with ultra-cheap AI
            intelligence_used = item.intelligence_used or {}
            ultra_cheap_used = intelligence_used.get("ultra_cheap_ai_used", False)
            if ultra_cheap_used:
                ultra_cheap_count += 1
            
            # ✅ NEW: Check intelligence attribution
            has_attribution = bool(item.intelligence_source)
            if has_attribution:
                attributed_count += 1
            
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
                "user_tier": item.generation_settings.get("user_tier", "standard") if item.generation_settings else "standard",
                
                # ✅ NEW: Intelligence source attribution
                "has_intelligence_attribution": has_attribution,
                "intelligence_attribution": item.get_source_attribution() if hasattr(item, 'get_source_attribution') else None
            }
            
            if include_body:
                content_data["content_body"] = item.content_body
            else:
                content_data["content_preview"] = self._generate_content_preview(item)
            
            # ✅ NEW: Add intelligence source summary if available
            if has_attribution and hasattr(item, 'get_intelligence_source_summary'):
                content_data["intelligence_source_summary"] = item.get_intelligence_source_summary()
            
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
            # ✅ NEW: Intelligence attribution statistics
            "intelligence_attribution_stats": {
                "attributed_content_count": attributed_count,
                "unattributed_content_count": len(content_list) - attributed_count,
                "attribution_rate": f"{(attributed_count / max(1, len(content_list))) * 100:.1f}%"
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
        """✅ CRUD MIGRATED: Get detailed content including full body with intelligence source information"""
        # Get content with verification - CRUD MIGRATED with intelligence source
        content_item = await self._get_content_with_verification(campaign_id, content_id)
        
        # Parse content body
        parsed_content = self._parse_content_body(content_item.content_body)
        
        # ✅ FIXED: Get intelligence source info using the backlink relationship
        intelligence_info = None
        if content_item.intelligence_source:
            intelligence_info = {
                "id": str(content_item.intelligence_source.id),
                "source_title": content_item.intelligence_source.source_title,
                "source_url": content_item.intelligence_source.source_url,
                "confidence_score": content_item.intelligence_source.confidence_score,
                "source_type": content_item.intelligence_source.source_type.value if content_item.intelligence_source.source_type else None,
                "is_amplified": content_item.intelligence_source.is_amplified(),
                "analysis_status": content_item.intelligence_source.analysis_status.value if content_item.intelligence_source.analysis_status else None,
                "ai_categories_available": {
                    "scientific_intelligence": bool(self._serialize_enum_field(content_item.intelligence_source.scientific_intelligence)),
                    "credibility_intelligence": bool(self._serialize_enum_field(content_item.intelligence_source.credibility_intelligence)),
                    "market_intelligence": bool(self._serialize_enum_field(content_item.intelligence_source.market_intelligence)),
                    "emotional_transformation_intelligence": bool(self._serialize_enum_field(content_item.intelligence_source.emotional_transformation_intelligence)),
                    "scientific_authority_intelligence": bool(self._serialize_enum_field(content_item.intelligence_source.scientific_authority_intelligence))
                }
            }
        
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
            
            # ✅ NEW: Intelligence source information
            "intelligence_source": intelligence_info,
            "has_intelligence_attribution": bool(intelligence_info),
            "source_attribution_text": content_item.get_source_attribution() if hasattr(content_item, 'get_source_attribution') else None,
            "can_regenerate_with_same_source": content_item.can_regenerate_with_same_source() if hasattr(content_item, 'can_regenerate_with_same_source') else False
        }
    
    async def update_content(
        self, campaign_id: str, content_id: str, update_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """✅ CRUD MIGRATED: Update generated content using CRUD patterns"""
        # Get content with verification - CRUD MIGRATED
        content_item = await self._get_content_with_verification(campaign_id, content_id)
        
        # Update allowed fields
        allowed_fields = [
            'content_title', 'content_body', 'content_metadata',
            'user_rating', 'is_published', 'published_at', 'performance_data'
        ]
        
        update_obj = {}
        for field, value in update_data.items():
            if field in allowed_fields:
                update_obj[field] = value
        
        # Add timestamp
        update_obj['updated_at'] = datetime.now(timezone.utc)
        
        # ✅ CRUD MIGRATION: Use intelligence_crud for content updates
        updated_content = await intelligence_crud.update_generated_content(
            db=self.db,
            content_id=content_id,
            update_data=update_obj
        )
        
        return {
            "id": str(updated_content.id),
            "message": "Content updated successfully",
            "updated_at": updated_content.updated_at.isoformat()
        }
    
    async def delete_content(self, campaign_id: str, content_id: str) -> Dict[str, Any]:
        """✅ CRUD MIGRATED: Delete generated content using CRUD patterns"""
        # Get content with verification - CRUD MIGRATED
        content_item = await self._get_content_with_verification(campaign_id, content_id)
        
        # ✅ CRUD MIGRATION: Use intelligence_crud for content deletion
        await intelligence_crud.delete_generated_content(
            db=self.db,
            content_id=content_id
        )
        
        # Update campaign counters
        await self._update_campaign_counters(campaign_id)
        
        return {"message": "Content deleted successfully"}
    
    # Private helper methods - CRUD MIGRATED
    
    async def _verify_campaign_access(self, campaign_id: str) -> Campaign:
        """✅ CRUD MIGRATED: Verify user has access to the campaign"""
        campaign = await campaign_crud.get_campaign_with_access_check(
            db=self.db,
            campaign_id=campaign_id,
            company_id=str(self.user.company_id)
        )
        
        if not campaign:
            raise HTTPException(
                status_code=403, 
                detail="Campaign not found or access denied"
            )
        return campaign
    
    async def _prepare_intelligence_data(self, campaign_id: str, campaign: Campaign) -> Dict[str, Any]:
        """✅ CRUD MIGRATED: Prepare intelligence data for content generation"""
        # ✅ CRUD MIGRATION: Get intelligence sources using CRUD
        intelligence_sources = await intelligence_crud.get_campaign_intelligence(
            db=self.db,
            campaign_id=campaign_id,
            company_id=str(self.user.company_id)
        )
        
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
        """✅ CRUD MIGRATED: Save generated content using CRUD patterns with intelligence attribution"""
        
        try:
            logger.info(f"💾 Starting content save process with intelligence attribution")
            
            intelligence_sources = intelligence_data.get("intelligence_sources", [])
            logger.info(f"📊 Processing {len(intelligence_sources)} intelligence sources")
            
            # ✅ NEW: Get primary intelligence source for attribution
            primary_intelligence_id = None
            if intelligence_sources:
                primary_intelligence_id = intelligence_sources[0]["id"]
                logger.info(f"🎯 Primary intelligence source for attribution: {primary_intelligence_id}")
            
            # Check for amplification data
            amplified_sources = []
            for source in intelligence_sources:
                try:
                    processing_metadata = self._serialize_enum_field(source.get("processing_metadata", {}))
                    if processing_metadata.get("amplification_applied", False):
                        amplified_sources.append(source["id"])
                except Exception as source_error:
                    logger.warning(f"⚠️ Error processing source amplification: {str(source_error)}")
                    continue
            
            logger.info(f"🔄 Found {len(amplified_sources)} amplified sources")
            
            # Extract ultra-cheap AI metadata safely
            metadata = result.get("metadata", {})
            ultra_cheap_ai_used = metadata.get("ultra_cheap_ai_used", False)
            cost_savings = metadata.get("cost_savings", 0.0)
            provider_used = metadata.get("provider_used", "unknown")
            generation_cost = metadata.get("generation_cost", 0.0)
            
            logger.info(f"💰 Ultra-cheap AI: {ultra_cheap_ai_used}, Cost: ${generation_cost:.4f}, Savings: ${cost_savings:.4f}")
            
            # Safely serialize content body
            try:
                content_body = json.dumps(result.get("content", {}), default=json_serial)
                logger.info(f"✅ Content body serialized successfully")
            except Exception as json_error:
                logger.error(f"❌ JSON serialization failed: {str(json_error)}")
                # Fallback to string representation
                content_body = str(result.get("content", {}))
                logger.warning("⚠️ Using string fallback for content body")
            
            # Prepare content data with safe field handling
            content_data = {
                "campaign_id": campaign_id,
                "company_id": str(self.user.company_id) if hasattr(self.user, 'company_id') and self.user.company_id else None,
                "user_id": str(self.user.id),
                "content_type": content_type,
                "content_title": result.get("title", f"Generated {content_type.title()}"),
                "content_body": content_body,
                "content_metadata": metadata,
                "generation_settings": preferences or {},
                
                # ✅ NEW: Intelligence source attribution
                "intelligence_id": primary_intelligence_id,
                
                "intelligence_used": {
                    "sources_count": len(intelligence_sources),
                    "primary_source_id": primary_intelligence_id,
                    "generation_timestamp": datetime.now(timezone.utc).isoformat(),
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
                    "company_session": str(self.user.company_id) if hasattr(self.user, 'company_id') and self.user.company_id else None,
                    "user_email": self.user.email,
                    "user_tier": getattr(self.user, 'tier', 'standard'),
                    "intelligence_attribution_applied": bool(primary_intelligence_id)
                },
                "performance_data": {
                    "generation_time": metadata.get("generation_time", 0.0),
                    "total_tokens": metadata.get("total_tokens", 0),
                    "quality_score": metadata.get("quality_score", 80),
                    "ultra_cheap_ai_used": ultra_cheap_ai_used,
                    "cost_efficiency": cost_savings,
                    "provider_performance": provider_used,
                    "railway_compatible": True,
                    "user_id": str(self.user.id),
                    "company_id": str(self.user.company_id) if hasattr(self.user, 'company_id') and self.user.company_id else None,
                    "generated_by": self.user.email,
                    "user_tier": getattr(self.user, 'tier', 'standard'),
                    "intelligence_source_attribution": bool(primary_intelligence_id)
                },
                "is_published": False
            }
            
            logger.info(f"📝 Content data prepared with intelligence attribution, calling CRUD create method")
            
            # ✅ CRUD MIGRATION: Use intelligence_crud to create content with intelligence attribution
            generated_content = await intelligence_crud.create_generated_content(
                db=self.db,
                content_data=content_data
            )
            
            content_id = str(generated_content.id)
            logger.info(f"✅ Content saved via CRUD with ID: {content_id}")
            logger.info(f"✅ Content saved for user {self.user.email} with intelligence attribution: {primary_intelligence_id}")
            logger.info(f"📊 Content attributed to {len(amplified_sources)} amplified sources")
            
            return content_id
            
        except Exception as save_error:
            logger.error(f"❌ Content save failed: {str(save_error)}")
            import traceback
            logger.error(f"❌ Save error traceback: {traceback.format_exc()}")
            raise save_error
    
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
        """✅ CRUD MIGRATED: Get content with full security verification and intelligence source loading"""
        content_item = await intelligence_crud.get_generated_content_by_id(
            db=self.db,
            content_id=content_id,
            campaign_id=campaign_id,
            company_id=str(self.user.company_id),
            include_intelligence_source=True  # ✅ NEW: Load intelligence source relationship
        )
        
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
    
    async def _update_campaign_counters(self, campaign_id: str):
        """Update campaign counters (non-critical)"""
        try:
            await update_campaign_counters(campaign_id, self.db)
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
    
    # ✅ NEW: Intelligence-specific content methods
    
    async def get_content_by_intelligence_source(
        self, 
        intelligence_id: str, 
        skip: int = 0, 
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get all content generated from a specific intelligence source
        📊 Enables source performance analysis and content provenance tracking
        """
        try:
            logger.info(f"📊 Getting content generated from intelligence source {intelligence_id}")
            
            # Use CRUD to get content by intelligence source
            content_items = await intelligence_crud.get_content_by_intelligence_source(
                db=self.db,
                intelligence_id=intelligence_id,
                company_id=str(self.user.company_id),
                skip=skip,
                limit=limit
            )
            
            # Format content items
            formatted_content = []
            for item in content_items:
                formatted_content.append({
                    "id": str(item.id),
                    "content_type": item.content_type,
                    "content_title": item.content_title,
                    "created_at": item.created_at.isoformat() if item.created_at else None,
                    "user_rating": item.user_rating,
                    "is_published": item.is_published,
                    "performance_score": item.performance_score,
                    "view_count": item.view_count,
                    "content_preview": self._generate_content_preview(item)
                })
            
            # Get intelligence source info for context
            intelligence_source = await intelligence_crud.get_intelligence_by_id(
                db=self.db,
                intelligence_id=intelligence_id,
                company_id=str(self.user.company_id)
            )
            
            source_info = None
            if intelligence_source:
                source_info = {
                    "id": str(intelligence_source.id),
                    "source_title": intelligence_source.source_title,
                    "source_url": intelligence_source.source_url,
                    "confidence_score": intelligence_source.confidence_score,
                    "is_amplified": intelligence_source.is_amplified()
                }
            
            return {
                "intelligence_source": source_info,
                "content_items": formatted_content,
                "total_content": len(formatted_content),
                "source_performance": {
                    "content_generation_count": len(content_items),
                    "published_content": sum(1 for item in content_items if item.is_published),
                    "average_rating": sum(item.user_rating for item in content_items if item.user_rating) / max(1, len([item for item in content_items if item.user_rating])),
                    "total_views": sum(item.view_count or 0 for item in content_items)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting content by intelligence source: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get content by intelligence source: {str(e)}")
    
    async def get_intelligence_performance_report(self, campaign_id: str) -> Dict[str, Any]:
        """
        Generate comprehensive intelligence performance report for a campaign
        📊 Provides detailed analytics on intelligence source effectiveness
        """
        try:
            logger.info(f"📊 Generating intelligence performance report for campaign {campaign_id}")
            
            # Verify campaign access
            await self._verify_campaign_access(campaign_id)
            
            # Get performance analytics
            performance_analytics = await intelligence_crud.get_intelligence_performance_analytics(
                db=self.db,
                campaign_id=campaign_id,
                company_id=str(self.user.company_id)
            )
            
            # Get content attribution report
            attribution_report = await intelligence_crud.get_content_attribution_report(
                db=self.db,
                campaign_id=campaign_id,
                company_id=str(self.user.company_id)
            )
            
            # Get underutilized sources
            underutilized_sources = await intelligence_crud.get_underutilized_intelligence_sources(
                db=self.db,
                campaign_id=campaign_id,
                company_id=str(self.user.company_id)
            )
            
            return {
                "campaign_id": campaign_id,
                "report_generated_at": datetime.now(timezone.utc).isoformat(),
                "performance_analytics": performance_analytics,
                "attribution_report": attribution_report,
                "underutilized_sources": underutilized_sources,
                "recommendations": self._generate_performance_recommendations(
                    performance_analytics, 
                    attribution_report, 
                    underutilized_sources
                )
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error generating intelligence performance report: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate performance report: {str(e)}")
    
    def _generate_performance_recommendations(
        self, 
        performance_analytics: Dict[str, Any], 
        attribution_report: Dict[str, Any], 
        underutilized_sources: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations based on intelligence performance analysis"""
        recommendations = []
        
        # Performance-based recommendations
        summary = performance_analytics.get("summary", {})
        total_sources = summary.get("total_sources", 0)
        total_content = summary.get("total_content_generated", 0)
        
        if total_content == 0:
            recommendations.append("No content generated yet - start by generating content from your highest-confidence intelligence sources")
        elif total_content < total_sources * 2:
            recommendations.append("Low content generation rate - consider generating more content types from existing sources")
        
        # Attribution recommendations
        attribution_summary = attribution_report.get("attribution_summary", {})
        attribution_rate = attribution_summary.get("attribution_rate", 0)
        
        if attribution_rate < 80:
            recommendations.append(f"Attribution rate is {attribution_rate}% - ensure all new content is properly linked to intelligence sources")
        
        # Underutilized source recommendations
        if len(underutilized_sources) > 0:
            high_potential = [s for s in underutilized_sources if s.get("potential_score", 0) > 75]
            if high_potential:
                recommendations.append(f"Found {len(high_potential)} high-potential underutilized sources - prioritize content generation from these")
        
        # Best practices
        best_source = summary.get("best_performing_source")
        if best_source:
            recommendations.append(f"Your best-performing source is '{best_source.get('source_title')}' - consider generating more content types from this source")
        
        if len(recommendations) == 0:
            recommendations.append("Intelligence performance looks good - continue generating diverse content from your top sources")
        
        return recommendations
    
    async def regenerate_content_with_same_source(
        self, 
        original_content_id: str, 
        campaign_id: str,
        content_type: Optional[str] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Regenerate content using the same intelligence source as the original
        🔄 Enables intelligent content iteration and A/B testing
        """
        try:
            logger.info(f"🔄 Regenerating content using same source as {original_content_id}")
            
            # Get original content with intelligence source
            original_content = await self._get_content_with_verification(campaign_id, original_content_id)
            
            if not original_content.intelligence_source:
                raise HTTPException(
                    status_code=400,
                    detail="Original content has no intelligence source attribution - cannot regenerate with same source"
                )
            
            # Use the same content type unless specified
            target_content_type = content_type or original_content.content_type
            
            # Prepare intelligence data using the same source
            intelligence_source = original_content.intelligence_source
            intelligence_data = {
                "campaign_id": campaign_id,
                "campaign_name": f"Regeneration from {intelligence_source.source_title}",
                "intelligence_sources": [{
                    "id": str(intelligence_source.id),
                    "source_type": intelligence_source.source_type.value if intelligence_source.source_type else "unknown",
                    "source_url": intelligence_source.source_url,
                    "confidence_score": intelligence_source.confidence_score or 0.0,
                    "offer_intelligence": self._serialize_enum_field(intelligence_source.offer_intelligence),
                    "psychology_intelligence": self._serialize_enum_field(intelligence_source.psychology_intelligence),
                    "content_intelligence": self._serialize_enum_field(intelligence_source.content_intelligence),
                    "competitive_intelligence": self._serialize_enum_field(intelligence_source.competitive_intelligence),
                    "brand_intelligence": self._serialize_enum_field(intelligence_source.brand_intelligence),
                    "scientific_intelligence": self._serialize_enum_field(intelligence_source.scientific_intelligence),
                    "credibility_intelligence": self._serialize_enum_field(intelligence_source.credibility_intelligence),
                    "market_intelligence": self._serialize_enum_field(intelligence_source.market_intelligence),
                    "emotional_transformation_intelligence": self._serialize_enum_field(intelligence_source.emotional_transformation_intelligence),
                    "scientific_authority_intelligence": self._serialize_enum_field(intelligence_source.scientific_authority_intelligence),
                    "processing_metadata": self._serialize_enum_field(intelligence_source.processing_metadata),
                }]
            }
            
            # Generate new content using the same source
            generation_request = {
                "content_type": target_content_type,
                "campaign_id": campaign_id,
                "preferences": preferences or {}
            }
            
            logger.info(f"🤖 Regenerating {target_content_type} using source: {intelligence_source.source_title}")
            
            # Use the existing generation method but with specific intelligence data
            result = await content_generation(target_content_type, intelligence_data, preferences or {})
            
            # Save the regenerated content
            content_id = await self._save_generated_content(
                campaign_id, target_content_type, result, preferences or {}, intelligence_data
            )
            
            return {
                "regenerated_content_id": content_id,
                "original_content_id": original_content_id,
                "content_type": target_content_type,
                "intelligence_source_used": {
                    "id": str(intelligence_source.id),
                    "source_title": intelligence_source.source_title,
                    "confidence_score": intelligence_source.confidence_score
                },
                "generated_content": result,
                "message": f"Successfully regenerated {target_content_type} using the same intelligence source"
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Error regenerating content with same source: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to regenerate content: {str(e)}")