# src/intelligence/amplifier/enhancement.py - REFACTORED MODULAR SYSTEM
"""
Each intelligence category has its own dedicated AI enhancement module
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Import all AI enhancement modules
try:
    from .enhancements.scientific_enhancer import ScientificIntelligenceEnhancer
    from .enhancements.market_enhancer import MarketIntelligenceEnhancer
    from .enhancements.credibility_enhancer import CredibilityIntelligenceEnhancer
    from .enhancements.content_enhancer import ContentIntelligenceEnhancer
    from .enhancements.emotional_enhancer import EmotionalTransformationEnhancer
    from .enhancements.authority_enhancer import ScientificAuthorityEnhancer
    
    ENHANCEMENT_MODULES_AVAILABLE = True
    logger.info("✅ All AI enhancement modules imported successfully")
    
except ImportError as e:
    ENHANCEMENT_MODULES_AVAILABLE = False
    logger.warning(f"⚠️ AI enhancement modules not available: {str(e)}")

# ============================================================================
# CORE ENHANCEMENT FUNCTIONS (Enhanced with modular AI system)
# ============================================================================

async def identify_opportunities(base_intel: Dict, preferences: Dict, providers: List) -> Dict[str, Any]:
    """
    REFACTORED: Identify enhancement opportunities using modular AI system
    """
    logger.info("🔍 Identifying enhancement opportunities with modular AI system...")
    
    if not ENHANCEMENT_MODULES_AVAILABLE:
        return _fallback_identify_opportunities(base_intel)
    
    try:
        # Initialize all enhancement modules
        enhancers = _initialize_enhancement_modules(providers)
        
        # Identify opportunities across all modules
        opportunities = {
            "scientific_validation": [],
            "credibility_enhancement": [],
            "competitive_positioning": [],
            "market_authority": [],
            "content_optimization": [],
            "emotional_transformation": []
        }
        
        # Extract product information
        product_data = _extract_product_data(base_intel)
        
        # Run opportunity identification across all modules in parallel
        opportunity_tasks = []
        
        if enhancers.get("scientific"):
            opportunity_tasks.append(
                _identify_scientific_opportunities(enhancers["scientific"], product_data, base_intel)
            )
        
        if enhancers.get("market"):
            opportunity_tasks.append(
                _identify_market_opportunities(enhancers["market"], product_data, base_intel)
            )
        
        if enhancers.get("credibility"):
            opportunity_tasks.append(
                _identify_credibility_opportunities(enhancers["credibility"], product_data, base_intel)
            )
        
        if enhancers.get("content"):
            opportunity_tasks.append(
                _identify_content_opportunities(enhancers["content"], product_data, base_intel)
            )
        
        if enhancers.get("emotional"):
            opportunity_tasks.append(
                _identify_emotional_opportunities(enhancers["emotional"], product_data, base_intel)
            )
        
        if enhancers.get("authority"):
            opportunity_tasks.append(
                _identify_authority_opportunities(enhancers["authority"], product_data, base_intel)
            )
        
        # Execute all opportunity identification tasks
        logger.info("⚡ Running opportunity identification across all AI modules...")
        opportunity_results = await asyncio.gather(*opportunity_tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(opportunity_results):
            if isinstance(result, Exception):
                logger.error(f"❌ Module {i} opportunity identification failed: {str(result)}")
                continue
            
            # Merge opportunities from each module
            for key, value in result.items():
                if key in opportunities and isinstance(value, list):
                    opportunities[key].extend(value)
        
        # Add metadata
        total_opportunities = sum(len(opp_list) for opp_list in opportunities.values())
        
        result = {
            **opportunities,
            "opportunity_metadata": {
                "total_opportunities": total_opportunities,
                "modules_used": len([r for r in opportunity_results if not isinstance(r, Exception)]),
                "priority_areas": _prioritize_opportunities(opportunities),
                "enhancement_potential": "high" if total_opportunities > 15 else "medium" if total_opportunities > 8 else "low",
                "identified_at": datetime.utcnow().isoformat(),
                "system_version": "modular_ai_2.0"
            }
        }
        
        logger.info(f"✅ Identified {total_opportunities} opportunities across all AI modules")
        return result
        
    except Exception as e:
        logger.error(f"❌ AI opportunity identification failed: {str(e)}")
        return _fallback_identify_opportunities(base_intel)

async def generate_enhancements(base_intel: Dict, opportunities: Dict, providers: List) -> Dict[str, Any]:
    """
    REFACTORED: Generate AI-powered enhancements using all modular enhancement systems
    """
    logger.info("🚀 Generating AI-powered enhancements with modular system...")
    
    if not ENHANCEMENT_MODULES_AVAILABLE:
        return _fallback_generate_enhancements(base_intel, opportunities)
    
    try:
        # Initialize all enhancement modules
        enhancers = _initialize_enhancement_modules(providers)
        
        # Extract product information
        product_data = _extract_product_data(base_intel)
        
        # Run all enhancement modules in parallel for maximum efficiency
        enhancement_tasks = []
        
        # Scientific Intelligence Enhancement
        if enhancers.get("scientific"):
            enhancement_tasks.append(
                enhancers["scientific"].generate_scientific_intelligence(product_data, base_intel)
            )
        
        # Market Intelligence Enhancement
        if enhancers.get("market"):
            enhancement_tasks.append(
                enhancers["market"].generate_market_intelligence(product_data, base_intel)
            )
        
        # Credibility Intelligence Enhancement
        if enhancers.get("credibility"):
            enhancement_tasks.append(
                enhancers["credibility"].generate_credibility_intelligence(product_data, base_intel)
            )
        
        # Content Intelligence Enhancement
        if enhancers.get("content"):
            enhancement_tasks.append(
                enhancers["content"].generate_content_intelligence(product_data, base_intel)
            )
        
        # Emotional Transformation Enhancement
        if enhancers.get("emotional"):
            enhancement_tasks.append(
                enhancers["emotional"].generate_emotional_transformation_intelligence(product_data, base_intel)
            )
        
        # Scientific Authority Enhancement
        if enhancers.get("authority"):
            enhancement_tasks.append(
                enhancers["authority"].generate_scientific_authority_intelligence(product_data, base_intel)
            )
        
        # Execute all enhancement tasks in parallel
        logger.info("⚡ Running all AI enhancement modules in parallel...")
        enhancement_results = await asyncio.gather(*enhancement_tasks, return_exceptions=True)
        
        # Process results and handle any errors
        enhancements = {
            "scientific_validation": {},
            "credibility_boosters": {},
            "competitive_advantages": {},
            "research_support": {},
            "market_positioning": {},
            "content_optimization": {},
            "emotional_transformation": {},
            "authority_establishment": {}
        }
        
        enhancement_names = [
            "scientific_validation",
            "market_positioning", 
            "credibility_boosters",
            "content_optimization",
            "emotional_transformation",
            "authority_establishment"
        ]
        
        successful_modules = []
        
        for i, result in enumerate(enhancement_results):
            if isinstance(result, Exception):
                logger.error(f"❌ Enhancement module {i} failed: {str(result)}")
                continue
            
            if i < len(enhancement_names):
                enhancements[enhancement_names[i]] = result
                successful_modules.append(enhancement_names[i])
        
        # Calculate enhancement metadata
        total_enhancements = sum(
            len(result) if isinstance(result, (list, dict)) else 1 
            for result in enhancements.values() 
            if result
        )
        
        confidence_boost = _calculate_confidence_boost(enhancements, base_intel)
        credibility_score = _calculate_credibility_score(enhancements, base_intel)
        
        enhancement_metadata = {
            "total_enhancements": total_enhancements,
            "confidence_boost": confidence_boost,
            "credibility_score": credibility_score,
            "modules_successful": successful_modules,
            "modules_failed": len(enhancement_results) - len(successful_modules),
            "enhancement_quality": "excellent" if len(successful_modules) >= 5 else "good" if len(successful_modules) >= 3 else "basic",
            "enhanced_at": datetime.utcnow().isoformat(),
            "enhancement_version": "modular_ai_2.0",
            "ai_providers_used": _get_providers_used(enhancers),
            "parallel_processing": True,
            "system_architecture": "modular_enhancement_modules"
        }
        
        result = {
            **enhancements,
            "enhancement_metadata": enhancement_metadata
        }
        
        logger.info(f"✅ Generated {total_enhancements} enhancements across {len(successful_modules)} modules - Confidence boost: {confidence_boost:.1%}")
        return result
        
    except Exception as e:
        logger.error(f"❌ AI enhancement generation failed: {str(e)}")
        return _fallback_generate_enhancements(base_intel, opportunities)

def create_enriched_intelligence(base_intel: Dict, enhancements: Dict) -> Dict[str, Any]:
    """
    🔥 FIXED: Create enriched intelligence with proper AI enhancement mapping to database columns
    """
    logger.info("✨ Creating enriched intelligence with modular AI system...")
    
    # Start with base intelligence
    enriched = base_intel.copy()
    
    # 🔥 CRITICAL FIX: Map AI enhancements to the correct database column names
    intelligence_mapping = {
        # Map AI enhancement keys to database column names
        "scientific_intelligence": enhancements.get("scientific_validation", {}),
        "market_intelligence": enhancements.get("market_positioning", {}),
        "credibility_intelligence": enhancements.get("credibility_boosters", {}),
        "emotional_transformation_intelligence": enhancements.get("emotional_transformation", {}),
        "scientific_authority_intelligence": enhancements.get("authority_establishment", {}),
        
        # Enhanced content_intelligence by merging existing + AI enhancements
        "content_intelligence": {
            **enriched.get("content_intelligence", {}),
            **enhancements.get("content_optimization", {})
        }
    }
    
    # Add all AI-generated intelligence categories to enriched data
    for intel_category, enhancement_data in intelligence_mapping.items():
        if enhancement_data:  # Only add if there's actual data
            enriched[intel_category] = enhancement_data
            logger.info(f"🔥 Added {intel_category} with {len(enhancement_data) if isinstance(enhancement_data, dict) else 'data'}")
        else:
            # Ensure category exists even if empty
            enriched[intel_category] = _get_fallback_category_data(intel_category)
            logger.warning(f"⚠️ Using fallback data for {intel_category}")
    
    # Update confidence score based on enhancements
    original_confidence = base_intel.get("confidence_score", 0.0)
    enhancement_metadata = enhancements.get("enhancement_metadata", {})
    confidence_boost = enhancement_metadata.get("confidence_boost", 0.0)
    
    enriched["confidence_score"] = min(original_confidence + confidence_boost, 1.0)
    
    # Add comprehensive enrichment metadata
    enriched["enrichment_metadata"] = {
        **enhancement_metadata,
        "original_confidence": original_confidence,
        "amplification_applied": True,
        "intelligence_categories_populated": len([cat for cat, data in intelligence_mapping.items() if data]),
        "total_intelligence_categories": len(intelligence_mapping),
        "system_architecture": "modular_ai_enhancement",
        "category_completion_rate": len([cat for cat, data in intelligence_mapping.items() if data]) / len(intelligence_mapping),
        "enrichment_timestamp": datetime.utcnow().isoformat(),
        # 🔥 ADD: Storage validation for debugging
        "storage_validation_applied": True,
        "extraction_successful": True,
        "amplification_timestamp": datetime.utcnow().isoformat()
    }
    
    categories_populated = len([cat for cat, data in intelligence_mapping.items() if data])
    logger.info(f"✅ Enriched intelligence created - Categories populated: {categories_populated}/6")
    logger.info(f"📊 Final confidence: {original_confidence:.2f} → {enriched['confidence_score']:.2f} (+{confidence_boost:.2f})")
    
    return enriched

# ============================================================================
# MODULAR SYSTEM HELPER FUNCTIONS
# ============================================================================

def _initialize_enhancement_modules(providers: List[Dict]) -> Dict[str, Any]:
    """Initialize all AI enhancement modules"""
    
    enhancers = {}
    
    try:
        enhancers["scientific"] = ScientificIntelligenceEnhancer(providers)
        logger.info("✅ Scientific enhancement module initialized")
    except Exception as e:
        logger.error(f"❌ Scientific enhancer initialization failed: {str(e)}")
    
    try:
        enhancers["market"] = MarketIntelligenceEnhancer(providers)
        logger.info("✅ Market enhancement module initialized")
    except Exception as e:
        logger.error(f"❌ Market enhancer initialization failed: {str(e)}")
    
    try:
        enhancers["credibility"] = CredibilityIntelligenceEnhancer(providers)
        logger.info("✅ Credibility enhancement module initialized")
    except Exception as e:
        logger.error(f"❌ Credibility enhancer initialization failed: {str(e)}")
    
    try:
        enhancers["content"] = ContentIntelligenceEnhancer(providers)
        logger.info("✅ Content enhancement module initialized")
    except Exception as e:
        logger.error(f"❌ Content enhancer initialization failed: {str(e)}")
    
    try:
        enhancers["emotional"] = EmotionalTransformationEnhancer(providers)
        logger.info("✅ Emotional enhancement module initialized")
    except Exception as e:
        logger.error(f"❌ Emotional enhancer initialization failed: {str(e)}")
    
    try:
        enhancers["authority"] = ScientificAuthorityEnhancer(providers)
        logger.info("✅ Authority enhancement module initialized")
    except Exception as e:
        logger.error(f"❌ Authority enhancer initialization failed: {str(e)}")
    
    logger.info(f"🚀 Initialized {len(enhancers)} enhancement modules")
    return enhancers

def _extract_product_data(base_intel: Dict[str, Any]) -> Dict[str, Any]:
    """Extract product data for AI enhancement modules"""
    
    return {
        "product_name": base_intel.get("product_name", "Product"),
        "source_url": base_intel.get("source_url", ""),
        "page_title": base_intel.get("page_title", ""),
        "confidence_score": base_intel.get("confidence_score", 0.0),
        "analysis_timestamp": base_intel.get("analysis_timestamp", datetime.utcnow().isoformat())
    }

async def _identify_scientific_opportunities(enhancer, product_data: Dict, base_intel: Dict) -> Dict[str, List[str]]:
    """Identify scientific enhancement opportunities"""
    
    try:
        # Check for health claims that need scientific backing
        offer_intel = base_intel.get("offer_intelligence", {})
        value_props = offer_intel.get("value_propositions", [])
        
        opportunities = []
        
        # Look for health-related claims
        for prop in value_props:
            if any(health_term in str(prop).lower() for health_term in ["health", "liver", "weight", "energy", "metabolism"]):
                opportunities.append(f"Add scientific validation for: {prop}")
        
        # Add general scientific opportunities
        opportunities.extend([
            "Generate clinical research backing",
            "Develop ingredient safety profiles",
            "Create mechanism of action explanations",
            "Add peer-reviewed study references"
        ])
        
        return {"scientific_validation": opportunities}
        
    except Exception as e:
        logger.error(f"❌ Scientific opportunity identification failed: {str(e)}")
        return {"scientific_validation": ["Scientific enhancement available"]}

async def _identify_market_opportunities(enhancer, product_data: Dict, base_intel: Dict) -> Dict[str, List[str]]:
    """Identify market enhancement opportunities"""
    
    try:
        competitive_intel = base_intel.get("competitive_intelligence", {})
        
        opportunities = [
            "Generate comprehensive market analysis",
            "Develop competitive positioning strategy",
            "Create pricing optimization insights",
            "Build target market profiles",
            "Identify market gaps and opportunities"
        ]
        
        return {"competitive_positioning": opportunities}
        
    except Exception as e:
        logger.error(f"❌ Market opportunity identification failed: {str(e)}")
        return {"competitive_positioning": ["Market analysis enhancement available"]}

async def _identify_credibility_opportunities(enhancer, product_data: Dict, base_intel: Dict) -> Dict[str, List[str]]:
    """Identify credibility enhancement opportunities"""
    
    try:
        confidence_score = base_intel.get("confidence_score", 0.0)
        
        opportunities = [
            "Generate trust indicators and signals",
            "Develop authority and expertise markers",
            "Create social proof enhancement",
            "Build reputation factors analysis",
            "Establish credibility scoring system"
        ]
        
        if confidence_score < 0.8:
            opportunities.append("Boost overall credibility score")
        
        return {"credibility_enhancement": opportunities}
        
    except Exception as e:
        logger.error(f"❌ Credibility opportunity identification failed: {str(e)}")
        return {"credibility_enhancement": ["Credibility enhancement available"]}

async def _identify_content_opportunities(enhancer, product_data: Dict, base_intel: Dict) -> Dict[str, List[str]]:
    """Identify content enhancement opportunities"""
    
    try:
        content_intel = base_intel.get("content_intelligence", {})
        
        opportunities = [
            "Enhance key messaging with AI insights",
            "Amplify social proof elements",
            "Develop success story frameworks",
            "Create content hierarchy optimization",
            "Generate engagement-focused messaging"
        ]
        
        return {"content_optimization": opportunities}
        
    except Exception as e:
        logger.error(f"❌ Content opportunity identification failed: {str(e)}")
        return {"content_optimization": ["Content enhancement available"]}

async def _identify_emotional_opportunities(enhancer, product_data: Dict, base_intel: Dict) -> Dict[str, List[str]]:
    """Identify emotional transformation opportunities"""
    
    try:
        psych_intel = base_intel.get("psychology_intelligence", {})
        
        opportunities = [
            "Map customer emotional journey",
            "Identify psychological triggers",
            "Develop emotional value propositions",
            "Create transformation narratives",
            "Build emotional engagement strategies"
        ]
        
        return {"emotional_transformation": opportunities}
        
    except Exception as e:
        logger.error(f"❌ Emotional opportunity identification failed: {str(e)}")
        return {"emotional_transformation": ["Emotional enhancement available"]}

async def _identify_authority_opportunities(enhancer, product_data: Dict, base_intel: Dict) -> Dict[str, List[str]]:
    """Identify scientific authority opportunities"""
    
    try:
        opportunities = [
            "Establish scientific research validation",
            "Build professional authority markers",
            "Create expertise demonstration content",
            "Develop industry recognition signals",
            "Generate thought leadership positioning"
        ]
        
        return {"market_authority": opportunities}
        
    except Exception as e:
        logger.error(f"❌ Authority opportunity identification failed: {str(e)}")
        return {"market_authority": ["Authority enhancement available"]}

def _prioritize_opportunities(opportunities: Dict[str, List]) -> List[str]:
    """Prioritize enhancement opportunities by impact"""
    
    priority_map = {
        "scientific_validation": 5,      # Highest priority
        "credibility_enhancement": 4,
        "competitive_positioning": 3,
        "content_optimization": 2,
        "emotional_transformation": 1,
        "market_authority": 1
    }
    
    priorities = []
    for opp_type, opp_list in opportunities.items():
        if opp_list:
            priority = priority_map.get(opp_type, 0)
            priorities.append((priority, opp_type, len(opp_list)))
    
    # Sort by priority (highest first)
    priorities.sort(reverse=True)
    
    return [f"{opp_type} ({count} opportunities)" for _, opp_type, count in priorities]

def _calculate_confidence_boost(enhancements: Dict, base_intel: Dict) -> float:
    """Calculate total confidence boost from all enhancements"""
    
    total_boost = 0.0
    
    # Count enhancements across all modules
    for enhancement_type, enhancement_data in enhancements.items():
        if isinstance(enhancement_data, dict) and enhancement_data:
            total_boost += 0.05  # 5% boost per populated category
        elif isinstance(enhancement_data, list) and enhancement_data:
            total_boost += min(len(enhancement_data) * 0.02, 0.10)  # Up to 10% per category
    
    # Cap the boost to prevent unrealistic scores
    return min(total_boost, 0.35)  # Maximum 35% boost

def _calculate_credibility_score(enhancements: Dict, base_intel: Dict) -> float:
    """Calculate overall credibility score from all enhancements"""
    
    base_confidence = base_intel.get("confidence_score", 0.0)
    confidence_boost = _calculate_confidence_boost(enhancements, base_intel)
    
    # Enhanced credibility calculation
    enhanced_credibility = min(base_confidence + confidence_boost, 1.0)
    
    return enhanced_credibility

def _get_providers_used(enhancers: Dict[str, Any]) -> List[str]:
    """Get list of AI providers used across all enhancers"""
    
    providers_used = set()
    
    for enhancer_name, enhancer in enhancers.items():
        if hasattr(enhancer, 'available_provider') and enhancer.available_provider:
            provider_name = enhancer.available_provider.get("name", "unknown")
            providers_used.add(provider_name)
    
    return list(providers_used)

def _get_fallback_category_data(category: str) -> Dict[str, Any]:
    """Get fallback data for intelligence categories"""
    
    fallback_data = {
        "scientific_intelligence": {
            "scientific_backing": ["General health and wellness support"],
            "research_quality_score": 0.5,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback"
        },
        "market_intelligence": {
            "market_analysis": {"market_size": {"current_estimate": "Growing market"}},
            "market_intelligence_score": 0.5,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback"
        },
        "credibility_intelligence": {
            "trust_indicators": {"trust_building_elements": ["Quality assurance"]},
            "overall_credibility_score": 0.6,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback"
        },
        "content_intelligence": {
            "key_messages": ["Quality health solution"],
            "content_structure": "Standard content",
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback"
        },
        "emotional_transformation_intelligence": {
            "emotional_journey": {"current_state": ["Seeking health solutions"]},
            "transformation_confidence": 0.5,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback"
        },
        "scientific_authority_intelligence": {
            "research_validation": {"evidence_strength": "Basic validation"},
            "authority_score": 0.6,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "fallback"
        }
    }
    
    return fallback_data.get(category, {"status": "Enhancement not available"})

# ============================================================================
# FALLBACK FUNCTIONS
# ============================================================================

def _fallback_identify_opportunities(base_intel: Dict) -> Dict[str, Any]:
    """Fallback opportunity identification when AI modules unavailable"""
    
    return {
        "scientific_validation": ["AI scientific enhancement not available"],
        "credibility_enhancement": ["AI credibility enhancement not available"], 
        "competitive_positioning": ["AI market enhancement not available"],
        "market_authority": ["AI authority enhancement not available"],
        "content_optimization": ["AI content enhancement not available"],
        "emotional_transformation": ["AI emotional enhancement not available"],
        "opportunity_metadata": {
            "total_opportunities": 6,
            "priority_areas": ["Install AI enhancement modules"],
            "enhancement_potential": "requires_ai_modules",
            "identified_at": datetime.utcnow().isoformat(),
            "system_version": "fallback"
        }
    }

def _fallback_generate_enhancements(base_intel: Dict, opportunities: Dict) -> Dict[str, Any]:
    """Fallback enhancement generation when AI modules unavailable"""
    
    return {
        "scientific_validation": {"note": "AI scientific enhancement not available"},
        "credibility_boosters": {"note": "AI credibility enhancement not available"},
        "competitive_advantages": {"note": "AI market enhancement not available"},
        "research_support": {"note": "AI research enhancement not available"},
        "market_positioning": {"note": "AI positioning enhancement not available"},
        "content_optimization": {"note": "AI content enhancement not available"},
        "emotional_transformation": {"note": "AI emotional enhancement not available"},
        "authority_establishment": {"note": "AI authority enhancement not available"},
        "enhancement_metadata": {
            "total_enhancements": 0,
            "confidence_boost": 0.0,
            "credibility_score": base_intel.get("confidence_score", 0.6),
            "modules_successful": [],
            "modules_failed": 6,
            "enhancement_quality": "fallback",
            "enhanced_at": datetime.utcnow().isoformat(),
            "enhancement_version": "fallback",
            "fallback_reason": "AI enhancement modules not available"
        }
    }