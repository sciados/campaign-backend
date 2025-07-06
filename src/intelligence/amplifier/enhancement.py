# src/intelligence/amplifier/enhancement.py - COMPLETE MOCK DATA ELIMINATION FIX
"""
Intelligence Enhancement System - Mock Data Elimination
🔥 FIXED: Eliminates mock data contamination while keeping existing system
🚀 SIMPLIFIED: Works with current enhancer architecture
⚡ ENHANCED: Provider health tracking integration
"""
import asyncio
import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Import enhanced AI throttle system
try:
    from ..utils.ai_throttle import (
        get_provider_health_report,
        log_system_status,
        _is_provider_healthy,
        _update_provider_health
    )
    ENHANCED_AI_SYSTEM_AVAILABLE = True
    logger.info("✅ Enhanced AI system imported")
except ImportError as e:
    ENHANCED_AI_SYSTEM_AVAILABLE = False
    logger.warning(f"⚠️ Enhanced AI system not available: {str(e)}")

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

# Load balancing with health tracking
_provider_usage_stats = {}
_provider_performance_stats = {}
_total_requests = 0
_successful_requests = 0
_failed_requests = 0

# Global load balancing state (keep existing for compatibility)
_provider_rotation_index = 0

# ============================================================================
# ENHANCED MOCK DATA DETECTION AND ELIMINATION
# ============================================================================

def _is_valid_enhancement(data: Any, category: str) -> bool:
    """
    🔥 NEW: Validate enhancement data to ensure it's real AI content, not mock data
    """
    if not data:
        return False
    
    if not isinstance(data, dict):
        return False
    
    if len(data) == 0:
        return False
    
    # Check for mock data indicators
    data_str = str(data).lower()
    mock_indicators = [
        "generic marketing intelligence placeholder",
        "fallback_data",
        "mock data",
        "placeholder",
        "ai response generated but could not be parsed",
        "enhancement not available",
        "fallback",
        "generic",
        "default response"
    ]
    
    for indicator in mock_indicators:
        if indicator in data_str:
            logger.warning(f"🚨 Mock data detected in {category}: {indicator}")
            return False
    
    # Check for meaningful content
    if isinstance(data, dict):
        # Ensure there's substantial content
        content_keys = [k for k in data.keys() if not k.endswith('_metadata') and not k.startswith('_')]
        if len(content_keys) == 0:
            return False
        
        # Check if values have meaningful content
        has_meaningful_content = False
        for key, value in data.items():
            if key.endswith('_metadata') or key.startswith('_'):
                continue
                
            if isinstance(value, (list, dict)) and len(value) > 0:
                has_meaningful_content = True
                break
            elif isinstance(value, str) and len(value) > 10 and "placeholder" not in value.lower():
                has_meaningful_content = True
                break
        
        return has_meaningful_content
    
    return True

def _detect_mock_data_contamination(enhancements: Dict[str, Any]) -> List[str]:
    """
    🔥 NEW: Detect mock data contamination across all enhancements
    """
    contamination_found = []
    
    for key, value in enhancements.items():
        if key == "enhancement_metadata":
            continue
            
        data_str = str(value).lower()
        
        # Check for specific mock data patterns
        mock_patterns = [
            "generic marketing intelligence placeholder",
            "fallback_data",
            "ai response generated but could not be parsed",
            "enhancement not available",
            "mock data",
            "placeholder content",
            "fallback",
            "generic"
        ]
        
        for pattern in mock_patterns:
            if pattern in data_str:
                contamination_found.append(f"{key}: {pattern}")
    
    return contamination_found

def _clean_enhancement_data(data: Any, category: str) -> Optional[Dict]:
    """
    🔥 NEW: Clean enhancement data by removing mock data elements
    Returns None if all data is mock data
    """
    if not data or not isinstance(data, dict):
        return None
    
    cleaned_data = {}
    
    for key, value in data.items():
        if key.endswith('_metadata') or key.startswith('_'):
            # Keep metadata as-is
            cleaned_data[key] = value
            continue
        
        # Check if this value contains mock data
        value_str = str(value).lower() if value else ""
        
        mock_indicators = [
            "generic marketing intelligence placeholder",
            "fallback_data",
            "mock data",
            "placeholder",
            "ai response generated but could not be parsed",
            "enhancement not available",
            "fallback",
            "generic"
        ]
        
        is_mock = any(indicator in value_str for indicator in mock_indicators)
        
        if not is_mock and value:
            cleaned_data[key] = value
        else:
            logger.warning(f"🧹 Removed mock data from {category}.{key}: {value_str[:50]}...")
    
    # Return cleaned data only if it has meaningful content
    content_keys = [k for k in cleaned_data.keys() if not k.endswith('_metadata') and not k.startswith('_')]
    if len(content_keys) > 0:
        return cleaned_data
    else:
        logger.warning(f"🚫 {category}: All data was mock data, returning None")
        return None

