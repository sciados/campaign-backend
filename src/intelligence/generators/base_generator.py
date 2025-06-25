# src/intelligence/generators/base_generator.py
"""
BASE GENERATOR CLASS
✅ Common functionality and patterns for all generators
✅ Standardized response formats
✅ AI provider management
✅ Error handling and fallbacks
"""

import os
import logging
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseContentGenerator(ABC):
    """Abstract base class for all content generators"""
    
    def __init__(self, generator_type: str):
        self.generator_type = generator_type
        self.ai_providers = self._initialize_ai_providers()
        self.generation_id = str(uuid.uuid4())[:8]
        logger.info(f"✅ {generator_type} Generator initialized with {len(self.ai_providers)} AI providers")
    
    def _initialize_ai_providers(self) -> List[Dict[str, Any]]:
        """Initialize AI providers with fallback handling"""
        providers = []
        
        # OpenAI Provider
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                import openai
                providers.append({
                    "name": "openai",
                    "client": openai.AsyncOpenAI(api_key=api_key),
                    "models": ["gpt-4", "gpt-3.5-turbo"],
                    "available": True,
                    "strengths": ["creativity", "versatility", "conversational"]
                })
                logger.info("✅ OpenAI provider initialized")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI provider failed: {str(e)}")
        
        # Anthropic Provider
        try:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                import anthropic
                providers.append({
                    "name": "anthropic", 
                    "client": anthropic.AsyncAnthropic(api_key=api_key),
                    "models": ["claude-3-5-sonnet-20241022"],
                    "available": True,
                    "strengths": ["long_form", "structured_content", "analysis"]
                })
                logger.info("✅ Anthropic provider initialized")
        except Exception as e:
            logger.warning(f"⚠️ Anthropic provider failed: {str(e)}")
        
        if not providers:
            logger.error("❌ No AI providers available - generators will use fallback content")
        
        return providers
    
    @abstractmethod
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Abstract method for content generation - must be implemented by subclasses"""
        pass
    
    def _extract_product_name(self, intelligence_data: Dict[str, Any]) -> str:
        """Extract product name from intelligence data"""
        try:
            offer_intel = intelligence_data.get("offer_intelligence", {})
            insights = offer_intel.get("insights", [])
            
            for insight in insights:
                if "called" in str(insight).lower():
                    words = str(insight).split()
                    for i, word in enumerate(words):
                        if word.lower() == "called" and i + 1 < len(words):
                            return words[i + 1].upper().replace(",", "").replace(".", "")
            
            # Fallback extraction methods
            products = offer_intel.get("products", [])
            if products:
                return str(products[0]).upper()
            
        except Exception as e:
            logger.warning(f"⚠️ Product name extraction failed: {str(e)}")
        
        return "PRODUCT"
    
    def _create_standardized_response(
        self, 
        content: Dict[str, Any],
        title: str,
        product_name: str,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create standardized response format"""
        
        if preferences is None:
            preferences = {}
        
        return {
            "content_type": self.generator_type,
            "title": title,
            "content": content,
            "metadata": {
                "generated_by": f"{self.generator_type}_generator",
                "product_name": product_name,
                "content_type": self.generator_type,
                "generation_id": self.generation_id,
                "generated_at": datetime.utcnow().isoformat(),
                "preferences_used": preferences,
                "ai_providers_available": len(self.ai_providers),
                "generator_version": "1.0.0"
            }
        }
    
    def _safe_int_conversion(self, value: str, default: int, min_val: int, max_val: int) -> int:
        """Safely convert string to integer with bounds checking"""
        try:
            result = int(value) if str(value).isdigit() else default
            return max(min_val, min(max_val, result))
        except:
            return default
    
    def _extract_angle_intelligence(self, intelligence_data: Dict[str, Any]) -> Dict[str, Dict]:
        """Extract angle-specific intelligence for content generation"""
        
        scientific_intel = intelligence_data.get("scientific_authority_intelligence", {})
        emotional_intel = intelligence_data.get("emotional_transformation_intelligence", {})
        community_intel = intelligence_data.get("community_social_proof_intelligence", {})
        urgency_intel = intelligence_data.get("urgency_scarcity_intelligence", {})
        lifestyle_intel = intelligence_data.get("lifestyle_confidence_intelligence", {})
        
        return {
            "scientific": {
                "focus": ", ".join(scientific_intel.get("clinical_studies", ["Research validation"])[:2]),
                "credibility": scientific_intel.get("credibility_score", 0.8)
            },
            "emotional": {
                "focus": ", ".join(emotional_intel.get("transformation_stories", ["Personal transformation"])[:2]),
                "credibility": 0.78
            },
            "community": {
                "focus": ", ".join(community_intel.get("social_proof_elements", ["Customer testimonials"])[:2]),
                "credibility": 0.75
            },
            "urgency": {
                "focus": ", ".join(urgency_intel.get("urgency_messages", ["Time-sensitive offers"])[:2]),
                "credibility": 0.70
            },
            "lifestyle": {
                "focus": ", ".join(lifestyle_intel.get("lifestyle_benefits", ["Confidence and energy"])[:2]),
                "credibility": 0.73
            }
        }
    
    def _get_provider_by_strength(self, required_strength: str) -> Optional[Dict[str, Any]]:
        """Get AI provider best suited for specific strength"""
        
        for provider in self.ai_providers:
            if required_strength in provider.get("strengths", []):
                return provider
        
        # Return first available provider if no specific match
        return self.ai_providers[0] if self.ai_providers else None
    
    async def _generate_with_provider_fallback(
        self, 
        generation_method,
        *args,
        **kwargs
    ) -> Any:
        """Try generation with multiple providers as fallback"""
        
        last_error = None
        
        for provider in self.ai_providers:
            try:
                logger.info(f"🤖 Attempting generation with {provider['name']}")
                result = await generation_method(provider, *args, **kwargs)
                
                if result:
                    logger.info(f"✅ Generation successful with {provider['name']}")
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Generation failed with {provider['name']}: {str(e)}")
                last_error = e
                continue
        
        logger.error(f"❌ All providers failed. Last error: {str(last_error)}")
        return None
    
    def _validate_intelligence_data(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and enhance intelligence data"""
        
        validation_result = {
            "is_valid": True,
            "missing_sections": [],
            "warnings": [],
            "quality_score": 0.0
        }
        
        # Check required sections
        required_sections = [
            "offer_intelligence",
            "psychology_intelligence", 
            "competitive_intelligence"
        ]
        
        present_sections = 0
        for section in required_sections:
            if section in intelligence_data and intelligence_data[section]:
                present_sections += 1
            else:
                validation_result["missing_sections"].append(section)
        
        validation_result["quality_score"] = present_sections / len(required_sections)
        
        # Add warnings based on quality
        if validation_result["quality_score"] < 0.5:
            validation_result["warnings"].append("Low intelligence data quality - may affect content generation")
        
        if not intelligence_data.get("confidence_score"):
            validation_result["warnings"].append("Missing confidence score - using default")
        
        if validation_result["quality_score"] < 0.3:
            validation_result["is_valid"] = False
        
        return validation_result


# ============================================================================
# UTILITIES MODULE
# ============================================================================

# src/intelligence/generators/utils.py
"""
GENERATOR UTILITIES
✅ Common utility functions for all generators
✅ Text processing and formatting
✅ Response validation
✅ Error handling helpers
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

def clean_text_content(text: str) -> str:
    """Clean and normalize text content"""
    
    if not text or not isinstance(text, str):
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters that might break formatting
    text = re.sub(r'[^\w\s\.,!?;:()\-\'"@#$%&]', '', text)
    
    # Fix common punctuation issues
    text = re.sub(r'\s+([,.!?;:])', r'\1', text)  # Remove space before punctuation
    text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', text)  # Ensure space after sentence endings
    
    return text.strip()

def extract_keywords_from_intelligence(intelligence_data: Dict[str, Any]) -> List[str]:
    """Extract relevant keywords from intelligence data"""
    
    keywords = []
    
    try:
        # Extract from offer intelligence
        offer_intel = intelligence_data.get("offer_intelligence", {})
        
        # Value propositions
        value_props = offer_intel.get("value_propositions", [])
        for prop in value_props:
            words = str(prop).split()
            keywords.extend([word.lower() for word in words if len(word) > 3])
        
        # Benefits
        benefits = offer_intel.get("benefits", [])
        for benefit in benefits:
            words = str(benefit).split()
            keywords.extend([word.lower() for word in words if len(word) > 3])
        
        # Psychology intelligence keywords
        psych_intel = intelligence_data.get("psychology_intelligence", {})
        emotional_triggers = psych_intel.get("emotional_triggers", [])
        keywords.extend([trigger.lower() for trigger in emotional_triggers if isinstance(trigger, str)])
        
        # Remove duplicates and common stop words
        stop_words = {'the', 'and', 'for', 'with', 'you', 'your', 'this', 'that', 'from', 'they', 'have', 'will'}
        keywords = list(set([k for k in keywords if k not in stop_words and len(k) > 2]))
        
    except Exception as e:
        logger.warning(f"⚠️ Keyword extraction failed: {str(e)}")
    
    return keywords[:20]  # Return top 20 keywords

def validate_content_response(response: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """Validate generated content response"""
    
    validation = {
        "is_valid": True,
        "missing_fields": [],
        "warnings": [],
        "quality_score": 0.0
    }
    
    # Check required fields
    for field in required_fields:
        if field not in response:
            validation["missing_fields"].append(field)
            validation["is_valid"] = False
    
    # Calculate quality score
    present_fields = len([f for f in required_fields if f in response])
    validation["quality_score"] = present_fields / len(required_fields) if required_fields else 1.0
    
    # Content-specific validation
    content = response.get("content", {})
    
    # Check if content is not empty
    if not content or (isinstance(content, dict) and not any(content.values())):
        validation["warnings"].append("Content appears to be empty")
        validation["quality_score"] *= 0.5
    
    # Check for fallback indicators
    if isinstance(content, dict) and content.get("fallback_generated"):
        validation["warnings"].append("Content generated using fallback method")
        validation["quality_score"] *= 0.7
    
    return validation

def format_duration_string(seconds: Union[int, float]) -> str:
    """Format duration in seconds to human-readable string"""
    
    if seconds < 60:
        return f"{int(seconds)} seconds"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        if remaining_seconds > 0:
            return f"{minutes}:{remaining_seconds:02d}"
        else:
            return f"{minutes} minutes"
    else:
        hours = int(seconds // 3600)
        remaining_minutes = int((seconds % 3600) // 60)
        return f"{hours}h {remaining_minutes}m"

def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length with suffix"""
    
    if not text or len(text) <= max_length:
        return text
    
    truncated = text[:max_length - len(suffix)]
    
    # Try to break at word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.8:  # Only if we don't lose too much content
        truncated = truncated[:last_space]
    
    return truncated + suffix

def count_words(text: str) -> int:
    """Count words in text"""
    
    if not text or not isinstance(text, str):
        return 0
    
    # Simple word count - split by whitespace
    words = text.split()
    return len(words)

def estimate_reading_time(text: str, words_per_minute: int = 200) -> str:
    """Estimate reading time for text"""
    
    word_count = count_words(text)
    minutes = word_count / words_per_minute
    
    if minutes < 1:
        return "Less than 1 minute"
    elif minutes < 60:
        return f"{int(minutes)} minute{'s' if minutes != 1 else ''}"
    else:
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        return f"{hours}h {remaining_minutes}m"

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    
    # Remove or replace unsafe characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 100:
        sanitized = sanitized[:100]
    
    return sanitized or "untitled"

def merge_preferences(default_prefs: Dict[str, Any], user_prefs: Dict[str, Any]) -> Dict[str, Any]:
    """Merge user preferences with defaults"""
    
    merged = default_prefs.copy()
    
    if user_prefs:
        for key, value in user_prefs.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                # Recursively merge nested dictionaries
                merged[key] = merge_preferences(merged[key], value)
            else:
                merged[key] = value
    
    return merged

def log_generation_metrics(
    generator_type: str,
    start_time: float,
    end_time: float,
    content_length: int = 0,
    success: bool = True
):
    """Log generation performance metrics"""
    
    duration = end_time - start_time
    
    logger.info(
        f"📊 {generator_type} Generation: "
        f"{'✅ Success' if success else '❌ Failed'} | "
        f"Duration: {duration:.2f}s | "
        f"Content: {content_length} chars"
    )

# Convenience functions for common patterns
def safe_get(data: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Safely get nested dictionary value using dot notation"""
    
    keys = key_path.split('.')
    current = data
    
    try:
        for key in keys:
            current = current[key]
        return current
    except (KeyError, TypeError):
        return default

def ensure_list(value: Any) -> List[Any]:
    """Ensure value is a list"""
    
    if value is None:
        return []
    elif isinstance(value, list):
        return value
    else:
        return [value]

def ensure_string(value: Any, default: str = "") -> str:
    """Ensure value is a string"""
    
    if value is None:
        return default
    elif isinstance(value, str):
        return value
    else:
        return str(value)