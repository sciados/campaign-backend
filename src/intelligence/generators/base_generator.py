# src/intelligence/generators/base_generator.py
"""
PHASE 2 ENHANCED BASE GENERATOR - CRUD INTEGRATION & STORAGE MANAGEMENT
✅ Applied Phase 1 CRUD patterns for database operations
✅ Integrated UniversalDualStorageManager with quota management
✅ Enhanced product name fixing from Phase 1
✅ Clean architecture with lazy loading to prevent circular imports
💰 Maximizes cost savings while maintaining quality
🔄 Dynamic routing through lazy imports and dependency injection
⚡ Intelligent fallback and error handling
"""

import os
import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from abc import ABC, abstractmethod
from uuid import UUID

# ✅ PHASE 2: Import CRUD integration from Phase 1
from src.core.crud.intelligence_crud import IntelligenceCRUD
from src.core.crud.campaign_crud import CampaignCRUD

# ✅ PHASE 2: Import storage system with quota management
try:
    from src.storage.universal_dual_storage import UniversalDualStorageManager
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ UniversalDualStorageManager not available, continuing without storage integration")
    UniversalDualStorageManager = None

# ✅ PHASE 2: Import product name utilities from Phase 1
try:
    from src.intelligence.utils.product_name_extractor import (
        extract_product_name_from_intelligence,
        get_product_details_summary
    )
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Product name extractor not available, using fallback")
    def extract_product_name_from_intelligence(data):
        return data.get("source_title", "this product")
    def get_product_details_summary(data):
        return {"name": "Default Product"}

try:
    from src.intelligence.utils.product_name_fix import (
        substitute_placeholders_in_data,
        validate_no_placeholders
    )
except ImportError:
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ Product name fix utilities not available, using fallback")
    def substitute_placeholders_in_data(data, product_name, fallback):
        return data
    def validate_no_placeholders(text, product_name):
        return True

logger = logging.getLogger(__name__)