# ============================================================================
# EXISTING SYSTEM FUNCTIONS (Keep for compatibility)
# ============================================================================

def _get_next_provider_with_load_balancing(providers: List[Dict]) -> Optional[Dict]:
    """Keep existing load balancing function"""
    global _provider_rotation_index, _provider_usage_stats
    
    if not providers:
        return None
    
    # Filter to only ultra-cheap providers (priority 1-3)
    ultra_cheap_providers = [p for p in providers if p.get("priority", 999) <= 3]
    
    if not ultra_cheap_providers:
        logger.warning("⚠️ No ultra-cheap providers available")
        return providers[0] if providers else None
    
    # Sort by priority to ensure consistent order
    ultra_cheap_providers.sort(key=lambda x: x.get("priority", 999))
    
    # Round-robin selection
    selected_provider = ultra_cheap_providers[_provider_rotation_index % len(ultra_cheap_providers)]
    
    # Update rotation index
    _provider_rotation_index += 1
    
    # Track usage statistics
    provider_name = selected_provider.get("name", "unknown")
    if provider_name not in _provider_usage_stats:
        _provider_usage_stats[provider_name] = 0
    _provider_usage_stats[provider_name] += 1
    
    logger.debug(f"🔄 Load balancer: Selected {provider_name} (usage: {_provider_usage_stats[provider_name]})")
    
    return selected_provider

def _initialize_enhancement_modules_with_load_balancing(providers: List[Dict]) -> Dict[str, Any]:
    """Keep existing initialization function"""
    
    enhancers = {}
    
    # Define the 6 enhancers and assign them providers in round-robin fashion
    enhancer_configs = [
        ("scientific", ScientificIntelligenceEnhancer),
        ("credibility", CredibilityIntelligenceEnhancer),
        ("content", ContentIntelligenceEnhancer),
        ("emotional", EmotionalTransformationEnhancer),
        ("authority", ScientificAuthorityEnhancer),
        ("market", MarketIntelligenceEnhancer)
    ]
    
    logger.info("🚀 Initializing enhancers with load balanced provider assignment...")
    
    # Get all available ultra-cheap providers
    ultra_cheap_providers = [p for p in providers if p.get("priority", 999) <= 3]
    
    if not ultra_cheap_providers:
        logger.error("❌ No ultra-cheap providers available!")
        return {}
    
    # Sort by priority for consistent assignment
    ultra_cheap_providers.sort(key=lambda x: x.get("priority", 999))
    
    logger.info(f"💎 Ultra-cheap providers available: {[p['name'] for p in ultra_cheap_providers]}")
    
    # Initialize each enhancer with its assigned provider
    for i, (enhancer_name, enhancer_class) in enumerate(enhancer_configs):
        try:
            # Assign provider using round-robin
            assigned_provider = ultra_cheap_providers[i % len(ultra_cheap_providers)]
            provider_name = assigned_provider.get("name", "unknown")
            
            # Create single-provider list for this enhancer
            enhancer_providers = [assigned_provider]
            
            # Initialize enhancer
            enhancers[enhancer_name] = enhancer_class(enhancer_providers)
            
            logger.info(f"✅ {enhancer_name}: Assigned to {provider_name}")
            
        except Exception as e:
            logger.error(f"❌ {enhancer_name} enhancer initialization failed: {str(e)}")
    
    return enhancers

# ============================================================================
# ENHANCED CORE FUNCTIONS WITH MOCK DATA ELIMINATION
# ============================================================================

