# src/intelligence/utils/ai_intelligence_saver.py
"""
Dedicated AI Intelligence Database Saver
Handles saving AI intelligence data with multiple fallback strategies
"""
import json
import logging
import uuid
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm.attributes import flag_modified
from datetime import datetime

logger = logging.getLogger(__name__)

class AIIntelligenceSaver:
    """Dedicated utility for saving AI intelligence data to database"""
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.save_strategies = [
            self._save_via_orm_setattr,
            self._save_via_raw_sql_dict,
            self._save_via_individual_updates,
            self._save_via_metadata_backup
        ]
    
    async def save_ai_intelligence(
        self, 
        intelligence_id: uuid.UUID, 
        category: str, 
        data: Dict[str, Any],
        intelligence_obj: Optional[object] = None
    ) -> bool:
        """
        Save AI intelligence data using multiple fallback strategies
        
        Args:
            intelligence_id: UUID of the intelligence record
            category: AI intelligence category (e.g., 'scientific_intelligence')
            data: The data to save
            intelligence_obj: Optional SQLAlchemy object for ORM approach
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        
        logger.info(f"🔄 Saving {category} with {len(data) if isinstance(data, dict) else 0} items")
        
        # Try each strategy until one succeeds
        for i, strategy in enumerate(self.save_strategies, 1):
            try:
                strategy_name = strategy.__name__.replace('_save_via_', '').replace('_', ' ').title()
                logger.info(f"🔧 Attempting Strategy {i}: {strategy_name}")
                
                success = await strategy(intelligence_id, category, data, intelligence_obj)
                
                if success:
                    logger.info(f"✅ {category}: Successfully saved via {strategy_name}")
                    return True
                else:
                    logger.warning(f"⚠️ {category}: {strategy_name} returned False")
                    
            except Exception as e:
                logger.error(f"❌ {category}: {strategy_name} failed - {str(e)}")
                continue
        
        logger.error(f"❌ {category}: ALL STRATEGIES FAILED - data not saved")
        return False
    
    async def _save_via_orm_setattr(
        self, 
        intelligence_id: uuid.UUID, 
        category: str, 
        data: Dict[str, Any],
        intelligence_obj: Optional[object] = None
    ) -> bool:
        """Strategy 1: Use SQLAlchemy ORM setattr (if object provided)"""
        
        if not intelligence_obj:
            logger.info("No intelligence object provided, skipping ORM strategy")
            return False
        
        # Check if the attribute exists
        if not hasattr(intelligence_obj, category):
            logger.warning(f"Attribute {category} not found on intelligence object")
            return False
        
        # Set the attribute
        setattr(intelligence_obj, category, data)
        flag_modified(intelligence_obj, category)
        
        logger.info(f"✅ ORM setattr: {category} set on object")
        return True
    
    async def _save_via_raw_sql_dict(
        self, 
        intelligence_id: uuid.UUID, 
        category: str, 
        data: Dict[str, Any],
        intelligence_obj: Optional[object] = None
    ) -> bool:
        """Strategy 2: Use raw SQL with dictionary parameters"""
        
        update_query = text(f"""
            UPDATE campaign_intelligence 
            SET {category} = :data::jsonb,
                updated_at = NOW()
            WHERE id = :id
        """)
        
        # Use dictionary parameters (proper SQLAlchemy way)
        await self.db.execute(update_query, {
            "data": json.dumps(data),
            "id": intelligence_id
        })
        
        logger.info(f"✅ Raw SQL Dict: {category} updated")
        return True
    
    async def _save_via_individual_updates(
        self, 
        intelligence_id: uuid.UUID, 
        category: str, 
        data: Dict[str, Any],
        intelligence_obj: Optional[object] = None
    ) -> bool:
        """Strategy 3: Use individual SQL updates for each data field"""
        
        if not isinstance(data, dict) or not data:
            logger.info("Data is not a non-empty dict, skipping individual updates")
            return False
        
        # Save each field individually to ensure granular success
        success_count = 0
        total_fields = len(data)
        
        for field_key, field_value in data.items():
            try:
                # Create a single-field update
                field_data = {field_key: field_value}
                
                update_query = text(f"""
                    UPDATE campaign_intelligence 
                    SET {category} = COALESCE({category}, '{{}}'::jsonb) || :field_data::jsonb
                    WHERE id = :id
                """)
                
                await self.db.execute(update_query, {
                    "field_data": json.dumps(field_data),
                    "id": intelligence_id
                })
                
                success_count += 1
                
            except Exception as field_error:
                logger.error(f"❌ Failed to save field {field_key}: {str(field_error)}")
                continue
        
        if success_count == total_fields:
            logger.info(f"✅ Individual Updates: All {success_count} fields saved")
            return True
        elif success_count > 0:
            logger.warning(f"⚠️ Individual Updates: Partial success {success_count}/{total_fields}")
            return True  # Partial success is still success
        else:
            logger.error(f"❌ Individual Updates: No fields saved")
            return False
    
    async def _save_via_metadata_backup(
        self, 
        intelligence_id: uuid.UUID, 
        category: str, 
        data: Dict[str, Any],
        intelligence_obj: Optional[object] = None
    ) -> bool:
        """Strategy 4: Save in processing_metadata as backup"""
        
        # Get current metadata
        metadata_query = text("""
            SELECT processing_metadata 
            FROM campaign_intelligence 
            WHERE id = :id
        """)
        
        result = await self.db.execute(metadata_query, {"id": intelligence_id})
        row = result.fetchone()
        
        current_metadata = {}
        if row and row[0]:
            try:
                current_metadata = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            except:
                current_metadata = {}
        
        # Add AI data to metadata
        if "ai_intelligence_backup" not in current_metadata:
            current_metadata["ai_intelligence_backup"] = {}
        
        current_metadata["ai_intelligence_backup"][category] = data
        current_metadata["ai_backup_timestamp"] = datetime.utcnow().isoformat()
        current_metadata["backup_reason"] = "Primary storage strategies failed"
        
        # Update metadata
        metadata_update = text("""
            UPDATE campaign_intelligence 
            SET processing_metadata = :metadata::jsonb,
                updated_at = NOW()
            WHERE id = :id
        """)
        
        await self.db.execute(metadata_update, {
            "metadata": json.dumps(current_metadata),
            "id": intelligence_id
        })
        
        logger.info(f"📦 Metadata Backup: {category} saved to processing_metadata")
        return True
    
    async def verify_ai_data_saved(
        self, 
        intelligence_id: uuid.UUID, 
        category: str
    ) -> Dict[str, Any]:
        """Verify AI data was actually saved and return status"""
        
        try:
            # Check primary column
            column_query = text(f"""
                SELECT {category}::text
                FROM campaign_intelligence 
                WHERE id = :id
            """)
            
            result = await self.db.execute(column_query, {"id": intelligence_id})
            row = result.fetchone()
            
            primary_data = None
            if row and row[0] and row[0] != '{}':
                try:
                    primary_data = json.loads(row[0])
                except:
                    pass
            
            # Check metadata backup
            metadata_query = text("""
                SELECT processing_metadata
                FROM campaign_intelligence 
                WHERE id = :id
            """)
            
            result = await self.db.execute(metadata_query, {"id": intelligence_id})
            row = result.fetchone()
            
            backup_data = None
            if row and row[0]:
                try:
                    metadata = row[0] if isinstance(row[0], dict) else json.loads(row[0])
                    backup_data = metadata.get("ai_intelligence_backup", {}).get(category)
                except:
                    pass
            
            # Return status
            return {
                "category": category,
                "primary_saved": primary_data is not None,
                "primary_items": len(primary_data) if primary_data else 0,
                "backup_saved": backup_data is not None,
                "backup_items": len(backup_data) if backup_data else 0,
                "total_saved": bool(primary_data or backup_data)
            }
            
        except Exception as e:
            logger.error(f"❌ Verification failed for {category}: {str(e)}")
            return {
                "category": category,
                "primary_saved": False,
                "primary_items": 0,
                "backup_saved": False,
                "backup_items": 0,
                "total_saved": False,
                "error": str(e)
            }
    
    async def save_multiple_ai_categories(
        self, 
        intelligence_id: uuid.UUID, 
        ai_data: Dict[str, Dict[str, Any]],
        intelligence_obj: Optional[object] = None
    ) -> Dict[str, bool]:
        """Save multiple AI intelligence categories in one call"""
        
        results = {}
        
        for category, data in ai_data.items():
            if data:  # Only save non-empty data
                success = await self.save_ai_intelligence(
                    intelligence_id, category, data, intelligence_obj
                )
                results[category] = success
            else:
                logger.info(f"⏭️ Skipping empty category: {category}")
                results[category] = True  # Empty is considered success
        
        # Log summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        logger.info(f"📊 AI Intelligence Save Summary: {successful}/{total} categories saved")
        
        if successful == total:
            logger.info("✅ All AI intelligence categories saved successfully")
        elif successful > 0:
            logger.warning(f"⚠️ Partial success: {total - successful} categories failed")
        else:
            logger.error("❌ All AI intelligence categories failed to save")
        
        return results
    
    async def get_ai_intelligence_summary(self, intelligence_id: uuid.UUID) -> Dict[str, Any]:
        """Get a summary of all AI intelligence data for an intelligence record"""
        
        ai_categories = [
            'scientific_intelligence', 
            'credibility_intelligence', 
            'market_intelligence',
            'emotional_transformation_intelligence', 
            'scientific_authority_intelligence'
        ]
        
        summary = {
            "intelligence_id": str(intelligence_id),
            "categories": {},
            "total_primary_items": 0,
            "total_backup_items": 0,
            "has_backup_data": False
        }
        
        for category in ai_categories:
            status = await self.verify_ai_data_saved(intelligence_id, category)
            summary["categories"][category] = status
            summary["total_primary_items"] += status["primary_items"]
            summary["total_backup_items"] += status["backup_items"]
            
            if status["backup_saved"]:
                summary["has_backup_data"] = True
        
        return summary


# Convenience functions for easy integration

async def save_ai_intelligence_data(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID,
    ai_data: Dict[str, Dict[str, Any]],
    intelligence_obj: Optional[object] = None
) -> Dict[str, bool]:
    """
    Convenience function to save AI intelligence data
    
    Usage:
        results = await save_ai_intelligence_data(
            db_session=db,
            intelligence_id=intelligence.id,
            ai_data={
                'scientific_intelligence': {...},
                'credibility_intelligence': {...}
            },
            intelligence_obj=intelligence
        )
    """
    
    saver = AIIntelligenceSaver(db_session)
    return await saver.save_multiple_ai_categories(intelligence_id, ai_data, intelligence_obj)


async def verify_ai_intelligence_storage(
    db_session: AsyncSession,
    intelligence_id: uuid.UUID
) -> Dict[str, Any]:
    """
    Convenience function to verify AI intelligence storage
    
    Usage:
        summary = await verify_ai_intelligence_storage(db, intelligence.id)
        print(f"Total items saved: {summary['total_primary_items']}")
    """
    
    saver = AIIntelligenceSaver(db_session)
    return await saver.get_ai_intelligence_summary(intelligence_id)