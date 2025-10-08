# src/content/services/integrated_content_service.py
"""
Content Service that integrates with existing intelligence/generators system
Uses your current EmailSequenceGenerator, AdCopyGenerator, etc.
"""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import logging
import json

logger = logging.getLogger(__name__)

class IntegratedContentService:
    """Content service that uses existing intelligence generators"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self._generators = {}
        self._initialize_generators()
    
    def _initialize_generators(self):
        """Initialize AI-powered generators with database session for prompt storage"""
        try:
            # Import AI-powered generators with Intelligence → Prompt → AI pipeline
            from src.content.generators import (
                EmailGenerator,
                AdCopyGenerator,
                SocialMediaGenerator,
                get_available_generators,
                BlogContentGenerator
            )

            # Initialize available generators WITH db_session for prompt storage
            available = get_available_generators()

            # available is a list of generator class names, not a dict
            if "EmailGenerator" in available:
                self._generators["email"] = EmailGenerator(db_session=self.db)
                self._generators["email_sequence"] = EmailGenerator(db_session=self.db)
                logger.info("Email sequence generator loaded")

            if "AdCopyGenerator" in available:
                self._generators["ad_copy"] = AdCopyGenerator(db_session=self.db)
                self._generators["advertisement"] = AdCopyGenerator(db_session=self.db)
                logger.info("Ad copy generator loaded")

            if "BlogContentGenerator" in available:
                self._generators["blog_post"] = BlogContentGenerator(db_session=self.db)
                self._generators["blogposts"] = BlogContentGenerator(db_session=self.db)
                logger.info("Blog Post generator loaded")

            if "SocialMediaGenerator" in available:
                self._generators["social_post"] = SocialMediaGenerator(db_session=self.db)
                self._generators["social_media"] = SocialMediaGenerator(db_session=self.db)
                logger.info("Social media generator loaded")

            # Always set factory to None to avoid errors
            self._factory = None

            logger.info(f"Initialized {len(self._generators)} content generators")

        except ImportError as e:
            logger.warning(f"Could not import existing generators: {e}")
            self._generators = {}
            self._factory = None
    
    async def generate_content(
        self,
        campaign_id: Union[str, UUID],
        content_type: str,
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate content using existing generator system"""
        try:
            logger.info(f"🎯 IntegratedContentService.generate_content called with user_id={user_id}, campaign_id={campaign_id}")
            logger.info(f"Generating {content_type} content for campaign {campaign_id}")
            
            # Create workflow tracking
            workflow_id = await self._create_workflow_record(
                campaign_id=campaign_id,
                user_id=user_id,
                company_id=company_id,
                content_types=[content_type],
                preferences=preferences or {}
            )
            
            # Get intelligence data for the campaign
            intelligence_data = await self._get_campaign_intelligence(campaign_id)
            
            # Generate content using existing generators
            logger.info(f"🔄 Calling _generate_with_existing_system with user_id={user_id}")
            result = await self._generate_with_existing_system(
                content_type=content_type,
                intelligence_data=intelligence_data,
                preferences=preferences or {},
                campaign_id=campaign_id,
                user_id=user_id
            )
            
            # Store in existing generated_content table
            content_id = await self._store_content_in_existing_table(
                campaign_id=campaign_id,
                user_id=user_id,
                company_id=company_id,
                content_type=content_type,
                content_data=result,
                generation_settings=preferences or {},
                intelligence_data=intelligence_data  # Pass intelligence data for tracking
            )
            
            # Update workflow as completed
            await self._update_workflow_status(workflow_id, "completed", items_completed=1)
            
            return {
                "success": True,
                "content_id": str(content_id),
                "content_type": content_type,
                "workflow_id": str(workflow_id),
                "generated_content": result,
                "generator_used": self._get_generator_name(content_type),
                "intelligence_sources_used": len(intelligence_data) if intelligence_data else 0,
                "message": f"{content_type} generated successfully using existing generator system"
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")

            # Rollback the transaction to clear failed state
            try:
                await self.db.rollback()
                logger.info("Transaction rolled back after error")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")

            # Try to update workflow status after rollback
            if 'workflow_id' in locals():
                try:
                    await self._update_workflow_status(workflow_id, "failed", error_details=str(e))
                    await self.db.commit()
                except Exception as workflow_error:
                    logger.error(f"Failed to update workflow status: {workflow_error}")

            return {
                "success": False,
                "error": str(e),
                "content_type": content_type,
                "campaign_id": str(campaign_id),
                "fallback_used": True
            }
    
    async def _get_campaign_intelligence(self, campaign_id: Union[str, UUID]) -> Optional[List[Dict]]:
        """
        Get campaign intelligence data including ALL 6 AI enhancer outputs
        This provides rich, AI-generated intelligence for content generation
        """
        try:
            # Get intelligence with ALL AI enhancer data for maximum variation
            query = text("""
                SELECT ic.product_name, ic.salespage_url, ic.confidence_score,
                       pd.features, pd.benefits, pd.ingredients, pd.conditions,
                       md.category, md.positioning, md.competitive_advantages, md.target_audience,
                       ic.scientific_intelligence,
                       ic.credibility_intelligence,
                       ic.market_intelligence,
                       ic.emotional_transformation_intelligence,
                       ic.scientific_authority_intelligence
                FROM intelligence_core ic
                LEFT JOIN product_data pd ON ic.id = pd.intelligence_id
                LEFT JOIN market_data md ON ic.id = md.intelligence_id
                WHERE ic.user_id IN (
                    SELECT user_id FROM campaigns WHERE id = :campaign_id
                )
                ORDER BY ic.confidence_score DESC
                LIMIT 10
            """)

            result = await self.db.execute(query, {"campaign_id": UUID(str(campaign_id))})
            rows = result.fetchall()

            intelligence_data = []
            for row in rows:
                # Parse JSON intelligence from AI enhancers
                scientific_intel = json.loads(row.scientific_intelligence) if row.scientific_intelligence else {}
                credibility_intel = json.loads(row.credibility_intelligence) if row.credibility_intelligence else {}
                market_intel = json.loads(row.market_intelligence) if row.market_intelligence else {}
                emotional_intel = json.loads(row.emotional_transformation_intelligence) if row.emotional_transformation_intelligence else {}
                authority_intel = json.loads(row.scientific_authority_intelligence) if row.scientific_authority_intelligence else {}

                data = {
                    # Basic data
                    "product_name": row.product_name,
                    "salespage_url": row.salespage_url,
                    "confidence_score": float(row.confidence_score) if row.confidence_score else 0.0,

                    # Product & Market data (RAG-extracted)
                    "features": row.features if row.features else [],
                    "benefits": row.benefits if row.benefits else [],
                    "ingredients": row.ingredients if row.ingredients else [],
                    "conditions": row.conditions if row.conditions else [],
                    "category": row.category,
                    "positioning": row.positioning,
                    "competitive_advantages": row.competitive_advantages if row.competitive_advantages else [],
                    "target_audience": row.target_audience,

                    # AI-Enhanced Intelligence (from 6 enhancers)
                    "scientific_intelligence": scientific_intel,
                    "credibility_intelligence": credibility_intel,
                    "market_intelligence": market_intel,
                    "emotional_transformation_intelligence": emotional_intel,
                    "scientific_authority_intelligence": authority_intel,

                    # Flag for prompt service to know enhanced data is available
                    "has_ai_enhancements": bool(scientific_intel or credibility_intel or market_intel or emotional_intel or authority_intel)
                }
                intelligence_data.append(data)

            logger.info(f"✅ Retrieved {len(intelligence_data)} intelligence records with AI enhancements for campaign")
            if intelligence_data:
                logger.info(f"   📊 AI Enhancement status: {intelligence_data[0].get('has_ai_enhancements', False)}")

            return intelligence_data

        except Exception as e:
            logger.error(f"Failed to get campaign intelligence: {e}")
            return []
    
    async def _generate_with_existing_system(
        self,
        content_type: str,
        intelligence_data: List[Dict],
        preferences: Dict[str, Any],
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Generate content using AI-powered generator system with Intelligence → Prompt → AI pipeline"""

        # Normalize content type
        content_type_normalized = content_type.lower()

        logger.info(f"🔍 Looking for generator: '{content_type_normalized}'")
        logger.info(f"📋 Available generators: {list(self._generators.keys())}")

        # Transform intelligence data to the format expected by new generators
        transformed_intelligence = self._transform_intelligence_for_ai_generators(intelligence_data)

        # Use AI-powered generators with new methods
        if content_type_normalized in self._generators:
            logger.info(f"✅ Found generator for: '{content_type_normalized}'")
            generator = self._generators[content_type_normalized]

            try:
                # Email sequence generation
                if 'email' in content_type_normalized:
                    # Support both 'email_count' and 'sequence_length' for backward compatibility
                    sequence_length = preferences.get("email_count") or preferences.get("sequence_length", 5)

                    result = await generator.generate_email_sequence(
                        campaign_id=campaign_id,
                        intelligence_data=transformed_intelligence,
                        sequence_length=sequence_length,
                        tone=preferences.get("tone", "persuasive"),
                        target_audience=preferences.get("target_audience"),
                        preferences=preferences,
                        user_id=user_id
                    )

                # Ad copy generation
                elif 'ad' in content_type_normalized:
                    result = await generator.generate_ad_copy(
                        campaign_id=campaign_id,
                        intelligence_data=transformed_intelligence,
                        platform=preferences.get("platform", "google"),
                        ad_format=preferences.get("ad_format", "responsive"),
                        variation_count=preferences.get("variation_count", 3),
                        tone=preferences.get("tone", "persuasive"),
                        target_audience=preferences.get("target_audience"),
                        preferences=preferences,
                        user_id=user_id
                    )

                # Social media generation
                elif 'social' in content_type_normalized:
                    result = await generator.generate_social_content(
                        campaign_id=campaign_id,
                        intelligence_data=transformed_intelligence,
                        platform=preferences.get("platform", "instagram"),
                        post_count=preferences.get("post_count", 5),
                        tone=preferences.get("tone", "engaging"),
                        target_audience=preferences.get("target_audience"),
                        preferences=preferences,
                        user_id=user_id
                    )

                # Blog post generation
                elif 'blog' in content_type_normalized:
                    result = await generator.generate_blog_post(
                        campaign_id=campaign_id,
                        intelligence_data=transformed_intelligence,
                        topic=preferences.get("topic"),
                        word_count=preferences.get("word_count", 1500),
                        tone=preferences.get("tone", "informative"),
                        target_audience=preferences.get("target_audience"),
                        include_sections=preferences.get("include_sections"),
                        preferences=preferences,
                        user_id=user_id
                    )

                else:
                    # Generic fallback
                    result = await generator.generate_content(transformed_intelligence, preferences)

                logger.info(f"✅ AI-powered content generated using {content_type} generator")
                return result

            except Exception as e:
                logger.error(f"❌ AI generator {content_type} failed: {e}")
                import traceback
                logger.error(traceback.format_exc())
        else:
            logger.warning(f"⚠️ No generator found for '{content_type_normalized}', using fallback")

        # Ultimate fallback - create basic content
        logger.info(f"📝 Creating fallback content for: {content_type}")
        return await self._create_fallback_content(content_type, intelligence_data, preferences)

    def _transform_intelligence_for_ai_generators(self, intelligence_data: List[Dict]) -> Dict[str, Any]:
        """Transform old intelligence format to new Intelligence → Prompt → AI format"""

        if not intelligence_data:
            return {
                "product_name": "Product",
                "offer_intelligence": {},
                "psychology_intelligence": {},
                "brand_intelligence": {},
                "market_intelligence": {}
            }

        # Use first intelligence record (highest confidence)
        intel = intelligence_data[0]

        return {
            "product_name": intel.get("product_name", "Product"),
            "salespage_url": intel.get("salespage_url"),
            "confidence_score": intel.get("confidence_score", 0.0),

            # Offer intelligence
            "offer_intelligence": {
                "key_features": intel.get("features", []),
                "benefits": intel.get("benefits", []),
                "ingredients": intel.get("ingredients", []),
                "conditions": intel.get("conditions", []),
                "competitive_advantages": intel.get("competitive_advantages", []),
                "value_proposition": intel.get("positioning", "")
            },

            # Psychology intelligence
            "psychology_intelligence": {
                "target_audience": intel.get("target_audience", "general audience"),
                "pain_points": intel.get("conditions", []),
                "emotional_triggers": ["transformation", "improvement"],
                "objections": []
            },

            # Brand intelligence
            "brand_intelligence": {
                "category": intel.get("category", ""),
                "positioning": intel.get("positioning", ""),
                "tone": "professional"
            },

            # Market intelligence
            "market_intelligence": {
                "category": intel.get("category", ""),
                "competitive_advantages": intel.get("competitive_advantages", [])
            },

            # Intelligence sources (for metadata)
            "intelligence_sources": ["campaign_intelligence"]
        }
    
    async def _create_fallback_content(
        self,
        content_type: str,
        intelligence_data: List[Dict],
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create fallback content when generators are unavailable"""
        
        product_name = preferences.get("product_name", "Your Product")
        if intelligence_data and intelligence_data[0].get("product_name"):
            product_name = intelligence_data[0]["product_name"]
        
        if "email" in content_type.lower():
            return {
                "content": {
                    "emails": [
                        {
                            "email_number": 1,
                            "subject": f"Introducing {product_name}",
                            "body": f"Hi [Name],\n\nI wanted to introduce you to {product_name}...\n\n[Generated content]",
                            "send_delay": "immediate"
                        }
                    ]
                },
                "metadata": {
                    "generator": "fallback",
                    "product_name": product_name,
                    "intelligence_used": len(intelligence_data)
                }
            }
        
        elif "social" in content_type.lower():
            return {
                "content": {
                    "posts": [
                        {
                            "platform": "general",
                            "text": f"Excited to share {product_name} with you! 🚀",
                            "hashtags": ["#Innovation", "#ProductLaunch"]
                        }
                    ]
                },
                "metadata": {
                    "generator": "fallback",
                    "product_name": product_name
                }
            }
        
        elif "ad" in content_type.lower():
            return {
                "content": {
                    "ads": [
                        {
                            "headline": f"Discover {product_name}",
                            "description": f"The solution you've been looking for.",
                            "call_to_action": "Learn More"
                        }
                    ]
                },
                "metadata": {
                    "generator": "fallback",
                    "product_name": product_name
                }
            }
        
        else:
            return {
                "content": {
                    "title": f"{content_type.title()} for {product_name}",
                    "body": f"Generated {content_type} content for {product_name}.",
                    "metadata": {"fallback": True}
                },
                "metadata": {
                    "generator": "fallback",
                    "content_type": content_type
                }
            }
    
    def _get_generator_name(self, content_type: str) -> str:
        """Get the name of the generator used"""
        if hasattr(self, '_factory') and self._factory:
            return "ContentGeneratorFactory"
        elif content_type.lower() in self._generators:
            return f"{content_type}Generator"
        else:
            return "FallbackGenerator"
    
    async def _create_workflow_record(
        self,
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        content_types: List[str],
        preferences: Dict[str, Any]
    ) -> UUID:
        """Create workflow tracking record in new table - skip if table doesn't exist"""
        workflow_id = uuid4()

        try:
            query = text("""
                INSERT INTO content_generation_workflows
                (id, campaign_id, user_id, company_id, workflow_type, content_types,
                 generation_preferences, workflow_status, items_requested)
                VALUES (:id, :campaign_id, :user_id, :company_id, :workflow_type,
                        :content_types, :preferences, 'processing', :items_requested)
            """)

            await self.db.execute(query, {
                "id": workflow_id,
                "campaign_id": UUID(str(campaign_id)),
                "user_id": UUID(str(user_id)),
                "company_id": UUID(str(company_id)),
                "workflow_type": "integrated_generation",
                "content_types": json.dumps(content_types),
                "preferences": json.dumps(preferences),
                "items_requested": len(content_types)
            })

            await self.db.commit()
        except Exception as e:
            logger.warning(f"Could not create workflow record, table might not exist: {e}")
            # Continue without workflow tracking if table doesn't exist

        return workflow_id
    
    async def _update_workflow_status(
        self,
        workflow_id: UUID,
        status: str,
        items_completed: int = 0,
        error_details: Optional[str] = None
    ):
        """Update workflow status - skip if table doesn't exist"""
        try:
            query = text("""
                UPDATE content_generation_workflows
                SET workflow_status = CAST(:status AS VARCHAR),
                    items_completed = :items_completed,
                    error_details = :error_details,
                    completed_at = CASE WHEN CAST(:status AS VARCHAR) IN ('completed', 'failed') THEN NOW() ELSE completed_at END,
                    updated_at = NOW()
                WHERE id = :workflow_id
            """)

            await self.db.execute(query, {
                "workflow_id": workflow_id,
                "status": status,
                "items_completed": items_completed,
                "error_details": error_details
            })
            await self.db.commit()
        except Exception as e:
            logger.warning(f"Could not update workflow status, table might not exist: {e}")
            # Continue without workflow tracking if table doesn't exist
    
    async def _store_content_in_existing_table(
        self,
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        content_type: str,
        content_data: Dict[str, Any],
        generation_settings: Dict[str, Any],
        intelligence_data: Optional[List[Dict]] = None
    ) -> UUID:
        """Store content in existing generated_content table with intelligence tracking"""

        content_id = uuid4()

        # Extract intelligence_id from the primary intelligence record (highest confidence)
        intelligence_id = None
        intelligence_used_count = 0

        if intelligence_data and len(intelligence_data) > 0:
            # Get the highest confidence intelligence record
            primary_intel = intelligence_data[0]
            intelligence_used_count = len(intelligence_data)

            # Try to get intelligence_id from the database
            try:
                query = text("""
                    SELECT ic.id
                    FROM intelligence_core ic
                    WHERE ic.product_name = :product_name
                      AND ic.user_id = :user_id
                    ORDER BY ic.confidence_score DESC
                    LIMIT 1
                """)
                result = await self.db.execute(query, {
                    "product_name": primary_intel.get("product_name"),
                    "user_id": UUID(str(user_id))
                })
                row = result.fetchone()
                if row:
                    intelligence_id = row.id
                    logger.info(f"📊 Linking content to intelligence_id: {intelligence_id}")
            except Exception as e:
                logger.warning(f"⚠️ Could not fetch intelligence_id: {e}")

        # Normalize content_type to match database check constraint
        normalized_content_type = content_type
        if content_type.lower() in ['email', 'email_sequence']:
            normalized_content_type = 'email_sequence'
        elif content_type.lower() in ['social', 'social_post', 'social_media']:
            normalized_content_type = 'social_media'
        elif content_type.lower() in ['ad', 'ad_copy', 'advertisement']:
            normalized_content_type = 'advertisement'
        elif content_type.lower() in ['blog', 'blog_post', 'blog_article']:
            normalized_content_type = 'blog_post'

        # Extract title and body from generated content
        content_title = f"{normalized_content_type.replace('_', ' ').title()}"
        content_body = ""

        # Handle different generator response structures
        # New AI generators return: {emails: [], ads: [], posts: [], article: {}}
        # Legacy generators return: {content: {emails: [], ...}}

        if content_data.get("emails"):
            # Email generator format
            content_title = f"Email Sequence ({len(content_data['emails'])} emails)"
            content_body = json.dumps(content_data["emails"])
        elif content_data.get("ads"):
            # Ad copy generator format
            content_title = f"Ad Copy ({len(content_data['ads'])} ads)"
            content_body = json.dumps(content_data["ads"])
        elif content_data.get("posts"):
            # Social media generator format
            content_title = f"Social Media Posts ({len(content_data['posts'])} posts)"
            content_body = json.dumps(content_data["posts"])
        elif content_data.get("article"):
            # Blog generator format
            article = content_data["article"]
            content_title = article.get("title", "Blog Article")
            content_body = article.get("content", "")
        elif content_data.get("content"):
            # Legacy format with nested content
            if isinstance(content_data["content"], dict):
                if "emails" in content_data["content"]:
                    content_title = f"Email Sequence ({len(content_data['content']['emails'])} emails)"
                    content_body = json.dumps(content_data["content"]["emails"])
                elif "posts" in content_data["content"]:
                    content_title = f"Social Media Posts ({len(content_data['content']['posts'])} posts)"
                    content_body = json.dumps(content_data["content"]["posts"])
                elif "ads" in content_data["content"]:
                    content_title = f"Ad Copy ({len(content_data['content']['ads'])} ads)"
                    content_body = json.dumps(content_data["content"]["ads"])
                else:
                    content_body = json.dumps(content_data["content"])
            else:
                content_body = str(content_data["content"])
        
        query = text("""
            INSERT INTO generated_content
            (id, user_id, campaign_id, company_id, content_type, content_title, content_body,
             content_metadata, generation_settings, generation_method, content_status,
             intelligence_id, intelligence_used)
            VALUES (:id, :user_id, :campaign_id, :company_id, :content_type, :content_title,
                    :content_body, :content_metadata, :generation_settings, 'existing_ai_system', 'generated',
                    :intelligence_id, :intelligence_used)
        """)
        
        # Extract metadata from different response structures
        metadata = content_data.get("generation_metadata", content_data.get("metadata", {}))
        sequence_info = content_data.get("sequence_info", content_data.get("content_info", {}))

        content_metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_used": self._get_generator_name(content_type),
            "generation_metadata": metadata,
            "content_info": sequence_info,
            "intelligence_enhanced": bool(metadata.get("intelligence_sources", 0) or content_data.get("intelligence_sources_used", 0)),
            "ai_provider": metadata.get("ai_provider", "unknown"),
            "prompt_quality_score": metadata.get("prompt_quality_score", 0)
        }
        
        await self.db.execute(query, {
            "id": content_id,
            "user_id": UUID(str(user_id)),
            "campaign_id": UUID(str(campaign_id)),
            "company_id": UUID(str(company_id)),
            "content_type": normalized_content_type,
            "content_title": content_title,
            "content_body": content_body,
            "content_metadata": json.dumps(content_metadata),
            "generation_settings": json.dumps(generation_settings),
            "intelligence_id": UUID(str(intelligence_id)) if intelligence_id else None,
            "intelligence_used": intelligence_used_count
        })
        
        await self.db.commit()
        return content_id
    
    async def get_campaign_content(
        self,
        campaign_id: Union[str, UUID],
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get content from existing generated_content table"""
        
        query_conditions = "WHERE campaign_id = :campaign_id"
        params = {"campaign_id": UUID(str(campaign_id)), "limit": limit, "offset": offset}
        
        if content_type:
            query_conditions += " AND content_type = :content_type"
            params["content_type"] = content_type
        
        query = text(f"""
            SELECT id, content_type, content_title, content_body, content_metadata,
                   generation_settings, user_rating, is_published, created_at, updated_at,
                   generation_method, content_status
            FROM generated_content 
            {query_conditions}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
        """)
        
        result = await self.db.execute(query, params)
        rows = result.fetchall()
        
        result_list = []
        for row in rows:
            try:
                result_list.append({
                    "id": str(row.id),
                    "content_type": row.content_type,
                    "content_title": row.content_title,
                    "content_body": row.content_body,
                    "content_metadata": self._safe_get_metadata_as_dict(row.content_metadata),
                    "generation_settings": self._safe_get_metadata_as_dict(row.generation_settings),
                    "user_rating": row.user_rating,
                    "is_published": row.is_published,
                    "created_at": row.created_at.isoformat() if row.created_at else None,
                    "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                    "generation_method": row.generation_method,
                    "content_status": row.content_status,
                    "generator_used": self._safe_get_generator_used(row.content_metadata)
                })
            except Exception as e:
                logger.error(f"Error processing content row {getattr(row, 'id', 'unknown')}: {e}")
                # Skip problematic rows but continue processing
                continue

        return result_list
    
    def _safe_get_metadata_as_dict(self, content_metadata) -> Dict[str, Any]:
        """Safely convert content_metadata to dictionary format"""
        try:
            if content_metadata is None:
                return {}

            # If it's already a dictionary, return it
            if isinstance(content_metadata, dict):
                return content_metadata

            # If it's a list, try to merge items into a single dict
            if isinstance(content_metadata, list):
                result = {}
                for item in content_metadata:
                    if isinstance(item, dict):
                        result.update(item)
                return result

            # If it's some other type, return empty dict
            return {}

        except Exception as e:
            logger.warning(f"Error converting metadata to dict: {e}")
            return {}

    def _safe_get_generator_used(self, content_metadata) -> str:
        """Safely extract generator_used from content_metadata that might be list or dict"""
        try:
            if content_metadata is None:
                return "unknown"

            # If it's a dictionary, use .get() method
            if isinstance(content_metadata, dict):
                return content_metadata.get("generator_used", "unknown")

            # If it's a list, try to find generator_used in list items
            if isinstance(content_metadata, list):
                for item in content_metadata:
                    if isinstance(item, dict) and "generator_used" in item:
                        return item["generator_used"]
                return "unknown"

            # If it's some other type, return unknown
            return "unknown"

        except Exception as e:
            logger.warning(f"Error extracting generator_used from metadata: {e}")
            return "unknown"

    def get_generator_status(self) -> Dict[str, Any]:
        """Get status of available generators"""
        try:
            from src.intelligence.generators import get_available_generators, get_generator_status

            existing_status = get_generator_status()

            return {
                "integrated_service": True,
                "existing_generators": existing_status,
                "loaded_generators": list(self._generators.keys()),
                "factory_available": hasattr(self, '_factory') and self._factory is not None,
                "total_available": len(self._generators),
                "railway_compatible": existing_status.get("railway_compatible", False),
                "ultra_cheap_ai_enabled": existing_status.get("ultra_cheap_ai_enabled", False)
            }

        except ImportError:
            return {
                "integrated_service": True,
                "existing_generators": {},
                "loaded_generators": list(self._generators.keys()),
                "factory_available": False,
                "total_available": len(self._generators),
                "error": "Could not import existing generator status"
            }

    async def get_campaign_content(
        self,
        campaign_id: str,
        content_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieve generated content for a campaign"""
        try:
            # Build dynamic query with optional content_type filter
            base_query = """
                SELECT id, content_type, content_title, content_body, content_metadata,
                       created_at, updated_at, is_published, user_rating, generation_method, content_status
                FROM generated_content
                WHERE campaign_id::text = :campaign_id
            """

            params = {"campaign_id": str(campaign_id)}  # Ensure string conversion
            print(f"DEBUG: get_campaign_content called with campaign_id={campaign_id}, content_type={content_type}")

            # Add content_type filter if specified
            if content_type:
                base_query += " AND content_type = :content_type"
                params["content_type"] = content_type

            # Add ordering and pagination
            base_query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
            params["limit"] = limit
            params["offset"] = offset

            query = text(base_query)
            print(f"DEBUG: Executing query: {base_query}")
            print(f"DEBUG: With params: {params}")
            result = await self.db.execute(query, params)
            rows = result.fetchall()
            print(f"DEBUG: Query returned {len(rows)} rows")

            content_list = []
            for row in rows:
                try:
                    # Parse metadata safely
                    metadata = {}
                    if row.content_metadata:
                        if isinstance(row.content_metadata, str):
                            metadata = json.loads(row.content_metadata)
                        else:
                            metadata = row.content_metadata

                    content_item = {
                        "id": str(row.id),  # Add both for compatibility
                        "content_id": str(row.id),
                        "content_type": row.content_type,
                        "title": row.content_title,
                        "content_title": row.content_title,  # Add both for compatibility
                        "body": row.content_body,
                        "content": row.content_body,  # Add both for compatibility
                        "metadata": metadata,
                        "content_metadata": metadata,  # Add both for compatibility
                        "created_at": row.created_at.isoformat() if row.created_at else None,
                        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
                        "is_published": row.is_published,
                        "user_rating": row.user_rating,
                        "generation_method": row.generation_method,
                        "content_status": row.content_status,
                        "generated_content": metadata.get("generated_content", {}),
                        "source": "integrated_content_service"
                    }
                    content_list.append(content_item)
                    print(f"DEBUG: Added content item with id={content_item['content_id']}, type={content_item['content_type']}")
                except Exception as parse_error:
                    logger.warning(f"Error parsing content row: {parse_error}")
                    continue

            logger.info(f"Retrieved {len(content_list)} content items for campaign {campaign_id}")
            return content_list

        except Exception as e:
            logger.error(f"Error retrieving content for campaign {campaign_id}: {e}")
            return []