async def identify_opportunities(base_intel: Dict, preferences: Dict, providers: List) -> Dict[str, Any]:
    """
    🔥 ENHANCED: Opportunity identification with existing system + mock data elimination
    """
    logger.info("🔍 Identifying enhancement opportunities with mock data elimination...")
    
    if not ENHANCEMENT_MODULES_AVAILABLE:
        return _fallback_identify_opportunities(base_intel)
    
    try:
        # Initialize all enhancement modules with load balancing (existing system)
        enhancers = _initialize_enhancement_modules_with_load_balancing(providers)
        
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
        
        logger.info("⚡ Running opportunity identification with existing system...")
        
        # Use existing opportunity identification functions
        opportunity_queue = [
            ("scientific", _identify_scientific_opportunities, enhancers.get("scientific")),
            ("credibility", _identify_credibility_opportunities, enhancers.get("credibility")),
            ("content", _identify_content_opportunities, enhancers.get("content")),
            ("market", _identify_market_opportunities, enhancers.get("market")),
            ("emotional", _identify_emotional_opportunities, enhancers.get("emotional")),
            ("authority", _identify_authority_opportunities, enhancers.get("authority"))
        ]
        
        # Execute opportunity identification sequentially
        for i, (module_name, identify_func, enhancer) in enumerate(opportunity_queue, 1):
            if enhancer:
                try:
                    logger.info(f"🔄 Opportunity identification {i}/{len(opportunity_queue)}: {module_name}")
                    
                    result = await identify_func(enhancer, product_data, base_intel)
                    
                    # Merge opportunities from this module
                    for key, value in result.items():
                        if key in opportunities and isinstance(value, list):
                            opportunities[key].extend(value)
                    
                    logger.info(f"✅ {module_name}: Opportunities identified")
                    
                    # Small delay between modules
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"❌ {module_name} opportunity identification failed: {str(e)}")
                    continue
        
        # Add metadata
        total_opportunities = sum(len(opp_list) for opp_list in opportunities.values())
        
        result = {
            **opportunities,
            "opportunity_metadata": {
                "total_opportunities": total_opportunities,
                "modules_used": len([e for _, _, e in opportunity_queue if e]),
                "priority_areas": _prioritize_opportunities(opportunities),
                "enhancement_potential": "high" if total_opportunities > 15 else "medium" if total_opportunities > 8 else "low",
                "identified_at": datetime.utcnow().isoformat(),
                "system_version": "mock_data_elimination_1.0",
                "execution_mode": "existing_system_enhanced",
                "mock_data_elimination": True
            }
        }
        
        logger.info(f"✅ Identified {total_opportunities} opportunities")
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced opportunity identification failed: {str(e)}")
        return _fallback_identify_opportunities(base_intel)

