# =====================================
# File: src/intelligence/services/enhancement_service.py
# =====================================

"""
Enhancement service for intelligence data improvement and augmentation.

Provides AI-powered enhancement of intelligence data including
content improvement, fact checking, and data enrichment.
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.shared.decorators import log_execution_time
from ..models.intelligence_models import AnalysisResult, ProductInfo, MarketInfo
from ..providers.ai_provider_router import AIProviderRouter, RequestComplexity

logger = logging.getLogger(__name__)


class EnhancementService:
    """Service for enhancing and augmenting intelligence data."""
    
    def __init__(self):
        self.ai_router = AIProviderRouter()
    
    @log_execution_time()
    async def enhance_analysis_result(
        self,
        analysis_result: AnalysisResult,
        enhancement_type: str = "comprehensive"
    ) -> AnalysisResult:
        """
        Enhance an existing analysis result with additional AI processing.
        
        Args:
            analysis_result: Original analysis result
            enhancement_type: Type of enhancement (basic, comprehensive, premium)
            
        Returns:
            AnalysisResult: Enhanced analysis result
        """
        try:
            logger.info(f"Enhancing analysis {analysis_result.intelligence_id} with {enhancement_type} enhancement")
            
            # Enhance product information
            enhanced_product_info = await self._enhance_product_info(
                analysis_result.product_info,
                enhancement_type
            )
            
            # Enhance market information
            enhanced_market_info = await self._enhance_market_info(
                analysis_result.market_info,
                enhancement_type
            )
            
            # Create enhanced result
            enhanced_result = AnalysisResult(
                intelligence_id=analysis_result.intelligence_id,
                product_name=analysis_result.product_name,
                confidence_score=min(1.0, analysis_result.confidence_score + 0.1),  # Slight confidence boost
                product_info=enhanced_product_info,
                market_info=enhanced_market_info,
                research=analysis_result.research,  # Keep existing research
                created_at=analysis_result.created_at
            )
            
            logger.info(f"Enhancement completed for {analysis_result.intelligence_id}")
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Enhancement failed for {analysis_result.intelligence_id}: {e}")
            # Return original result if enhancement fails
            return analysis_result
    
    async def _enhance_product_info(self, product_info: ProductInfo, enhancement_type: str) -> ProductInfo:
        """Enhance product information using AI."""
        
        complexity = RequestComplexity.MODERATE if enhancement_type == "basic" else RequestComplexity.COMPLEX
        
        # Enhance features
        enhanced_features = await self._enhance_text_list(
            product_info.features,
            "product features",
            complexity
        )
        
        # Enhance benefits
        enhanced_benefits = await self._enhance_text_list(
            product_info.benefits,
            "product benefits",
            complexity
        )
        
        return ProductInfo(
            features=enhanced_features,
            benefits=enhanced_benefits,
            ingredients=product_info.ingredients,  # Keep original
            conditions=product_info.conditions,    # Keep original
            usage_instructions=product_info.usage_instructions  # Keep original
        )
    
    async def _enhance_market_info(self, market_info: MarketInfo, enhancement_type: str) -> MarketInfo:
        """Enhance market information using AI."""
        
        complexity = RequestComplexity.MODERATE if enhancement_type == "basic" else RequestComplexity.COMPLEX
        
        # Enhance competitive advantages
        enhanced_advantages = await self._enhance_text_list(
            market_info.competitive_advantages,
            "competitive advantages",
            complexity
        )
        
        # Enhance positioning if available
        enhanced_positioning = market_info.positioning
        if market_info.positioning and enhancement_type in ["comprehensive", "premium"]:
            try:
                response = await self.ai_router.route_request(
                    request_type="enhance_positioning",
                    content=market_info.positioning,
                    complexity=complexity
                )
                enhanced_positioning = response.get("response", market_info.positioning)
            except Exception as e:
                logger.warning(f"Failed to enhance positioning: {e}")
        
        return MarketInfo(
            category=market_info.category,  # Keep original
            positioning=enhanced_positioning,
            competitive_advantages=enhanced_advantages,
            target_audience=market_info.target_audience  # Keep original
        )
    
    async def _enhance_text_list(
        self, 
        text_list: List[str], 
        content_type: str, 
        complexity: RequestComplexity
    ) -> List[str]:
        """Enhance a list of text items using AI."""
        
        if not text_list:
            return text_list
        
        try:
            content = f"Enhance and improve these {content_type}: {', '.join(text_list)}"
            
            response = await self.ai_router.route_request(
                request_type=f"enhance_{content_type}",
                content=content,
                complexity=complexity
            )
            
            # Parse enhanced response
            enhanced_text = response.get("response", "")
            
            # Simple parsing - in practice you'd use more sophisticated parsing
            if enhanced_text:
                # Split by common delimiters and clean up
                enhanced_items = [
                    item.strip().strip("-•").strip() 
                    for item in enhanced_text.replace("\n", ",").split(",")
                    if item.strip()
                ]
                
                if enhanced_items and len(enhanced_items) >= len(text_list):
                    return enhanced_items[:len(text_list) * 2]  # Allow up to double
            
        except Exception as e:
            logger.warning(f"Failed to enhance {content_type}: {e}")
        
        # Return original if enhancement fails
        return text_list