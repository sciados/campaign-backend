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
        """Initialize existing generators from intelligence module"""
        try:
            # Import your existing generators
            from src.content.generators import (
                EmailGenerator,
                AdCopyGenerator,
                SocialMediaGenerator,
                get_available_generators,
                BlogContentGenerator
            )
            
            # Initialize available generators
            available = get_available_generators()
            
            if available.get("email_sequence", False):
                self._generators["email"] = EmailGenerator()
                self._generators["email_sequence"] = EmailGenerator()
                logger.info("Email sequence generator loaded")
            
            if available.get("ad_copy", False):
                self._generators["ad_copy"] = AdCopyGenerator()
                self._generators["advertisement"] = AdCopyGenerator()
                logger.info("Ad copy generator loaded")

            if available.get("blog_post", False):
                self._generators["blog_post"] = BlogContentGenerator()
                self._generators["blogposts"] = BlogContentGenerator()
                logger.info("Blog Post generator loaded")
            
            if available.get("social_media", False):
                self._generators["social_post"] = SocialMediaGenerator()
                self._generators["social_media"] = SocialMediaGenerator()
                logger.info("Social media generator loaded")
            
            # Try to use factory if available
            # if available.get("factory", False):
            #    self._factory = ContentGeneratorFactory()
            #    logger.info("Content generator factory loaded")
            # else:
            #    self._factory = None
            
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
            result = await self._generate_with_existing_system(
                content_type=content_type,
                intelligence_data=intelligence_data,
                preferences=preferences or {},
                campaign_id=campaign_id
            )
            
            # Store in existing generated_content table
            content_id = await self._store_content_in_existing_table(
                campaign_id=campaign_id,
                user_id=user_id,
                company_id=company_id,
                content_type=content_type,
                content_data=result,
                generation_settings=preferences or {}
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
            if 'workflow_id' in locals():
                await self._update_workflow_status(workflow_id, "failed", error_details=str(e))
            
            return {
                "success": False,
                "error": str(e),
                "content_type": content_type,
                "campaign_id": str(campaign_id),
                "fallback_used": True
            }
    
    async def _get_campaign_intelligence(self, campaign_id: Union[str, UUID]) -> Optional[List[Dict]]:
        """Get campaign intelligence data from existing intelligence_core table"""
        try:
            query = text("""
                SELECT ic.product_name, ic.source_url, ic.confidence_score,
                       pd.features, pd.benefits, pd.ingredients, pd.conditions,
                       md.category, md.positioning, md.competitive_advantages, md.target_audience
                FROM intelligence_core ic
                LEFT JOIN product_data pd ON ic.id = pd.intelligence_id
                LEFT JOIN market_data md ON ic.id = md.intelligence_id
                WHERE ic.user_id IN (
                    SELECT user_id FROM campaigns WHERE id = :campaign_id
                ) OR ic.id IN (
                    SELECT intelligence_id FROM campaign_intelligence 
                    WHERE campaign_id = :campaign_id
                )
                ORDER BY ic.confidence_score DESC
                LIMIT 10
            """)
            
            result = await self.db.execute(query, {"campaign_id": UUID(str(campaign_id))})
            rows = result.fetchall()
            
            intelligence_data = []
            for row in rows:
                data = {
                    "product_name": row.product_name,
                    "source_url": row.source_url,
                    "confidence_score": float(row.confidence_score) if row.confidence_score else 0.0,
                    "features": row.features if row.features else [],
                    "benefits": row.benefits if row.benefits else [],
                    "ingredients": row.ingredients if row.ingredients else [],
                    "conditions": row.conditions if row.conditions else [],
                    "category": row.category,
                    "positioning": row.positioning,
                    "competitive_advantages": row.competitive_advantages if row.competitive_advantages else [],
                    "target_audience": row.target_audience
                }
                intelligence_data.append(data)
            
            logger.info(f"Retrieved {len(intelligence_data)} intelligence records for campaign")
            return intelligence_data
            
        except Exception as e:
            logger.error(f"Failed to get campaign intelligence: {e}")
            return []
    
    async def _generate_with_existing_system(
        self,
        content_type: str,
        intelligence_data: List[Dict],
        preferences: Dict[str, Any],
        campaign_id: Union[str, UUID]
    ) -> Dict[str, Any]:
        """Generate content using existing generator system"""
        
        # Normalize content type
        content_type_normalized = content_type.lower()
        
        # Try factory first if available
        if self._factory:
            try:
                result = await self._factory.generate_content(
                    content_type=content_type_normalized,
                    intelligence_data=intelligence_data,
                    preferences=preferences
                )
                
                if not result.get("error") and not result.get("fallback"):
                    logger.info(f"Content generated using factory for {content_type}")
                    return result
                    
            except Exception as e:
                logger.warning(f"Factory generation failed: {e}")
        
        # Fallback to direct generator access
        if content_type_normalized in self._generators:
            generator = self._generators[content_type_normalized]
            
            try:
                if hasattr(generator, 'generate_content'):
                    result = await generator.generate_content(intelligence_data, preferences)
                elif hasattr(generator, 'generate_email_sequence') and 'email' in content_type_normalized:
                    result = await generator.generate_email_sequence(intelligence_data, preferences)
                elif hasattr(generator, 'generate_ad_copy') and 'ad' in content_type_normalized:
                    result = await generator.generate_ad_copy(intelligence_data, preferences)
                elif hasattr(generator, 'generate_social_posts') and 'social' in content_type_normalized:
                    result = await generator.generate_social_posts(intelligence_data, preferences)
                else:
                    # Try generic generate method
                    result = await generator.generate_content(intelligence_data, preferences)
                
                logger.info(f"Content generated using {content_type} generator")
                return result
                
            except Exception as e:
                logger.error(f"Generator {content_type} failed: {e}")
        
        # Ultimate fallback - create basic content
        return await self._create_fallback_content(content_type, intelligence_data, preferences)
    
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
        if self._factory:
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
        """Create workflow tracking record in new table"""
        workflow_id = uuid4()
        
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
        return workflow_id
    
    async def _update_workflow_status(
        self,
        workflow_id: UUID,
        status: str,
        items_completed: int = 0,
        error_details: Optional[str] = None
    ):
        """Update workflow status"""
        query = text("""
            UPDATE content_generation_workflows 
            SET workflow_status = :status, 
                items_completed = :items_completed,
                error_details = :error_details,
                completed_at = CASE WHEN :status IN ('completed', 'failed') THEN NOW() ELSE completed_at END,
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
    
    async def _store_content_in_existing_table(
        self,
        campaign_id: Union[str, UUID],
        user_id: Union[str, UUID],
        company_id: Union[str, UUID],
        content_type: str,
        content_data: Dict[str, Any],
        generation_settings: Dict[str, Any]
    ) -> UUID:
        """Store content in existing generated_content table"""
        
        content_id = uuid4()
        
        # Extract title and body from generated content
        content_title = f"{content_type.title()} Content"
        content_body = ""
        
        if content_data.get("content"):
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
             content_metadata, generation_settings, generation_method, content_status)
            VALUES (:id, :user_id, :campaign_id, :company_id, :content_type, :content_title, 
                    :content_body, :content_metadata, :generation_settings, 'existing_ai_system', 'generated')
        """)
        
        content_metadata = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_used": self._get_generator_name(content_type),
            "original_response": content_data.get("metadata", {}),
            "intelligence_enhanced": bool(content_data.get("intelligence_sources_used", 0))
        }
        
        await self.db.execute(query, {
            "id": content_id,
            "user_id": UUID(str(user_id)),
            "campaign_id": UUID(str(campaign_id)),
            "company_id": UUID(str(company_id)),
            "content_type": content_type,
            "content_title": content_title,
            "content_body": content_body,
            "content_metadata": json.dumps(content_metadata),
            "generation_settings": json.dumps(generation_settings)
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
        
        return [
            {
                "id": str(row.id),
                "content_type": row.content_type,
                "content_title": row.content_title,
                "content_body": row.content_body,
                "content_metadata": row.content_metadata if row.content_metadata else {},
                "generation_settings": row.generation_settings if row.generation_settings else {},
                "user_rating": row.user_rating,
                "is_published": row.is_published,
                "created_at": row.created_at.isoformat(),
                "updated_at": row.updated_at.isoformat(),
                "generation_method": row.generation_method,
                "content_status": row.content_status,
                "generator_used": (row.content_metadata or {}).get("generator_used", "unknown")
            }
            for row in rows
        ]
    
    def get_generator_status(self) -> Dict[str, Any]:
        """Get status of available generators"""
        try:
            from src.intelligence.generators import get_available_generators, get_generator_status
            
            existing_status = get_generator_status()
            
            return {
                "integrated_service": True,
                "existing_generators": existing_status,
                "loaded_generators": list(self._generators.keys()),
                "factory_available": self._factory is not None,
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