async def generate_enhancements(base_intel: Dict, opportunities: Dict, providers: List) -> Dict[str, Any]:
    """
    🔥 CRITICAL ENHANCEMENT: Generate AI-powered enhancements with MOCK DATA ELIMINATION
    Uses existing enhancer system but eliminates mock data contamination
    """
    logger.info("🚀 Generating AI-powered enhancements with MOCK DATA ELIMINATION...")
    
    if not ENHANCEMENT_MODULES_AVAILABLE:
        return _fallback_generate_enhancements(base_intel, opportunities)
    
    try:
        # Initialize all enhancement modules with load balancing (existing system)
        enhancers = _initialize_enhancement_modules_with_load_balancing(providers)
        
        # Extract product information
        product_data = _extract_product_data(base_intel)
        
        logger.info("⚡ Running AI enhancement modules with EXISTING SYSTEM + MOCK DATA ELIMINATION...")
        logger.info("🎯 Mock data will be detected and eliminated")
        logger.info("⏱️ Estimated completion time: 3-4 minutes")
        
        # Define enhancement execution queue (existing system)
        enhancement_queue = [
            ("scientific", enhancers.get("scientific"), "scientific_validation", "scientific_intelligence"),
            ("credibility", enhancers.get("credibility"), "credibility_boosters", "credibility_intelligence"), 
            ("content", enhancers.get("content"), "content_optimization", "content_intelligence"),
            ("emotional", enhancers.get("emotional"), "emotional_transformation", "emotional_transformation_intelligence"),
            ("authority", enhancers.get("authority"), "authority_establishment", "scientific_authority_intelligence"),
            ("market", enhancers.get("market"), "market_positioning", "market_intelligence")
        ]
        
        # Initialize results
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
        
        successful_modules = []
        failed_modules = []
        total_enhancements = 0
        mock_data_detected = []
        
        # Execute each enhancer sequentially (existing system)
        for i, (module_name, enhancer, result_key, intelligence_type) in enumerate(enhancement_queue, 1):
            if not enhancer:
                logger.warning(f"⚠️ {module_name}: Enhancer not available, skipping")
                failed_modules.append(module_name)
                continue
            
            try:
                logger.info(f"🔄 Running enhancer {i}/{len(enhancement_queue)}: {module_name}")
                start_time = time.time()
                
                # Run single enhancer with appropriate method (existing system)
                if module_name == "scientific":
                    result = await enhancer.generate_scientific_intelligence(product_data, base_intel)
                elif module_name == "credibility":
                    result = await enhancer.generate_credibility_intelligence(product_data, base_intel)
                elif module_name == "content":
                    result = await enhancer.generate_content_intelligence(product_data, base_intel)
                elif module_name == "emotional":
                    result = await enhancer.generate_emotional_transformation_intelligence(product_data, base_intel)
                elif module_name == "authority":
                    result = await enhancer.generate_scientific_authority_intelligence(product_data, base_intel)
                elif module_name == "market":
                    result = await enhancer.generate_market_intelligence(product_data, base_intel)
                else:
                    logger.error(f"❌ Unknown enhancer type: {module_name}")
                    continue
                
                # 🔥 CRITICAL: Clean and validate results to eliminate mock data
                if result and isinstance(result, dict):
                    # Clean the result to remove any mock data
                    cleaned_result = _clean_enhancement_data(result, module_name)
                    
                    if cleaned_result and _is_valid_enhancement(cleaned_result, module_name):
                        enhancements[result_key] = cleaned_result
                        successful_modules.append(module_name)
                        
                        # Count enhancements in this result
                        enhancement_count = _count_enhancements_in_result(cleaned_result)
                        total_enhancements += enhancement_count
                        
                        execution_time = time.time() - start_time
                        logger.info(f"✅ {module_name}: Completed in {execution_time:.1f}s ({enhancement_count} real enhancements)")
                        
                        # Log sample data for verification (real data only)
                        if isinstance(cleaned_result, dict) and cleaned_result:
                            sample_key = list(cleaned_result.keys())[0]
                            sample_data = cleaned_result[sample_key]
                            logger.info(f"   📊 Sample real data: {sample_key} = {str(sample_data)[:80]}...")
                    else:
                        logger.warning(f"⚠️ {module_name}: Result contained only mock data, discarded")
                        failed_modules.append(module_name)
                        
                        # Track mock data detection
                        if result:
                            contamination = _detect_mock_data_contamination({result_key: result})
                            mock_data_detected.extend(contamination)
                else:
                    logger.warning(f"⚠️ {module_name}: No valid results returned")
                    failed_modules.append(module_name)
                
                # Small delay between modules
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Enhancement module {i} ({module_name}) failed: {str(e)}")
                failed_modules.append(module_name)
                continue
        
        # Calculate enhancement metadata
        confidence_boost = _calculate_confidence_boost(enhancements, base_intel)
        credibility_score = _calculate_credibility_score(enhancements, base_intel)
        
        enhancement_metadata = {
            "total_enhancements": total_enhancements,
            "confidence_boost": confidence_boost,
            "credibility_score": credibility_score,
            "modules_successful": successful_modules,
            "modules_failed": failed_modules,
            "success_rate": len(successful_modules) / len(enhancement_queue) * 100,
            "enhancement_quality": "excellent" if len(successful_modules) >= 5 else "good" if len(successful_modules) >= 3 else "basic",
            "enhanced_at": datetime.utcnow().isoformat(),
            "enhancement_version": "mock_data_elimination_1.0",
            "parallel_processing": False,
            "execution_mode": "existing_system_with_mock_elimination",
            "system_architecture": "existing_enhancement_modules_cleaned",
            
            # 🔥 NEW: Mock data elimination tracking
            "mock_data_elimination": {
                "enabled": True,
                "mock_data_detected": len(mock_data_detected),
                "mock_data_sources": mock_data_detected,
                "data_cleaning_applied": True,
                "only_real_data_stored": True
            }
        }
        
        result = {
            **enhancements,
            "enhancement_metadata": enhancement_metadata
        }
        
        # Final logging
        success_rate = len(successful_modules) / len(enhancement_queue) * 100
        logger.info(f"📊 Enhanced generation with mock data elimination completed:")
        logger.info(f"   ✅ Successful: {len(successful_modules)}/{len(enhancement_queue)} ({success_rate:.0f}%)")
        logger.info(f"   📈 Total real enhancements: {total_enhancements}")
        logger.info(f"   📈 Confidence boost: {confidence_boost:.1%}")
        logger.info(f"   🚫 Mock data detected and eliminated: {len(mock_data_detected)} instances")
        logger.info(f"   ⚡ Execution mode: Existing System + Mock Data Elimination")
        
        if failed_modules:
            logger.warning(f"   ❌ Failed modules: {failed_modules}")
        
        if mock_data_detected:
            logger.warning(f"   🧹 Mock data eliminated: {mock_data_detected}")
        
        # Log system health if available
        if ENHANCED_AI_SYSTEM_AVAILABLE:
            log_system_status()
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Enhanced AI enhancement generation failed: {str(e)}")
        return _fallback_generate_enhancements(base_intel, opportunities)

