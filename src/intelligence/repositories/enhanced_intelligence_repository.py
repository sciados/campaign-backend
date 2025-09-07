# =====================================
# File: src/intelligence/repositories/enhanced_intelligence_repository.py
# =====================================

"""
Enhanced Intelligence Repository with Complete Data Storage

Extends the existing repository to store the complete 12,000+ character
intelligence data while maintaining the normalized structure.
"""

import logging
import json
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select, update
from datetime import datetime
import uuid

from src.core.database.models import IntelligenceCore, ProductData, MarketData
from ..models.intelligence_models import ProductInfo, MarketInfo

logger = logging.getLogger(__name__)


class EnhancedIntelligenceRepository:
    """Enhanced repository for storing complete intelligence with normalized data."""
    
    async def create_complete_intelligence_with_full_data(
        self,
        source_url: str,
        product_name: str,
        user_id: str,
        company_id: Optional[str],
        analysis_method: str,
        confidence_score: float,
        product_info: ProductInfo,
        market_info: MarketInfo,
        full_intelligence_data: Dict[str, Any],  # NEW: Complete intelligence storage
        session: AsyncSession
    ) -> IntelligenceCore:
        """
        Store complete intelligence with both normalized and full data.
        
        This method stores:
        1. Normalized data in separate tables (ProductData, MarketData)
        2. Complete intelligence JSON in intelligence_core.full_analysis_data
        
        Args:
            source_url: Source URL analyzed
            product_name: Extracted product name
            user_id: User who requested analysis
            company_id: Optional company ID
            analysis_method: Analysis method used (fast/deep/enhanced)
            confidence_score: Analysis confidence score
            product_info: Normalized product information
            market_info: Normalized market information
            full_intelligence_data: Complete intelligence data (12,000+ chars)
            session: Database session
            
        Returns:
            IntelligenceCore: Created intelligence record
        """
        try:
            # Step 1: Create main intelligence record with complete data
            intelligence_id = str(uuid.uuid4())
            
            # First, check if we need to add the full_analysis_data column
            await self._ensure_full_data_column_exists(session)
            
            intelligence = IntelligenceCore(
                id=intelligence_id,
                product_name=product_name,
                source_url=source_url,
                confidence_score=confidence_score,
                analysis_method=analysis_method,
                user_id=user_id,
                company_id=company_id
            )
            
            session.add(intelligence)
            await session.flush()  # Get the ID
            
            # Step 2: Store complete intelligence data in JSONB column
            await self._store_complete_intelligence_data(
                intelligence_id=intelligence_id,
                full_data=full_intelligence_data,
                session=session
            )
            
            # Step 3: Store normalized product data
            product_data = ProductData(
                id=str(uuid.uuid4()),
                intelligence_id=intelligence_id,
                features=product_info.features,
                benefits=product_info.benefits,
                ingredients=product_info.ingredients,
                conditions=product_info.conditions,
                usage_instructions=product_info.usage_instructions
            )
            session.add(product_data)
            
            # Step 4: Store normalized market data  
            market_data = MarketData(
                id=str(uuid.uuid4()),
                intelligence_id=intelligence_id,
                category=market_info.category,
                positioning=market_info.positioning,
                competitive_advantages=market_info.competitive_advantages,
                target_audience=market_info.target_audience
            )
            session.add(market_data)
            
            await session.flush()
            
            # Log storage success with data sizes
            intelligence_size = len(str(full_intelligence_data))
            logger.info(f"Stored complete intelligence record:")
            logger.info(f"  - Intelligence ID: {intelligence_id}")
            logger.info(f"  - Product: {product_name}")
            logger.info(f"  - Method: {analysis_method}")
            logger.info(f"  - Confidence: {confidence_score:.3f}")
            logger.info(f"  - Complete data size: {intelligence_size:,} characters")
            logger.info(f"  - Product features: {len(product_info.features)}")
            logger.info(f"  - Market advantages: {len(market_info.competitive_advantages)}")
            
            return intelligence
            
        except Exception as e:
            logger.error(f"Failed to store complete intelligence: {e}")
            await session.rollback()
            raise
    
    async def _ensure_full_data_column_exists(self, session: AsyncSession) -> None:
        """Ensure the full_analysis_data JSONB column exists in intelligence_core."""
        try:
            # Check if column exists by trying to select it
            result = await session.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name='intelligence_core' AND column_name='full_analysis_data'")
            )
            column_exists = result.scalar()
            
            if not column_exists:
                logger.info("Adding full_analysis_data column to intelligence_core table")
                await session.execute(
                    text("ALTER TABLE intelligence_core ADD COLUMN full_analysis_data JSONB")
                )
                await session.commit()
                logger.info("Successfully added full_analysis_data column")
            
        except Exception as e:
            logger.warning(f"Could not check/add full_analysis_data column: {e}")
            # Continue without the column - will store only normalized data
    
    async def _store_complete_intelligence_data(
        self,
        intelligence_id: str,
        full_data: Dict[str, Any],
        session: AsyncSession
    ) -> None:
        """Store complete intelligence data in JSONB column."""
        try:
            # Clean the data for JSON storage
            clean_data = self._prepare_data_for_json_storage(full_data)
            
            # Update the intelligence record with complete data
            await session.execute(
                text("UPDATE intelligence_core SET full_analysis_data = :full_data WHERE id = :id"),
                {"id": intelligence_id, "full_data": json.dumps(clean_data)}
            )
            
            logger.info(f"Stored {len(str(clean_data)):,} characters of complete intelligence data")
            
        except Exception as e:
            logger.error(f"Failed to store complete intelligence data: {e}")
            # Don't fail the entire operation - normalized data is still stored
    
    def _prepare_data_for_json_storage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare intelligence data for JSON storage by handling datetime objects."""
        try:
            # Convert datetime objects to ISO strings
            clean_data = {}
            
            for key, value in data.items():
                if isinstance(value, datetime):
                    clean_data[key] = value.isoformat()
                elif isinstance(value, dict):
                    clean_data[key] = self._clean_dict_for_json(value)
                elif isinstance(value, list):
                    clean_data[key] = self._clean_list_for_json(value)
                else:
                    clean_data[key] = value
            
            return clean_data
            
        except Exception as e:
            logger.warning(f"Error preparing data for JSON storage: {e}")
            # Return original data and let JSON serialization handle it
            return data
    
    def _clean_dict_for_json(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively clean dictionary for JSON storage."""
        clean_dict = {}
        for key, value in d.items():
            if isinstance(value, datetime):
                clean_dict[key] = value.isoformat()
            elif isinstance(value, dict):
                clean_dict[key] = self._clean_dict_for_json(value)
            elif isinstance(value, list):
                clean_dict[key] = self._clean_list_for_json(value)
            else:
                clean_dict[key] = value
        return clean_dict
    
    def _clean_list_for_json(self, lst: list) -> list:
        """Recursively clean list for JSON storage."""
        clean_list = []
        for item in lst:
            if isinstance(item, datetime):
                clean_list.append(item.isoformat())
            elif isinstance(item, dict):
                clean_list.append(self._clean_dict_for_json(item))
            elif isinstance(item, list):
                clean_list.append(self._clean_list_for_json(item))
            else:
                clean_list.append(item)
        return clean_list
    
    async def get_complete_intelligence_by_id(
        self,
        intelligence_id: str,
        session: AsyncSession
    ) -> Optional[Dict[str, Any]]:
        """Retrieve complete intelligence data including full analysis."""
        try:
            # Get basic intelligence record
            result = await session.execute(
                select(IntelligenceCore).where(IntelligenceCore.id == intelligence_id)
            )
            intelligence = result.scalar_one_or_none()
            
            if not intelligence:
                return None
            
            # Try to get complete data
            try:
                full_data_result = await session.execute(
                    text("SELECT full_analysis_data FROM intelligence_core WHERE id = :id"),
                    {"id": intelligence_id}
                )
                full_data_row = full_data_result.fetchone()
                full_analysis_data = full_data_row[0] if full_data_row and full_data_row[0] else None
            except Exception as e:
                logger.warning(f"Could not retrieve full analysis data: {e}")
                full_analysis_data = None
            
            # Build complete response
            complete_data = {
                "intelligence_id": intelligence.id,
                "product_name": intelligence.product_name,
                "source_url": intelligence.source_url,
                "confidence_score": intelligence.confidence_score,
                "analysis_method": intelligence.analysis_method,
                "created_at": intelligence.created_at,
                "full_analysis_data": full_analysis_data,
                "has_complete_data": full_analysis_data is not None,
                "complete_data_size": len(str(full_analysis_data)) if full_analysis_data else 0
            }
            
            return complete_data
            
        except Exception as e:
            logger.error(f"Failed to retrieve complete intelligence: {e}")
            return None
    
    async def get_intelligence_stats(self, session: AsyncSession) -> Dict[str, Any]:
        """Get statistics about stored intelligence data."""
        try:
            # Get total records
            total_result = await session.execute(
                text("SELECT COUNT(*) FROM intelligence_core")
            )
            total_records = total_result.scalar()
            
            # Get records with complete data
            complete_data_result = await session.execute(
                text("SELECT COUNT(*) FROM intelligence_core WHERE full_analysis_data IS NOT NULL")
            )
            complete_data_records = complete_data_result.scalar()
            
            # Get average data sizes
            avg_size_result = await session.execute(
                text("""
                    SELECT 
                        AVG(COALESCE(LENGTH(full_analysis_data::text), 0)) as avg_complete_size,
                        MAX(COALESCE(LENGTH(full_analysis_data::text), 0)) as max_complete_size
                    FROM intelligence_core 
                    WHERE full_analysis_data IS NOT NULL
                """)
            )
            avg_size_row = avg_size_result.fetchone()
            avg_complete_size = int(avg_size_row[0]) if avg_size_row and avg_size_row[0] else 0
            max_complete_size = int(avg_size_row[1]) if avg_size_row and avg_size_row[1] else 0
            
            # Get recent analysis methods
            methods_result = await session.execute(
                text("""
                    SELECT analysis_method, COUNT(*) as count
                    FROM intelligence_core
                    WHERE created_at > NOW() - INTERVAL '7 days'
                    GROUP BY analysis_method
                """)
            )
            recent_methods = {row[0]: row[1] for row in methods_result.fetchall()}
            
            return {
                "total_records": total_records,
                "complete_data_records": complete_data_records,
                "complete_data_percentage": (complete_data_records / total_records * 100) if total_records > 0 else 0,
                "avg_complete_size_chars": avg_complete_size,
                "max_complete_size_chars": max_complete_size,
                "recent_analysis_methods": recent_methods,
                "data_quality_status": "healthy" if complete_data_records > 0 else "needs_attention"
            }
            
        except Exception as e:
            logger.error(f"Failed to get intelligence stats: {e}")
            return {
                "total_records": 0,
                "complete_data_records": 0,
                "error": str(e)
            }
    
    async def search_intelligence_by_product(
        self,
        product_name: str,
        user_id: str,
        limit: int = 10,
        session: AsyncSession = None
    ) -> list:
        """Search intelligence records by product name."""
        try:
            result = await session.execute(
                select(IntelligenceCore)
                .where(
                    IntelligenceCore.product_name.ilike(f"%{product_name}%"),
                    IntelligenceCore.user_id == user_id
                )
                .order_by(IntelligenceCore.created_at.desc())
                .limit(limit)
            )
            
            records = result.scalars().all()
            
            # Convert to dictionaries for easier handling
            search_results = []
            for record in records:
                search_results.append({
                    "intelligence_id": record.id,
                    "product_name": record.product_name,
                    "source_url": record.source_url,
                    "confidence_score": record.confidence_score,
                    "analysis_method": record.analysis_method,
                    "created_at": record.created_at
                })
            
            return search_results
            
        except Exception as e:
            logger.error(f"Failed to search intelligence by product: {e}")
            return []
    
    async def get_user_intelligence_summary(
        self,
        user_id: str,
        session: AsyncSession
    ) -> Dict[str, Any]:
        """Get summary of intelligence data for a specific user."""
        try:
            # Get user's total records
            total_result = await session.execute(
                text("SELECT COUNT(*) FROM intelligence_core WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            total_records = total_result.scalar()
            
            # Get user's records with complete data
            complete_result = await session.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM intelligence_core 
                    WHERE user_id = :user_id AND full_analysis_data IS NOT NULL
                """),
                {"user_id": user_id}
            )
            complete_records = complete_result.scalar()
            
            # Get user's recent analysis methods
            methods_result = await session.execute(
                text("""
                    SELECT analysis_method, COUNT(*) as count
                    FROM intelligence_core
                    WHERE user_id = :user_id 
                    AND created_at > NOW() - INTERVAL '30 days'
                    GROUP BY analysis_method
                """),
                {"user_id": user_id}
            )
            recent_methods = {row[0]: row[1] for row in methods_result.fetchall()}
            
            # Get user's average confidence scores
            confidence_result = await session.execute(
                text("""
                    SELECT AVG(confidence_score) as avg_confidence
                    FROM intelligence_core
                    WHERE user_id = :user_id
                """),
                {"user_id": user_id}
            )
            avg_confidence = confidence_result.scalar() or 0.0
            
            return {
                "user_id": user_id,
                "total_intelligence_records": total_records,
                "complete_data_records": complete_records,
                "complete_data_percentage": (complete_records / total_records * 100) if total_records > 0 else 0,
                "recent_analysis_methods": recent_methods,
                "average_confidence_score": float(avg_confidence),
                "data_quality": "good" if complete_records > 0 else "limited"
            }
            
        except Exception as e:
            logger.error(f"Failed to get user intelligence summary: {e}")
            return {"error": str(e)}
    
    async def delete_intelligence_record(
        self,
        intelligence_id: str,
        user_id: str,
        session: AsyncSession
    ) -> bool:
        """Delete an intelligence record (with user authorization)."""
        try:
            # Verify the record belongs to the user
            result = await session.execute(
                select(IntelligenceCore).where(
                    IntelligenceCore.id == intelligence_id,
                    IntelligenceCore.user_id == user_id
                )
            )
            intelligence = result.scalar_one_or_none()
            
            if not intelligence:
                logger.warning(f"Intelligence {intelligence_id} not found or not owned by user {user_id}")
                return False
            
            # Delete the record (cascading deletes will handle related data)
            await session.delete(intelligence)
            await session.commit()
            
            logger.info(f"Deleted intelligence record {intelligence_id} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete intelligence record: {e}")
            await session.rollback()
            return False
    
    async def update_intelligence_confidence(
        self,
        intelligence_id: str,
        new_confidence_score: float,
        session: AsyncSession
    ) -> bool:
        """Update confidence score for an intelligence record."""
        try:
            await session.execute(
                text("UPDATE intelligence_core SET confidence_score = :score WHERE id = :id"),
                {"score": new_confidence_score, "id": intelligence_id}
            )
            await session.commit()
            
            logger.info(f"Updated confidence score for {intelligence_id} to {new_confidence_score}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update confidence score: {e}")
            await session.rollback()
            return False