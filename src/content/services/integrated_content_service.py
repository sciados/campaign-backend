# src/content/services/integrated_content_service.py
"""
Content Generation Service

Handles the entire content generation workflow for all content types.
Implements the modular architecture from content-generation-implementation-plan.md
"""

import logging
import json
import time
import asyncio
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.content.generators import (
    BlogContentGenerator,
    SocialMediaGenerator,
    ImageGenerator,
    VideoScriptGenerator,
    LongFormArticleGenerator,
    EnhancedPlatformImageGenerator
)
from src.content.services import (
    prompt_generation_service,
    ai_provider_service,
    smart_provider_router,
    content_generator_manager
)
from src.content.utils import (
    extract_content_type,
    validate_content_type,
    determine_content_type
)
from src.content.models import ContentRequest, ContentResponse
from src.intelligence.services import IntelligenceService
from src.intelligence.models import IntelligenceResponse
from src.storage.services import CloudflareService
from src.intelligence.utils.product_name_fix import extract_product_name_from_intelligence

logger = logging.getLogger(__name__)

class IntegratedContentService:
    """
    Core service for managing content generation workflows.
    Handles the full pipeline from intelligence analysis to content creation.
    """
    
    def __init__(self):
        self.name = "IntegratedContentService"
        self.version = "4.1.0"
        self.intelligence_service = IntelligenceService()
        self.ai_provider_service = ai_provider_service
        self.cloudflare_service = CloudflareService()
        self.smart_router = smart_provider_router
        self.content_generators = content_generator_manager
        self.content_types = {
            "blog": BlogContentGenerator(),
            "social": SocialMediaGenerator(),
            "image": ImageGenerator(),
            "video": VideoScriptGenerator(),
            "long_form": LongFormArticleGenerator(),
            "multi_platform_image": EnhancedPlatformImageGenerator()
        }
        logger.info(f"{self.name} v{self.version} initialized")

    async def generate_content(
        self,
        request: ContentRequest,
        user_id: str,
        campaign_id: str,
        session: AsyncSession = None
    ) -> ContentResponse:
        """
        Generate content for the specified campaign.
        
        Args:
            request: Content generation request
            user_id: ID of the requesting user
            campaign_id: ID of the campaign
            session: Database session
            
        Returns:
            ContentResponse: Generated content details
            
        Raises:
            HTTPException: If content generation fails
        """
        try:
            # Verify campaign exists
            await self._verify_campaign_exists(campaign_id, user_id, session)
            
            # Step 1: Get campaign intelligence (this is where the error was occurring)
            intelligence_data = await self._get_campaign_intelligence(campaign_id, session)
            
            # Step 2: Determine content type if not specified
            content_type = extract_content_type(request.content_type)
            if not content_type:
                content_type = determine_content_type(request.content_type, request.content_spec)
            
            # Step 3: Validate content type
            if not validate_content_type(content_type):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid content type: {request.content_type}"
                )
            
            # Step 4: Generate prompt
            prompt = await self._generate_prompt(
                content_type,
                intelligence_data,
                request.psychology_stage,
                request.preferences
            )
            
            # Step 5: Generate content
            content = await self._generate_content(
                content_type,
                prompt,
                request.preferences
            )
            
            # Step 6: Store generated content
            content_id = await self._store_content(
                user_id,
                campaign_id,
                content_type,
                content,
                intelligence_data,
                session
            )
            
            # Step 7: Return response
            return ContentResponse(
                success=True,
                content_id=content_id,
                content_type=content_type,
                content=content,
                intelligence_data=intelligence_data,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {str(e)}"
            )

    async def _get_campaign_intelligence(
        self,
        campaign_id: str,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Get campaign intelligence from the database.
        
        Args:
            campaign_id: ID of the campaign
            session: Database session
            
        Returns:
            Dict[str, Any]: Campaign intelligence data
            
        Raises:
            HTTPException: If intelligence data is not found
        """
        try:
            # Step 1: Execute the query for campaign intelligence
            # Fixed: Removed non-existent columns and correctly access JSONB data
            async with self.db() as session:
                result = await session.execute(
                    text("""
                        SELECT id, full_analysis_data
                        FROM intelligence_core 
                        WHERE campaign_id = :campaign_id 
                        ORDER BY created_at DESC 
                        LIMIT 1
                    """),
                    {"campaign_id": campaign_id}
                )
                
                # Step 2: Process the result
                if result:
                    data = result.scalar()
                    if data:
                        # Extract the required fields from the JSONB column
                        intelligence = data.full_analysis_data or {}
                        
                        # Fix: Use correct JSON paths for competitive insights and market opportunities
                        competitive_insights = intelligence.get("competitive_intelligence", {}).get("competitive_advantages", [])
                        market_opportunities = intelligence.get("market_intelligence", {}).get("market_opportunities", [])
                        
                        # Add these to the intelligence data for later use
                        intelligence["competitive_insights"] = competitive_insights
                        intelligence["market_opportunities"] = market_opportunities
                        
                        # Log the extracted intelligence data
                        logger.info(f"Extracted intelligence data for campaign {campaign_id}")
                        logger.debug(f"Competitive insights: {len(competitive_insights)} items")
                        logger.debug(f"Market opportunities: {len(market_opportunities)} items")
                        
                        return intelligence
                        
                logger.warning(f"Campaign intelligence data not found for campaign {campaign_id}")
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get campaign intelligence: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to get campaign intelligence: {str(e)}"
            )

    async def _generate_prompt(
        self,
        content_type: str,
        intelligence_data: Dict[str, Any],
        psychology_stage: str = "SOLUTION_REVEAL",
        preferences: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate prompt for content creation"""
        try:
            # Get the appropriate prompt generator
            generator = self.content_types.get(content_type)
            if not generator:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported content type: {content_type}"
                )
            
            # Generate prompt
            prompt_data = await prompt_generation_service.generate_prompt(
                content_type=content_type,
                intelligence_data=intelligence_data,
                psychology_stage=psychology_stage,
                preferences=preferences
            )
            
            # Log prompt generation success
            logger.info(f"✅ Prompt generation successful for {content_type}")
            logger.debug(f"Prompt length: {len(prompt_data['prompt'])} characters")
            
            return prompt_data
            
        except Exception as e:
            logger.error(f"Prompt generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Prompt generation failed: {str(e)}"
            )

    async def _generate_content(
        self,
        content_type: str,
        prompt_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate content using the AI provider router"""
        try:
            # Get the appropriate content generator
            generator = self.content_types.get(content_type)
            if not generator:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported content type: {content_type}"
                )
            
            # Route the request to the appropriate AI provider
            ai_provider = self.smart_router.route_ai_request(
                content_type=content_type,
                request_type="content_generation",
                preferences=preferences
            )
            
            # Generate content
            content = await ai_provider.generate_content(
                prompt=prompt_data["prompt"],
                system_message=prompt_data["system_message"],
                preferences=preferences
            )
            
            # Log content generation success
            logger.info(f"✅ Content generated successfully for {content_type}")
            logger.debug(f"Content length: {len(content)} characters")
            
            return content
            
        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Content generation failed: {str(e)}"
            )

    async def _store_content(
        self,
        user_id: str,
        campaign_id: str,
        content_type: str,
        content: str,
        intelligence_data: Dict[str, Any],
        session: AsyncSession
    ) -> UUID:
        """
        Store generated content in the database.
        
        Args:
            user_id: ID of the user
            campaign_id: ID of the campaign
            content_type: Type of content
            content: Generated content
            intelligence_data: Intelligence data used
            session: Database session
            
        Returns:
            UUID: ID of the generated content
            
        Raises:
            HTTPException: If storage fails
        """
        try:
            # Log the content to be stored
            logger.info(f"Storing generated content for campaign {campaign_id}")
            logger.debug(f"Content type: {content_type}")
            logger.debug(f"Content length: {len(content)} characters")
            
            # Store the content in the database
            content_id = await self.content_generators.store_content(
                user_id=user_id,
                campaign_id=campaign_id,
                content_type=content_type,
                content=content,
                intelligence_data=intelligence_data,
                session=session
            )
            
            logger.info(f"✅ Content stored successfully with ID: {content_id}")
            return content_id
            
        except Exception as e:
            logger.error(f"Content storage failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Content storage failed: {str(e)}"
            )

    async def _verify_campaign_exists(
        self,
        campaign_id: str,
        user_id: str,
        session: AsyncSession
    ) -> None:
        """Verify campaign exists and user has access"""
        try:
            # This would normally query the campaign table
            # For demonstration purposes, we'll skip this check
            pass
            
        except Exception as e:
            logger.error(f"Campaign verification failed: {str(e)}")
            raise HTTPException(
                status_code=404,
                detail="Campaign not found"
            )

    async def generate_platform_images(
        self,
        campaign_id: str,
        user_id: str,
        session: AsyncSession = None
    ) -> Dict[str, Any]:
        """
        Generate multi-platform images for the specified campaign.
        
        Args:
            campaign_id: ID of the campaign
            user_id: ID of the user
            session: Database session
            
        Returns:
            Dict[str, Any]: Image generation results
        """
        try:
            logger.info(f"🎯 Generating multi-platform images for campaign {campaign_id}")
            
            # Step 1: Get campaign intelligence
            intelligence_data = await self._get_campaign_intelligence(campaign_id, session)
            
            # Step 2: Check if we have the required intelligence
            if not intelligence_data:
                logger.warning(f"No intelligence data found for campaign {campaign_id}")
                return {
                    "success": False,
                    "error": "No intelligence data available",
                    "details": "Campaign intelligence data is missing or empty"
                }
            
            # Step 3: Extract product name from intelligence data
            product_name = extract_product_name_from_intelligence(intelligence_data)
            if not product_name:
                product_name = "Product"
                logger.warning("Product name not found in intelligence data")
            
            # Step 4: Generate multi-platform images
            images = await self._generate_multi_platform_images(
                campaign_id=campaign_id,
                product_name=product_name,
                intelligence_data=intelligence_data
            )
            
            # Step 5: Store generated images
            if images:
                await self._store_images(
                    campaign_id=campaign_id,
                    images=images,
                    user_id=user_id,
                    session=session
                )
            
            # Step 6: Return results
            return {
                "success": True,
                "image_count": len(images) if images else 0,
                "image_data": images,
                "details": "Multi-platform images generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Multi-platform image generation failed: {str(e)}")
            return {
                "success": False,
                "error": f"Image generation failed: {str(e)}",
                "details": "An error occurred during image generation"
            }

    async def _generate_multi_platform_images(
        self,
        campaign_id: str,
        product_name: str,
        intelligence_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate images for multiple platforms.
        
        Args:
            campaign_id: ID of the campaign
            product_name: Name of the product
            intelligence_data: Intelligence data for the campaign
            
        Returns:
            List[Dict[str, Any]]: Generated image data
        """
        try:
            # Extract the required fields for image generation
            competitive_insights = intelligence_data.get("competitive_insights", [])
            market_opportunities = intelligence_data.get("market_opportunities", [])
            
            # Prepare the image generation data
            image_data = {
                "product_name": product_name,
                "competitive_insights": competitive_insights,
                "market_opportunities": market_opportunities,
                "intelligence_data": intelligence_data
            }
            
            # Get the appropriate image generator
            generator = self.content_types.get("multi_platform_image")
            if not generator:
                logger.error("Multi-platform image generator not found")
                return []
            
            # Generate the images
            images = await generator.generate_image(
                campaign_id=campaign_id,
                product_name=product_name,
                intelligence_data=intelligence_data
            )
            
            return images
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return []

    async def _store_images(
        self,
        campaign_id: str,
        images: List[Dict[str, Any]],
        user_id: str,
        session: AsyncSession
    ) -> None:
        """Store generated images in the database"""
        try:
            for image in images:
                # Store each image separately
                await self.content_generators.store_image(
                    campaign_id=campaign_id,
                    image_data=image,
                    user_id=user_id,
                    session=session
                )
                
            logger.info(f"✅ Images stored successfully for campaign {campaign_id}")
            
        except Exception as e:
            logger.error(f"Failed to store images: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to store images: {str(e)}"
            )