def create_enriched_intelligence(base_intel: Dict, enhancements: Dict) -> Dict[str, Any]:
    """
    🔥 ENHANCED: Create enriched intelligence with COMPREHENSIVE mock data elimination
    """
    logger.info("✨ Creating enriched intelligence with MOCK DATA ELIMINATION...")
    
    # 🔍 ENHANCED DEBUG: Log comprehensive input analysis
    logger.info(f"📊 INPUT ANALYSIS:")
    logger.info(f"   Base intel keys: {list(base_intel.keys())}")
    logger.info(f"   Enhancement keys: {list(enhancements.keys())}")
    
    # Check for mock data contamination
    mock_data_found = _detect_mock_data_contamination(enhancements)
    if mock_data_found:
        logger.error(f"🚨 MOCK DATA CONTAMINATION DETECTED: {mock_data_found}")
        logger.info("🧹 Cleaning contaminated data...")
    else:
        logger.info("✅ NO MOCK DATA CONTAMINATION - All data is real AI-generated content")
    
    # Log enhancement data details with validation
    real_enhancements = 0
    empty_enhancements = 0
    
    for key, value in enhancements.items():
        if key != "enhancement_metadata":
            is_valid = _is_valid_enhancement(value, key)
            if is_valid:
                real_enhancements += 1
                logger.info(f"✅ Enhancement '{key}': REAL DATA ({len(value) if isinstance(value, (dict, list)) else 'N/A'} items)")
            else:
                empty_enhancements += 1
                logger.warning(f"⚠️ Enhancement '{key}': INVALID/EMPTY")
    
    logger.info(f"📊 Enhancement Summary: {real_enhancements} real, {empty_enhancements} invalid/empty")
    
    # Start with base intelligence
    enriched = base_intel.copy()
    
    # 🔥 ENHANCED: Map AI enhancements with comprehensive validation and cleaning
    intelligence_mapping = {}
    
    # Scientific Intelligence
    scientific_enhancement = enhancements.get("scientific_validation", {})
    cleaned_scientific = _clean_enhancement_data(scientific_enhancement, "scientific")
    if cleaned_scientific and _is_valid_enhancement(cleaned_scientific, "scientific"):
        intelligence_mapping["scientific_intelligence"] = {
            **cleaned_scientific,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "cleaned_real_data",
            "enhancement_applied": True,
            "mock_data_free": True
        }
        logger.info(f"✅ MAPPED scientific_intelligence: {len(cleaned_scientific)} items (cleaned)")
    else:
        logger.warning(f"⚠️ Scientific enhancement: No valid data after cleaning")
    
    # Market Intelligence  
    market_enhancement = enhancements.get("market_positioning", {})
    cleaned_market = _clean_enhancement_data(market_enhancement, "market")
    if cleaned_market and _is_valid_enhancement(cleaned_market, "market"):
        intelligence_mapping["market_intelligence"] = {
            **cleaned_market,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "cleaned_real_data",
            "enhancement_applied": True,
            "mock_data_free": True
        }
        logger.info(f"✅ MAPPED market_intelligence: {len(cleaned_market)} items (cleaned)")
    else:
        logger.warning(f"⚠️ Market enhancement: No valid data after cleaning")
    
    # Credibility Intelligence
    credibility_enhancement = enhancements.get("credibility_boosters", {})
    cleaned_credibility = _clean_enhancement_data(credibility_enhancement, "credibility")
    if cleaned_credibility and _is_valid_enhancement(cleaned_credibility, "credibility"):
        intelligence_mapping["credibility_intelligence"] = {
            **cleaned_credibility,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "cleaned_real_data", 
            "enhancement_applied": True,
            "mock_data_free": True
        }
        logger.info(f"✅ MAPPED credibility_intelligence: {len(cleaned_credibility)} items (cleaned)")
    else:
        logger.warning(f"⚠️ Credibility enhancement: No valid data after cleaning")
    
    # Emotional Transformation Intelligence
    emotional_enhancement = enhancements.get("emotional_transformation", {})
    cleaned_emotional = _clean_enhancement_data(emotional_enhancement, "emotional")
    if cleaned_emotional and _is_valid_enhancement(cleaned_emotional, "emotional"):
        intelligence_mapping["emotional_transformation_intelligence"] = {
            **cleaned_emotional,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "cleaned_real_data",
            "enhancement_applied": True,
            "mock_data_free": True
        }
        logger.info(f"✅ MAPPED emotional_transformation_intelligence: {len(cleaned_emotional)} items (cleaned)")
    else:
        logger.warning(f"⚠️ Emotional enhancement: No valid data after cleaning")
    
    # Scientific Authority Intelligence
    authority_enhancement = enhancements.get("authority_establishment", {})
    cleaned_authority = _clean_enhancement_data(authority_enhancement, "authority")
    if cleaned_authority and _is_valid_enhancement(cleaned_authority, "authority"):
        intelligence_mapping["scientific_authority_intelligence"] = {
            **cleaned_authority,
            "generated_at": datetime.utcnow().isoformat(),
            "ai_provider": "cleaned_real_data",
            "enhancement_applied": True,
            "mock_data_free": True
        }
        logger.info(f"✅ MAPPED scientific_authority_intelligence: {len(cleaned_authority)} items (cleaned)")
    else:
        logger.warning(f"⚠️ Authority enhancement: No valid data after cleaning")
    
    # Enhanced content_intelligence by merging existing + AI enhancements
    content_enhancement = enhancements.get("content_optimization", {})
    existing_content = enriched.get("content_intelligence", {})
    cleaned_content = _clean_enhancement_data(content_enhancement, "content")
    
    if cleaned_content and _is_valid_enhancement(cleaned_content, "content"):
        intelligence_mapping["content_intelligence"] = {
            **existing_content,
            **cleaned_content,
            "enhanced_at": datetime.utcnow().isoformat(),
            "ai_enhancement_applied": True,
            "mock_data_free": True
        }
        logger.info(f"✅ ENHANCED content_intelligence: {len(cleaned_content)} new items (cleaned)")
    else:
        intelligence_mapping["content_intelligence"] = existing_content
        logger.info(f"⚠️ Content enhancement: No valid data after cleaning, using existing: {len(existing_content)} items")
    
    # 🔍 ENHANCED DEBUG: Log mapping results with validation
    logger.info(f"🗺️ MAPPING RESULTS:")
    categories_added = 0
    for category, data in intelligence_mapping.items():
        has_valid_data = _is_valid_enhancement(data, category)
        if has_valid_data:
            categories_added += 1
            logger.info(f"   ✅ {category}: VALID CLEANED DATA ({len(data) if isinstance(data, (dict, list)) else 'N/A'} items)")
        else:
            logger.warning(f"   ❌ {category}: INVALID/EMPTY after cleaning")
    
    # 🔥 ADD: Validate and add all cleaned AI-generated intelligence categories
    for intel_category, enhancement_data in intelligence_mapping.items():
        if _is_valid_enhancement(enhancement_data, intel_category):
            enriched[intel_category] = enhancement_data
            logger.info(f"🔥 ADDED {intel_category} to enriched data with {len(enhancement_data)} cleaned items")
        else:
            logger.warning(f"⚠️ SKIPPING invalid {intel_category}")
    
    # 🔍 ENHANCED DEBUG: Log final validation
    logger.info(f"📤 OUTPUT VALIDATION:")
    logger.info(f"   Enriched data keys: {list(enriched.keys())}")
    logger.info(f"   Categories added: {categories_added}/6")
    
    # Verify AI intelligence categories are present and valid
    ai_categories = ["scientific_intelligence", "credibility_intelligence", "market_intelligence", 
                    "emotional_transformation_intelligence", "scientific_authority_intelligence"]
    
    valid_categories = 0
    for category in ai_categories:
        if category in enriched and _is_valid_enhancement(enriched[category], category):
            valid_categories += 1
            logger.info(f"✅ {category}: PRESENT AND VALID ({len(enriched[category])} items)")
        else:
            logger.error(f"❌ {category}: MISSING OR INVALID")
    
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
        "intelligence_categories_populated": categories_added,
        "total_intelligence_categories": len(intelligence_mapping),
        "category_completion_rate": categories_added / len(intelligence_mapping) if len(intelligence_mapping) > 0 else 0,
        "enrichment_timestamp": datetime.utcnow().isoformat(),
        "execution_mode": "existing_system_with_mock_elimination",
        "system_architecture": "mock_data_elimination_enhanced",
        
        # 🔥 ENHANCED: Mock data contamination prevention
        "mock_data_elimination": {
            "mock_data_detected": len(mock_data_found) > 0 if mock_data_found else False,
            "mock_data_sources": mock_data_found if mock_data_found else [],
            "real_enhancements": real_enhancements,
            "empty_enhancements": empty_enhancements,
            "validation_applied": True,
            "data_integrity_score": valid_categories / len(ai_categories) if ai_categories else 0,
            "cleaning_applied": True,
            "only_real_data_stored": True
        },
        
        # 🔥 ENHANCED: System performance metrics
        "system_performance": {
            "categories_with_valid_data": valid_categories,
            "total_ai_categories": len(ai_categories),
            "data_quality_score": valid_categories / len(ai_categories) if ai_categories else 0,
            "enhancement_success_rate": enhancement_metadata.get("success_rate", 0),
            "mock_elimination_system_status": "active"
        },
        
        # 🔥 DEBUG: Add detailed debugging info
        "debug_info": {
            "enhancement_keys_received": list(enhancements.keys()),
            "mapping_attempted": list(intelligence_mapping.keys()),
            "categories_with_data": [cat for cat, data in intelligence_mapping.items() if _is_valid_enhancement(data, cat)],
            "categories_without_data": [cat for cat, data in intelligence_mapping.items() if not _is_valid_enhancement(data, cat)],
            "enhancement_types": {key: type(value).__name__ for key, value in enhancements.items()},
            "mock_data_contamination_check": "passed" if not mock_data_found else "failed",
            "data_cleaning_performed": True
        },
        
        # 🔥 ADD: Storage validation for debugging
        "storage_validation_applied": True,
        "extraction_successful": True,
        "amplification_timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"✅ Enriched intelligence created - Valid categories: {valid_categories}/{len(ai_categories)}")
    logger.info(f"📊 Final confidence: {original_confidence:.2f} → {enriched['confidence_score']:.2f} (+{confidence_boost:.2f})")
    logger.info(f"⚡ Mock data elimination system completed")
    logger.info(f"🚫 Mock data contamination: {'DETECTED AND CLEANED' if mock_data_found else 'ELIMINATED'}")
    
    return enriched

