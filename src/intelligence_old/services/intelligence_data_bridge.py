# =====================================
# File: src/intelligence/services/intelligence_data_bridge.py
# =====================================

"""
Intelligence Data Bridge for New Schema Compatibility

This module bridges the gap between the original enhancers (which expect old data formats)
and the new database schema with consolidated intelligence storage.

CRITICAL: This ensures the 6 original enhancers can read/write to the new table structure.
"""

import logging
import json
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from src.core.database.models import IntelligenceCore, ProductData, MarketData, KnowledgeBase
from src.intelligence.repositories.enhanced_intelligence_repository import EnhancedIntelligenceRepository

logger = logging.getLogger(__name__)


class IntelligenceDataBridge:
    """
    Bridge between original enhancers and new database schema.
    
    Provides compatibility layer so the 6 original enhancers can:
    1. Read intelligence data from new consolidated schema
    2. Update intelligence data in new schema format
    3. Maintain backward compatibility with enhancer expectations
    """
    
    def __init__(self):
        self.enhanced_repo = EnhancedIntelligenceRepository()
    
    async def get_intelligence_for_enhancers(
        self,
        intelligence_id: str,
        session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve intelligence data in format expected by original enhancers.
        
        Converts new schema data back to the format the enhancers expect,
        allowing them to work without modification.
        
        Args:
            intelligence_id: Intelligence record ID
            session: Database session
            
        Returns:
            Dict in format expected by original enhancers, or None if not found
        """
        try:
            # Get complete intelligence data from new schema
            complete_data = await self.enhanced_repo.get_complete_intelligence_by_id(
                intelligence_id, session
            )
            
            if not complete_data:
                logger.warning(f"No intelligence found for ID: {intelligence_id}")
                return None
            
            # If we have complete analysis data, use it
            full_analysis = complete_data.get("full_analysis_data")
            if full_analysis:
                logger.info(f"Retrieved complete analysis data ({len(str(full_analysis)):,} chars)")
                return full_analysis
            
            # Fallback: reconstruct from normalized data
            logger.info("No complete data found, reconstructing from normalized data")
            reconstructed_data = await self._reconstruct_from_normalized_data(
                intelligence_id, session
            )
            
            return reconstructed_data
            
        except Exception as e:
            logger.error(f"Failed to get intelligence for enhancers: {e}")
            return None
    
    async def _reconstruct_from_normalized_data(
        self,
        intelligence_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Reconstruct intelligence from normalized tables."""
        try:
            # Get core intelligence
            core_result = await session.execute(
                select(IntelligenceCore).where(IntelligenceCore.id == intelligence_id)
            )
            core = core_result.scalar_one_or_none()
            
            if not core:
                return {}
            
            # Get product data
            product_result = await session.execute(
                select(ProductData).where(ProductData.intelligence_id == intelligence_id)
            )
            product_data = product_result.scalar_one_or_none()
            
            # Get market data
            market_result = await session.execute(
                select(MarketData).where(MarketData.intelligence_id == intelligence_id)
            )
            market_data = market_result.scalar_one_or_none()
            
            # Reconstruct in expected format
            reconstructed = {
                "offer_intelligence": {
                    "products": [core.product_name],
                    "key_features": product_data.features if product_data else [],
                    "primary_benefits": product_data.benefits if product_data else [],
                    "ingredients": product_data.ingredients if product_data else [],
                    "conditions": product_data.conditions if product_data else [],
                    "usage_instructions": product_data.usage_instructions if product_data else [],
                    "value_propositions": []
                },
                "psychology_intelligence": {
                    "target_audience": market_data.target_audience if market_data else "",
                    "emotional_triggers": [],
                    "persuasion_techniques": []
                },
                "competitive_intelligence": {
                    "competitive_advantages": market_data.competitive_advantages if market_data else [],
                    "market_positioning": market_data.positioning if market_data else "",
                    "category": market_data.category if market_data else ""
                },
                "content_intelligence": {
                    "key_messages": [],
                    "call_to_actions": []
                },
                "brand_intelligence": {
                    "brand_voice": "",
                    "brand_values": [],
                    "credibility_signals": []
                },
                "confidence_score": core.confidence_score
            }
            
            logger.info(f"Reconstructed intelligence from normalized data")
            return reconstructed
            
        except Exception as e:
            logger.error(f"Failed to reconstruct from normalized data: {e}")
            return {}
    
    async def update_intelligence_with_enhancements(
        self,
        intelligence_id: str,
        enhancements: Dict[str, Any],
        session: AsyncSession
    ) -> bool:
        """
        Update intelligence record with enhancement results.
        
        Takes the output from the 6 enhancers and stores it back in the
        new database schema, preserving all the rich intelligence data.
        
        Args:
            intelligence_id: Intelligence record ID
            enhancements: Enhancement data from the 6 enhancers
            session: Database session
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Get existing complete data
            existing_data = await self.enhanced_repo.get_complete_intelligence_by_id(
                intelligence_id, session
            )
            
            if not existing_data:
                logger.error(f"Cannot update intelligence {intelligence_id} - not found")
                return False
            
            # Merge enhancements with existing data
            current_full_data = existing_data.get("full_analysis_data", {})
            
            # Add each enhancement to the complete data
            for enhancement_name, enhancement_data in enhancements.items():
                current_full_data[enhancement_name] = enhancement_data
                logger.info(f"Added {enhancement_name}: {len(str(enhancement_data))} chars")
            
            # Calculate enhanced confidence score
            enhanced_confidence = self._calculate_enhanced_confidence(
                current_full_data, existing_data.get("confidence_score", 0.5)
            )
            
            # Update both complete data and confidence score
            await session.execute(
                text("""
                    UPDATE intelligence_core 
                    SET full_analysis_data = :full_data,
                        confidence_score = :confidence_score
                    WHERE id = :id
                """),
                {
                    "id": intelligence_id,
                    "full_data": json.dumps(current_full_data),
                    "confidence_score": enhanced_confidence
                }
            )
            
            await session.commit()
            
            # Log enhancement success
            total_size = len(str(current_full_data))
            enhancement_count = len([k for k in enhancements.keys() if k.endswith("_enhancement")])
            
            logger.info(f"Intelligence enhancement completed:")
            logger.info(f"  - Intelligence ID: {intelligence_id}")
            logger.info(f"  - Enhancements applied: {enhancement_count}")
            logger.info(f"  - Total data size: {total_size:,} characters")
            logger.info(f"  - Enhanced confidence: {enhanced_confidence:.3f}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update intelligence with enhancements: {e}")
            await session.rollback()
            return False
    
    def _calculate_enhanced_confidence(
        self,
        complete_data: Dict[str, Any],
        base_confidence: float
    ) -> float:
        """Calculate enhanced confidence score based on enhancement success."""
        try:
            # Count successful enhancements
            enhancement_keys = [k for k in complete_data.keys() if k.endswith("_enhancement")]
            successful_enhancements = []
            
            for key in enhancement_keys:
                enhancement = complete_data[key]
                if isinstance(enhancement, dict):
                    # Check if enhancement was successful
                    if (enhancement.get("enhancement_applied") or 
                        enhancement.get("enhancement_confidence", 0) > 0.5 or
                        len(str(enhancement)) > 100):  # Has substantial content
                        successful_enhancements.append(key)
            
            # Calculate confidence boost
            if successful_enhancements:
                success_rate = len(successful_enhancements) / 6  # 6 total enhancers
                confidence_boost = success_rate * 0.25  # Up to 0.25 boost
                enhanced_confidence = min(1.0, base_confidence + confidence_boost)
                
                logger.info(f"Confidence enhancement: {base_confidence:.3f} → {enhanced_confidence:.3f}")
                logger.info(f"Successful enhancers: {len(successful_enhancements)}/6")
                
                return enhanced_confidence
            else:
                logger.warning("No successful enhancements detected")
                return base_confidence
                
        except Exception as e:
            logger.error(f"Error calculating enhanced confidence: {e}")
            return base_confidence
    
    async def get_intelligence_summary(
        self,
        intelligence_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get a summary of intelligence data for monitoring."""
        try:
            complete_data = await self.enhanced_repo.get_complete_intelligence_by_id(
                intelligence_id, session
            )
            
            if not complete_data:
                return {"error": "Intelligence not found"}
            
            full_analysis = complete_data.get("full_analysis_data", {})
            
            # Analyze enhancement status
            enhancement_summary = {}
            total_chars = 0
            
            for key, value in full_analysis.items():
                if key.endswith("_enhancement"):
                    enhancer_name = key.replace("_enhancement", "")
                    char_count = len(str(value))
                    total_chars += char_count
                    
                    status = "success"
                    if isinstance(value, dict):
                        if value.get("fallback_used") or value.get("status") == "failed":
                            status = "fallback"
                        elif value.get("status") == "timeout":
                            status = "timeout"
                    
                    enhancement_summary[enhancer_name] = {
                        "status": status,
                        "chars": char_count
                    }
            
            return {
                "intelligence_id": intelligence_id,
                "product_name": complete_data.get("product_name"),
                "analysis_method": complete_data.get("analysis_method"),
                "confidence_score": complete_data.get("confidence_score"),
                "total_chars": total_chars,
                "complete_data_available": complete_data.get("has_complete_data", False),
                "enhancement_summary": enhancement_summary,
                "created_at": complete_data.get("created_at")
            }
            
        except Exception as e:
            logger.error(f"Failed to get intelligence summary: {e}")
            return {"error": str(e)}
    
    async def cleanup_incomplete_intelligence(self, session: AsyncSession) -> Dict[str, int]:
        """Clean up intelligence records with incomplete data."""
        try:
            # Find records with very small or missing complete data
            result = await session.execute(
                text("""
                    SELECT id, product_name, 
                           COALESCE(LENGTH(full_analysis_data::text), 0) as data_size
                    FROM intelligence_core 
                    WHERE COALESCE(LENGTH(full_analysis_data::text), 0) < 1000
                    AND created_at < NOW() - INTERVAL '1 hour'
                """)
            )
            
            incomplete_records = result.fetchall()
            
            logger.info(f"Found {len(incomplete_records)} incomplete intelligence records")
            
            # For now, just log them - could implement cleanup logic here
            for record in incomplete_records:
                logger.warning(f"Incomplete intelligence: {record[0]} ({record[1]}) - {record[2]} chars")
            
            return {
                "incomplete_found": len(incomplete_records),
                "cleanup_performed": 0  # Could implement actual cleanup
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup incomplete intelligence: {e}")
            return {"error": str(e)}