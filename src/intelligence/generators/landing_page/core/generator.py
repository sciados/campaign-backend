# src/intelligence/generators/landing_page/core/generator.py
"""
Main Enhanced Landing Page Generator class.
This is the primary interface for generating landing pages.
"""

import os
import logging
from typing import Dict, List, Any, Optional

from .config import PAGE_CONFIGS, COLOR_SCHEMES, DEFAULT_PREFERENCES, AI_PROVIDER_CONFIG
from .types import GenerationPreferences, GenerationResult, PageType, ColorScheme
from ..intelligence.extractor import IntelligenceExtractor
from ..intelligence.niche_detector import NicheDetector
from ..templates.manager import TemplateManager
from ..components.modular import ModularLandingPageBuilder
from ..variants.generator import VariantGenerator
from ..analytics.performance import PerformancePrediction
from ..utils.validation import validate_preferences, validate_intelligence_data

logger = logging.getLogger(__name__)

class EnhancedLandingPageGenerator:
    """
    Enhanced Landing Page Generator
    
    Main class that orchestrates the entire landing page generation process:
    1. Intelligence extraction and niche detection
    2. Template selection and customization
    3. Modular page construction
    4. A/B variant generation
    5. Performance prediction and optimization
    """
    
    def __init__(self):
        self.ai_providers = self._initialize_ai_providers()
        self.intelligence_extractor = IntelligenceExtractor()
        self.niche_detector = NicheDetector()
        self.template_manager = TemplateManager()
        self.page_builder = ModularLandingPageBuilder()
        self.variant_generator = VariantGenerator()
        self.performance_predictor = PerformancePrediction()
        
        logger.info("✅ Enhanced Landing Page Generator initialized")
    
    async def generate_landing_page(
        self,
        intelligence_data: Dict[str, Any],
        preferences: Optional[Dict[str, Any]] = None
    ) -> GenerationResult:
        """
        Generate enhanced landing page with intelligence integration
        
        Args:
            intelligence_data: Processed intelligence from competitor analysis
            preferences: User preferences for page generation
            
        Returns:
            GenerationResult with complete landing page and metadata
        """
        
        try:
            # Step 1: Validate and process inputs
            validated_preferences = validate_preferences(preferences or {})
            validated_intelligence = validate_intelligence_data(intelligence_data)
            
            # Step 2: Extract enhanced intelligence
            product_info = self.intelligence_extractor.extract_product_info(validated_intelligence)
            conversion_intelligence = self.intelligence_extractor.extract_conversion_intelligence(validated_intelligence)
            
            # Step 3: Detect niche and select template
            detected_niche = self.niche_detector.detect_niche(product_info, conversion_intelligence)
            template = self.template_manager.get_template(
                page_type=validated_preferences.page_type,
                niche=detected_niche
            )
            
            # Step 4: Build the landing page
            page_result = await self.page_builder.build_complete_landing_page(
                product_info=product_info,
                conversion_intelligence=conversion_intelligence,
                template=template,
                preferences=validated_preferences
            )
            
            # Step 5: Generate A/B test variants (if requested)
            variants = []
            if validated_preferences.generate_variants:
                variants = await self.variant_generator.generate_variants(
                    base_html=page_result["complete_html"],
                    product_info=product_info,
                    template=template
                )
            
            # Step 6: Generate performance predictions
            performance_predictions = self.performance_predictor.predict_performance(
                intelligence_data=validated_intelligence,
                page_config=template.config,
                conversion_intelligence=conversion_intelligence
            )
            
            # Step 7: Compile final result
            return GenerationResult(
                content_type="landing_page",
                title=f"{product_info.name} Landing Page - {validated_preferences.page_type.value.title()}",
                html_code=page_result["complete_html"],
                sections=page_result["sections"],
                conversion_elements=template.config.conversion_elements,
                metadata={
                    "generated_by": "enhanced_landing_page_ai",
                    "product_name": product_info.name,
                    "detected_niche": detected_niche.value,
                    "template_used": template.name,
                    "amplified_intelligence": conversion_intelligence.amplified_intelligence,
                    "performance_score": performance_predictions["optimization_score"]
                },
                variants=variants,
                performance_predictions=performance_predictions
            )
            
        except Exception as e:
            logger.error(f"Landing page generation failed: {str(e)}")
            return await self._generate_fallback_page(intelligence_data, preferences)
    
    def _initialize_ai_providers(self) -> List[Dict[str, Any]]:
        """Initialize AI providers for content generation"""
        providers = []
        
        # Initialize Anthropic
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                import anthropic
                providers.append({
                    "name": "anthropic",
                    "client": anthropic.AsyncAnthropic(api_key=api_key),
                    **AI_PROVIDER_CONFIG["anthropic"]
                })
                logger.info("✅ Anthropic provider initialized")
        except Exception as e:
            logger.warning(f"Anthropic not available: {str(e)}")
        
        # Initialize OpenAI
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                providers.append({
                    "name": "openai", 
                    "client": openai.AsyncOpenAI(api_key=api_key),
                    **AI_PROVIDER_CONFIG["openai"]
                })
                logger.info("✅ OpenAI provider initialized")
        except Exception as e:
            logger.warning(f"OpenAI not available: {str(e)}")
        
        return providers
    
    async def _generate_fallback_page(
        self, 
        intelligence_data: Dict[str, Any], 
        preferences: Optional[Dict[str, Any]]
    ) -> GenerationResult:
        """Generate a fallback page when main generation fails"""
        
        logger.warning("⚠️ Using fallback landing page generation")
        
        # Use basic template and simple content
        fallback_html = self.template_manager.get_fallback_template()
        
        return GenerationResult(
            content_type="landing_page",
            title="Landing Page - Fallback Generated",
            html_code=fallback_html,
            sections=["hero", "benefits", "cta", "footer"],
            conversion_elements=["cta_button", "form"],
            metadata={
                "generated_by": "fallback_generator",
                "fallback_reason": "Main generation failed",
                "performance_score": 70
            },
            variants=[],
            performance_predictions={"predicted_conversion_rate": "2.0%"}
        )