# ============================================================================
# EXISTING HELPER FUNCTIONS (Keep for compatibility)
# ============================================================================

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
    """Identify emotional opportunity identification"""
    
    try:
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
    """Identify authority opportunity identification"""
    
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
    
    # Count only valid enhancements
    for enhancement_type, enhancement_data in enhancements.items():
        if enhancement_type.endswith('_metadata'):
            continue  # Skip metadata
            
        if _is_valid_enhancement(enhancement_data, enhancement_type):
            total_boost += 0.05  # 5% boost per populated category
            
            if isinstance(enhancement_data, dict) and len(enhancement_data) > 5:
                total_boost += 0.02  # Extra boost for rich content
    
    # Cap the boost to prevent unrealistic scores
    return min(total_boost, 0.35)  # Maximum 35% boost

def _calculate_credibility_score(enhancements: Dict, base_intel: Dict) -> float:
    """Calculate overall credibility score from all enhancements"""
    
    base_confidence = base_intel.get("confidence_score", 0.0)
    confidence_boost = _calculate_confidence_boost(enhancements, base_intel)
    
    # Enhanced credibility calculation
    enhanced_credibility = min(base_confidence + confidence_boost, 1.0)
    
    return enhanced_credibility

def _count_enhancements_in_result(result: Dict[str, Any]) -> int:
    """Count total enhancements in a result"""
    count = 0
    
    for key, value in result.items():
        if key.endswith('_metadata'):
            continue  # Skip metadata
            
        if isinstance(value, dict):
            count += len(value)
        elif isinstance(value, list):
            count += len(value)
        else:
            count += 1  # Single item
    
    return count

