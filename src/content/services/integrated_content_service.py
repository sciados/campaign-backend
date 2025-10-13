# src/content/services/integrated_content_service.py
"""
Integrated Content Service v4.1.0
Orchestrates all content generators with intelligence integration and enhanced platform image generation.
FIXED: Enhanced platform image generator loading
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone
from uuid import UUID, uuid4
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, insert, update, delete

from src.content.services.prompt_generation_service import PromptGenerationService
from src.content.services.ai_provider_service import AIProviderService
from src.content.services.prompt_storage_service import PromptStorageService

# Import all generators
from src.content.generators.email_generator import EmailGenerator
from src.content.generators.ad_copy_generator import AdCopyGenerator
from src.content.generators.blog_content_generator import BlogContentGenerator
from src.content.generators.social_media_generator import SocialMediaGenerator
from src.content.generators.image_generator import ImageGenerator
from src.content.generators.video_script_generator import VideoScriptGenerator
from src.content.generators.long_form_article_generator import LongFormArticleGenerator

# FIXED: Enhanced platform image generator import
try:
    from src.content.generators.enhanced_platform_image_generator import EnhancedPlatformImageGenerator
    ENHANCED_IMAGE_GENERATOR_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("✅ Enhanced platform image generator imported successfully")
except ImportError as e:
    ENHANCED_IMAGE_GENERATOR_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ Enhanced platform image generator not available: {e}")

logger = logging.getLogger(__name__)

class IntegratedContentService:
    """
    Integrated content generation service that orchestrates all content types
    with intelligence system integration and enhanced platform image generation.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.version = "4.1.0"
        self.prompt_service = PromptGenerationService()
        self.ai_provider_service = AIProviderService()
        # ✅ FIXED: Pass db_session to PromptStorageService
        self.prompt_storage_service = PromptStorageService(db_session)
    
        # Initialize content generators
        self.generators = {}
        self._initialize_generators()
    
        logger.info(f"✅ IntegratedContentService v{self.version} initialized")

    def _initialize_generators(self):
        """Initialize all content generators including enhanced platform image generator"""
        try:
            # Standard generators
            self.generators.update({
                # Email generators
                'email': EmailGenerator(),
                'email_sequence': EmailGenerator(),
                
                # Ad copy generators  
                'ad_copy': AdCopyGenerator(),
                'advertisement': AdCopyGenerator(),
                
                # Blog generators
                'blog_post': BlogContentGenerator(),
                'blogposts': BlogContentGenerator(),
                
                # Social media generators
                'social_post': SocialMediaGenerator(),
                'social_media': SocialMediaGenerator(),
                
                # Image generators
                'image': ImageGenerator(),
                'marketing_image': ImageGenerator(),
                
                # Video generators
                'video_script': VideoScriptGenerator(),
                'video': VideoScriptGenerator(),
                
                # Long form content
                'long_form_article': LongFormArticleGenerator(),
            })
            
            # FIXED: Enhanced platform image generator initialization
            if ENHANCED_IMAGE_GENERATOR_AVAILABLE:
                try:
                    enhanced_generator = EnhancedPlatformImageGenerator()
                    self.generators.update({
                        'platform_image': enhanced_generator,
                        'enhanced_image': enhanced_generator,
                        'multi_platform_image': enhanced_generator
                    })
                    logger.info("✅ Enhanced platform image generator loaded")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to initialize enhanced platform image generator: {e}")
                    logger.info("🔄 Using fallback image generator for platform images")
                    # Fallback to regular image generator
                    self.generators.update({
                        'platform_image': ImageGenerator(),
                        'enhanced_image': ImageGenerator(),
                        'multi_platform_image': ImageGenerator()
                    })
            else:
                logger.info("🔄 Using fallback image generator for platform images")
                # Fallback to regular image generator
                self.generators.update({
                    'platform_image': ImageGenerator(),
                    'enhanced_image': ImageGenerator(),
                    'multi_platform_image': ImageGenerator()
                })
            
            logger.info(f"📊 Initialized {len(self.generators)} content generators")
            
        except Exception as e:
            logger.error(f"❌ Generator initialization failed: {e}")
            # Minimal fallback generators
            self.generators = {
                'email': EmailGenerator(),
                'ad_copy': AdCopyGenerator(),
                'blog_post': BlogContentGenerator(),
                'social_media': SocialMediaGenerator(),
                'image': ImageGenerator(),
                'video_script': VideoScriptGenerator()
            }
            logger.warning(f"⚠️ Using minimal generator set: {len(self.generators)} generators")

    async def generate_content(
        self,
        campaign_id: str,
        content_type: str,
        user_id: str,
        company_id: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate content using the appropriate generator with intelligence integration.
        ENHANCED: Supports enhanced platform image generation
        """
        try:
            logger.info(f"🎯 IntegratedContentService.generate_content called with user_id={user_id}, campaign_id={campaign_id}")
            logger.info(f"📋 Generating {content_type} content for campaign {campaign_id}")
            
            # Get existing intelligence data for AI enhancements
            ai_enhancements = await self._get_campaign_intelligence(campaign_id)
            if ai_enhancements:
                logger.info(f"📊 Extracted AI enhancements from full_analysis_data: {', '.join([f'{k}={v}' for k, v in ai_enhancements.items()])}")
                logger.info(f"✅ Retrieved {len(ai_enhancements)} intelligence records with AI enhancements for campaign")
                logger.info(f"   📊 AI Enhancement status: {bool(ai_enhancements)}")
            
            # Generate content with existing system
            logger.info(f"🔄 Calling _generate_with_existing_system with user_id={user_id}")
            return await self._generate_with_existing_system(
                campaign_id=campaign_id,
                content_type=content_type,
                user_id=user_id,
                company_id=company_id,
                preferences=preferences or {},
                ai_enhancements=ai_enhancements or {}
            )
            
        except Exception as e:
            logger.error(f"❌ Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "content_type": content_type,
                "campaign_id": campaign_id
            }

    async def _generate_with_existing_system(
        self,
        campaign_id: str,
        content_type: str,
        user_id: str,
        company_id: str,
        preferences: Dict[str, Any],
        ai_enhancements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate content using existing generator system with AI enhancements"""
        
        # Find appropriate generator
        logger.info(f"🔍 Looking for generator: '{content_type}'")
        logger.info(f"📋 Available generators: {list(self.generators.keys())}")
        
        generator = self.generators.get(content_type)
        if not generator:
            logger.warning(f"⚠️ No generator found for '{content_type}', trying fallbacks...")
            # Try common fallbacks
            fallback_mapping = {
                'platform_image': 'image',
                'enhanced_image': 'image', 
                'multi_platform_image': 'image',
                'marketing_image': 'image',
                'social_post': 'social_media',
                'blogposts': 'blog_post',
                'advertisement': 'ad_copy'
            }
            fallback_type = fallback_mapping.get(content_type)
            if fallback_type:
                generator = self.generators.get(fallback_type)
                logger.info(f"🔄 Using fallback generator: {fallback_type}")
        
        if not generator:
            raise ValueError(f"No generator available for content type: {content_type}")
        
        logger.info(f"✅ Found generator for: '{content_type}'")
        
        # ENHANCED: Handle platform-specific image generation
        if content_type in ['platform_image', 'enhanced_image', 'multi_platform_image']:
            if ENHANCED_IMAGE_GENERATOR_AVAILABLE and isinstance(generator, EnhancedPlatformImageGenerator):
                return await self._generate_enhanced_platform_image(
                    generator=generator,
                    campaign_id=campaign_id,
                    content_type=content_type,
                    user_id=user_id,
                    preferences=preferences,
                    ai_enhancements=ai_enhancements
                )
            else:
                logger.info("🔄 Using regular image generator for platform image")
                # Fall back to regular image generation
                preferences['enhanced_prompt'] = f"Platform-optimized image for {preferences.get('platform_format', 'social media')}"
        
        # Generate content based on generator type
        if hasattr(generator, 'generate_content'):
            # Modern generator with AI integration
            generation_result = await generator.generate_content(
                campaign_id=campaign_id,
                preferences=preferences,
                ai_enhancements=ai_enhancements
            )
        elif hasattr(generator, 'generate_marketing_image'):
            # ImageGenerator specific method
            intelligence_data = await self._get_full_intelligence_for_generator(campaign_id)
            generation_result = await generator.generate_marketing_image(
                campaign_id=campaign_id,
                intelligence_data=intelligence_data,
                image_type=preferences.get('image_type', 'hero_image'),
                style=preferences.get('style', 'modern_professional'),
                dimensions=preferences.get('dimensions', '1024x1024'),
                provider=preferences.get('provider', 'dall-e-3'),  # Default to dall-e-3 (supported: dall-e-3, flux-schnell, sdxl)
                user_id=user_id
            )
        elif hasattr(generator, 'generate_long_form_article'):
            # LongFormArticleGenerator specific method
            intelligence_data = await self._get_full_intelligence_for_generator(campaign_id)
            generation_result = await generator.generate_long_form_article(
                campaign_id=campaign_id,
                intelligence_data=intelligence_data,
                topic=preferences.get('topic', 'Ultimate Guide'),
                word_count=preferences.get('word_count', 5000),
                article_type=preferences.get('article_type', 'ultimate_guide'),
                target_keywords=preferences.get('target_keywords'),
                tone=preferences.get('tone', 'authoritative'),
                target_audience=preferences.get('target_audience'),
                preferences=preferences,
                user_id=user_id
            )
        elif hasattr(generator, 'generate'):
            # Legacy generator interface
            generation_result = await generator.generate(
                campaign_id=campaign_id,
                **preferences
            )
        else:
            raise ValueError(f"Generator {type(generator)} has no generate method")
        
        if not generation_result.get("success"):
            raise Exception(f"Content generation failed: {generation_result.get('error')}")
        
        logger.info(f"✅ AI-powered content generated using {content_type} generator")
        
        # Store the generated content
        content_id = await self._store_generated_content(
            campaign_id=campaign_id,
            content_type=content_type,
            user_id=user_id,
            company_id=company_id,
            generation_result=generation_result,
            preferences=preferences,
            ai_enhancements=ai_enhancements
        )
        
        # Link to intelligence if available
        if ai_enhancements.get("intelligence_id"):
            await self._link_content_to_intelligence(content_id, ai_enhancements["intelligence_id"])
        
        # Return enhanced result
        return {
            "success": True,
            "content_id": content_id,
            "content_type": content_type,
            "campaign_id": campaign_id,
            "generation_result": generation_result,
            "ai_enhanced": bool(ai_enhancements),
            "generator_type": type(generator).__name__
        }

    async def _generate_enhanced_platform_image(
        self,
        generator: EnhancedPlatformImageGenerator,
        campaign_id: str,
        content_type: str,
        user_id: str,
        preferences: Dict[str, Any],
        ai_enhancements: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate enhanced platform-specific images using the enhanced generator.
        FIXED: Proper enhanced platform image generation
        """
        try:
            logger.info(f"🎨 Generating enhanced platform image with content_type: {content_type}")
            
            if content_type == 'multi_platform_image':
                # Multi-platform batch generation
                platforms = preferences.get('platforms', ['instagram_feed'])
                result = await generator.generate_multi_platform_batch(
                    user_id=user_id,
                    campaign_id=campaign_id,
                    platforms=platforms,
                    image_type=preferences.get('image_type', 'marketing'),
                    batch_style=preferences.get('batch_style', {}),
                    ai_enhancements=ai_enhancements,
                    user_tier=preferences.get('user_tier', 'professional')
                )
            else:
                # Single platform generation
                platform_format = preferences.get('platform_format', 'instagram_feed')
                result = await generator.generate_platform_image(
                    user_id=user_id,
                    campaign_id=campaign_id,
                    platform_format=platform_format,
                    image_type=preferences.get('image_type', 'marketing'),
                    style_preferences=preferences.get('style_preferences', {}),
                    ai_enhancements=ai_enhancements,
                    user_tier=preferences.get('user_tier', 'professional')
                )
            
            if result.get('success'):
                logger.info(f"✅ Enhanced platform image generated successfully")
                return result
            else:
                logger.warning(f"⚠️ Enhanced generation failed: {result.get('error')}")
                raise Exception(f"Enhanced generation failed: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Enhanced platform image generation failed: {e}")
            # Fall back to regular image generation
            logger.info("🔄 Falling back to regular image generation")
            
            regular_generator = ImageGenerator()
            fallback_preferences = {
                **preferences,
                'enhanced_prompt': f"Platform-optimized image for {preferences.get('platform_format', 'social media')}"
            }
            
            return await regular_generator.generate_content(
                campaign_id=campaign_id,
                preferences=fallback_preferences,
                ai_enhancements=ai_enhancements
            )

    async def _get_campaign_intelligence(self, campaign_id: str) -> Dict[str, Any]:
        """Get intelligence data for campaign with AI enhancements"""
        try:
            query = text("""
                SELECT id, full_analysis_data, competitive_insights, market_opportunities
                FROM intelligence
                WHERE campaign_id = :campaign_id
                ORDER BY created_at DESC
                LIMIT 1
            """)

            result = await self.db.execute(query, {"campaign_id": campaign_id})
            row = result.fetchone()

            if not row:
                return {}

            # Extract AI enhancements from analysis data
            full_analysis = row.full_analysis_data if row.full_analysis_data else {}

            ai_enhancements = {
                "intelligence_id": str(row.id),
                "scientific": bool(full_analysis.get("scientific_credibility")),
                "credibility": bool(full_analysis.get("credibility_signals")),
                "market": bool(full_analysis.get("market_positioning")),
                "emotional": bool(full_analysis.get("emotional_triggers")),
                "authority": bool(full_analysis.get("authority_markers")),
                "content": bool(full_analysis.get("content_analysis"))
            }

            # Add specific enhancement data
            if full_analysis.get("emotional_triggers"):
                ai_enhancements["emotional_triggers"] = full_analysis["emotional_triggers"]
            if full_analysis.get("target_demographics"):
                ai_enhancements["target_demographics"] = full_analysis["target_demographics"]
            if full_analysis.get("brand_values"):
                ai_enhancements["brand_values"] = full_analysis["brand_values"]

            return ai_enhancements

        except Exception as e:
            logger.warning(f"Failed to get campaign intelligence: {e}")
            return {}

    async def _get_full_intelligence_for_generator(self, campaign_id: str) -> Dict[str, Any]:
        """Get full intelligence data in the format expected by image and long-form generators"""
        try:
            query = text("""
                SELECT full_analysis_data, competitive_insights, market_opportunities
                FROM intelligence
                WHERE campaign_id = :campaign_id
                ORDER BY created_at DESC
                LIMIT 1
            """)

            result = await self.db.execute(query, {"campaign_id": campaign_id})
            row = result.fetchone()

            if not row:
                return {}

            # Return full analysis data as expected by generators
            intelligence_data = row.full_analysis_data if row.full_analysis_data else {}

            # Add competitive insights and market opportunities if available
            if row.competitive_insights:
                intelligence_data["competitive_insights"] = row.competitive_insights
            if row.market_opportunities:
                intelligence_data["market_opportunities"] = row.market_opportunities

            return intelligence_data

        except Exception as e:
            logger.warning(f"Failed to get full intelligence data: {e}")
            return {}

    async def _store_generated_content(
        self,
        campaign_id: str,
        content_type: str,
        user_id: str,
        company_id: str,
        generation_result: Dict[str, Any],
        preferences: Dict[str, Any],
        ai_enhancements: Dict[str, Any]
    ) -> str:
        """Store generated content in database"""
        try:
            content_id = str(uuid4())
            
            # Extract content based on result structure
            if 'results' in generation_result and isinstance(generation_result['results'], list):
                # Multi-platform results
                content_body = json.dumps(generation_result['results'])
                content_title = f"Multi-Platform {content_type.replace('_', ' ').title()}"
            elif 'image' in generation_result and isinstance(generation_result['image'], dict):
                # ImageGenerator result format: {"image": {"url": "...", ...}}
                content_body = generation_result['image']['url']
                content_title = f"{content_type.replace('_', ' ').title()} - {generation_result['image'].get('image_type', 'Marketing Image')}"
            elif 'image_url' in generation_result:
                # Single image result (legacy format)
                content_body = generation_result['image_url']
                content_title = f"{content_type.replace('_', ' ').title()}"
            elif 'article' in generation_result and isinstance(generation_result['article'], dict):
                # LongFormArticleGenerator result format
                article = generation_result['article']
                content_body = article.get('content', '')
                content_title = article.get('title', f"{content_type.replace('_', ' ').title()}")
            elif 'content' in generation_result:
                # Text content (generic)
                content_body = generation_result['content']
                content_title = generation_result.get('title', f"{content_type.replace('_', ' ').title()}")
            else:
                # Fallback
                content_body = json.dumps(generation_result)
                content_title = f"{content_type.replace('_', ' ').title()}"
            
            # Prepare metadata
            metadata = {
                "preferences": preferences,
                "ai_enhanced": bool(ai_enhancements),
                "generation_method": "integrated_service_v4.1",
                "generator_version": self.version,
                **generation_result.get('metadata', {})
            }
            
            # Insert into database
            query = text("""
                INSERT INTO generated_content 
                (id, campaign_id, user_id, company_id, content_type, content_title, 
                 content_body, content_metadata, generation_method, content_status, created_at, updated_at)
                VALUES 
                (:id, :campaign_id::uuid, :user_id::uuid, :company_id::uuid, :content_type, :content_title,
                 :content_body, :content_metadata, :generation_method, :content_status, :created_at, :updated_at)
            """)
            
            await self.db.execute(query, {
                "id": content_id,
                "campaign_id": campaign_id,
                "user_id": user_id,
                "company_id": company_id or user_id,  # Fallback to user_id if no company
                "content_type": content_type,
                "content_title": content_title,
                "content_body": content_body,
                "content_metadata": json.dumps(metadata),
                "generation_method": "integrated_service",
                "content_status": "generated",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            })
            
            await self.db.commit()
            logger.info(f"✅ Content stored with ID: {content_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store content: {e}")
            await self.db.rollback()
            raise

    async def _link_content_to_intelligence(self, content_id: str, intelligence_id: str):
        """Link generated content to intelligence analysis"""
        try:
            logger.info(f"📊 Linking content to intelligence_id: {intelligence_id}")
            
            query = text("""
                UPDATE generated_content 
                SET content_metadata = content_metadata || jsonb_build_object('intelligence_id', :intelligence_id)
                WHERE id = :content_id
            """)
            
            await self.db.execute(query, {
                "content_id": content_id,
                "intelligence_id": intelligence_id
            })
            
            await self.db.commit()
            
        except Exception as e:
            logger.warning(f"Failed to link content to intelligence: {e}")

    async def get_campaign_content(
        self,
        campaign_id: str,
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get generated content for a campaign"""
        try:
            logger.info(f"📋 Retrieved content for campaign {campaign_id}")
            
            if content_type:
                query = text("""
                    SELECT id, content_type, content_title, content_body, content_metadata,
                            created_at, updated_at, is_published, user_rating, generation_method, 
            content_status
                    FROM generated_content
                    WHERE campaign_id = :campaign_id AND content_type = :content_type
                    ORDER BY created_at DESC LIMIT :limit OFFSET :offset
                 """)
                params = {"campaign_id": campaign_id, "content_type": content_type, "limit": limit, "offset": offset}
            else:
                query = text("""
                    SELECT id, content_type, content_title, content_body, content_metadata,
                            created_at, updated_at, is_published, user_rating, generation_method, 
            content_status
                    FROM generated_content
                    WHERE campaign_id = :campaign_id
                    ORDER BY created_at DESC LIMIT :limit OFFSET :offset
                """)
                params = {"campaign_id": campaign_id, "limit": limit, "offset": offset}
            
            print(f"DEBUG: get_campaign_content called with campaign_id={campaign_id}, content_type={content_type}")
            print(f"DEBUG: Executing query: {query}")
            print(f"DEBUG: With params: {params}")
            
            result = await self.db.execute(query, params)
            rows = result.fetchall()
            
            print(f"DEBUG: Query returned {len(rows)} rows")
            
            content_items = []
            for row in rows:
                try:
                    metadata = json.loads(row.content_metadata) if row.content_metadata else {}
                except:
                    metadata = {}
                
                content_item = {
                    "id": str(row.id),
                    "content_type": row.content_type,
                    "content_title": row.content_title,
                    "content_body": row.content_body,
                    "metadata": metadata,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                    "is_published": row.is_published,
                    "user_rating": row.user_rating,
                    "generation_method": row.generation_method,
                    "content_status": row.content_status,
                    "ai_enhanced": metadata.get("ai_enhanced", False)
                }
                
                content_items.append(content_item)
                print(f"DEBUG: Added content item with id={row.id}, type={row.content_type}")
            
            logger.info(f"📊 Retrieved {len(content_items)} content items for campaign {campaign_id}")
            return content_items
            
        except Exception as e:
            logger.error(f"❌ Failed to get campaign content: {e}")
            return []

    async def get_content_detail(self, content_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific content item"""
        try:
            query = text("""
                SELECT id, campaign_id, content_type, content_title, content_body, content_metadata,
                       created_at, updated_at, is_published, user_rating, generation_method, content_status
                FROM generated_content
                WHERE id = :content_id
            """)
            
            result = await self.db.execute(query, {"content_id": content_id})
            row = result.fetchone()
            
            if not row:
                return None
            
            try:
                metadata = json.loads(row.content_metadata) if row.content_metadata else {}
            except:
                metadata = {}
            
            return {
                "id": str(row.id),
                "campaign_id": str(row.campaign_id),
                "content_type": row.content_type,
                "content_title": row.content_title,
                "content_body": row.content_body,
                "metadata": metadata,
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                "is_published": row.is_published,
                "user_rating": row.user_rating,
                "generation_method": row.generation_method,
                "content_status": row.content_status,
                "ai_enhanced": metadata.get("ai_enhanced", False)
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get content detail: {e}")
            return None

    async def update_content(
        self,
        content_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """Update existing content"""
        try:
            # Build dynamic update query
            update_fields = []
            params = {"content_id": content_id, "updated_at": datetime.now(timezone.utc)}
            
            for field, value in updates.items():
                if field in ['content_title', 'content_body', 'is_published', 'user_rating', 'content_status']:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = value
                elif field == 'metadata':
                    update_fields.append("content_metadata = :content_metadata")
                    params['content_metadata'] = json.dumps(value)
            
            if not update_fields:
                return False
            
            update_fields.append("updated_at = :updated_at")
            
            query = text(f"""
                UPDATE generated_content 
                SET {', '.join(update_fields)}
                WHERE id = :content_id
            """)
            
            result = await self.db.execute(query, params)
            await self.db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to update content: {e}")
            await self.db.rollback()
            return False

    async def delete_content(self, content_id: str) -> bool:
        """Delete content item"""
        try:
            query = text("DELETE FROM generated_content WHERE id = :content_id")
            result = await self.db.execute(query, {"content_id": content_id})
            await self.db.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            logger.error(f"❌ Failed to delete content: {e}")
            await self.db.rollback()
            return False

    async def get_generation_stats(self, user_id: str) -> Dict[str, Any]:
        """Get content generation statistics for a user"""
        try:
            query = text("""
                SELECT 
                    content_type,
                    COUNT(*) as count,
                    COUNT(CASE WHEN is_published THEN 1 END) as published_count,
                    AVG(user_rating) as avg_rating
                FROM generated_content
                WHERE user_id::text = :user_id
                GROUP BY content_type
                ORDER BY count DESC
            """)
            
            result = await self.db.execute(query, {"user_id": user_id})
            rows = result.fetchall()
            
            stats = {
                "content_types": {},
                "total_generated": 0,
                "total_published": 0,
                "average_rating": 0.0
            }
            
            for row in rows:
                stats["content_types"][row.content_type] = {
                    "count": row.count,
                    "published_count": row.published_count,
                    "avg_rating": float(row.avg_rating) if row.avg_rating else 0.0
                }
                stats["total_generated"] += row.count
                stats["total_published"] += row.published_count
            
            if stats["total_generated"] > 0:
                total_rating = sum(
                    type_stats["count"] * type_stats["avg_rating"] 
                    for type_stats in stats["content_types"].values()
                )
                stats["average_rating"] = total_rating / stats["total_generated"]
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Failed to get generation stats: {e}")
            return {"content_types": {}, "total_generated": 0, "total_published": 0, "average_rating": 0.0}

    def get_available_generators(self) -> List[str]:
        """Get list of available content generators"""
        return list(self.generators.keys())

    def get_generator_info(self, generator_type: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific generator"""
        generator = self.generators.get(generator_type)
        if not generator:
            return None
        
        return {
            "type": generator_type,
            "class": type(generator).__name__,
            "version": getattr(generator, 'version', 'unknown'),
            "description": getattr(generator, 'description', 'No description available'),
            "capabilities": getattr(generator, 'capabilities', []),
            "enhanced_platform_support": isinstance(generator, EnhancedPlatformImageGenerator) if ENHANCED_IMAGE_GENERATOR_AVAILABLE else False
        }

    async def health_check(self) -> Dict[str, Any]:
        """Health check for the integrated content service"""
        try:
            # Test database connection
            await self.db.execute(text("SELECT 1"))
            
            # Test generator availability
            generator_health = {}
            for gen_type, generator in self.generators.items():
                try:
                    # Basic generator test
                    if hasattr(generator, 'health_check'):
                        health = await generator.health_check()
                        generator_health[gen_type] = health
                    else:
                        generator_health[gen_type] = {"status": "available", "class": type(generator).__name__}
                except Exception as e:
                    generator_health[gen_type] = {"status": "error", "error": str(e)}
            
            return {
                "status": "healthy",
                "version": self.version,
                "generators": generator_health,
                "total_generators": len(self.generators),
                "enhanced_platform_support": ENHANCED_IMAGE_GENERATOR_AVAILABLE,
                "database": "connected"
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "version": self.version
            }