class BaseContentGenerator(ABC):
    """✅ PHASE 2: Enhanced base class with CRUD integration and storage management"""
    
    def __init__(self, generator_type: str):
        self.generator_type = generator_type
        self.generation_id = str(uuid.uuid4())[:8]
        
        # ✅ PHASE 2: Initialize CRUD systems (injected by factory)
        self.intelligence_crud = None  # Will be injected by factory
        self.campaign_crud = None      # Will be injected by factory
        self.storage = None            # Will be injected by factory
        self.db = None                 # Will be injected by factory
        
        # Lazy-loaded dependencies (prevents circular imports)
        self._dynamic_router = None
        self._smart_router = None
        self._ultra_cheap_provider = None
        
        # Enhanced cost tracking with real-time optimization
        self.cost_tracker = {
            "total_requests": 0,
            "total_cost": 0.0,
            "savings_vs_expensive": 0.0,
            "provider_distribution": {},
            "optimization_decisions": [],
            "session_start": datetime.now(timezone.utc),
            # ✅ PHASE 2: Add storage and CRUD metrics
            "storage_operations": 0,
            "storage_quota_checks": 0,
            "crud_operations": 0,
            "database_writes": 0,
            "product_name_fixes": 0
        }
        
        logger.info(f"✅ Phase 2 {generator_type} Generator - Enhanced with CRUD & storage integration")
    
    # ✅ PHASE 2: CRUD integration methods
    async def _prepare_intelligence_data_with_crud(
        self, 
        campaign_id: str, 
        user_id: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """✅ PHASE 2: Prepare intelligence data using CRUD with Phase 1 patterns"""
        
        if not self.intelligence_crud or not self.db:
            logger.warning("⚠️ CRUD not available, using fallback intelligence preparation")
            return {"source_title": "Default Product", "campaign_id": campaign_id}
        
        try:
            # Get intelligence sources using CRUD with company security
            intelligence_sources = await self.intelligence_crud.get_campaign_intelligence(
                db=self.db,
                campaign_id=UUID(campaign_id),
                company_id=UUID(company_id) if company_id else None,
                include_content_stats=True
            )
            
            # ✅ PHASE 2: Track CRUD operation
            self.cost_tracker["crud_operations"] += 1
            
            # ✅ PHASE 2: Extract product name using Phase 1 centralized extractor
            actual_product_name = "this product"  # Generic fallback
            
            if intelligence_sources and len(intelligence_sources) > 0:
                first_source = intelligence_sources[0]
                if hasattr(first_source, 'source_title') and first_source.source_title:
                    actual_product_name = first_source.source_title.strip()
                    logger.info(f"🎯 Using source_title from CRUD: '{actual_product_name}'")
            
            # Prepare intelligence data structure with CORRECT product name
            intelligence_data = {
                "campaign_id": campaign_id,
                "user_id": user_id,
                "company_id": company_id,
                "source_title": actual_product_name,  # ✅ PHASE 2: Direct source title
                "target_audience": "individuals seeking solutions",
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
                        "brand_intelligence": self._serialize_enum_field(source.brand_intelligence)
                    }
                    intelligence_data["intelligence_sources"].append(source_data)
                    
                    # Merge into aggregate intelligence
                    for intel_type in ["offer_intelligence", "psychology_intelligence", "content_intelligence", "competitive_intelligence", "brand_intelligence"]:
                        self._merge_intelligence_category(intelligence_data, source_data, intel_type)
                        
                except Exception as source_error:
                    logger.warning(f"⚠️ Error processing source {source.id}: {str(source_error)}")
                    continue
            
            # ✅ PHASE 2: Apply Phase 1 product name fixes
            fixed_intelligence_data = await self._apply_phase1_product_fixes(intelligence_data)
            
            logger.info(f"✅ CRUD prepared intelligence data: {len(intelligence_data['intelligence_sources'])} sources")
            return fixed_intelligence_data
            
        except Exception as e:
            logger.error(f"❌ CRUD intelligence preparation failed: {e}")
            # Fallback to basic intelligence data
            return {
                "campaign_id": campaign_id,
                "user_id": user_id,
                "company_id": company_id,
                "source_title": "Default Product",
                "crud_error": str(e),
                "fallback_used": True
            }
    
    async def _apply_phase1_product_fixes(self, intelligence_data: Dict[str, Any]) -> Dict[str, Any]:
        """✅ PHASE 2: Apply Phase 1 product name fixing patterns"""
        try:
            # Extract product name using centralized Phase 1 utilities
            product_name = extract_product_name_from_intelligence(intelligence_data)
            
            # Apply placeholder substitutions to intelligence data
            fixed_data = substitute_placeholders_in_data(intelligence_data, product_name, product_name)
            
            # Validate no placeholders remain
            if not validate_no_placeholders(str(fixed_data), product_name):
                logger.warning(f"⚠️ Some placeholders may remain in intelligence data for {product_name}")
            
            # Ensure source_title is set correctly
            fixed_data["source_title"] = product_name
            fixed_data["product_name_source"] = "phase1_extraction"
            fixed_data["phase2_enhanced"] = True
            
            # ✅ PHASE 2: Track product name fixes
            self.cost_tracker["product_name_fixes"] += 1
            
            logger.info(f"✅ Applied Phase 1 product fixes for '{product_name}'")
            return fixed_data
            
        except Exception as e:
            logger.warning(f"⚠️ Phase 1 product fixes failed: {e}, using original data")
            return intelligence_data
    
    async def _store_generated_content_with_crud(
        self,
        result: Dict[str, Any],
        content_type: str,
        campaign_id: Optional[str] = None,
        user_id: Optional[str] = None,
        company_id: Optional[str] = None,
        intelligence_data: Optional[Dict[str, Any]] = None,
        intelligence_id: Optional[str] = None
    ):
        """✅ PHASE 2: Store generated content using CRUD with intelligence attribution"""
        
        if not self.intelligence_crud or not self.db:
            logger.warning("⚠️ CRUD not available, skipping content storage")
            return
        
        try:
            # Prepare content data for storage with intelligence attribution
            content_data = {
                "campaign_id": UUID(campaign_id) if campaign_id else None,
                "user_id": UUID(user_id) if user_id else None,
                "company_id": UUID(company_id) if company_id else None,
                "content_type": content_type,
                "content_data": result,
                "source_intelligence": intelligence_data or {},
                "generation_metadata": result.get("metadata", {}),
                "generated_at": datetime.now(timezone.utc),
                "generator_type": self.generator_type,
                "generation_id": self.generation_id,
                # ✅ PHASE 2: Add intelligence attribution
                "intelligence_id": UUID(intelligence_id) if intelligence_id else None
            }
            
            # Store using intelligence CRUD
            stored_content = await self.intelligence_crud.create_generated_content(
                db=self.db,
                content_data=content_data
            )
            
            # ✅ PHASE 2: Track CRUD operation
            self.cost_tracker["crud_operations"] += 1
            self.cost_tracker["database_writes"] += 1
            
            logger.info(f"✅ Stored {content_type} content with CRUD: {stored_content.id}")
            
            # Add storage reference to result metadata
            if "metadata" not in result:
                result["metadata"] = {}
            result["metadata"]["stored_content_id"] = str(stored_content.id)
            result["metadata"]["crud_stored"] = True
            
        except Exception as e:
            logger.error(f"❌ Failed to store content with CRUD: {e}")
            # Don't fail the generation, just log the storage issue
    
    # ✅ PHASE 2: Storage integration methods
    async def _check_storage_quota_before_generation(
        self, 
        user_id: str, 
        estimated_size_mb: float = 1.0
    ) -> Dict[str, Any]:
        """✅ PHASE 2: Check storage quota before generation"""
        
        if not self.storage:
            logger.warning("⚠️ Storage system not available, allowing generation")
            return {"allowed": True, "reason": "storage_system_unavailable"}
        
        try:
            # ✅ PHASE 2: Track quota check
            self.cost_tracker["storage_quota_checks"] += 1
            
            # Check current usage and quota
            quota_info = await self.storage.get_user_quota(user_id) if hasattr(self.storage, 'get_user_quota') else {
                "used_mb": 0.0, "limit_mb": 1000.0
            }
            
            available_mb = quota_info["limit_mb"] - quota_info["used_mb"]
            allowed = available_mb >= estimated_size_mb
            
            quota_result = {
                "allowed": allowed,
                "used_mb": quota_info["used_mb"],
                "limit_mb": quota_info["limit_mb"],
                "available_mb": available_mb,
                "required_mb": estimated_size_mb,
                "quota_check_performed": True
            }
            
            if not allowed:
                logger.warning(f"⚠️ Storage quota exceeded for user {user_id}: {available_mb:.1f}MB available, {estimated_size_mb:.1f}MB required")
            
            return quota_result
            
        except Exception as e:
            logger.warning(f"⚠️ Storage quota check failed: {e}")
            return {"allowed": True, "error": str(e), "fallback_allowed": True}
    
    async def _store_file_content_with_storage(
        self,
        content: Any,
        user_id: str,
        filename: str,
        content_type: str = "application/octet-stream"
    ) -> Optional[str]:
        """✅ PHASE 2: Store file content using storage system"""
        
        if not self.storage:
            logger.warning("⚠️ Storage system not available, skipping file storage")
            return None
        
        try:
            # ✅ PHASE 2: Track storage operation
            self.cost_tracker["storage_operations"] += 1
            
            # Convert content to bytes if needed
            if isinstance(content, str):
                content_bytes = content.encode('utf-8')
            elif isinstance(content, bytes):
                content_bytes = content
            else:
                logger.warning(f"⚠️ Unsupported content type for storage: {type(content)}")
                return None
            
            # Check quota before upload
            content_size_mb = len(content_bytes) / 1024 / 1024
            quota_check = await self._check_storage_quota_before_generation(user_id, content_size_mb)
            
            if not quota_check["allowed"]:
                logger.warning(f"⚠️ Storage upload blocked by quota: {quota_check}")
                return None
            
            # Upload using storage system
            stored_url = await self.storage.upload(user_id, content_bytes, filename)
            
            if stored_url:
                # Update usage if supported
                if hasattr(self.storage, 'update_usage'):
                    await self.storage.update_usage(user_id, len(content_bytes))
                
                logger.info(f"✅ Stored file: {filename} ({content_size_mb:.2f}MB) -> {stored_url}")
                return stored_url
            else:
                logger.warning(f"⚠️ Storage upload failed for {filename}")
                return None
                
        except Exception as e:
            logger.error(f"❌ File storage failed: {e}")
            return None
    
    # Existing dynamic AI methods with Phase 2 enhancements...
    async def _get_dynamic_router(self):
        """Lazy load dynamic router to prevent circular imports"""
        if self._dynamic_router is None:
            try:
                # Import only when needed
                from ..adapters.dynamic_router import get_dynamic_router
                self._dynamic_router = await get_dynamic_router()
                logger.debug(f"🔄 Dynamic router loaded for {self.generator_type}")
            except ImportError as e:
                logger.warning(f"⚠️ Dynamic router not available: {e}")
                self._dynamic_router = False  # Mark as unavailable
        return self._dynamic_router if self._dynamic_router is not False else None
    
    async def _get_smart_router(self):
        """Lazy load smart router to prevent circular imports"""
        if self._smart_router is None:
            try:
                # Import only when needed
                from ..utils.smart_router import get_smart_router
                self._smart_router = get_smart_router()
                logger.debug(f"🔄 Smart router loaded for {self.generator_type}")
            except ImportError as e:
                logger.warning(f"⚠️ Smart router not available: {e}")
                self._smart_router = False  # Mark as unavailable
        return self._smart_router if self._smart_router is not False else None
    
    async def _get_ultra_cheap_provider(self):
        """Lazy load ultra cheap provider to prevent circular imports"""
        if self._ultra_cheap_provider is None:
            try:
                # Import only when needed
                from ..utils.ultra_cheap_ai_provider import UltraCheapAIProvider
                self._ultra_cheap_provider = UltraCheapAIProvider()
                logger.debug(f"🔄 Ultra cheap provider loaded for {self.generator_type}")
            except ImportError as e:
                logger.warning(f"⚠️ Ultra cheap provider not available: {e}")
                self._ultra_cheap_provider = False  # Mark as unavailable
        return self._ultra_cheap_provider if self._ultra_cheap_provider is not False else None
    
    async def _generate_with_dynamic_ai(
        self,
        content_type: str,
        prompt: str,
        system_message: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3,
        task_complexity: str = "standard",
        user_id: Optional[str] = None,
        storage_estimate_mb: float = 0.0
    ) -> Dict[str, Any]:
        """✅ PHASE 2: Enhanced generation with storage quota checking"""
        
        start_time = time.time()
        
        # ✅ PHASE 2: Check storage quota if needed
        if user_id and storage_estimate_mb > 0:
            quota_check = await self._check_storage_quota_before_generation(user_id, storage_estimate_mb)
            if not quota_check["allowed"]:
                return {
                    "success": False,
                    "error": "Storage quota exceeded",
                    "quota_info": quota_check
                }
        
        # Try dynamic router first
        dynamic_router = await self._get_dynamic_router()
        if dynamic_router:
            try:
                result = await self._generate_with_dynamic_router(
                    dynamic_router, content_type, prompt, system_message, 
                    max_tokens, temperature, task_complexity
                )
                
                if result.get("success"):
                    generation_time = time.time() - start_time
                    self._track_generation_metrics(result, generation_time)
                    
                    # ✅ PHASE 2: Add Phase 2 metadata
                    result["metadata"] = result.get("metadata", {})
                    result["metadata"]["phase2_enhanced"] = True
                    result["metadata"]["crud_available"] = bool(self.intelligence_crud)
                    result["metadata"]["storage_available"] = bool(self.storage)
                    
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Dynamic router failed: {e}")
        
        # Try smart router fallback
        smart_router = await self._get_smart_router()
        if smart_router:
            try:
                result = await self._generate_with_smart_router(
                    smart_router, prompt, system_message, max_tokens, temperature
                )
                
                if result.get("success"):
                    generation_time = time.time() - start_time
                    self._track_generation_metrics(result, generation_time)
                    
                    # ✅ PHASE 2: Add Phase 2 metadata
                    result["metadata"] = result.get("metadata", {})
                    result["metadata"]["phase2_enhanced"] = True
                    result["metadata"]["crud_available"] = bool(self.intelligence_crud)
                    result["metadata"]["storage_available"] = bool(self.storage)
                    
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Smart router failed: {e}")
        
        # Try ultra cheap provider fallback
        ultra_cheap = await self._get_ultra_cheap_provider()
        if ultra_cheap:
            try:
                result = await self._generate_with_ultra_cheap(
                    ultra_cheap, prompt, system_message, max_tokens, temperature
                )
                
                if result.get("success"):
                    generation_time = time.time() - start_time
                    self._track_generation_metrics(result, generation_time)
                    
                    # ✅ PHASE 2: Add Phase 2 metadata
                    result["metadata"] = result.get("metadata", {})
                    result["metadata"]["phase2_enhanced"] = True
                    result["metadata"]["crud_available"] = bool(self.intelligence_crud)
                    result["metadata"]["storage_available"] = bool(self.storage)
                    
                    return result
                    
            except Exception as e:
                logger.warning(f"⚠️ Ultra cheap provider failed: {e}")
        
        # Final fallback to static generation
        return await self._fallback_static_generation(prompt, system_message, max_tokens, temperature)
    
    # Rest of the existing methods remain the same...
    async def _generate_with_dynamic_router(
        self, 
        router, 
        content_type: str, 
        prompt: str, 
        system_message: str,
        max_tokens: int,
        temperature: float,
        task_complexity: str
    ) -> Dict[str, Any]:
        """Generate using dynamic router"""
        
        # Define generation function for the router
        async def generation_function(provider_context: Dict[str, Any], **kwargs) -> str:
            client = provider_context["client"]
            model = provider_context["model"]
            provider_name = provider_context["provider_name"]
            
            # Route to appropriate provider implementation
            return await self._call_provider(provider_name, client, model, prompt, system_message, max_tokens, temperature)
        
        # Execute with optimal provider
        result, metadata = await router.execute_with_optimal_provider(
            content_type=content_type,
            generation_function=generation_function,
            task_complexity=task_complexity,
            prompt=prompt,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        estimated_cost = self._estimate_cost(result, metadata["provider_used"])
        
        return {
            "success": True,
            "content": result,
            "provider_used": metadata["provider_used"],
            "cost": estimated_cost,
            "quality_score": 85,
            "generation_time": 0,
            "optimization_metadata": {
                "selection_reason": metadata["selection_reason"],
                "fallback_used": metadata["fallback_used"],
                "dynamic_routing": True,
                "content_type": content_type,
                "task_complexity": task_complexity
            }
        }
    
    async def _generate_with_smart_router(
        self, 
        router, 
        prompt: str, 
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate using smart router"""
        
        try:
            result = await router.route_request(
                prompt=prompt,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature,
                routing_params={
                    "content_type": "text",
                    "cost_priority": 0.9,
                    "quality_threshold": 0.75,
                    "speed_priority": 0.8
                }
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "content": result["content"],
                    "provider_used": result.get("provider_used", "smart_router"),
                    "cost": result.get("cost", 0.001),
                    "quality_score": 80,
                    "optimization_metadata": {
                        "smart_routing": True,
                        "routing_optimization": result.get("routing_optimization", {})
                    }
                }
        except Exception as e:
            logger.error(f"Smart router error: {e}")
        
        return {"success": False, "error": "Smart router failed"}
    
    async def _generate_with_ultra_cheap(
        self, 
        provider, 
        prompt: str, 
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Generate using ultra cheap provider"""
        
        try:
            result = await provider.generate_text(
                prompt=prompt,
                system_message=system_message,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "content": result["content"],
                    "provider_used": result.get("provider", "ultra_cheap"),
                    "cost": result.get("cost", 0.001),
                    "quality_score": 75,
                    "optimization_metadata": {
                        "ultra_cheap": True,
                        "cost_optimization": result.get("cost_optimization", {})
                    }
                }
        except Exception as e:
            logger.error(f"Ultra cheap provider error: {e}")
        
        return {"success": False, "error": "Ultra cheap provider failed"}
    
    # Provider calling methods remain the same...
    async def _call_provider(
        self, 
        provider_name: str, 
        client, 
        model: str, 
        prompt: str, 
        system_message: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Call specific provider (implement specific logic per provider)"""
        
        if provider_name == "groq":
            return await self._call_groq(client, model, prompt, system_message, max_tokens, temperature)
        elif provider_name == "deepseek":
            return await self._call_openai_compatible(client, model, prompt, system_message, max_tokens, temperature)
        elif provider_name == "together":
            return await self._call_openai_compatible(client, model, prompt, system_message, max_tokens, temperature)
        elif provider_name == "anthropic":
            return await self._call_anthropic(client, model, prompt, system_message, max_tokens, temperature)
        else:
            raise ValueError(f"Unsupported provider: {provider_name}")
    
    async def _call_groq(self, client, model: str, prompt: str, system_message: str, max_tokens: int, temperature: float) -> str:
        """Call Groq API"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    async def _call_openai_compatible(self, client, model: str, prompt: str, system_message: str, max_tokens: int, temperature: float) -> str:
        """Call OpenAI-compatible APIs (DeepSeek, Together)"""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
        
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return response.choices[0].message.content
    
    async def _call_anthropic(self, client, model: str, prompt: str, system_message: str, max_tokens: int, temperature: float) -> str:
        """Call Anthropic API"""
        full_prompt = f"{system_message}\n\n{prompt}" if system_message else prompt
        
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": full_prompt}]
        )
        
        return response.content[0].text
    
    async def _fallback_static_generation(self, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Dict[str, Any]:
        """Fallback to static provider selection when all routing fails"""
        logger.warning("🔄 Using static fallback generation")
        
        # Try providers in order of preference from Railway environment
        fallback_providers = [
            ("groq", "GROQ_API_KEY"),
            ("deepseek", "DEEPSEEK_API_KEY"),
            ("together", "TOGETHER_API_KEY"),
            ("anthropic", "ANTHROPIC_API_KEY")
        ]
        
        for provider_name, env_key in fallback_providers:
            api_key = os.getenv(env_key)
            if api_key:
                try:
                    # Basic provider call without circular imports
                    result_content = await self._basic_provider_call(provider_name, api_key, prompt, system_message, max_tokens, temperature)
                    
                    if result_content:
                        return {
                            "success": True,
                            "content": result_content,
                            "provider_used": provider_name,
                            "cost": 0.001,
                            "quality_score": 70,
                            "generation_time": 2.0,
                            "optimization_metadata": {
                                "fallback_used": True,
                                "fallback_reason": "All dynamic routing failed",
                                "phase2_enhanced": True
                            }
                        }
                        
                except Exception as e:
                    logger.warning(f"⚠️ Fallback provider {provider_name} failed: {e}")
                    continue
        
        # Final emergency fallback
        return {
            "success": False,
            "content": f"Emergency fallback content for {self.generator_type} - all providers failed",
            "provider_used": "emergency_fallback",
            "cost": 0.0,
            "quality_score": 30,
            "generation_time": 0.1,
            "optimization_metadata": {
                "fallback_used": True,
                "fallback_reason": "All providers failed",
                "phase2_enhanced": True
            }
        }
    
    async def _basic_provider_call(self, provider_name: str, api_key: str, prompt: str, system_message: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Basic provider call without any dependencies"""
        
        if provider_name == "groq":
            try:
                import groq
                client = groq.AsyncGroq(api_key=api_key)
                return await self._call_groq(client, "llama-3.3-70b-versatile", prompt, system_message, max_tokens, temperature)
            except ImportError:
                logger.warning("Groq not available")
                
        elif provider_name == "deepseek":
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=api_key, base_url="https://api.deepseek.com")
                return await self._call_openai_compatible(client, "deepseek-chat", prompt, system_message, max_tokens, temperature)
            except ImportError:
                logger.warning("OpenAI client not available for DeepSeek")
        
        elif provider_name == "together":
            try:
                import openai
                client = openai.AsyncOpenAI(api_key=api_key, base_url="https://api.together.xyz/v1")
                return await self._call_openai_compatible(client, "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo", prompt, system_message, max_tokens, temperature)
            except ImportError:
                logger.warning("OpenAI client not available for Together")
                
        elif provider_name == "anthropic":
            try:
                import anthropic
                client = anthropic.AsyncAnthropic(api_key=api_key)
                return await self._call_anthropic(client, "claude-sonnet-4-20250514", prompt, system_message, max_tokens, temperature)
            except ImportError:
                logger.warning("Anthropic client not available")
        
        return None
    
    def _estimate_cost(self, content: str, provider_used: str) -> float:
        """Estimate generation cost based on content and provider"""
        # Rough token estimation
        token_count = len(content.split()) * 1.3
        
        # Cost per 1K tokens based on Railway providers
        cost_rates = {
            "groq": 0.00013,
            "deepseek": 0.00089,
            "together": 0.0008,
            "anthropic": 0.009,
            "ultra_cheap": 0.0005,
            "smart_router": 0.0007,
            "emergency_fallback": 0.0
        }
        
        rate = cost_rates.get(provider_used, 0.001)
        return (token_count / 1000) * rate
    
    def _track_generation_metrics(self, result: Dict[str, Any], generation_time: float):
        """✅ PHASE 2: Enhanced generation metrics tracking"""
        self.cost_tracker["total_requests"] += 1
        self.cost_tracker["total_cost"] += result.get("cost", 0)
        
        provider_used = result.get("provider_used", "unknown")
        if provider_used not in self.cost_tracker["provider_distribution"]:
            self.cost_tracker["provider_distribution"][provider_used] = {
                "count": 0,
                "total_cost": 0.0,
                "avg_time": 0.0
            }
        
        provider_stats = self.cost_tracker["provider_distribution"][provider_used]
        provider_stats["count"] += 1
        provider_stats["total_cost"] += result.get("cost", 0)
        provider_stats["avg_time"] = (provider_stats["avg_time"] * (provider_stats["count"] - 1) + generation_time) / provider_stats["count"]
    
    async def get_optimization_analytics(self) -> Dict[str, Any]:
        """✅ PHASE 2: Enhanced analytics with CRUD and storage metrics"""
        
        # Calculate session statistics
        session_duration = (datetime.now(timezone.utc) - self.cost_tracker["session_start"]).total_seconds() / 3600
        
        total_requests = self.cost_tracker["total_requests"]
        if total_requests > 0:
            avg_cost_per_request = self.cost_tracker["total_cost"] / total_requests
            expensive_cost_per_request = 0.030  # OpenAI rate
            estimated_savings = (expensive_cost_per_request - avg_cost_per_request) * total_requests
        else:
            estimated_savings = 0
        
        return {
            "session_info": {
                "generator_type": self.generator_type,
                "session_duration_hours": round(session_duration, 2),
                "total_requests": total_requests,
                "enhanced_routing_enabled": True,
                "phase2_enhanced": True,
                "crud_integration": bool(self.intelligence_crud),
                "storage_integration": bool(self.storage)
            },
            "cost_optimization": {
                "total_cost": round(self.cost_tracker["total_cost"], 4),
                "average_cost_per_request": round(avg_cost_per_request, 4) if total_requests > 0 else 0,
                "estimated_savings": round(estimated_savings, 4),
                "savings_percentage": round((estimated_savings / (estimated_savings + self.cost_tracker["total_cost"])) * 100, 1) if estimated_savings > 0 else 0
            },
            "provider_distribution": self.cost_tracker["provider_distribution"],
            "optimization_decisions": self.cost_tracker["optimization_decisions"][-10:],  # Last 10 decisions
            # ✅ PHASE 2: Add new metrics
            "phase2_metrics": {
                "storage_operations": self.cost_tracker["storage_operations"],
                "storage_quota_checks": self.cost_tracker["storage_quota_checks"],
                "crud_operations": self.cost_tracker["crud_operations"],
                "database_writes": self.cost_tracker["database_writes"],
                "product_name_fixes": self.cost_tracker["product_name_fixes"]
            },
            "system_integration": {
                "crud_available": bool(self.intelligence_crud and self.campaign_crud),
                "storage_available": bool(self.storage),
                "database_session": bool(self.db)
            }
        }
    
    def _create_enhanced_response(
        self, 
        content: Dict[str, Any],
        title: str,
        product_name: str,
        ai_result: Dict[str, Any],
        preferences: Dict[str, Any] = None,
        campaign_id: Optional[str] = None,
        user_id: Optional[str] = None,
        company_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """✅ PHASE 2: Enhanced response creation with CRUD and storage metadata"""
        
        if preferences is None:
            preferences = {}
        
        return {
            "content_type": self.generator_type,
            "title": title,
            "content": content,
            "metadata": {
                "generated_by": f"phase2_enhanced_{self.generator_type}_generator",
                "product_name": product_name,
                "content_type": self.generator_type,
                "generation_id": self.generation_id,
                "generated_at": datetime.now(timezone.utc),
                "preferences_used": preferences,
                "campaign_id": campaign_id,
                "user_id": user_id,
                "company_id": company_id,
                "ai_optimization": {
                    "provider_used": ai_result.get("provider_used"),
                    "generation_cost": ai_result.get("cost", 0.0),
                    "quality_score": ai_result.get("quality_score", 0),
                    "generation_time": ai_result.get("generation_time", 0.0),
                    "enhanced_routing_enabled": True,
                    "optimization_metadata": ai_result.get("optimization_metadata", {}),
                    "fallback_used": ai_result.get("optimization_metadata", {}).get("fallback_used", False)
                },
                # ✅ PHASE 2: Add integration status
                "system_integration": {
                    "phase2_enhanced": True,
                    "crud_integration": bool(self.intelligence_crud),
                    "storage_integration": bool(self.storage),
                    "product_name_fixes_applied": True,
                    "database_tracking": bool(self.db)
                },
                "generator_version": "3.0.0-phase2-crud-storage-enhanced"
            }
        }
    
    # Utility methods for enum serialization and intelligence processing
    def _serialize_enum_field(self, field_value):
        """Serialize enum fields to prevent issues"""
        if hasattr(field_value, 'value'):
            return field_value.value
        elif isinstance(field_value, dict):
            return {k: self._serialize_enum_field(v) for k, v in field_value.items()}
        elif isinstance(field_value, list):
            return [self._serialize_enum_field(item) for item in field_value]
        else:
            return field_value
    
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
    
    @abstractmethod
    async def generate_content(self, intelligence_data: Dict[str, Any], preferences: Dict[str, Any] = None) -> Dict[str, Any]:
        """Abstract method for content generation - must be implemented by subclasses"""
        pass


# 🔧 CRITICAL FIX: Add BaseGenerator alias for backward compatibility
BaseGenerator = BaseContentGenerator


# ✅ PHASE 2: Enhanced integration adapter with CRUD and storage
class Phase2RoutingMixin:
    """✅ PHASE 2: Mixin to add enhanced routing with CRUD and storage to existing generators"""
    
    async def _call_ultra_cheap_ai_with_phase2_routing(
        self,
        prompt: str,
        intelligence: Dict[str, Any],
        content_type: str = "text",
        system_message: str = "",
        max_tokens: int = 2000,
        temperature: float = 0.3,
        task_complexity: str = "standard",
        user_id: Optional[str] = None,
        campaign_id: Optional[str] = None,
        company_id: Optional[str] = None,
        storage_estimate_mb: float = 0.0
    ) -> Dict[str, Any]:
        """✅ PHASE 2: Enhanced AI calling with CRUD and storage integration"""
        
        # Get enhanced base generator instance if not exists
        if not hasattr(self, '_phase2_generator'):
            self._phase2_generator = BaseContentGenerator(
                getattr(self, 'generator_type', 'content')
            )
            
            # ✅ PHASE 2: Inject CRUD and storage dependencies if available
            if hasattr(self, 'intelligence_crud'):
                self._phase2_generator.intelligence_crud = self.intelligence_crud
            if hasattr(self, 'campaign_crud'):
                self._phase2_generator.campaign_crud = self.campaign_crud
            if hasattr(self, 'storage'):
                self._phase2_generator.storage = self.storage
            if hasattr(self, 'db'):
                self._phase2_generator.db = self.db
        
        # ✅ PHASE 2: Apply Phase 1 product fixes before generation
        fixed_intelligence = await self._phase2_generator._apply_phase1_product_fixes(intelligence)
        
        # Use enhanced routing for generation with storage check
        result = await self._phase2_generator._generate_with_dynamic_ai(
            content_type=content_type,
            prompt=prompt,
            system_message=system_message,
            max_tokens=max_tokens,
            temperature=temperature,
            task_complexity=task_complexity,
            user_id=user_id,
            storage_estimate_mb=storage_estimate_mb
        )
        
        # ✅ PHASE 2: Store generated content if successful and CRUD available
        if result.get("success") and campaign_id:
            await self._phase2_generator._store_generated_content_with_crud(
                result=result,
                content_type=content_type,
                campaign_id=campaign_id,
                user_id=user_id,
                company_id=company_id,
                intelligence_data=fixed_intelligence
            )
        
        return result


# ✅ PHASE 2: Enhanced convenience functions for easy migration
async def enhance_existing_generator_with_phase2(generator_instance, intelligence_crud=None, storage=None, db=None):
    """✅ PHASE 2: Enhance existing generator with Phase 2 capabilities"""
    
    # Add Phase 2 routing mixin
    class Phase2Generator(generator_instance.__class__, Phase2RoutingMixin):
        pass
    
    # Create enhanced instance
    enhanced = Phase2Generator()
    
    # Copy existing attributes
    for attr_name in dir(generator_instance):
        if not attr_name.startswith('_') and not callable(getattr(generator_instance, attr_name)):
            setattr(enhanced, attr_name, getattr(generator_instance, attr_name))
    
    # ✅ PHASE 2: Inject CRUD and storage dependencies
    if intelligence_crud:
        enhanced.intelligence_crud = intelligence_crud
    if storage:
        enhanced.storage = storage
    if db:
        enhanced.db = db
    
    logger.info(f"✅ Enhanced {generator_instance.__class__.__name__} with Phase 2 capabilities")
    return enhanced

def inject_phase2_dependencies(generator_instance, intelligence_crud=None, campaign_crud=None, storage=None, db=None):
    """✅ PHASE 2: Inject Phase 2 dependencies into existing generator"""
    
    if intelligence_crud:
        generator_instance.intelligence_crud = intelligence_crud
    if campaign_crud:
        generator_instance.campaign_crud = campaign_crud
    if storage:
        generator_instance.storage = storage
    if db:
        generator_instance.db = db
    
    # Add Phase 2 tracking if not exists
    if not hasattr(generator_instance, 'cost_tracker'):
        generator_instance.cost_tracker = {
            "storage_operations": 0,
            "storage_quota_checks": 0,
            "crud_operations": 0,
            "database_writes": 0,
            "product_name_fixes": 0
        }
    
    logger.info(f"✅ Injected Phase 2 dependencies into {generator_instance.__class__.__name__}")

async def create_phase2_content_with_full_integration(
    generator_type: str,
    intelligence_data: Dict[str, Any],
    preferences: Dict[str, Any] = None,
    user_id: Optional[str] = None,
    campaign_id: Optional[str] = None,
    company_id: Optional[str] = None,
    intelligence_crud=None,
    storage=None,
    db=None
) -> Dict[str, Any]:
    """✅ PHASE 2: Create content with full Phase 2 integration"""
    
    # Create base generator with Phase 2 capabilities
    generator = BaseContentGenerator(generator_type)
    
    # Inject dependencies
    inject_phase2_dependencies(generator, intelligence_crud, None, storage, db)
    
    # Prepare intelligence data with CRUD
    if campaign_id and company_id:
        enhanced_intelligence = await generator._prepare_intelligence_data_with_crud(
            campaign_id=campaign_id,
            user_id=user_id,
            company_id=company_id
        )
    else:
        enhanced_intelligence = await generator._apply_phase1_product_fixes(intelligence_data)
    
    # Generate content (this would need to be implemented per generator type)
    # For now, return a placeholder that shows Phase 2 integration
    result = {
        "content_type": generator_type,
        "title": f"Phase 2 Enhanced {generator_type.title()}",
        "content": {
            "generated_with_phase2": True,
            "intelligence_data_enhanced": True,
            "product_name": enhanced_intelligence.get("source_title", "Default Product"),
            "note": "This is a Phase 2 enhanced content generation result"
        }
    }
    
    # Store content if CRUD available
    if campaign_id:
        await generator._store_generated_content_with_crud(
            result=result,
            content_type=generator_type,
            campaign_id=campaign_id,
            user_id=user_id,
            company_id=company_id,
            intelligence_data=enhanced_intelligence
        )
    
    return generator._create_enhanced_response(
        content=result["content"],
        title=result["title"],
        product_name=enhanced_intelligence.get("source_title", "Default Product"),
        ai_result={"success": True, "provider_used": "phase2_integration", "cost": 0.0},
        preferences=preferences,
        campaign_id=campaign_id,
        user_id=user_id,
        company_id=company_id
    )

# ✅ PHASE 2: Health check for Phase 2 integration
async def check_phase2_integration_health(
    intelligence_crud=None,
    storage=None,
    db=None
) -> Dict[str, Any]:
    """Check health of Phase 2 integration components"""
    
    health_report = {
        "phase2_integration": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {}
    }
    
    # Check CRUD health
    if intelligence_crud:
        try:
            # Simple health check - could be expanded
            health_report["components"]["intelligence_crud"] = {
                "status": "available",
                "type": str(type(intelligence_crud).__name__)
            }
        except Exception as e:
            health_report["components"]["intelligence_crud"] = {
                "status": "error",
                "error": str(e)
            }
    else:
        health_report["components"]["intelligence_crud"] = {"status": "not_available"}
    
    # Check storage health
    if storage:
        try:
            storage_health = await storage.health_check() if hasattr(storage, 'health_check') else {"status": "unknown"}
            health_report["components"]["storage"] = {
                "status": "available",
                "type": str(type(storage).__name__),
                "health_check": storage_health
            }
        except Exception as e:
            health_report["components"]["storage"] = {
                "status": "error",
                "error": str(e)
            }
    else:
        health_report["components"]["storage"] = {"status": "not_available"}
    
    # Check database session
    if db:
        try:
            health_report["components"]["database"] = {
                "status": "available",
                "session_active": True
            }
        except Exception as e:
            health_report["components"]["database"] = {
                "status": "error",
                "error": str(e)
            }
    else:
        health_report["components"]["database"] = {"status": "not_available"}
    
    # Overall health assessment
    available_components = sum(1 for comp in health_report["components"].values() if comp["status"] == "available")
    total_components = len(health_report["components"])
    
    health_report["summary"] = {
        "available_components": available_components,
        "total_components": total_components,
        "integration_percentage": round((available_components / total_components) * 100, 1),
        "fully_integrated": available_components == total_components
    }
    
    return health_report

# Backward compatibility aliases
DynamicRoutingMixin = Phase2RoutingMixin  # For backward compatibility