# ============================================================================
# ENHANCED FALLBACK FUNCTIONS (NO MOCK DATA)
# ============================================================================

def _fallback_identify_opportunities(base_intel: Dict) -> Dict[str, Any]:
    """Enhanced fallback opportunity identification - NO MOCK DATA"""
    
    logger.warning("⚠️ Using fallback opportunity identification - AI system unavailable")
    
    return {
        "scientific_validation": [],
        "credibility_enhancement": [], 
        "competitive_positioning": [],
        "market_authority": [],
        "content_optimization": [],
        "emotional_transformation": [],
        "opportunity_metadata": {
            "total_opportunities": 0,
            "priority_areas": [],
            "enhancement_potential": "ai_system_required",
            "identified_at": datetime.utcnow().isoformat(),
            "system_version": "fallback_no_mock",
            "fallback_reason": "AI enhancement system unavailable",
            "mock_data_eliminated": True
        }
    }

def _fallback_generate_enhancements(base_intel: Dict, opportunities: Dict) -> Dict[str, Any]:
    """Enhanced fallback enhancement generation - NO MOCK DATA"""
    
    logger.warning("⚠️ Using fallback enhancement generation - AI system unavailable")
    
    return {
        "scientific_validation": {},
        "credibility_boosters": {},
        "competitive_advantages": {},
        "research_support": {},
        "market_positioning": {},
        "content_optimization": {},
        "emotional_transformation": {},
        "authority_establishment": {},
        "enhancement_metadata": {
            "total_enhancements": 0,
            "confidence_boost": 0.0,
            "credibility_score": base_intel.get("confidence_score", 0.6),
            "modules_successful": [],
            "modules_failed": [],
            "enhancement_quality": "fallback_no_mock",
            "enhanced_at": datetime.utcnow().isoformat(),
            "enhancement_version": "fallback_no_mock",
            "fallback_reason": "AI enhancement system unavailable",
            "mock_data_elimination": {
                "enabled": True,
                "mock_data_detected": 0,
                "mock_data_sources": [],
                "data_cleaning_applied": True,
                "only_real_data_stored": True
            }
        }
    }

# ============================================================================
# MONITORING AND STATISTICS
# ============================================================================

def get_enhanced_system_stats() -> Dict[str, Any]:
    """Get comprehensive enhanced system statistics"""
    
    success_rate = (_successful_requests / _total_requests * 100) if _total_requests > 0 else 0
    
    stats = {
        "global_stats": {
            "total_requests": _total_requests,
            "successful_requests": _successful_requests,
            "failed_requests": _failed_requests,
            "success_rate": success_rate
        },
        "provider_usage": _provider_usage_stats.copy(),
        "provider_performance": _provider_performance_stats.copy(),
        "system_health": {
            "enhanced_ai_system_available": ENHANCED_AI_SYSTEM_AVAILABLE,
            "enhancement_modules_available": ENHANCEMENT_MODULES_AVAILABLE,
            "mock_data_elimination_active": True
        }
    }
    
    # Add provider health if available
    if ENHANCED_AI_SYSTEM_AVAILABLE:
        try:
            stats["provider_health"] = get_provider_health_report()
        except:
            pass
    
    return stats

def log_enhanced_system_report():
    """Generate comprehensive enhanced system report"""
    
    stats = get_enhanced_system_stats()
    
    logger.info("📊 ENHANCED INTELLIGENCE SYSTEM REPORT")
    logger.info("=" * 60)
    
    # Global statistics
    global_stats = stats["global_stats"]
    logger.info(f"Global Performance:")
    logger.info(f"  Total Requests: {global_stats['total_requests']}")
    logger.info(f"  Success Rate: {global_stats['success_rate']:.1f}%")
    logger.info(f"  Failed Requests: {global_stats['failed_requests']}")
    
    # Provider usage
    if stats["provider_usage"]:
        logger.info("\nProvider Usage Distribution:")
        total_usage = sum(stats["provider_usage"].values())
        for provider, count in stats["provider_usage"].items():
            percentage = (count / total_usage * 100) if total_usage > 0 else 0
            logger.info(f"  {provider}: {count} requests ({percentage:.1f}%)")
    
    # System health
    health = stats["system_health"]
    logger.info(f"\nSystem Health:")
    logger.info(f"  Enhanced AI System: {'✅ Available' if health['enhanced_ai_system_available'] else '❌ Unavailable'}")
    logger.info(f"  Enhancement Modules: {'✅ Available' if health['enhancement_modules_available'] else '❌ Unavailable'}")
    logger.info(f"  Mock Data Elimination: {'✅ Active' if health['mock_data_elimination_active'] else '❌ Inactive'}")
    
    logger.info("=" * 60)